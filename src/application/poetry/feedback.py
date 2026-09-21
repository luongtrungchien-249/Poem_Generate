"""§24 FEEDBACK LOOP — và cái van giữa phản hồi thô với dữ liệu huấn luyện.

    Raw Feedback -> Quality Review -> Validated Example -> Few-shot / Benchmark

§24 dặn thẳng: *"Feedback không tự động trở thành training data."* Bước Quality
Review ở giữa là toàn bộ lý do tồn tại của file này.

════ VÌ SAO CÁI VAN NÀY QUAN TRỌNG HƠN VẺ NGOÀI ════

Kho few-shot của dự án có một bất biến: mọi ví dụ đều ĐÚNG LUẬT (xem
`poetry/dataset.py`). Nếu phản hồi 👍 của người dùng tự động chảy vào kho ví dụ,
bất biến ấy vỡ trong im lặng — người dùng khen một bài vì nó hay, không vì nó đủ
7 tiếng mỗi dòng.

Vì vậy `duyet_lam_mau()` chạy lại `rule.py`, và một cái 👍 KHÔNG đủ để qua.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypeAlias

# `rule.py` ĐÓNG BĂNG: chỉ đọc.
from application.rule import kiem_tra_bai_tho

DanhGia: TypeAlias = Literal["tot", "xau"]
TrangThaiDuyet: TypeAlias = Literal["cho_duyet", "da_duyet", "tu_choi"]


@dataclass(frozen=True, slots=True)
class PhanHoi:
    """Một bản ghi phản hồi — §24, đủ trường để truy lại toàn bộ ngữ cảnh."""

    trace_id: str
    yeu_cau: str
    bai_tho: str
    danh_gia: DanhGia
    binh_luan: str = ""
    sua_cua_nguoi: str = ""  # người dùng tự sửa lại bài
    quyet_dinh_hitl: str = ""
    so_luot_sua: int = 0


@dataclass(frozen=True, slots=True)
class KetQuaDuyet:
    trang_thai: TrangThaiDuyet
    ly_do: str
    # Văn bản đủ tư cách làm ví dụ mẫu. Rỗng khi chưa duyệt.
    mau: str = ""


def duyet_lam_mau(ph: PhanHoi) -> KetQuaDuyet:
    """Quality Review — quyết định một phản hồi có được thành ví dụ mẫu không.

    Bốn cửa, theo thứ tự. Cửa nào cũng đủ để từ chối.
    """
    # 1. Phản hồi xấu thì không bao giờ thành mẫu. Hiển nhiên, nhưng phải viết ra:
    #    một pipeline gom "mọi phản hồi có nội dung" sẽ nuốt cả phản hồi 👎.
    if ph.danh_gia != "tot":
        return KetQuaDuyet("tu_choi", "người dùng đánh giá không tốt")

    # 2. Ưu tiên bản người dùng TỰ SỬA nếu có — đó là tín hiệu mạnh hơn một cái 👍,
    #    vì họ đã bỏ công viết lại.
    van_ban = ph.sua_cua_nguoi.strip() or ph.bai_tho.strip()
    if not van_ban:
        return KetQuaDuyet("tu_choi", "không có văn bản thơ")

    # 3. ⛔ CỬA QUAN TRỌNG NHẤT: chạy lại luật. Một cái 👍 KHÔNG thay được phán
    #    quyết của `rule.py`. Người dùng khen bài vì nó hay, không vì nó đúng luật.
    v = kiem_tra_bai_tho(van_ban)
    if not v.dat:
        return KetQuaDuyet(
            "tu_choi",
            f"được khen nhưng KHÔNG đạt luật (dừng ở tầng {v.tang_dung_lai}) — "
            "đưa vào kho mẫu sẽ phá bất biến của few-shot",
        )

    # 4. Bài phải sửa quá nhiều lượt mới đạt thì để người xem trước khi thành mẫu.
    if ph.so_luot_sua >= 3:
        return KetQuaDuyet("cho_duyet", f"đạt nhưng mất {ph.so_luot_sua} lượt sửa")

    return KetQuaDuyet("da_duyet", "đạt luật, được đánh giá tốt", mau=van_ban)


@dataclass(slots=True)
class HangDoiPhanHoi:
    """Hàng đợi trong bộ nhớ.

    ⚠️ MẤT KHI RESTART. Bản bền vững thuộc Bước 5 (Postgres) — ADR-0003. Ghi ở đây
    thay vì để người vận hành tự phát hiện sau khi mất dữ liệu.
    """

    da_duyet: list[str] = field(default_factory=list)
    cho_duyet: list[PhanHoi] = field(default_factory=list)
    tu_choi: list[tuple[PhanHoi, str]] = field(default_factory=list)

    def nhan(self, ph: PhanHoi) -> KetQuaDuyet:
        kq = duyet_lam_mau(ph)
        if kq.trang_thai == "da_duyet":
            self.da_duyet.append(kq.mau)
        elif kq.trang_thai == "cho_duyet":
            self.cho_duyet.append(ph)
        else:
            self.tu_choi.append((ph, kq.ly_do))
        return kq
