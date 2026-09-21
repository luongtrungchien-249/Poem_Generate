"""Kho khoá API bền vững — G13.

Thu hồi có hiệu lực NGAY: mỗi request tra thẳng DB, không có bản sao trong bộ nhớ
để mà cũ.

⚠️ ĐÁNH ĐỔI PHẢI NÓI RÕ: một truy vấn DB cho mỗi request. Đó là cái giá của việc
thu hồi tức thì. Muốn nhanh hơn thì phải nhớ đệm, và nhớ đệm bao lâu chính là độ
trễ thu hồi bấy lâu — một cái van, không phải một tối ưu miễn phí. Chưa thêm nhớ
đệm ở đây vì chưa có số đo nào nói rằng nó cần.
"""

from __future__ import annotations

import time

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncEngine

from domain.policy.api_key import BanGhiKhoa, bam_khoa, sinh_khoa

from .bang import khoa_api


class SqlApiKeyStore:
    """`ApiKeyStorePort` trên SQLAlchemy async."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine

    async def tra(self, bam: str) -> BanGhiKhoa | None:
        async with self._engine.connect() as conn:
            hang = (
                await conn.execute(select(khoa_api).where(khoa_api.c.bam == bam))
            ).first()
        if hang is None:
            return None
        return BanGhiKhoa(
            bam=hang.bam,
            tenant_id=hang.tenant_id,
            ten=hang.ten or "",
            tao_luc=float(hang.tao_luc),
            het_han_luc=None if hang.het_han_luc is None else float(hang.het_han_luc),
            thu_hoi_luc=None if hang.thu_hoi_luc is None else float(hang.thu_hoi_luc),
        )

    async def phat_hanh(
        self, tenant_id: str, *, ten: str = "", song_giay: float | None = None
    ) -> str:
        khoa = sinh_khoa()
        bay_gio = time.time()
        async with self._engine.begin() as conn:
            await conn.execute(
                insert(khoa_api).values(
                    # CHỈ băm được ghi. Khoá nguyên văn chỉ tồn tại trong giá trị
                    # trả về của hàm này, và biến mất khi người gọi buông nó.
                    bam=bam_khoa(khoa),
                    tenant_id=tenant_id,
                    ten=ten,
                    tao_luc=bay_gio,
                    het_han_luc=None if song_giay is None else bay_gio + song_giay,
                    thu_hoi_luc=None,
                )
            )
        return khoa

    async def thu_hoi(self, bam: str) -> bool:
        async with self._engine.begin() as conn:
            kq = await conn.execute(
                update(khoa_api)
                .where(khoa_api.c.bam == bam, khoa_api.c.thu_hoi_luc.is_(None))
                .values(thu_hoi_luc=time.time())
            )
        return bool(kq.rowcount)

    # ---- tiện ích vận hành, không thuộc port -------------------------------

    async def nap_tu_cau_hinh(self, bang_khoa: dict[str, str]) -> int:
        """Nạp bảng khoá từ biến môi trường vào kho, nếu chưa có.

        Cầu nối để cấu hình `API_KEYS` cũ vẫn dùng được sau khi chuyển sang kho
        bền vững — nếu không thì mọi triển khai đang chạy sẽ mất hết khoá sau khi
        nâng cấp.

        Ghi khoá cho sẵn vào DB dưới dạng BĂM như mọi khoá khác.
        """
        them = 0
        bay_gio = time.time()
        async with self._engine.begin() as conn:
            for khoa, tenant in bang_khoa.items():
                bam = bam_khoa(khoa)
                co = await conn.scalar(select(khoa_api.c.bam).where(khoa_api.c.bam == bam))
                if co:
                    continue
                await conn.execute(
                    insert(khoa_api).values(
                        bam=bam, tenant_id=tenant, ten="tu_cau_hinh",
                        tao_luc=bay_gio, het_han_luc=None, thu_hoi_luc=None,
                    )
                )
                them += 1
        return them

    async def xoa_han(self, bam: str) -> bool:
        """Xoá hẳn một bản ghi.

        Khác `thu_hoi`: thu hồi GIỮ LẠI dấu vết để truy vết về sau, xoá thì không.
        Dùng cho dọn dẹp dữ liệu test, không dùng cho vận hành.
        """
        async with self._engine.begin() as conn:
            kq = await conn.execute(delete(khoa_api).where(khoa_api.c.bam == bam))
        return bool(kq.rowcount)
