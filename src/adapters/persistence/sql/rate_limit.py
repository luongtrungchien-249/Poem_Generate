"""`RateLimitPort` DÙNG CHUNG giữa các tiến trình.

════ ĐÂY LÀ PHẦN ĐÓNG ĐÚNG KHOẢNG TRỐNG CÒN LẠI CỦA BƯỚC 5 ════

Sau G9, kho quan hệ đã bền vững. Nhưng bộ đếm rate-limit vẫn nằm trong RAM của
từng tiến trình, nên:

    chạy N uvicorn worker  ->  N bộ đếm riêng  ->  hạn mức thực tế NHÂN N

Đó là **lỗ kiểm soát chi phí**, không phải lỗ tiện nghi. Đặt trần 500 lượt gọi
model mỗi ngày rồi chạy 4 worker nghĩa là trần thật là 2.000 — và không ai biết
cho tới lúc nhìn hoá đơn.

`within_daily_budget` là chốt chặn CHI TIỀN, được `verify_output` hỏi lại ở MỖI
lượt sửa. Nó phải đếm trên một nguồn duy nhất.

════ MỘT ĐÁNH ĐỔI PHẢI NÓI RÕ ════

Bộ đếm này chạm DB ở mỗi lần kiểm — chậm hơn bộ đếm trong RAM vài bậc. Đó là cái
giá của việc đếm đúng. Nếu độ trễ thành vấn đề thì lời giải là Redis (Bước 5,
chưa làm), KHÔNG phải quay về đếm trong RAM: đếm nhanh mà sai thì không phải là
kiểm soát chi phí.
"""

from __future__ import annotations

import time

from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from application.ports.rate_limit import Pass, RateLimitOutcome, Silent, Warn
from domain.conversation.thread import ThreadScope

from .bang import dau_vet_goi, ngan_sach_ngay


class SqlRateLimiter:
    """Cửa sổ trượt cho tần suất, bộ đếm theo ngày cho ngân sách — cả hai trong DB."""

    def __init__(
        self,
        engine: AsyncEngine,
        *,
        so_yeu_cau_moi_phut: int = 20,
        nguong_canh_bao: int = 15,
        so_lan_goi_model_moi_ngay: int = 500,
    ) -> None:
        self._engine = engine
        self._max_phut = so_yeu_cau_moi_phut
        self._canh_bao = nguong_canh_bao
        self._max_ngay = so_lan_goi_model_moi_ngay

    @staticmethod
    def _khoa(scope: ThreadScope, sender_id: str) -> str:
        return f"{scope.platform}:{scope.thread_id}:{sender_id}"

    @staticmethod
    def _ngay_hom_nay() -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    async def check(self, scope: ThreadScope, sender_id: str) -> RateLimitOutcome:
        khoa = self._khoa(scope, sender_id)
        bay_gio = time.time()
        nguong = bay_gio - 60.0

        async with self._engine.begin() as conn:
            # Dọn dấu vết quá cũ TRƯỚC khi đếm. Không dọn thì bảng phình vô hạn, và
            # phép đếm phải quét qua toàn bộ lịch sử để bỏ đi phần lớn.
            await conn.execute(
                delete(dau_vet_goi).where(
                    dau_vet_goi.c.khoa == khoa, dau_vet_goi.c.moc < nguong
                )
            )
            so_lan = (
                await conn.scalar(
                    select(func.count()).select_from(dau_vet_goi).where(
                        dau_vet_goi.c.khoa == khoa
                    )
                )
            ) or 0

            if so_lan >= self._max_phut:
                cu_nhat = await conn.scalar(
                    select(func.min(dau_vet_goi.c.moc)).where(dau_vet_goi.c.khoa == khoa)
                )
                cho_ms = int(max(0.0, 60.0 - (bay_gio - float(cu_nhat or bay_gio))) * 1000)
                # Im lặng chứ không báo: trả lời "bạn bị chặn" cho mỗi tin nhắn vượt
                # hạn mức là tự biến bộ chặn thành bộ khuếch đại.
                return Silent(tier="phut", retry_after_ms=cho_ms)

            await conn.execute(insert(dau_vet_goi).values(khoa=khoa, moc=bay_gio))

        return Warn(tier="phut", retry_after_ms=2000) if so_lan + 1 >= self._canh_bao else Pass()

    async def should_warn(self, scope: ThreadScope, sender_id: str) -> bool:
        khoa = self._khoa(scope, sender_id)
        async with self._engine.connect() as conn:
            so_lan = (
                await conn.scalar(
                    select(func.count()).select_from(dau_vet_goi).where(
                        dau_vet_goi.c.khoa == khoa, dau_vet_goi.c.moc >= time.time() - 60.0
                    )
                )
            ) or 0
        return so_lan >= self._canh_bao

    async def within_daily_budget(self, scope: ThreadScope) -> bool:
        """Đếm MỖI lần hỏi, vì mỗi lần hỏi ứng với một lần định gọi model."""
        khoa = f"{scope.platform}:{scope.thread_id}"
        ngay = self._ngay_hom_nay()

        async with self._engine.begin() as conn:
            hien_tai = await conn.scalar(
                select(ngan_sach_ngay.c.so_lan).where(
                    ngan_sach_ngay.c.khoa == khoa, ngan_sach_ngay.c.ngay == ngay
                )
            )
            if hien_tai is None:
                await conn.execute(
                    insert(ngan_sach_ngay).values(khoa=khoa, ngay=ngay, so_lan=1)
                )
                return True
            if int(hien_tai) >= self._max_ngay:
                return False
            # Cộng dồn bằng biểu thức SQL, KHÔNG bằng `so_lan = hien_tai + 1`: hai
            # tiến trình đọc cùng một giá trị rồi cùng ghi sẽ mất một lượt đếm, và
            # trần ngân sách bị nới ra âm thầm.
            await conn.execute(
                update(ngan_sach_ngay)
                .where(ngan_sach_ngay.c.khoa == khoa, ngan_sach_ngay.c.ngay == ngay)
                .values(so_lan=ngan_sach_ngay.c.so_lan + 1)
            )
        return True
