"""YÊU CẦU NGƯỜI DÙNG + CỔNG THÔNG TIN ĐẦY ĐỦ — thi hành chỉ thị 5.

    *"Cần thỏa mãn đầy đủ mọi thông tin trước khi cho thơ cho người dùng."*
    — chủ dự án, 21/09/2026

Cổng này CHẶN. Thiếu thông tin thì hệ thống hỏi lại, KHÔNG sinh thơ rồi xin lỗi sau.

VÌ SAO MỖI TRƯỜNG PHẢI MANG THEO NGUỒN
    Tài liệu đích §3.2 cấm *"tự suy đoán khi thông tin quan trọng bị thiếu"*. Nhưng
    một `PoetryRequirement` chỉ có giá trị mà không có nguồn thì không ai kiểm được
    là hệ thống đã HỎI hay đã ĐOÁN — cả hai đều cho ra cùng một object.

    Vì vậy mỗi trường là một `Truong(gia_tri, nguon)`. Trường mang `suy_doan` không
    bao giờ được qua cổng. Đây là nguyên tắc N3 (*ghi công khai điều không kiểm
    được*) áp cho tầng yêu cầu.

NĂM CA HỎI LẠI
    ca 0  có trường mang nguồn `suy_doan`         — §3.2 cấm tự suy đoán
    ca 1  thiếu chủ đề                            — §8.2 tài liệu đích
    ca 2  mâu thuẫn thể loại (tự do + Đường luật) — §8.2
    ca 3  ràng buộc vần mơ hồ                     — §8.2
    ca 4  số dòng có, nhưng không phải bội của 4  — QĐ-D5
    ca 5  KHÔNG nói số dòng                       — chủ dự án, 21/09/2026
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal, TypeAlias

# `rule.py` ĐÓNG BĂNG: chỉ đọc đúng một hằng số, không import gì có thể ghi.
from application.rule import SO_TIENG_MOI_DONG

MA_THE_MAC_DINH = "that_ngon_tu_do"

NguonTruong: TypeAlias = Literal["nguoi_dung", "mac_dinh", "suy_doan"]


@dataclass(frozen=True, slots=True)
class Truong:
    """Một trường yêu cầu, kèm nguồn gốc của nó.

    `nguon` không phải siêu dữ liệu trang trí — nó là thứ cổng B1 kiểm.
    """

    gia_tri: object
    nguon: NguonTruong

    @property
    def co_gia_tri(self) -> bool:
        gt = self.gia_tri
        if gt is None:
            return False
        return bool(str(gt).strip()) if isinstance(gt, str) else True


def nguoi_dung(gia_tri: object) -> Truong:
    return Truong(gia_tri=gia_tri, nguon="nguoi_dung")


def mac_dinh(gia_tri: object) -> Truong:
    return Truong(gia_tri=gia_tri, nguon="mac_dinh")


def suy_doan(gia_tri: object) -> Truong:
    """Dùng khi mô hình tự đoán. Trường loại này KHÔNG qua được cổng B1."""
    return Truong(gia_tri=gia_tri, nguon="suy_doan")


TRONG = Truong(gia_tri=None, nguon="mac_dinh")


@dataclass(frozen=True, slots=True)
class PoetryRequirement:
    """Yêu cầu đã chuẩn hoá — §7.2 của tài liệu đích, cộng `nguon` từng trường.

    `the_tho` cố định ở bản này. Thêm thể khác là quyết định kiến trúc, không phải
    thêm một chuỗi.
    """

    chu_de: Truong = TRONG
    so_dong: Truong = TRONG
    cam_xuc: Truong = TRONG
    phong_cach: Truong = TRONG
    rang_buoc_van: Truong = TRONG
    rang_buoc_thanh: Truong = TRONG
    van_ban_goc: str = ""
    the_tho: str = MA_THE_MAC_DINH

    def cac_truong(self) -> tuple[tuple[str, Truong], ...]:
        return (
            ("chu_de", self.chu_de),
            ("so_dong", self.so_dong),
            ("cam_xuc", self.cam_xuc),
            ("phong_cach", self.phong_cach),
            ("rang_buoc_van", self.rang_buoc_van),
            ("rang_buoc_thanh", self.rang_buoc_thanh),
        )

    @property
    def so_dong_int(self) -> int | None:
        gt = self.so_dong.gia_tri
        return gt if isinstance(gt, int) else None


# ══════════════════════════════════════════════════════════════════════════════
# CỔNG THÔNG TIN ĐẦY ĐỦ
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class DuThongTin:
    """Đã đủ để sang bước lập kế hoạch."""

    bang_chung: str


@dataclass(frozen=True, slots=True)
class CanHoi:
    """Chưa đủ. `cau_hoi` là thứ gửi thẳng cho người dùng."""

    ca: int
    cau_hoi: str
    ly_do: str
    truong_thieu: tuple[str, ...]


KetQuaCong: TypeAlias = DuThongTin | CanHoi

# Ca 2 — người dùng vừa xin thất ngôn tự do vừa đòi luật Đường. Hai vế loại trừ
# nhau: F1–F4 đã GỠ BỎ niêm/đối/độc vận khỏi thể này.
_DAU_HIEU_DUONG_LUAT = re.compile(
    r"\b(bát\s*cú|bat\s*cu|đường\s*luật|duong\s*luat|tứ\s*tuyệt|tu\s*tuyet|niêm|niem)\b",
    re.IGNORECASE,
)
_DAU_HIEU_TU_DO = re.compile(r"\b(tự\s*do|tu\s*do)\b", re.IGNORECASE)

# Ca 3 — ràng buộc vần nói bằng tính từ, không nói bằng sơ đồ. "Chặt" là chặt thế
# nào: độc vận cả bài, hay chỉ cần vần chính thay vì vần thông? Hai cách hiểu cho
# ra hai bài khác hẳn nhau, nên phải hỏi.
_VAN_MO_HO = re.compile(
    r"\bvần\b[^.,;\n]{0,20}\b(chặt|chat|chuẩn|chuan|nghiêm|nghiem|đẹp|dep)\b",
    re.IGNORECASE,
)


def danh_gia_du_thong_tin(req: PoetryRequirement) -> KetQuaCong:
    """Cổng B1. Trả `CanHoi` ngay khi gặp ca đầu tiên chưa thoả.

    THỨ TỰ KIỂM theo đúng §8.2 tài liệu đích, rồi tới QĐ-D5. Mỗi lần chỉ hỏi MỘT
    câu — hỏi dồn bốn câu một lúc là đẩy việc của hệ thống sang cho người dùng.
    `truong_thieu` vẫn liệt kê đủ để tầng trên biết còn thiếu bao nhiêu.

    KHÔNG hàm nào ở đây được tự điền giá trị. Cổng này chỉ phán *đủ* hay *chưa đủ*.
    """
    thieu = tuple(ten for ten, t in req.cac_truong() if not t.co_gia_tri)
    doan = tuple(ten for ten, t in req.cac_truong() if t.nguon == "suy_doan")

    # Trường suy đoán kiểm TRƯỚC mọi ca khác: một trường có giá trị nhưng do máy
    # đoán còn nguy hiểm hơn một trường trống, vì nó trông như đã có thông tin.
    if doan:
        return CanHoi(
            ca=0,
            cau_hoi=(
                "Tôi chưa chắc về "
                + ", ".join(doan)
                + ". Bạn xác nhận giúp để tôi không tự đoán nhé?"
            ),
            ly_do=f"các trường {', '.join(doan)} đang mang nguồn 'suy_doan'",
            truong_thieu=doan,
        )

    # Ca 1 — thiếu chủ đề. Đây là ví dụ chính của §3.2: "Viết cho tôi một bài thơ."
    if not req.chu_de.co_gia_tri:
        return CanHoi(
            ca=1,
            cau_hoi="Bạn muốn bài thơ viết về chủ đề nào?",
            ly_do="chưa có chủ đề",
            truong_thieu=thieu,
        )

    # Ca 2 — mâu thuẫn thể loại.
    goc = req.van_ban_goc
    if _DAU_HIEU_DUONG_LUAT.search(goc) and _DAU_HIEU_TU_DO.search(goc):
        return CanHoi(
            ca=2,
            cau_hoi=(
                "Bạn muốn ưu tiên đặc trưng thất ngôn tự do, hay áp dụng luật "
                "bằng-trắc của thất ngôn bát cú?"
            ),
            ly_do="yêu cầu vừa nêu thơ tự do vừa nêu luật Đường — hai vế loại trừ nhau",
            truong_thieu=thieu,
        )

    # Ca 3 — ràng buộc vần mơ hồ.
    if _VAN_MO_HO.search(goc) and not req.rang_buoc_van.co_gia_tri:
        return CanHoi(
            ca=3,
            cau_hoi=(
                "Bạn muốn vần chân theo một sơ đồ cố định (ví dụ aabb, abab), "
                "hay chỉ cần duy trì liên kết vần tự nhiên?"
            ),
            ly_do='yêu cầu nói vần "chặt" nhưng chưa nói chặt theo nghĩa nào',
            truong_thieu=thieu,
        )

    # Ca 4 — QĐ-D5. H4 là luật CỨNG: số dòng phải là bội của 4.
    #
    # Chặn ở ĐÂY chứ không ở vòng sửa là có chủ đích. `rule.py::_tang1_hinh_thuc`
    # đã dặn: với thơ do mô hình sinh ra, ràng buộc này thuộc về ĐỀ BÀI, không
    # phải về vòng sửa một bản nháp đã có — vì "sửa" H4 nghĩa là thêm hoặc xoá một
    # câu thơ, điều nguyên tắc P2 cấm.
    n = req.so_dong_int
    if n is not None and (n <= 0 or n % 4 != 0):
        gan = max(4, (n // 4) * 4)
        return CanHoi(
            ca=4,
            cau_hoi=(
                f"Số dòng của thể này phải là bội của 4, nhưng bạn yêu cầu {n} dòng. "
                f"Bạn muốn {gan} dòng hay {gan + 4} dòng?"
            ),
            ly_do=f"H4 là luật cứng, {n} không chia hết cho 4",
            truong_thieu=thieu,
        )

    # Ca 5 — KHÔNG NÓI số dòng. Bổ sung 21/09/2026 theo chủ dự án:
    #
    #     "Nếu người dùng không yêu cầu số dòng thì tôi cần bạn hỏi lại số dòng
    #      (bao nhiêu dòng cũng được nhưng cần phải là bội của 4)"
    #
    # VÌ SAO ĐÂY LÀ CA CHẶN CHỨ KHÔNG PHẢI MỘT MẶC ĐỊNH HỢP LÝ. Thoạt nhìn có thể
    # chọn 8 dòng rồi đi tiếp. Nhưng số dòng quyết định bài thơ ra sao — một bài 4
    # dòng và một bài 16 dòng là hai tác phẩm khác hẳn nhau, không phải hai biến
    # thể của cùng một bài. Tự chọn hộ là quyết định thay tác giả.
    #
    # Chú ý CÂU CHỮ của câu hỏi: nó phải nói rõ CẢ HAI vế, đúng như F5 + H4 đã hợp
    # nhất — không giới hạn về LƯỢNG, nhưng ràng buộc về HÌNH DẠNG. Hỏi cụt thành
    # "bạn muốn bao nhiêu dòng?" thì người dùng sẽ trả lời 6 hoặc 10 và phải hỏi
    # lại lần nữa ở ca 4; hỏi cụt thành "4 hay 8?" thì lại bịa ra một giới hạn mà
    # luật không có.
    if n is None:
        return CanHoi(
            ca=5,
            cau_hoi=(
                "Bạn muốn bài thơ dài bao nhiêu dòng? Bao nhiêu dòng cũng được, "
                "nhưng phải là bội của 4 — ví dụ 4, 8, 12, 16…"
            ),
            ly_do="chưa có số dòng; số dòng quyết định hình dạng bài thơ nên không tự chọn hộ",
            truong_thieu=thieu,
        )

    # Tới đây thì chủ đề và số dòng — hai trường QUYẾT ĐỊNH bài thơ ra sao — đều đã
    # có. Các trường còn lại (cảm xúc, phong cách, ràng buộc vần/thanh) không đổi
    # việc bài có đúng luật hay không, nên chúng KHÔNG chặn; `truong_thieu` vẫn liệt
    # kê đủ để tầng trên biết còn thiếu gì mà hỏi thêm nếu muốn.
    return DuThongTin(
        bang_chung=(
            f"đủ thông tin: chủ đề={req.chu_de.gia_tri!r}"
            + f", {n} dòng (= 4 × {n // 4})"
            + f"; không trường nào mang nguồn 'suy_doan'; mỗi dòng {SO_TIENG_MOI_DONG} tiếng"
        )
    )
