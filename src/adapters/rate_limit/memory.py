"""`RateLimitPort` in-memory — cho dev và test.

⚠️ HẠN CHẾ PHẢI BIẾT, ghi ở đây thay vì để người vận hành tự phát hiện:

    khởi động lại tiến trình  -> mất sạch bộ đếm, hạn mức reset về 0
    chạy nhiều uvicorn worker -> mỗi tiến trình một bộ đếm riêng, nên hạn mức
                                 thực tế bị nhân lên bằng số worker

Nghĩa là bản này KHÔNG dùng được ở production như một cơ chế kiểm soát chi phí.
Nó tồn tại để đường thơ có đủ ba port mà chạy được ngay hôm nay. Bản Redis dùng
chung giữa các tiến trình thuộc Bước 5 — xem `docs/adr/0003-lo-trinh-adapter-that.md`.

`within_daily_budget` là chốt chặn CHI TIỀN, được `verify_output` hỏi lại ở MỖI
lượt sửa chứ không hỏi một lần rồi tin mãi — vì mỗi lượt sửa là một lần gọi model
có tính tiền.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque

from application.ports.rate_limit import Pass, RateLimitOutcome, Silent, Warn
from domain.conversation.thread import ThreadScope


class InMemoryRateLimiter:
    """Cửa sổ trượt cho tần suất, bộ đếm theo ngày cho ngân sách."""

    def __init__(
        self,
        *,
        so_yeu_cau_moi_phut: int = 20,
        nguong_canh_bao: int = 15,
        so_lan_goi_model_moi_ngay: int = 500,
    ) -> None:
        self._max_phut = so_yeu_cau_moi_phut
        self._canh_bao = nguong_canh_bao
        self._max_ngay = so_lan_goi_model_moi_ngay
        self._dau_vet: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._dem_ngay: dict[tuple[str, str], int] = defaultdict(int)

    @staticmethod
    def _khoa(scope: ThreadScope, sender_id: str) -> tuple[str, str]:
        return (f"{scope.platform}:{scope.thread_id}", sender_id)

    @staticmethod
    def _ngay_hom_nay() -> str:
        return time.strftime("%Y-%m-%d", time.gmtime())

    def _don(self, khoa: tuple[str, str], bay_gio: float) -> deque[float]:
        q = self._dau_vet[khoa]
        while q and bay_gio - q[0] > 60.0:
            q.popleft()
        return q

    async def check(self, scope: ThreadScope, sender_id: str) -> RateLimitOutcome:
        bay_gio = time.monotonic()
        khoa = self._khoa(scope, sender_id)
        q = self._don(khoa, bay_gio)

        if len(q) >= self._max_phut:
            # Im lặng chứ không báo: trả lời "bạn bị chặn" cho mỗi tin nhắn vượt hạn
            # mức là tự biến bộ chặn thành bộ khuếch đại.
            return Silent(tier="phut", retry_after_ms=int((60.0 - (bay_gio - q[0])) * 1000))

        q.append(bay_gio)
        if len(q) >= self._canh_bao:
            return Warn(tier="phut", retry_after_ms=2000)
        return Pass()

    async def should_warn(self, scope: ThreadScope, sender_id: str) -> bool:
        q = self._don(self._khoa(scope, sender_id), time.monotonic())
        return len(q) >= self._canh_bao

    async def within_daily_budget(self, scope: ThreadScope) -> bool:
        """Đếm MỖI lần hỏi, vì mỗi lần hỏi ứng với một lần định gọi model."""
        khoa = (f"{scope.platform}:{scope.thread_id}", self._ngay_hom_nay())
        if self._dem_ngay[khoa] >= self._max_ngay:
            return False
        self._dem_ngay[khoa] += 1
        return True
