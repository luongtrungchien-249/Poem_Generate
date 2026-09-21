"""§33.3 — metric LUẬT THƠ, đo bằng `rule.py`.

════ LỢI THẾ HIẾM: KHÔNG CẦN GÁN NHÃN TAY ════

Hầu hết hệ thống sinh văn bản không có thước đo khách quan nào, nên phải thuê người
chấm. Ở đây `rule.py` LÀ ground truth: tất định, giải thích được, và cùng một bộ
luật dùng để chấm cũng là bộ luật dùng để chặn đầu ra.

Nghĩa là §33.3 đo được chính xác, không có sai số của người chấm.

⚠️ NHƯNG PHẢI NÓI RÕ GIỚI HẠN. Đo bằng chính bộ kiểm đang chặn đầu ra thì metric
này KHÔNG trả lời được "bộ luật có đúng không" — nó chỉ trả lời "mô hình có tuân
bộ luật không". Hai câu hỏi khác nhau, và câu đầu chỉ người đọc thơ trả lời được.
"""

from __future__ import annotations

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from application.poetry.quality import danh_gia_chat_luong  # noqa: E402
from application.rule import kiem_tra_bai_tho  # noqa: E402


@dataclass(frozen=True, slots=True)
class DoLuongTho:
    """§33.3. Mọi tỉ lệ tính trên SỐ BÀI, không phải số dòng.

    Đơn vị phán quyết là BÀI — một bài 32 dòng có 31 dòng hoàn hảo và 1 dòng sai
    là bài hỏng, không phải "bài đạt 97%". Trộn hai đơn vị là cách làm đẹp số liệu
    mà không làm đẹp sản phẩm.
    """

    so_bai: int
    ty_le_dat: float  # qua cả bảy tầng
    ty_le_thuoc_the: float  # chỉ H1–H4
    ty_le_dung_so_tieng: float  # tầng 2
    ty_le_dung_khuon: float  # tầng 4 — nút cổ chai
    ty_le_co_van_chan: float  # tầng 5
    ty_le_dat_chat_luong: float
    chan_theo_tang: dict[int, int]  # tầng nào chặn bao nhiêu bài

    def to_dict(self) -> dict[str, object]:
        return {
            "so_bai": self.so_bai,
            "ty_le_dat": self.ty_le_dat,
            "ty_le_thuoc_the": self.ty_le_thuoc_the,
            "ty_le_dung_so_tieng": self.ty_le_dung_so_tieng,
            "ty_le_dung_khuon": self.ty_le_dung_khuon,
            "ty_le_co_van_chan": self.ty_le_co_van_chan,
            "ty_le_dat_chat_luong": self.ty_le_dat_chat_luong,
            "chan_theo_tang": self.chan_theo_tang,
        }


def _ty_le(n: int, tong: int) -> float:
    return round(n / tong, 4) if tong else 0.0


def do_luong_tho(cac_bai: list[str], *, chu_de: str | None = None) -> DoLuongTho:
    """Chấm một tập bài. Bài rỗng vẫn được tính vào mẫu số.

    Loại bài rỗng khỏi mẫu số sẽ làm tỉ lệ đạt đẹp lên mà chất lượng không đổi —
    đúng kiểu nắn số liệu mà §1.1 của plan luật cấm.
    """
    tong = len(cac_bai)
    dat = thuoc_the = so_tieng = khuon = van = chat_luong = 0
    chan: Counter[int] = Counter()

    for bai in cac_bai:
        v = kiem_tra_bai_tho(bai)
        if v.dat:
            dat += 1
        if v.thuoc_the:
            thuoc_the += 1
        if v.tang_dung_lai:
            chan[v.tang_dung_lai] += 1

        theo_tang = {t.so: t for t in v.tang}
        if theo_tang[2].da_chay and theo_tang[2].dat:
            so_tieng += 1
        if theo_tang[4].da_chay and theo_tang[4].dat:
            khuon += 1
        if theo_tang[5].da_chay and theo_tang[5].dat:
            van += 1

        if danh_gia_chat_luong(v, chu_de=chu_de).dat:
            chat_luong += 1

    return DoLuongTho(
        so_bai=tong,
        ty_le_dat=_ty_le(dat, tong),
        ty_le_thuoc_the=_ty_le(thuoc_the, tong),
        ty_le_dung_so_tieng=_ty_le(so_tieng, tong),
        ty_le_dung_khuon=_ty_le(khuon, tong),
        ty_le_co_van_chan=_ty_le(van, tong),
        ty_le_dat_chat_luong=_ty_le(chat_luong, tong),
        chan_theo_tang=dict(sorted(chan.items())),
    )
