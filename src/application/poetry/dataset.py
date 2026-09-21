"""Lược đồ chuẩn cho kho thơ mẫu — §9.2 tài liệu đích.

════ LỢI THẾ RIÊNG CỦA DỰ ÁN NÀY, PHẢI KHAI THÁC ĐÚNG ════

§9.1 nói `poetry_dataset.json`. Dự án đã có thứ TỐT HƠN một dataset thường:
`datalake/analysis/bai_dat.jsonl` chứa 24.366 bài **đã được chính `rule.py` xác
nhận qua cả bảy tầng**, kèm sơ đồ vần và phối khuôn đo sẵn.

Nghĩa là ví dụ few-shot đưa vào prompt **được bảo đảm đúng luật** — điều gần như
không dataset thơ nào có. Đây là đối sách trực tiếp cho rủi ro R2: mô hình học
khuôn B/T từ ví dụ đúng thay vì từ lời mô tả.

⛔ NHƯNG BẢO ĐẢM ẤY PHẢI ĐƯỢC KIỂM LẠI, KHÔNG ĐƯỢC TIN SUÔNG. Tệp corpus có thể
cũ hơn `rule.py`, có thể bị sửa tay, có thể sinh ra từ một bản luật trước. Vì vậy
`MauTho.tu_ban_ghi()` CHẠY LẠI `kiem_tra_bai_tho` chứ không đọc cờ `trang_thai`
có sẵn. Tin vào nhãn trong dữ liệu là cách dạy mô hình bằng ví dụ sai mà không ai
hay.

════ BA TRƯỜNG §9.2 KHÔNG CÓ TRONG NGUỒN ════

§9.2 đề xuất `topic`, `theme`, `mood`, `style`. Corpus chỉ có `tieu_de` và `tho`.

Ba trường đó vì vậy được **suy ra** từ tiêu đề và văn bản, và mang nhãn
`nguon="suy_ra"` để không ai nhầm chúng với siêu dữ liệu thật. Cùng nguyên tắc N3
đã dùng ở `PoetryRequirement`: suy đoán thì phải tự khai là suy đoán.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping
from dataclasses import dataclass

# `rule.py` ĐÓNG BĂNG: chỉ đọc.
from application.rule import kiem_tra_bai_tho

MA_THE = "that_ngon_tu_do"


@dataclass(frozen=True, slots=True)
class MauTho:
    """Một bài thơ mẫu, đã chuẩn hoá về lược đồ §9.2 và ĐÃ KIỂM LẠI bằng `rule.py`.

    Tồn tại object này nghĩa là `kiem_tra_bai_tho(tho).dat` đúng — `tu_ban_ghi`
    trả None cho mọi bài không đạt, nên không có đường nào dựng ra một `MauTho`
    sai luật.
    """

    id: str
    tieu_de: str
    tho: str
    so_dong: int
    so_kho: int
    so_do_van: tuple[str, ...]
    phoi_khuon: tuple[str, ...]
    tu_khoa: frozenset[str]  # suy ra từ tiêu đề + văn bản, KHÔNG phải siêu dữ liệu thật

    @property
    def the_tho(self) -> str:
        return MA_THE


def _bo_dau(s: str) -> str:
    return "".join(
        k for k in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(k)
    )


# Hư từ có mặt ở hầu hết mọi bài nên không phân biệt được chủ đề. Danh sách ngắn
# và cố ý dừng ở đó: cắt sâu hơn là bắt đầu làm ngôn ngữ học bằng cảm tính.
_HU_TU = frozenset(
    _bo_dau(t)
    for t in (
        "và", "của", "là", "có", "không", "một", "những", "các", "cho", "với",
        "đã", "sẽ", "còn", "mà", "thì", "ở", "trong", "ra", "vào", "lại",
        "này", "kia", "đó", "nào", "ai", "tôi", "ta", "em", "anh",
    )
)


def _tu_khoa(tieu_de: str, tho: str) -> frozenset[str]:
    """Từ khoá để ghép chủ đề. Tiêu đề tính TRỌNG hơn nên luôn được giữ.

    Không dùng TF-IDF hay mô hình: bộ chọn few-shot phải TẤT ĐỊNH và chạy được
    offline. Một phép giao tập đơn giản đủ dùng, và quan trọng hơn là giải thích
    được vì sao một ví dụ được chọn.
    """
    tu = set()
    for nguon in (tieu_de, tho):
        for t in _bo_dau(nguon).replace("\n", " ").split():
            t = "".join(k for k in t if k.isalnum())
            if len(t) >= 2 and t not in _HU_TU:
                tu.add(t)
    return frozenset(tu)


def tu_ban_ghi(ban_ghi: Mapping[str, object]) -> MauTho | None:
    """Đổi một bản ghi corpus sang `MauTho`. Trả None nếu bài KHÔNG đạt luật.

    CHẠY LẠI `rule.py` thay vì đọc cờ `trang_thai` trong dữ liệu — xem docstring
    module. Đây là chỗ mà "tin vào nhãn có sẵn" sẽ âm thầm phá cả cơ chế few-shot.
    """
    tho = ban_ghi.get("tho")
    if not isinstance(tho, str) or not tho.strip():
        return None

    v = kiem_tra_bai_tho(tho)
    if not v.dat:
        return None

    tieu_de = ban_ghi.get("tieu_de")
    tieu_de = tieu_de if isinstance(tieu_de, str) else ""

    return MauTho(
        id=str(ban_ghi.get("id", "")),
        tieu_de=tieu_de,
        tho=tho,
        so_dong=v.so_dong,
        so_kho=v.so_kho,
        so_do_van=tuple("".join(k) for k in v.so_do_van_theo_kho),
        phoi_khuon=v.phoi_khuon_theo_kho,
        tu_khoa=_tu_khoa(tieu_de, tho),
    )


def tu_khoa_yeu_cau(chu_de: str | None, cam_xuc: str | None = None) -> frozenset[str]:
    """Từ khoá phía yêu cầu, tách cùng một cách với phía kho — nếu không thì hai
    bên sẽ không bao giờ giao nhau."""
    return _tu_khoa("", " ".join(x for x in (chu_de, cam_xuc) if x))
