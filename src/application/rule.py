"""LUẬT THƠ THẤT NGÔN TỰ DO — đặc tả thi hành được.

Nguồn luật: `docs/Luat_Tho_That_Ngon_Tu_Do.md`.
File này là bản *cưỡng chế được* của tài liệu đó: mỗi điều luật vừa là một dòng dữ
liệu trong bảng `LUAT`, vừa có một hàm kiểm tương ứng. Tài liệu nào không cưỡng chế
được thì sớm muộn sẽ lệch khỏi mã nguồn mà không ai hay.

BỐ CỤC FILE
    §1  Bảng mã luật            H / S / F dưới dạng dữ liệu
    §2  Kiểu dữ liệu kết quả    Violation, BaoCaoDong, PoemVerdict
    §3  Đếm âm tiết             phục vụ H1, H2
    §4  Thanh điệu B/T          phục vụ S1–S3
    §5  Tách vần và hiệp vần    phục vụ S6–S12
    §6  Khuôn luân phiên        phục vụ S2, §4.2–4.3 của tài liệu
    §7  Sơ đồ vần               phục vụ §9 Bước 3
    §8  Loại trừ Đường luật     phục vụ §9 Bước 2
    §9  Hàm kiểm tổng           kiem_tra_bai_tho()

RANH GIỚI THẨM QUYỀN — đọc trước khi sửa file này
    Chỉ H1, H2, H3 có quyền đặt `PoemVerdict.dat = False`.
    Mọi quy tắc S chỉ được *mô tả*, không được loại bài. Đây là §9 Bước 4 của tài
    liệu: các lựa chọn mềm dùng để đánh giá bài chặt hay lỏng, không dùng để loại.

    Bộ kiểm *phán*, mô hình *sửa*. Không hàm nào trong file này được sửa văn bản
    thơ. Sửa bằng code là âm thầm thay đổi tác phẩm rồi ghi lại như thể mô hình
    viết ra như thế.

CÁC QUYẾT ĐỊNH CÀI ĐẶT (tài liệu luật để mở, ghi rõ ở đây)
    Đ1  Phép loại trừ Đường luật chỉ *cảnh báo*, không chặn — vì kiểm "đối" tự động
        không đủ tin cậy để loại bài khỏi thể.
    Đ2  Chuẩn đọc số: văn viết miền Bắc — "nghìn", "mươi lăm", "mươi mốt", "mươi tư",
        "linh". Cần tất định vì H1 phụ thuộc vào nó.
    Đ3  Vần được phép lệch thanh (ví dụ §11 của tài liệu dùng "xanh" B với "mảnh" T),
        nhưng báo cáo tách riêng hai loại.
    Đ4  Bảng vần thông là hằng số module, không đọc từ cấu hình. Sửa bảng thì test
        ngữ liệu vàng phải xanh lại.
    Đ6  Ranh giới khổ là dòng trống. Tài liệu chỉ quy định phân dòng (H3), phân khổ
        là quy ước cài đặt.
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Literal, TypeAlias

# ══════════════════════════════════════════════════════════════════════════════
# §1. BẢNG MÃ LUẬT
#
# Tài liệu luật được nạp vào đây dưới dạng DỮ LIỆU, không phải chú thích. Nhờ đó
# một test có thể đối chiếu: mọi điều luật loại "cung" đều phải có hàm kiểm trong
# `HAM_KIEM_CUNG`. Thêm một luật cứng mới mà quên viết hàm kiểm thì test đỏ.
# ══════════════════════════════════════════════════════════════════════════════

LoaiLuat: TypeAlias = Literal["cung", "mem", "loai_bo"]


@dataclass(frozen=True, slots=True)
class DieuLuat:
    ma: str
    thanh_phan: str
    noi_dung: str
    loai: LoaiLuat


LUAT: tuple[DieuLuat, ...] = (
    # --- Ràng buộc cứng: điều kiện nhận diện thể (tài liệu §2) ---
    DieuLuat("H1", "Độ dài dòng", "Mỗi dòng phải có đúng 7 tiếng", "cung"),
    DieuLuat("H2", "Phạm vi áp dụng", "H1 áp dụng cho toàn bộ các dòng, không ngoại lệ", "cung"),
    DieuLuat("H3", "Hình thức",
             "Văn bản phải được phân dòng, từ 4 dòng trở lên", "cung"),
    # H4 do chủ dự án bổ sung ngày 18/09/2026, nguyên văn: "số dòng trong mỗi bài
    # thơ là bội của 4 (đây là Rule cứng không có ngoại lệ)".
    #
    # H4 thoạt nhìn chọi với F5 và S16, nên chủ dự án đã cho HỢP NHẤT cả ba thay vì
    # để một bên ghi đè bên kia. Ba điều nay nói cùng một chuyện, không chồng chéo:
    #     F5, S16  số dòng KHÔNG GIỚI HẠN VỀ LƯỢNG  (không trần, không sàn cố định)
    #     H4       số dòng PHẢI LÀ BỘI CỦA 4        (ràng buộc hình dạng)
    # Tập hợp lệ là {4, 8, 12, 16, ...} — vừa vô hạn vừa chia hết cho 4.
    DieuLuat("H4", "Số dòng", "Số dòng trong bài phải là bội của 4", "cung"),
    # --- Điều bị loại khỏi thể: không sinh ra phép kiểm nào (tài liệu §3) ---
    DieuLuat("F1", "Niêm", "Không áp dụng luật niêm giữa các dòng", "loai_bo"),
    DieuLuat("F2", "Đối", "Không yêu cầu cặp đối bắt buộc", "loai_bo"),
    DieuLuat("F3", "Vần", "Không yêu cầu độc vận cho toàn bài", "loai_bo"),
    DieuLuat("F4", "Bố cục", "Không yêu cầu Khai – Thừa – Chuyển – Hợp", "loai_bo"),
    # F5 + S16 hợp nhất 18/09/2026 theo chủ dự án: "gộp lại sửa thành bội của 4,
    # và không giới hạn số dòng". Hai vế nói về HAI CHUYỆN KHÁC NHAU nên cùng đúng:
    #   "không giới hạn số dòng" -> về LƯỢNG, không có trần cũng không có sàn cố định
    #   "bội của 4"              -> về HÌNH DẠNG, tập {4, 8, 12, ...} vẫn vô hạn
    DieuLuat("F5", "Số dòng",
             "Số dòng không giới hạn về lượng, nhưng phải là bội của 4", "loai_bo"),
    # --- Thanh luật (tài liệu §4) ---
    # S1 sửa lời 18/09/2026 theo chủ dự án: "P1, P3, P5 CÓ THỂ tự do". Chữ "có
    # thể" thay "hoàn toàn" giữ nguyên tính chất QUYỀN của điều, và nói đúng hơn:
    # tự do là thứ tác giả ĐƯỢC dùng, không phải thứ bắt buộc phải dùng.
    #
    # S7 GỘP VÀO S1 cùng ngày. Lý do của chủ dự án: "S7 không được liên quan ở
    # phần vần". Vần lưng ở P4/P5 là một QUYỀN về vị trí trong dòng, cùng loại
    # với quyền tự do thanh ở P1/P3/P5 — nó không nói gì về sơ đồ vần giữa các
    # dòng, vốn là việc của tầng 5. Gộp vào S1 để mỗi điều ở đúng chỗ của nó.
    DieuLuat("S1", "Thanh luật",
             "P1, P3, P5 có thể tự do về thanh; có thể dùng thêm vần lưng ở P4 hoặc P5",
             "mem"),
    DieuLuat("S2", "Thanh luật", "P2, P4, P6 nên luân phiên bằng – trắc", "mem"),
    DieuLuat("S3", "Thanh luật", "P7 gắn với vần, cần chọn có chủ đích", "mem"),
    # S4 và S5 ĐÃ XOÁ ngày 18/09/2026 theo chủ dự án: "Xóa mã S4, S5 luôn đi vì
    # chưa có cho bài hiện tại". S4 là quyền phá khuôn, S5 là cách phá khuôn cho
    # khéo; QĐ-2 đã cấm phá khuôn nên cả hai không còn đối tượng.
    #
    # SỐ HIỆU KHÔNG ĐÁNH LẠI. S4, S5, S7 để trống vĩnh viễn. Dồn S6 lên thành S4
    # sẽ khiến mọi tham chiếu cũ trong báo cáo, test và dữ liệu đã xuất trỏ sai
    # điều luật mà không ai biết — im lặng và không sửa được.
    # --- Vần (tài liệu §5) ---
    DieuLuat("S6", "Vần", "Vần chủ đạo là vần chân, đặt ở P7", "mem"),
    # S8 ĐÃ XOÁ ngày 18/09/2026. Nguyên văn cũ: "Bài có thể không gieo vần".
    #
    # Lý do: QĐ-7b đặt tiêu chí "cụm bốn dòng phải có ít nhất một cặp hiệp vần
    # chân", tức là loại đúng những bài KHÔNG gieo vần. Giữ S8 lại thì bảng luật
    # vừa cho phép vừa cấm cùng một chuyện — và nguyên tắc N2 (điều loại QUYỀN
    # không bao giờ được đánh trượt) sẽ bị vi phạm ngay tại tầng 5.
    #
    # Chủ dự án chọn XOÁ thay vì ghi vào GHI_DE_BOI_QUYET_DINH: không còn điều
    # nào cho phép bài không vần, nên QĐ-7b không ghi đè gì cả.
    DieuLuat("S9", "Vần", "Có thể dùng vần bằng, vần trắc hoặc phối hợp", "mem"),
    DieuLuat("S10", "Vần", "Chấp nhận vần thông, không yêu cầu vần chính tuyệt đối", "mem"),
    DieuLuat("S11", "Vần", "Sơ đồ vần nên nhất quán trong phạm vi một khổ", "mem"),
    DieuLuat("S12", "Vần", "Có thể đổi vần khi sang khổ mới", "mem"),
    # --- Nhịp (tài liệu §6) ---
    DieuLuat("S13", "Nhịp", "Nhịp do nghĩa của dòng quyết định", "mem"),
    DieuLuat("S14", "Nhịp", "Nên có một nhịp chủ đạo", "mem"),
    DieuLuat("S15", "Nhịp", "Đổi nhịp nên trùng chỗ chuyển ý", "mem"),
    # --- Khổ và bố cục (tài liệu §7) ---
    # S16 hợp nhất với F5 — xem chú thích ở F5.
    DieuLuat("S16", "Khổ",
             "Số dòng trong bài không hạn định về lượng, nhưng phải là bội của 4",
             "mem"),
    DieuLuat("S17", "Khổ", "Khổ phổ biến là 4 dòng; dùng được 2, 3, 5, 6 dòng", "mem"),
    DieuLuat("S18", "Khổ", "Có thể viết liên hoàn, không chia khổ", "mem"),
    DieuLuat("S19", "Bố cục", "Triển khai theo mạch cảm xúc hoặc mạch tự sự", "mem"),
    DieuLuat("S20", "Bố cục", "Có thể dùng điệp dòng, điệp khổ, điệp cấu trúc", "mem"),
    DieuLuat("S21", "Bố cục", "Có thể kết mở", "mem"),
)

MA_LUAT: dict[str, DieuLuat] = {d.ma: d for d in LUAT}
MA_CUNG: frozenset[str] = frozenset(d.ma for d in LUAT if d.loai == "cung")

SO_TIENG_MOI_DONG = 7


# ══════════════════════════════════════════════════════════════════════════════
# §1b. PHÂN LOẠI 17 ĐIỀU MỀM — bắt buộc / quyền / mô tả
#
# Rà từng câu chữ tài liệu. Ba loại này KHÁC NHAU VỀ THẨM QUYỀN:
#
#   bat_buoc  tài liệu dùng chữ "nên" hoặc "cần"     -> CÓ THỂ sinh tiêu chí chặn
#   quyen     tài liệu dùng "có thể", "chấp nhận"    -> KHÔNG BAO GIỜ được đánh trượt
#   mo_ta     phát biểu về thông lệ                   -> không sinh tiêu chí
#
# Nguyên tắc N2 của plan: trượt vì tác giả dùng một QUYỀN là mâu thuẫn tự thân.
# Test `test_khong_dieu_QUYEN_nao_lam_tieu_chi_chan` cưỡng chế điều này.
# ══════════════════════════════════════════════════════════════════════════════

LoaiMem: TypeAlias = Literal["bat_buoc", "quyen", "mo_ta"]

LOAI_DIEU_MEM: dict[str, LoaiMem] = {
    "S1": "quyen",     # "P1, P3, P5 CÓ THỂ tự do" + "CÓ THỂ dùng vần lưng" (gộp S7)
    "S2": "bat_buoc",  # "P2, P4, P6 NÊN luân phiên bằng – trắc"
    "S3": "bat_buoc",  # "P7 ... CẦN được chọn có chủ đích"  -> N3: không kiểm được
    "S6": "mo_ta",     # "Vần chủ đạo là vần chân, đặt ở P7"
    "S9": "quyen",     # "CÓ THỂ dùng vần bằng, vần trắc hoặc phối hợp"
    "S10": "quyen",    # "CHẤP NHẬN vần thông"
    "S11": "bat_buoc",  # "Sơ đồ vần NÊN nhất quán trong phạm vi một khổ"
    "S12": "quyen",    # "CÓ THỂ đổi vần khi sang khổ mới"
    "S13": "mo_ta",    # "Nhịp do nghĩa của dòng quyết định"
    "S14": "bat_buoc",  # "NÊN CÓ một nhịp chủ đạo"
    "S15": "bat_buoc",  # "Đổi nhịp NÊN trùng chỗ chuyển ý"  -> N3: không kiểm được
    "S16": "quyen",    # "Số dòng trong bài không hạn định"
    "S17": "mo_ta",    # "Khổ phổ biến là 4 dòng; cũng dùng được 2, 3, 5, 6"
    "S18": "quyen",    # "CÓ THỂ viết liên hoàn"
    "S19": "mo_ta",    # "Bố cục triển khai theo mạch cảm xúc hoặc tự sự"
    "S20": "quyen",    # "CÓ THỂ dùng điệp dòng, điệp khổ"
    "S21": "quyen",    # "CÓ THỂ kết mở"
}


# ══════════════════════════════════════════════════════════════════════════════
# §1c. BẢY TẦNG
#
# Một bài phải qua tầng N mới sang tầng N+1. Dừng sớm KHÔNG phải để chạy nhanh mà
# để đúng: tính khuôn trên một dòng 6 tiếng là gán cho tác giả một lựa chọn phong
# cách mà họ chưa hề thực hiện.
#
# `tieu_chi_tu` là các điều luật THỰC SỰ sinh ra phán quyết của tầng. `ma_luat`
# rộng hơn: gồm mọi điều luật thuộc phạm vi tầng, kể cả điều chỉ để mô tả.
# ══════════════════════════════════════════════════════════════════════════════

MucChan: TypeAlias = Literal["chan", "ghi_nhan"]


@dataclass(frozen=True, slots=True)
class DinhNghiaTang:
    so: int
    ten: str
    ma_luat: tuple[str, ...]  # mọi điều luật thuộc tầng này
    tieu_chi_tu: tuple[str, ...]  # điều luật sinh ra tiêu chí đạt/trượt
    khong_kiem_duoc: tuple[str, ...]  # điều đòi ý đồ hoặc ngữ nghĩa (N3)
    muc: MucChan
    trich_luat: str  # nguyên văn câu luật làm căn cứ


TANG: tuple[DinhNghiaTang, ...] = (
    DinhNghiaTang(
        so=1, ten="Hình thức và số dòng",
        ma_luat=("H3", "H4"), tieu_chi_tu=("H3", "H4"), khong_kiem_duoc=(),
        muc="chan",
        trich_luat="Văn bản phải được phân dòng, từ 4 dòng trở lên. Một khối liền "
                   "mạch không xuống dòng không thuộc thể này. [H4, 18/09/2026: số "
                   "dòng trong bài phải là bội của 4 — luật cứng, không ngoại lệ]",
    ),
    DinhNghiaTang(
        so=2, ten="Độ dài dòng",
        ma_luat=("H1", "H2"), tieu_chi_tu=("H1", "H2"), khong_kiem_duoc=(),
        muc="chan",
        trich_luat="Mỗi dòng phải có đúng 7 tiếng. Ràng buộc này áp dụng cho toàn bộ "
                   "các dòng của bài, không có ngoại lệ.",
    ),
    DinhNghiaTang(
        so=3, ten="Đối chiếu Đường luật",
        ma_luat=("F1", "F2", "F3", "F4", "F5"),
        # KHÔNG CÓ TIÊU CHÍ CHẶN. F1–F5 là các ràng buộc đã được GỠ BỎ khỏi thể,
        # không phải điều kiện loại trừ — xem chú thích của `_tang3_loai_tru_duong_luat`.
        tieu_chi_tu=(),
        # Phép ĐỐI đòi so sánh từ loại và ngữ nghĩa giữa hai dòng — không suy ra
        # được từ hình thức. Bố cục Khai–Thừa–Chuyển–Hợp cũng vậy.
        khong_kiem_duoc=("F2", "F4"),
        muc="ghi_nhan",
        trich_luat="Việc một bài thất ngôn tự do vẫn có niêm, có đối, có độc vận là "
                   "được phép. Nhưng đó là lựa chọn của tác giả, không phải tiêu chí "
                   "nhận diện thể. (§3) · F5: Không giới hạn số dòng ở con số 4 hoặc 8.",
    ),
    DinhNghiaTang(
        so=4, ten="Thanh luật",
        ma_luat=("S1", "S2", "S3"), tieu_chi_tu=("S2",),
        khong_kiem_duoc=("S3",),
        muc="chan",
        trich_luat="P2, P4, P6 nên luân phiên bằng – trắc để tạo nhạc tính. "
                   "[QĐ-1: áp lên TOÀN BỘ dòng; QĐ-2: không cho phá khuôn]",
    ),
    DinhNghiaTang(
        so=5, ten="Vần",
        ma_luat=("S6", "S9", "S10", "S11", "S12"), tieu_chi_tu=("S11",),
        khong_kiem_duoc=(),
        muc="chan",
        trich_luat="Sơ đồ vần nên nhất quán trong phạm vi một khổ. "
                   "[QĐ-7b: cụm bốn dòng liên tiếp phải có ít nhất một cặp hiệp "
                   "vần chân; QĐ-3: so vần theo âm chính + âm cuối]",
    ),
    DinhNghiaTang(
        so=6, ten="Nhịp",
        ma_luat=("S13", "S14", "S15"), tieu_chi_tu=("S14",),
        khong_kiem_duoc=("S15",),
        muc="chan",
        trich_luat="Nên có một nhịp chủ đạo để bài có xương sống âm thanh. "
                   "[QĐ-4b: phải tồn tại một kiểu nhịp phủ mọi dòng]",
    ),
    DinhNghiaTang(
        so=7, ten="Khổ và bố cục",
        ma_luat=("S16", "S17", "S18", "S19", "S20", "S21"), tieu_chi_tu=(),
        khong_kiem_duoc=("S19",),
        muc="chan",
        trich_luat="Số dòng trong bài không hạn định; có thể viết liên hoàn, không chia khổ.",
    ),
)

TANG_THEO_SO: dict[int, DinhNghiaTang] = {t.so: t for t in TANG}

# Điều luật nào bị quyết định của chủ dự án ghi đè, và ghi đè bằng gì.
# Ghi ở đây để mã nguồn và tài liệu không nói hai điều khác nhau.
# Văn bản docs/Luat_Tho_That_Ngon_Tu_Do.md KHÔNG bị sửa một chữ nào.
GHI_DE_BOI_QUYET_DINH: dict[str, str] = {
    "S13": "QĐ-4 + QĐ-4b: tài liệu nói nhịp không cố định cho toàn bài, "
           "dự án đòi một nhịp chủ đạo phủ mọi dòng",
    "S15": "QĐ-4b: tài liệu cho đổi nhịp, dự án đòi một nhịp chủ đạo",
}

# F5 và S16 KHÔNG nằm trong bảng trên, dù H4 mới ra đời cùng ngày.
# Lý do: chủ dự án đã cho hợp nhất chúng thay vì để mâu thuẫn — "không giới hạn số
# dòng" nói về LƯỢNG, "bội của 4" nói về HÌNH DẠNG, hai vế cùng đúng. Không có gì
# bị ghi đè nên không ghi vào đây; ghi bừa vào sẽ báo một mâu thuẫn không tồn tại.


# ══════════════════════════════════════════════════════════════════════════════
# §2. KIỂU DỮ LIỆU KẾT QUẢ
#
# Kết quả kiểm mang theo *dấu vết chẩn đoán*, không chỉ một cờ đúng/sai. Vòng sửa
# ở tầng trên cần biết dòng nào hỏng, hỏng bao nhiêu tiếng, và phải giữ lại vần
# nào — "sai rồi, viết lại đi" là phản hồi gần như vô dụng cho mô hình.
# ══════════════════════════════════════════════════════════════════════════════

Thanh: TypeAlias = Literal["B", "T"]
# "pha" = có đủ 7 tiếng nhưng không khớp khuôn nào (QĐ-2 không cho phép).
# "khong_xac_dinh" = dòng không đủ 7 tiếng nên khuôn không có nghĩa.
Khuon: TypeAlias = Literal["bang", "trac", "pha", "khong_xac_dinh"]
KieuHiepVan: TypeAlias = Literal["chinh", "thong", "khong"]


@dataclass(frozen=True, slots=True)
class ViPham:
    """Một vi phạm ràng buộc cứng, đủ thông tin để sinh yêu cầu sửa có địa chỉ."""

    ma: str  # mã luật, ví dụ "H1"
    dong: int | None  # số thứ tự dòng, đếm từ 1. None = vi phạm cấp bài
    ky_vong: str
    thuc_te: str
    goi_y: str


@dataclass(frozen=True, slots=True)
class BaoCaoDong:
    """Mô tả đầy đủ một dòng thơ sau khi phân tích."""

    so: int
    van_ban: str
    tieng: tuple[str, ...]
    so_tieng: int
    thanh: tuple[Thanh, ...]
    khuon: Khuon
    van_cuoi: str  # phần vần của tiếng thứ 7, đã bỏ dấu thanh
    thanh_cuoi: Thanh | None


@dataclass(frozen=True, slots=True)
class KetQuaHiepVan:
    hiep: bool
    kieu: KieuHiepVan
    dong_thanh: bool  # hai tiếng cùng lớp thanh (B–B hoặc T–T)


@dataclass(frozen=True, slots=True)
class KetQuaTang:
    """Kết quả một tầng, kèm BẰNG CHỨNG để người đọc kiểm lại được.

    `da_chay = False` nghĩa là tầng này bị bỏ qua vì một tầng trước đã chặn. Khi
    đó `dat` không mang ý nghĩa gì — không được đọc nó như "tầng này đã qua".
    Ghi ra như vậy thay vì lặng lẽ cho qua, đúng nguyên tắc N3 của plan.
    """

    so: int
    ten: str
    ma_luat: tuple[str, ...]
    muc: MucChan
    da_chay: bool
    dat: bool
    trich_luat: str
    bang_chung: str
    chi_tiet: Mapping[str, object] = field(default_factory=dict)
    vi_pham: tuple[ViPham, ...] = ()


@dataclass(frozen=True, slots=True)
class PoemVerdict:
    """Phán quyết đầy đủ, kèm dấu vết bảy tầng.

    HAI CỜ, CỐ Ý KHÔNG GỘP:
        `thuoc_the`  chỉ H1–H3 — câu trả lời của TÀI LIỆU LUẬT (§2)
        `dat`        qua toàn bộ bảy tầng — câu trả lời của DỰ ÁN (QĐ-1 → QĐ-6)

    Gộp hai cờ làm một thì bộ kiểm sẽ trả lời sai câu hỏi "bài này có thuộc thể
    thất ngôn tự do không", vì §9 Bước 4 nói rõ lựa chọn mềm không dùng để loại bài.
    """

    dat: bool
    thuoc_the: bool
    tang: tuple[KetQuaTang, ...]
    tang_dung_lai: int | None  # tầng nào đã chặn; None = không tầng nào chặn
    vi_pham: tuple[ViPham, ...]
    dong: tuple[BaoCaoDong, ...]
    so_dong: int
    so_kho: int
    so_do_van_theo_kho: tuple[tuple[str, ...], ...]
    phoi_khuon_theo_kho: tuple[str, ...]  # §4.3, chỉ có nghĩa với khổ 4 dòng
    # §6c: mã 1..16 của từng cụm 4 dòng LIÊN TIẾP (khác `phoi_khuon_theo_kho`, vốn
    # chia theo KHỔ). None = cụm có dòng phá khuôn.
    ma_phoi_khuon_theo_cum: tuple[int | None, ...]
    ty_le_theo_khuon: float
    van_lech_thanh: tuple[tuple[int, int], ...]  # các cặp dòng hiệp vần khác lớp thanh
    van_lung: tuple[tuple[int, int], ...]  # S1 (gộp S7): (số dòng, vị trí 4 hoặc 5)
    nghi_duong_luat: bool
    ghi_chu: tuple[str, ...]


# ══════════════════════════════════════════════════════════════════════════════
# §3. ĐẾM ÂM TIẾT  —  phục vụ H1, H2
#
# Tài liệu §2.1 nói tiếng được đếm theo âm tiết, "tương ứng với đơn vị viết cách
# nhau bởi dấu cách". Hai vế này không luôn trùng nhau: chính tài liệu cho ví dụ
# "ra-đi-ô" = 3 tiếng, trong khi đó là MỘT đơn vị cách nhau bởi dấu cách.
#
# Vì vậy ở đây âm tiết là đơn vị đếm, còn tách theo dấu cách chỉ là bước đầu:
#   - dấu câu bị loại trước khi đếm
#   - từ có gạch nối tách tiếp theo gạch nối        ("ra-đi-ô" -> 3)
#   - chữ số quy về cách đọc rồi đếm                 (Đ2)
# ══════════════════════════════════════════════════════════════════════════════

# Dấu câu nhận diện theo PHÂN LOẠI UNICODE, không theo danh sách liệt kê tay.
# Lý do: danh sách liệt kê luôn thiếu. Bản trước thiếu gạch ngang dài "—" và gạch
# ngang ngắn "–", nên một dòng 6 tiếng có gạch ngang bị đếm thành 7 tiếng và LỌT
# qua H1 — sai theo hướng nguy hiểm nhất: bài sai luật được coi là đạt.
# Gạch nối "-" là ngoại lệ duy nhất vì nó mang thông tin tách âm tiết ("ra-đi-ô").
_GACH_NOI = "-"


def _la_dau_cau(ky_tu: str) -> bool:
    if ky_tu == _GACH_NOI:
        return False
    return unicodedata.category(ky_tu).startswith(("P", "S"))


def _got_dau_cau_hai_dau(tu: str) -> str:
    i, j = 0, len(tu)
    while i < j and _la_dau_cau(tu[i]):
        i += 1
    while j > i and _la_dau_cau(tu[j - 1]):
        j -= 1
    return tu[i:j]


_CHU_SO = re.compile(r"^\d+$")
_SO_THAP_PHAN = re.compile(r"^(\d+)[.,](\d+)$")

_DON_VI = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")
_HANG = ("", "nghìn", "triệu", "tỷ")


def _doc_nhom_ba(n: int, day_du: bool) -> list[str]:
    """Đọc một nhóm ba chữ số. `day_du` = True thì đọc cả hàng trăm dù bằng 0.

    Các biến thể đọc đã chốt ở Đ2: 21 -> "hai mươi mốt", 24 -> "hai mươi tư",
    15 -> "mười lăm", 105 -> "một trăm linh năm".
    """
    tram, chuc, dv = n // 100, (n // 10) % 10, n % 10
    ra: list[str] = []

    if tram > 0 or day_du:
        ra += [_DON_VI[tram], "trăm"]

    if chuc == 0:
        if dv > 0:
            if tram > 0 or day_du:
                ra += ["linh", _DON_VI[dv]]
            else:
                ra += [_DON_VI[dv]]
    elif chuc == 1:
        ra += ["mười"]
        if dv == 5:
            ra += ["lăm"]
        elif dv > 0:
            ra += [_DON_VI[dv]]
    else:
        ra += [_DON_VI[chuc], "mươi"]
        if dv == 1:
            ra += ["mốt"]
        elif dv == 4:
            ra += ["tư"]
        elif dv == 5:
            ra += ["lăm"]
        elif dv > 0:
            ra += [_DON_VI[dv]]

    return ra


def doc_so(n: int) -> list[str]:
    """Quy một số nguyên về danh sách âm tiết theo cách đọc (Đ2)."""
    if n == 0:
        return ["không"]

    nhom: list[int] = []
    while n > 0:
        nhom.append(n % 1000)
        n //= 1000
    nhom.reverse()  # nhóm có trọng số lớn nhất đứng trước

    ra: list[str] = []
    for i, gia_tri in enumerate(nhom):
        la_nhom_dau = i == 0
        if gia_tri == 0:
            continue
        ra += _doc_nhom_ba(gia_tri, day_du=not la_nhom_dau)
        bac = len(nhom) - i - 1
        if bac > 0:
            ra.append(_HANG[bac])
    return ra


def _doc_chu_so_roi(chuoi: str) -> list[str]:
    """Đọc rời từng chữ số: "007" -> không không bảy."""
    return [_DON_VI[int(c)] for c in chuoi]


def _doc_token_so(token: str) -> list[str]:
    """Quy một token toàn chữ số (hoặc số thập phân) về danh sách âm tiết (Đ2)."""
    m = _SO_THAP_PHAN.match(token)
    if m:
        return _doc_token_so(m.group(1)) + ["phẩy"] + _doc_chu_so_roi(m.group(2))
    if len(token) > 1 and token[0] == "0":
        return _doc_chu_so_roi(token)
    return doc_so(int(token))


def tach_tieng(dong: str) -> tuple[str, ...]:
    """Tách một dòng thành danh sách tiếng (âm tiết) theo đúng §2.1.

    Thứ tự xử lý có chủ đích: gọt dấu câu hai đầu TRƯỚC khi thử khớp số thập phân,
    vì "3,5." vẫn phải đọc là "ba phẩy năm" chứ không phải thành hai token rời.
    """
    ra: list[str] = []
    for tho in dong.split():
        tu = _got_dau_cau_hai_dau(tho)
        if not tu:
            continue
        if _SO_THAP_PHAN.match(tu):
            ra.extend(_doc_token_so(tu))
            continue
        sach = "".join(" " if _la_dau_cau(c) else c for c in tu)
        for cum in sach.split():
            for phan in cum.split(_GACH_NOI):
                if not phan:
                    continue
                if _CHU_SO.match(phan):
                    ra.extend(_doc_token_so(phan))
                else:
                    ra.append(phan)
    return tuple(ra)


def dem_tieng(dong: str) -> int:
    """H1: số tiếng của một dòng."""
    return len(tach_tieng(dong))


# ══════════════════════════════════════════════════════════════════════════════
# §4. THANH ĐIỆU  —  phục vụ S1–S3
#
# B = ngang, huyền.  T = sắc, hỏi, ngã, nặng   (tài liệu §1).
#
# Kỹ thuật: phân rã Unicode NFD rồi tìm dấu thanh trong phần tổ hợp. Cần cẩn thận
# vì ă â ê ô ơ ư mang dấu phụ NHƯNG không phải dấu thanh — breve, circumflex và
# horn phải bị bỏ qua, nếu không "ơ" sẽ bị đọc nhầm thành tiếng có dấu.
# ══════════════════════════════════════════════════════════════════════════════

_DAU_SAC = "́"
_DAU_HUYEN = "̀"
_DAU_HOI = "̉"
_DAU_NGA = "̃"
_DAU_NANG = "̣"

_DAU_THANH = frozenset({_DAU_SAC, _DAU_HUYEN, _DAU_HOI, _DAU_NGA, _DAU_NANG})
# Dấu phụ tạo ký tự nền, KHÔNG phải dấu thanh: ă(breve) â ê ô(circumflex) ơ ư(horn)
_DAU_NEN = frozenset({"̆", "̂", "̛"})


def _dau_thanh_cua(tieng: str) -> str | None:
    for ky_tu in unicodedata.normalize("NFD", tieng):
        if ky_tu in _DAU_THANH:
            return ky_tu
    return None


def thanh_cua(tieng: str) -> Thanh:
    """Phân lớp thanh của một tiếng: B (bằng) hoặc T (trắc)."""
    dau = _dau_thanh_cua(tieng)
    if dau is None or dau == _DAU_HUYEN:
        return "B"
    return "T"


def bo_dau_thanh(tieng: str) -> str:
    """Bỏ dấu thanh, GIỮ NGUYÊN dấu nền. "về" -> "vê", chứ không thành "ve"."""
    phan_ra = unicodedata.normalize("NFD", tieng)
    giu = "".join(c for c in phan_ra if c not in _DAU_THANH)
    return unicodedata.normalize("NFC", giu)


# ══════════════════════════════════════════════════════════════════════════════
# §5. TÁCH VẦN VÀ HIỆP VẦN  —  phục vụ S6, S9–S12
#
# Phần vần = âm tiết sau khi bỏ phụ âm đầu. Cắt theo khớp DÀI NHẤT, vì "ngh" phải
# được thử trước "ng", và "ng" trước "n". Nếu cắt xong mà không còn gì thì lùi lại
# một bước: "gì" không phải là "gi" + rỗng, mà là "g" + "ì".
#
# S10 cho phép vần thông nhưng tài liệu không cung cấp bảng vần. Bảng dùng ở đây
# lấy từ Trần Trọng Kim, "Việt thi" I-6 — xem `CAP_VAN_THONG` bên dưới và hồ sơ
# nguồn ở docs/Nguon_Bang_Van_Thong.md.
# ══════════════════════════════════════════════════════════════════════════════

_PHU_AM_DAU = (
    "ngh", "ng", "nh", "ch", "gh", "gi", "kh", "ph", "th", "tr", "qu",
    "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "x",
)

# ══════════════════════════════════════════════════════════════════════════════
# BẢNG VẦN THÔNG — nguồn: Trần Trọng Kim, "Việt thi", mục I-6 "Vần thông"
#   bản số hoá Wikisource : https://vi.wikisource.org/wiki/Vi%E1%BB%87t_thi/I-6
#   đối chiếu             : Bùi Kỷ, "Quốc văn cụ thể", NXB Tân Việt, Sài Gòn 1950
#   hồ sơ nguồn đầy đủ    : docs/Nguon_Bang_Van_Thong.md  (QĐ-5, duyệt 18/09/2026)
#
# ĐÂY LÀ ĐỒ THỊ, KHÔNG PHẢI PHÂN HOẠCH — và đó không phải lựa chọn của dự án.
# Chính Trần Trọng Kim viết:
#
#     "ang thông với ương (không thông được với uông vì a không thông được với ô)"
#     ... rồi vài dòng sau: "uông thông với ương"
#
# Tức là ang~ương, uông~ương, nhưng ang ≁ uông. Đo trên toàn bảng: 55 vần,
# 73 cạnh, 16 bộ ba vi phạm bắc cầu. Ép bảng này thành các lớp tương đương rời
# nhau sẽ BỊA THÊM 16 cặp hiệp vần mà nguồn KHÔNG cho — tức là nới luật, điều
# nguyên tắc N1 cấm.
#
# Vì vậy `hiep_van` là quan hệ HAI NGÔI ĐỐI XỨNG, KHÔNG bắc cầu, và sơ đồ vần
# KHÔNG suy bằng gom nhóm bắc cầu (xem `suy_so_do_van`).
#
# Dữ liệu dưới đây chép đúng cách liệt kê của tác giả: `_NHOM_TTK` là các cụm
# "... thông với nhau", `_CAP_TTK` là các phát biểu rời "X thông với Y". Giữ
# nguyên hai dạng để đối chiếu lại với sách được, và vì gộp chúng lại là SAI:
# "ăn thông với ân" và "ăn thông với uân" là hai câu rời  ⇒  ân ≁ uân.
# ══════════════════════════════════════════════════════════════════════════════

# 🔶 SD-1 (giả định, ghi ở §4 docs/Nguon_Bang_Van_Thong.md): quan hệ hiệp vần xét
# trên VẦN, không xét thanh điệu. Căn cứ: tác giả viết phần vần trắc "cũng theo
# một nguyên-tắc như" phần vần bằng, và mọi cặp vần trắc ông dẫn đều quy về một
# quy tắc đã có ở phần vần bằng. Thêm nữa, tiếng Việt không có âm tiết thanh bằng
# kết thúc bằng -c/-ch/-p/-t, nên hai danh sách BÙ NHAU chứ không mâu thuẫn.
_NHOM_TTK: tuple[tuple[str, ...], ...] = (
    ("e", "ê", "i"),
    ("o", "ô", "u"),
    ("ai", "oi", "ôi", "ơi", "ươi", "ui"),
    ("ao", "eo", "êu", "iêu", "yêu", "iu", "ưu"),
    ("en", "in", "iên", "uyên"),
    ("on", "ôn", "uôn"),
    ("ăng", "âng", "ưng"),
    ("ong", "ông", "ung"),
    ("anh", "ênh", "inh"),
)

_CAP_TTK: tuple[tuple[str, str], ...] = (
    ("a", "ơ"), ("ơ", "ư"),      # nguyên tắc gốc; KHÔNG suy ra a~ư
    ("ai", "ay"),                # "ay" chỉ thông với "ai", KHÔNG với oi/ôi/ơi/ươi/ui
    ("ao", "au"),
    ("am", "ơm"), ("ăm", "âm"), ("êm", "im"),
    ("an", "ơn"), ("ăn", "ân"), ("ăn", "uân"),   # hai câu rời ⇒ ân ≁ uân
    ("on", "un"),                # câu rời ⇒ un ≁ ôn, un ≁ uôn
    ("ang", "ương"),             # tác giả ghi rõ: KHÔNG thông với uông
    ("uông", "ương"),
    # 🔶 SD-2: bốn cặp lấy từ phần vần trắc, sau khi bỏ thanh theo SD-1, không
    # trùng quy tắc nào ở phần vần bằng. Đây là ví dụ của chính tác giả.
    ("o", "ua"), ("ia", "uê"), ("ac", "ươc"), ("ât", "ưt"),
)


def _dung_cap_van_thong() -> frozenset[frozenset[str]]:
    canh: set[frozenset[str]] = set()
    for nhom in _NHOM_TTK:
        for i, a in enumerate(nhom):
            for b in nhom[i + 1:]:
                canh.add(frozenset((a, b)))
    for a, b in _CAP_TTK:
        canh.add(frozenset((a, b)))
    return frozenset(canh)


#: Tập cạnh hiệp vần thông. Tra cứu O(1), đối xứng, KHÔNG bắc cầu.
CAP_VAN_THONG: frozenset[frozenset[str]] = _dung_cap_van_thong()

#: Bốn sơ đồ vần bốn dòng của §5.2 tài liệu luật, kèm đúng tên tài liệu gọi.
#:
#: ⚠️ TỪ 18/09/2026 ĐÂY KHÔNG CÒN LÀ TẬP TIÊU CHÍ. Nó là BẢNG TÊN: cụm nào khớp
#: một trong bốn sơ đồ này thì biên bản gọi đúng tên tài liệu đặt ("vần cách",
#: "vần ôm"…). Tiêu chí chặn nay là `cua_so_co_van_chan` — có vần chân là đạt,
#: bất kể sơ đồ nào. Xem QĐ-7b.
#:
#: "Vần chân khổ liên kết" (K1 a a x a, K2 b b x b, K3 c c x c) không phải sơ đồ
#: thứ năm: nó là `aaxa` lặp lại qua nhiều khổ, chữ cái đổi theo khổ. Một cửa sổ
#: bốn dòng bất kỳ của nó vẫn là `aaxa`.
#:
#: "Vần hỗn hợp: phối nhiều sơ đồ trên trong cùng một bài" cũng không phải sơ đồ
#: thứ năm — nó là lý do vì sao QĐ-7 chỉ đòi MỘT cửa sổ khớp, chứ không đòi cả
#: bài theo một sơ đồ duy nhất.
SO_DO_KHO_TAI_LIEU: Mapping[str, str] = MappingProxyType({
    "aabb": "vần liền",
    "abab": "vần cách",
    "abba": "vần ôm",
    "aaxa": "vần ba dòng, kế thừa Đường luật",
})


def khop_so_do_bon_dong(tieng_cuoi: tuple[str, ...]) -> str | None:
    """Bốn tiếng cuối này khớp sơ đồ nào của §5.2, hay không khớp sơ đồ nào.

    Trả về mã sơ đồ ("aabb", "abab", "abba", "aaxa") hoặc None.

    Phép khớp là NGHIÊM NGẶT hai chiều: hai dòng cùng chữ cái thì bắt buộc hiệp
    vần, và hai dòng khác chữ cái thì bắt buộc KHÔNG hiệp. Dòng mang 'x' phải
    buông — không hiệp với dòng nào trong cửa sổ. Nếu chỉ đòi chiều thuận thì
    "aabb" sẽ nuốt luôn cả bài bốn dòng cùng một vần, mà tài liệu gọi đó là
    chuyện khác.
    """
    if len(tieng_cuoi) != 4 or not all(tieng_cuoi):
        return None
    # `suy_so_do_van` đã cho nhãn chuẩn tắc: chữ cái theo thứ tự xuất hiện, 'x'
    # cho dòng buông, '?' khi quan hệ vần trong cửa sổ không bắc cầu. Vì nhãn là
    # chuẩn tắc nên so chuỗi là đủ, không cần dò hoán vị chữ cái.
    ma = "".join(suy_so_do_van(tieng_cuoi))
    return ma if ma in SO_DO_KHO_TAI_LIEU else None


def cua_so_khop_so_do(
    tieng_cuoi_moi_dong: tuple[str, ...],
) -> tuple[tuple[int, str], ...]:
    """Mọi cụm BỐN DÒNG LIÊN TIẾP khớp một sơ đồ §5.2, quét suốt cả bài.

    Trả về các cặp (số dòng bắt đầu tính từ 1, mã sơ đồ).

    QĐ-7: cửa sổ trượt trên TOÀN BÀI theo thứ tự đọc, KHÔNG dừng ở ranh giới
    khổ. Chủ dự án nói "trong bài phải có ít nhất 4 dòng liên tiếp", không nói
    "trong một khổ", nên cửa sổ được phép vắt qua hai khổ.
    """
    return tuple(
        (i + 1, ma)
        for i in range(len(tieng_cuoi_moi_dong) - 3)
        if (ma := khop_so_do_bon_dong(tieng_cuoi_moi_dong[i:i + 4])) is not None
    )


def cua_so_co_van_chan(
    tieng_cuoi_moi_dong: tuple[str, ...],
) -> tuple[tuple[int, str], ...]:
    """Mọi cụm BỐN DÒNG LIÊN TIẾP có ít nhất MỘT cặp hiệp vần chân.

    Trả về các cặp (số dòng bắt đầu tính từ 1, sơ đồ vần thực tế của cụm).

    ĐÂY LÀ TIÊU CHÍ CHẶN CỦA TẦNG 5 từ 18/09/2026 — nguyên văn chủ dự án:

        "vần chân sẽ là như vậy trong phạm vi 4 câu
         (Nếu không có vần chân nào thì trượt)"

    VÌ SAO KHÔNG DÙNG DANH SÁCH SƠ ĐỒ. Bản trước đòi cụm phải khớp ĐÚNG một
    trong bốn sơ đồ §5.2 (`cua_so_khop_so_do`). Chủ dự án mở rộng: danh sách
    *"aabb, abab, abba, aaxa, aaaa, aaba, ..."* kết bằng dấu ba chấm, và câu
    trong ngoặc mới là luật thật — **có vần chân thì đạt, không có thì trượt**.

    Liệt kê một danh sách đóng sẽ phải trả lời "còn `axax` thì sao, `xaax` thì
    sao" cho từng sơ đồ một, mà tài liệu không cho căn cứ nào để phân biệt.
    Tiêu chí này không có danh sách, không có ngưỡng phần trăm — không phạm N1.

    CÁCH KIỂM: sơ đồ của cụm có ít nhất một nhãn khác 'x'. Nhãn 'x' nghĩa là
    dòng ấy không hiệp với dòng nào trong cụm, nên "mọi nhãn đều x" tương đương
    "không cặp nào hiệp". Nhãn '?' (quan hệ vần không bắc cầu — xem
    `suy_so_do_van`) VẪN TÍNH LÀ CÓ VẦN: dòng ấy có hiệp với một dòng khác, chỉ
    là cả cụm không quy về một sơ đồ chữ cái gọn ghẽ được.

    Hệ quả: cụm duy nhất bị loại là `xxxx`.
    """
    ra: list[tuple[int, str]] = []
    for i in range(len(tieng_cuoi_moi_dong) - 3):
        cum = tieng_cuoi_moi_dong[i:i + 4]
        if not all(cum):
            continue
        so_do = "".join(suy_so_do_van(cum))
        if any(nhan != "x" for nhan in so_do):
            ra.append((i + 1, so_do))
    return tuple(ra)


def van_cua(tieng: str) -> str:
    """Trả phần vần của một tiếng, đã bỏ dấu thanh và hạ chữ thường.

    GIỮ LẠI để tương thích ngược. Phép so vần chính thức nay dùng
    `phan_tich_am_tiet()` ở §5b — xem QĐ-3 trong docs/Plan_Rule_Phan_Tang.md.
    """
    goc = bo_dau_thanh(tieng).lower()
    for dau in _PHU_AM_DAU:
        if goc.startswith(dau):
            con_lai = goc[len(dau):]
            if con_lai:  # không cắt đến mức rỗng
                return con_lai
    return goc


# ══════════════════════════════════════════════════════════════════════════════
# §5b. PHÂN TÍCH ÂM TIẾT  —  QĐ-3
#
# Vì sao có phần này: phép so vần cũ cắt phụ âm đầu rồi so phần còn lại, nên
#
#     van_cua("hoa") = "oa"   ≠   van_cua("ha") = "a"    -> KHÔNG hiệp vần
#
# Sai. Trong `hoa`, chữ `o` là ÂM ĐỆM /w/ chứ không phải một phần của âm chính.
# Âm chính của cả `hoa` lẫn `ha` đều là /a/, không có âm cuối, nên hai tiếng này
# HIỆP VẦN — đúng như thơ ca tiếng Việt vẫn gieo (`hoa` với `nhà`, `ta`).
#
# CẤU TRÚC ÂM TIẾT TIẾNG VIỆT (ngữ âm học phổ thông, không phải quy ước tự đặt):
#
#     ÂM TIẾT = Thanh điệu + [Âm đầu] + VẦN
#     VẦN     = [Âm đệm] + Âm chính + [Âm cuối]
#
# Phép so vần chính: trùng ÂM CHÍNH và ÂM CUỐI. Âm đệm không cản trở hiệp vần.
#
# Bảng VẦN THÔNG (âm chính nào được phép hiệp với âm chính nào) CHƯA có ở đây:
# theo QĐ-5 và điều kiện nghiệm thu H, bảng đó phải có nguồn được chủ dự án duyệt
# trước khi vào mã. Không được tự liệt kê.
# ══════════════════════════════════════════════════════════════════════════════

# Phụ âm đầu, xếp dài trước ngắn để khớp tham lam đúng ("ngh" trước "ng" trước "n").
_AM_DAU = (
    "ngh", "ng", "nh", "ch", "gh", "gi", "kh", "ph", "th", "tr", "qu",
    "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "x",
)

# Âm cuối: phụ âm cuối và bán nguyên âm cuối. Hai ký tự thử trước một ký tự.
_AM_CUOI = ("ng", "nh", "ch", "c", "m", "n", "p", "t", "i", "y", "o", "u")

# Nguyên âm đôi viết khác nhau tuỳ có âm cuối hay không.
# Không có âm cuối: ia, ua, ưa   |   Có âm cuối: iê, uô, ươ
# Qua bước chuẩn hoá, cả hai dạng về cùng một âm chính để so vần cho đúng.
_CHUAN_HOA_AM_CHINH = {
    "ia": "iê", "ya": "iê", "yê": "iê",
    "ua": "uô",
    "ưa": "ươ",
    "y": "i",
}

# Chữ "u" là ÂM ĐỆM khi đứng trước các nguyên âm này: huy, huê, huân, huơ.
# KHÔNG có "a" trong danh sách: "ua" của `mua` là nguyên âm đôi /uo/, không phải
# âm đệm + a. Trường hợp duy nhất "u" là âm đệm trước "a" là sau âm đầu "q"
# (`qua`), và nhánh xử lý "qu" ở dưới đã lấy chữ "u" đó ra rồi.
_SAU_AM_DEM_U = ("y", "ê", "â", "ơ")


@dataclass(frozen=True, slots=True)
class AmTiet:
    """Một âm tiết tiếng Việt đã tách đủ năm thành phần."""

    goc: str
    am_dau: str
    am_dem: str
    am_chinh: str
    am_cuoi: str
    thanh: Thanh

    @property
    def van(self) -> str:
        """Phần vần đầy đủ, gồm cả âm đệm."""
        return self.am_dem + self.am_chinh + self.am_cuoi

    @property
    def van_hiep(self) -> str:
        """Phần dùng để so vần: âm chính + âm cuối, BỎ âm đệm.

        Âm đệm không cản trở hiệp vần trong thơ tiếng Việt — `hoa` gieo được với
        `ta`, `nhà`.
        """
        return self.am_chinh + self.am_cuoi


def phan_tich_am_tiet(tieng: str) -> AmTiet:
    """Tách một âm tiết thành âm đầu, âm đệm, âm chính, âm cuối, thanh điệu."""
    thanh = thanh_cua(tieng)
    s = bo_dau_thanh(tieng).lower()
    goc = s

    # ── 1. Âm đầu, khớp tham lam dài nhất ──
    am_dau = ""
    for pa in _AM_DAU:
        if s.startswith(pa) and len(s) > len(pa):
            am_dau, s = pa, s[len(pa):]
            break

    # ── 2. Âm đệm ──
    # "qu": theo ngữ âm là /k/ + /w/, nên q là âm đầu còn u là âm đệm.
    am_dem = ""
    if am_dau == "qu":
        am_dau, am_dem = "q", "u"
    elif s.startswith("o") and len(s) > 1 and s[1] in "aăe":
        # hoa, hoặc, hoe — "o" đứng trước a/ă/e là âm đệm
        am_dem, s = "o", s[1:]
    elif s.startswith("u") and len(s) > 1 and s[1] in _SAU_AM_DEM_U:
        # huy, huê, huân, huơ
        am_dem, s = "u", s[1:]

    # ── 3. Âm cuối, khớp tham lam dài nhất, nhưng không được ăn hết âm chính ──
    am_cuoi = ""
    for ac in _AM_CUOI:
        if s.endswith(ac) and len(s) > len(ac):
            am_cuoi, s = ac, s[: -len(ac)]
            break

    # ── 4. Phần còn lại là âm chính, chuẩn hoá nguyên âm đôi ──
    am_chinh = _CHUAN_HOA_AM_CHINH.get(s, s)

    return AmTiet(
        goc=goc,
        am_dau=am_dau,
        am_dem=am_dem,
        am_chinh=am_chinh,
        am_cuoi=am_cuoi,
        thanh=thanh,
    )


def hiep_van(tieng_a: str, tieng_b: str) -> KetQuaHiepVan:
    """Hai tiếng có hiệp vần không, và hiệp theo kiểu nào.

    VẦN CHÍNH — hai vần trùng khít. Trần Trọng Kim, "Việt thi" I-5: *"Vần chính
    là những tiếng cùng đồng một âm vần với nhau."*
    VẦN THÔNG — cặp nằm trong `CAP_VAN_THONG`, dựng từ "Việt thi" I-6.

    ⚠️ QUAN HỆ NÀY KHÔNG BẮC CẦU. `hiep_van("vang", "vương")` và
    `hiep_van("vuông", "vương")` đều True, nhưng `hiep_van("vang", "vuông")` là
    False — đúng như tác giả ghi rõ trong ngoặc. Vì vậy KHÔNG được dùng hàm này
    để gom cụm bắc cầu; gom cụm sẽ xếp chung những dòng mà nguồn nói là không
    hiệp nhau.

    🔶 SD-3: vần có âm đệm mà bảng không nhắc (oa, oe, uy…) chỉ hiệp VẦN CHÍNH,
    không suy rộng. Đây là hướng chặt, không nới.

    Đ3: cặp lệch lớp thanh VẪN được coi là hiệp — ví dụ §11 của tài liệu dùng
    "xanh" (B) hiệp với "mảnh" (T) — nhưng kết quả ghi rõ để báo cáo tách bạch.
    """
    van_a, van_b = van_cua(tieng_a), van_cua(tieng_b)
    dong_thanh = thanh_cua(tieng_a) == thanh_cua(tieng_b)

    if van_a == van_b:
        return KetQuaHiepVan(hiep=True, kieu="chinh", dong_thanh=dong_thanh)

    if frozenset((van_a, van_b)) in CAP_VAN_THONG:
        return KetQuaHiepVan(hiep=True, kieu="thong", dong_thanh=dong_thanh)

    return KetQuaHiepVan(hiep=False, kieu="khong", dong_thanh=dong_thanh)


def van_lung_cua_dong(tieng: tuple[str, ...]) -> tuple[int, ...]:
    """S1 (phần gộp từ S7) — vị trí (4 hoặc 5) có vần hiệp với P7 của chính dòng đó.

    Đ5: tài liệu nói "có thể dùng thêm vần lưng ở P4 hoặc P5" nhưng KHÔNG nói vần
    lưng hiệp với tiếng nào. Ở đây chọn cách hẹp nhất và nói rõ: hiệp với P7 cùng
    dòng. Đây là số liệu MÔ TẢ, không bao giờ làm bài trượt.
    """
    if len(tieng) != SO_TIENG_MOI_DONG:
        return ()
    return tuple(vi_tri for vi_tri in (4, 5) if hiep_van(tieng[vi_tri - 1], tieng[6]).hiep)


# ══════════════════════════════════════════════════════════════════════════════
# §6. KHUÔN LUÂN PHIÊN  —  phục vụ S2
#
# Tài liệu §4.2:  khuôn bằng = P2 B, P4 T, P6 B    |    khuôn trắc = P2 T, P4 B, P6 T
# Dòng không khớp khuôn nào là "pha" (phá khuôn). Hàm này chỉ PHÂN LOẠI; việc
# "pha" có thành vi phạm hay không do tầng 4 quyết (QĐ-2: có).
# ══════════════════════════════════════════════════════════════════════════════


def khuon_cua_dong(tieng: tuple[str, ...]) -> Khuon:
    """Khuôn chỉ có nghĩa trên dòng ĐÚNG 7 tiếng.

    Dòng thiếu hoặc thừa tiếng thì P2/P4/P6 không còn là P2/P4/P6 của thể, nên trả
    "khong_xac_dinh" chứ không trả "pha". Gọi một dòng sai luật là "phá khuôn" tức
    là gán cho nó một lựa chọn phong cách mà tác giả chưa hề thực hiện.
    """
    if len(tieng) != SO_TIENG_MOI_DONG:
        return "khong_xac_dinh"
    p2, p4, p6 = thanh_cua(tieng[1]), thanh_cua(tieng[3]), thanh_cua(tieng[5])
    if (p2, p4, p6) == ("B", "T", "B"):
        return "bang"
    if (p2, p4, p6) == ("T", "B", "T"):
        return "trac"
    return "pha"


# Hai mẫu phối khuôn khổ 4 dòng của tài liệu §4.3. Đây là MÔ TẢ, không phải ràng
# buộc: bảng 16 tổ hợp ở §6c cho thấy cả 16 đều hợp lệ, không riêng hai mẫu này.
PHOI_KHUON_CO_DIEN: tuple[Khuon, ...] = ("bang", "trac", "trac", "bang")
PHOI_KHUON_DAO: tuple[Khuon, ...] = ("trac", "bang", "bang", "trac")

PhoiKhuon: TypeAlias = Literal["co_dien", "dao", "khac", "khong_xac_dinh"]


def phoi_khuon_cua_kho(khuon: tuple[Khuon, ...]) -> PhoiKhuon:
    """Xếp một khổ vào mẫu phối khuôn của §4.3.

    Chỉ định nghĩa cho khổ 4 dòng — hai mẫu trong tài liệu đều là mẫu 4 dòng.

    Ghi chú đáng để ý: mẫu "giữ âm hưởng cổ điển" (B T T B) chính là quan hệ NIÊM
    của Đường luật, chỉ không gọi tên. F1 nói thể này không áp dụng niêm, nên theo
    mẫu này càng sát thì càng tiến gần vùng bị §9 Bước 2 nghi ngờ.
    """
    if len(khuon) != 4 or "khong_xac_dinh" in khuon:
        return "khong_xac_dinh"
    if khuon == PHOI_KHUON_CO_DIEN:
        return "co_dien"
    if khuon == PHOI_KHUON_DAO:
        return "dao"
    return "khac"


# ══════════════════════════════════════════════════════════════════════════════
# §6c. MƯỜI SÁU TỔ HỢP KHUÔN CỦA CỤM BỐN DÒNG  —  bổ sung 18/09/2026
#
# Chủ dự án bổ sung: *"trong tổ hợp các câu trong bài thơ xét 4 dòng một thì đây
# sẽ là tổ hợp có thể xác định được"*, kèm bảng 16 dòng dưới đây.
#
# ĐỌC BẢNG CHO ĐÚNG — mỗi ô là BA GIÁ TRỊ THANH Ở P2, P4, P6 CỦA MỘT DÒNG:
#
#        cụm 4 dòng  =  D1      D2      D3      D4
#        mỗi ô       =  P2-P4-P6 của dòng ấy
#
#        "B-T-B"  nghĩa là  P2 = B,  P4 = T,  P6 = B   -> khuôn bằng  (§4.2)
#        "T-B-T"  nghĩa là  P2 = T,  P4 = B,  P6 = T   -> khuôn trắc  (§4.2)
#
# P1, P3, P5 KHÔNG xuất hiện trong bảng, và đó là chủ ý: S1 nói chúng có thể tự
# do. P7 cũng không, vì P7 thuộc về vần (S3, S6) chứ không thuộc khuôn luân phiên.
# Vậy bảng nói về ĐÚNG BA vị trí trong bảy vị trí của dòng.
#
# BẢNG NÀY LÀ TẬP ĐẦY ĐỦ, và đó là điều quan trọng nhất phải hiểu về nó:
#
#     mỗi dòng có 2 khuôn hợp lệ  ->  cụm 4 dòng có 2^4 = 16 tổ hợp
#
# Nên dùng bảng làm tiêu chí CHẶN thì không loại thêm bài nào so với tiêu chí đã
# có ở tầng 4: bài nào mọi dòng khớp khuôn thì mọi cụm 4 dòng của nó tự động nằm
# trong bảng. Hai cách phát biểu là TƯƠNG ĐƯƠNG, không phải cái sau chặt hơn.
#
# Vậy bảng này thêm được gì? Hai thứ, và cả hai đều thật:
#
#   1. NÓ CHỐT RẰNG CẢ 16 ĐỀU HỢP LỆ. Tài liệu §4.3 nêu hai mẫu — "giữ âm hưởng
#      cổ điển" (#6) và "mẫu đảo" (#11) — mà không nói rõ 14 mẫu còn lại có được
#      dùng không. Bảng này trả lời dứt khoát: được. Nhờ vậy `phoi_khuon_cua_kho`
#      trả "khac" không còn là một vùng xám; nó là 14 tổ hợp có tên, có số.
#
#   2. NÓ CHO MỖI CỤM MỘT MÃ TRA CỨU ĐƯỢC. Biên bản nói "cụm 1 = #6 (cổ điển)"
#      thay vì "cụm 1 khớp khuôn" — người đọc đối chiếu thẳng với bảng.
#
# THỨ TỰ BẢNG KHÔNG TUỲ TIỆN: đọc B-T-B = 0, T-B-T = 1, C1 là bit cao nhất, thì
# mã = giá trị nhị phân + 1. #1 = 0000, #16 = 1111. Test ghim tính chất này, nên
# không ai gõ nhầm thứ tự mà bảng vẫn lặng lẽ đúng.
#
# PHẠM VI: cụm là 4 dòng LIÊN TIẾP tính từ đầu bài, không phải khổ. H4 bảo đảm số
# dòng là bội của 4 nên phép chia cụm luôn chẵn, không có cụm thừa.
# ══════════════════════════════════════════════════════════════════════════════

# Nguyên văn bảng của chủ dự án, chép đúng thứ tự. Đây là DỮ LIỆU, không phải mã
# sinh ra — để sửa bảng không phải sửa thuật toán, và để đối chiếu được bằng mắt.
#                                       D1     D2     D3     D4
#                                       └─ mỗi cột: P2-P4-P6 của dòng đó ─┘
PHOI_KHUON_16: tuple[tuple[Khuon, Khuon, Khuon, Khuon], ...] = (
    ("bang", "bang", "bang", "bang"),  # 1   B-T-B  B-T-B  B-T-B  B-T-B
    ("bang", "bang", "bang", "trac"),  # 2   B-T-B  B-T-B  B-T-B  T-B-T
    ("bang", "bang", "trac", "bang"),  # 3   B-T-B  B-T-B  T-B-T  B-T-B
    ("bang", "bang", "trac", "trac"),  # 4   B-T-B  B-T-B  T-B-T  T-B-T
    ("bang", "trac", "bang", "bang"),  # 5   B-T-B  T-B-T  B-T-B  B-T-B
    ("bang", "trac", "bang", "trac"),  # 6   B-T-B  T-B-T  B-T-B  T-B-T
    ("bang", "trac", "trac", "bang"),  # 7   B-T-B  T-B-T  T-B-T  B-T-B  <- §4.3 cổ điển
    ("bang", "trac", "trac", "trac"),  # 8   B-T-B  T-B-T  T-B-T  T-B-T
    ("trac", "bang", "bang", "bang"),  # 9   T-B-T  B-T-B  B-T-B  B-T-B
    ("trac", "bang", "bang", "trac"),  # 10  T-B-T  B-T-B  B-T-B  T-B-T  <- §4.3 đảo
    ("trac", "bang", "trac", "bang"),  # 11  T-B-T  B-T-B  T-B-T  B-T-B
    ("trac", "bang", "trac", "trac"),  # 12  T-B-T  B-T-B  T-B-T  T-B-T
    ("trac", "trac", "bang", "bang"),  # 13  T-B-T  T-B-T  B-T-B  B-T-B
    ("trac", "trac", "bang", "trac"),  # 14  T-B-T  T-B-T  B-T-B  T-B-T
    ("trac", "trac", "trac", "bang"),  # 15  T-B-T  T-B-T  T-B-T  B-T-B
    ("trac", "trac", "trac", "trac"),  # 16  T-B-T  T-B-T  T-B-T  T-B-T
)

# Tra ngược: tổ hợp -> mã 1..16. Dựng từ bảng trên nên không thể lệch khỏi nó.
MA_PHOI_KHUON_16: dict[tuple[Khuon, ...], int] = {
    bo: i for i, bo in enumerate(PHOI_KHUON_16, start=1)
}

# Hai mẫu §4.3 nằm ở đâu trong bảng 16. Tra bằng bảng thay vì gõ số, để đổi thứ
# tự bảng thì hai hằng số này tự đi theo.
MA_PHOI_KHUON_CO_DIEN: int = MA_PHOI_KHUON_16[PHOI_KHUON_CO_DIEN]
MA_PHOI_KHUON_DAO: int = MA_PHOI_KHUON_16[PHOI_KHUON_DAO]


def chia_cum_bon_dong(khuon: tuple[Khuon, ...]) -> tuple[tuple[Khuon, ...], ...]:
    """Chia dãy khuôn của cả bài thành các cụm 4 dòng liên tiếp.

    Cụm thiếu 4 dòng ở cuối bị BỎ, không được đệm cho đủ. H4 bảo đảm số dòng là
    bội của 4 nên trường hợp đó không xảy ra qua đường chạy thường; bỏ đi là cách
    an toàn khi hàm được gọi trực tiếp.
    """
    return tuple(
        tuple(khuon[i:i + 4]) for i in range(0, len(khuon) - len(khuon) % 4, 4)
    )


def ma_phoi_khuon_cua_cum(cum: tuple[Khuon, ...]) -> int | None:
    """Mã 1..16 của một cụm 4 dòng, hoặc None nếu cụm không nằm trong bảng.

    `cum` là bốn khuôn, mỗi khuôn tóm tắt BA giá trị thanh ở P2, P4, P6 của một
    dòng — xem `khuon_cua_dong`. Không phải bốn giá trị thanh, không phải cả bảy
    vị trí của dòng.

    None xảy ra đúng khi cụm chứa một dòng "pha" hoặc "khong_xac_dinh" — tức là
    tầng 4 đã có việc để làm rồi. Hàm này KHÔNG dựng vi phạm: nó chỉ tra bảng.
    """
    return MA_PHOI_KHUON_16.get(cum)


# ══════════════════════════════════════════════════════════════════════════════
# §6b. NHỊP  —  tài liệu §6, S13–S15
#
# Bảy kiểu ngắt nhịp của tài liệu, cả bảy đều cộng đúng 7 tiếng.
#
# CỐ Ý KHÔNG suy ra nhịp từ hình thức. S13 nói rõ nhịp do NGHĨA của dòng quyết
# định. Ngay ví dụ §11 cũng cho thấy điều đó: dòng "Con ngõ nhỏ dài hơn tiếng ve"
# được tài liệu gán 4/3, trong khi ngữ pháp tự nhiên hơn là 3/4. Đoán nhịp bằng
# hình thức sẽ tạo ra số liệu sai mà trông như đúng.
#
# Thứ kiểm được là một nhịp ĐÃ ĐƯỢC KHAI BÁO có hợp lệ hay không — dùng khi người
# viết (hoặc mô hình) tự nói mình đang ngắt theo nhịp nào.
# ══════════════════════════════════════════════════════════════════════════════

NHIP_TAI_LIEU: dict[str, tuple[int, ...]] = {
    "4/3": (4, 3),
    "3/4": (3, 4),
    "2/2/3": (2, 2, 3),
    "2/5": (2, 5),
    "5/2": (5, 2),
    "1/6": (1, 6),
    "3/2/2": (3, 2, 2),
}


def nhip_hop_le(cach_ngat: tuple[int, ...]) -> bool:
    """Một cách ngắt hợp lệ khi các vế cộng đúng 7 và không vế nào rỗng."""
    return bool(cach_ngat) and all(v > 0 for v in cach_ngat) and sum(cach_ngat) == SO_TIENG_MOI_DONG


# ── QĐ-4, QĐ-4b, QĐ-6 ──────────────────────────────────────────────────────────


def nhip_kha_di_cua_dong(so_tieng: int, nhip_khai_bao: str | None = None) -> frozenset[str]:
    """Tập kiểu nhịp mà một dòng ngắt theo được.

    QĐ-6 chốt: chỉ dùng bảy kiểu nhịp trong tài liệu, KHÔNG thêm thư viện tách từ.
    Tài liệu cho bảy kiểu nhưng không cho ranh giới từ, nên có hai chế độ:

    - **Có khai báo nhịp** (thơ do mô hình sinh): chỉ kiểu được khai báo, và chỉ
      khi nó thuộc bảy kiểu. Khai báo kiểu lạ trả về tập rỗng -> dòng trượt.
    - **Không khai báo** (corpus có sẵn): mọi kiểu đều khả dĩ về mặt số học, vì
      4+3 = 3+4 = 2+2+3 = 7. Bằng chứng của tầng 6 phải nói rõ chỉ kiểm được số
      học, đúng nguyên tắc N3.
    """
    if so_tieng != SO_TIENG_MOI_DONG:
        return frozenset()
    if nhip_khai_bao is None:
        return frozenset(NHIP_TAI_LIEU)
    return frozenset({nhip_khai_bao}) if nhip_khai_bao in NHIP_TAI_LIEU else frozenset()


def nhip_chu_dao(nhip_kha_di_tung_dong: tuple[frozenset[str], ...]) -> str | None:
    """Nhịp chủ đạo = kiểu nhịp tương thích với MỌI dòng của bài (QĐ-4b).

    Trả None nghĩa là không tồn tại kiểu nào phủ hết bài, tức bài trượt tầng 6.

    "Ưu tiên nhịp của bài thơ": khi nhiều kiểu cùng phủ hết, lấy kiểu đứng trước
    theo đúng thứ tự liệt kê ở §6 tài liệu, không lấy kiểu tiện tay.
    """
    if not nhip_kha_di_tung_dong:
        return None
    giao = set(nhip_kha_di_tung_dong[0])
    for tap in nhip_kha_di_tung_dong[1:]:
        giao &= tap
    for ten in NHIP_TAI_LIEU:  # dict giữ thứ tự chèn = thứ tự tài liệu
        if ten in giao:
            return ten
    return None


# ══════════════════════════════════════════════════════════════════════════════
# §7. SƠ ĐỒ VẦN  —  phục vụ §9 Bước 3 của tài liệu
#
# Gom các dòng có tiếng cuối hiệp vần với nhau thành nhóm, gán nhãn a, b, c…
# Dòng không hiệp với dòng nào nhận nhãn 'x' (ký hiệu của tài liệu §1).
# Sơ đồ tính TRONG TỪNG KHỔ, vì S11 yêu cầu nhất quán trong khổ còn S12 cho phép
# đổi vần khi sang khổ mới.
# ══════════════════════════════════════════════════════════════════════════════


def suy_so_do_van(tieng_cuoi: tuple[str, ...]) -> tuple[str, ...]:
    """Sơ đồ vần của một khổ: a/b/c cho dòng hiệp vần, 'x' cho dòng buông.

    KHÔNG gom cụm bắc cầu. Quan hệ hiệp vần theo Trần Trọng Kim không bắc cầu
    (xem chú thích ở `CAP_VAN_THONG`), nên "gom cụm" là phép sai: nó xếp chung
    những dòng mà nguồn nói là KHÔNG hiệp nhau, tức là tự nới luật.

    CÁCH LÀM: một sơ đồ chữ cái chỉ tồn tại khi quan hệ hiệp vần HẠN CHẾ TRONG
    KHỔ NÀY tình cờ là quan hệ tương đương — tức mỗi thành phần liên thông của
    đồ thị hiệp vần là một CLIQUE, mọi cặp bên trong đều hiệp. Khi đó nhãn là duy
    nhất và không phụ thuộc thứ tự dòng.

    Thành phần KHÔNG phải clique thì khổ ấy không có sơ đồ vần xác định, và mọi
    dòng trong thành phần nhận nhãn '?'. Đây là TÌNH TRẠNG THẬT của khổ thơ chứ
    không phải lỗi phần mềm — ví dụ ba dòng kết bằng "vang / vương / vuông":
    vang~vương và vương~vuông, nhưng vang ≁ vuông.
    """
    n = len(tieng_cuoi)
    ke: list[set[int]] = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            a, b = tieng_cuoi[i], tieng_cuoi[j]
            if a and b and hiep_van(a, b).hiep:
                ke[i].add(j)
                ke[j].add(i)

    nhan = ["x"] * n
    da_xet = [False] * n
    chu = 0
    for goc in range(n):
        if da_xet[goc]:
            continue
        da_xet[goc] = True
        thanh_phan = [goc]
        hang_doi = [goc]
        while hang_doi:
            u = hang_doi.pop()
            for v in ke[u]:
                if not da_xet[v]:
                    da_xet[v] = True
                    thanh_phan.append(v)
                    hang_doi.append(v)
        if len(thanh_phan) < 2:
            continue
        la_clique = all(
            b in ke[a] for a in thanh_phan for b in thanh_phan if a != b
        )
        if la_clique:
            for i in thanh_phan:
                nhan[i] = _nhan_van(chu)
            chu += 1
        else:
            for i in thanh_phan:
                nhan[i] = "?"
    return tuple(nhan)


def _nhan_van(chi_so: int) -> str:
    """a, b, … z, aa, ab, … — không giới hạn ở 26 lớp vần."""
    ten = ""
    chi_so += 1
    while chi_so > 0:
        chi_so, du = divmod(chi_so - 1, 26)
        ten = chr(ord("a") + du) + ten
    return ten


def suy_so_do_van_toan_bai(
    tieng_cuoi_theo_kho: tuple[tuple[str, ...], ...],
) -> tuple[tuple[str, ...], ...]:
    """Sơ đồ vần của cả bài, chữ cái đánh LIÊN TỤC qua các khổ (Đ7).

    Đúng ký hiệu §5.2 của tài liệu: "K1: a a x a, K2: b b x b, K3: c c x c" — khổ
    sau đổi vần thì đổi chữ cái. Bản trước đánh lại từ "a" ở mỗi khổ nên hai khổ
    vần hoàn toàn khác nhau lại mang cùng nhãn, đọc ra là sai.

    Việc GOM NHÓM vẫn xét trong phạm vi một khổ (S11); chỉ chữ cái là chung toàn
    bài. Nhờ vậy S12 "đổi vần khi sang khổ mới" hiện ra ngay trên sơ đồ.
    """
    ket_qua: list[tuple[str, ...]] = []
    lop_toan_bai: list[list[str]] = []  # mỗi lớp giữ ĐỦ các tiếng đã xếp vào nó

    for cuoi in tieng_cuoi_theo_kho:
        trong_kho = suy_so_do_van(cuoi)

        # Gom các tiếng theo nhãn trong khổ, giữ thứ tự nhãn xuất hiện.
        thanh_vien: dict[str, list[str]] = {}
        for i, nh in enumerate(trong_kho):
            if nh in ("x", "?"):
                continue
            thanh_vien.setdefault(nh, []).append(cuoi[i])

        anh_xa: dict[str, str] = {}
        for nh, tieng_cua_nhom in thanh_vien.items():
            # Nhập vào lớp cũ CHỈ KHI mọi tiếng của nhóm hiệp với mọi tiếng đã có
            # trong lớp ấy. So với một đại diện là không đủ: quan hệ không bắc
            # cầu nên "hiệp với đại diện" không kéo theo "hiệp với cả lớp", và
            # kết quả sẽ phụ thuộc vào tiếng nào tình cờ được chọn làm đại diện.
            khop = [
                k for k, lop in enumerate(lop_toan_bai)
                if all(hiep_van(x, y).hiep for x in tieng_cua_nhom for y in lop)
            ]
            if len(khop) == 1:
                lop_toan_bai[khop[0]].extend(tieng_cua_nhom)
                anh_xa[nh] = _nhan_van(khop[0])
            else:
                # Không khớp lớp nào, HOẶC khớp nhiều lớp (nhập nhằng do không
                # bắc cầu). Cả hai trường hợp đều mở lớp mới thay vì nhập bừa.
                lop_toan_bai.append(list(tieng_cua_nhom))
                anh_xa[nh] = _nhan_van(len(lop_toan_bai) - 1)

        ket_qua.append(tuple(anh_xa.get(nh, nh) for nh in trong_kho))

    return tuple(ket_qua)


# ══════════════════════════════════════════════════════════════════════════════
# §8. LOẠI TRỪ ĐƯỜNG LUẬT  —  §9 Bước 2 của tài liệu
#
# Tài liệu §2 nói H1–H3 là "điều kiện cần và đủ", nhưng §9 Bước 2 lại thêm một
# điều kiện phủ định: bài Đường luật thì không thuộc thất ngôn tự do. Hai chỗ này
# mâu thuẫn, và Đ1 chốt cách xử lý: kiểm ở mức CẢNH BÁO, không chặn.
#
# Lý do: Bước 2 đòi kiểm "có đối theo mẫu", mà đối là quan hệ từ loại và ngữ nghĩa
# giữa hai dòng — kiểm tự động sẽ báo nhầm, và báo nhầm ở đây nghĩa là loại oan
# một bài hợp lệ. Vì vậy hàm này chỉ xét số dòng, độc vận và niêm; thiếu vế "đối"
# nên kết quả gọi là *nghi ngờ*, không phải kết luận.
# ══════════════════════════════════════════════════════════════════════════════


def nghi_la_duong_luat(dong: tuple[BaoCaoDong, ...]) -> bool:
    n = len(dong)
    if n not in (4, 8):
        return False

    so_do = suy_so_do_van(tuple(d.tieng[-1] if d.tieng else "" for d in dong))
    nhan_that = [nh for nh in so_do if nh != "x"]
    # Độc vận: chỉ một lớp vần, phủ ít nhất n-1 dòng
    if len(set(nhan_that)) != 1 or len(nhan_that) < n - 1:
        return False

    khuon = [d.khuon for d in dong]
    if "pha" in khuon:
        return False

    # Niêm: các cặp dòng phải đồng khuôn theo mẫu Đường luật
    cap = [(1, 2), (3, 0)] if n == 4 else [(1, 2), (3, 4), (5, 6), (7, 0)]
    return all(khuon[i] == khuon[j] for i, j in cap)


# ══════════════════════════════════════════════════════════════════════════════
# §9. CHUẨN BỊ CHUNG CHO CÁC TẦNG
#
# Ba hàm dưới đây chạy TRƯỚC bảy tầng và phục vụ cả bảy:
#   `tach_kho`         cắt bài thành khổ, ranh giới là dòng trống
#   `_phan_tich_dong`  phân tích một dòng đúng MỘT lần: tiếng, thanh, khuôn, vần cuối
#   `_bo_qua`          dựng kết quả cho tầng không được chạy vì đã bị chặn trước
#
# VÌ SAO PHÂN TÍCH MỘT LẦN RỒI DÙNG CHUNG: nếu mỗi tầng tự tách tiếng thì bảy tầng
# có thể hiểu khác nhau về cùng một dòng thơ, và khi số liệu lệch sẽ không ai truy
# được lệch từ đâu. Phân tích một lần thì bảy tầng buộc phải nói về cùng một vật.
#
# GHI CHÚ LỊCH SỬ — chỗ này từng nói khác. Bản trước mô tả một quy trình bốn bước
# trong đó `dat` chỉ do H1–H3 quyết định, và ghi rằng nhịp "cố ý không suy ra tự
# động". Cả hai đều đã lỗi thời: `dat` nay là kết quả của cả bảy tầng, và tầng 6
# có suy nhịp — dù còn rỗng nghĩa khi thiếu bộ tách từ, xem `_tang6_nhip`.
# ══════════════════════════════════════════════════════════════════════════════


def tach_kho(van_ban: str) -> tuple[tuple[str, ...], ...]:
    """Tách bài thành các khổ. Ranh giới khổ là dòng trống (Đ6)."""
    kho: list[tuple[str, ...]] = []
    hien_tai: list[str] = []
    for dong in van_ban.splitlines():
        if dong.strip():
            hien_tai.append(dong.strip())
        elif hien_tai:
            kho.append(tuple(hien_tai))
            hien_tai = []
    if hien_tai:
        kho.append(tuple(hien_tai))
    return tuple(kho)


def _phan_tich_dong(so: int, van_ban: str) -> BaoCaoDong:
    tieng = tach_tieng(van_ban)
    thanh = tuple(thanh_cua(t) for t in tieng)
    return BaoCaoDong(
        so=so,
        van_ban=van_ban,
        tieng=tieng,
        so_tieng=len(tieng),
        thanh=thanh,
        khuon=khuon_cua_dong(tieng),
        van_cuoi=van_cua(tieng[-1]) if tieng else "",
        thanh_cuoi=thanh[-1] if thanh else None,
    )


def _bo_qua(t: DinhNghiaTang, tang_chan: int) -> KetQuaTang:
    """Tầng không được chạy vì một tầng trước đã chặn.

    Ghi ra thay vì lặng lẽ cho qua: `da_chay=False` nói rõ tầng này CHƯA kiểm,
    khác hẳn với "đã kiểm và đạt".
    """
    return KetQuaTang(
        so=t.so, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc,
        da_chay=False, dat=False, trich_luat=t.trich_luat,
        bang_chung=f"bỏ qua vì tầng {tang_chan} đã chặn",
    )


# ══════════════════════════════════════════════════════════════════════════════
# §9b. BẢY TẦNG KIỂM  —  phần thi hành của bảng `TANG` ở §1c
#
# Mỗi tầng là MỘT hàm, ứng với MỘT nhóm điều luật, và tuân đúng bốn quy ước sau.
# Đọc bốn quy ước này một lần thì đọc được cả bảy hàm.
#
#   1. CHỮ KÝ GIỐNG NHAU. Nhận dữ liệu đã phân tích sẵn, trả về một `KetQuaTang`.
#      Tầng không tự tách tiếng, không tự đọc văn bản gốc — phân tích làm một
#      lần ở `kiem_tra_bai_tho` rồi dùng chung, để bảy tầng không thể hiểu khác
#      nhau về cùng một dòng thơ.
#
#   2. KHÔNG TẦNG NÀO GỌI TẦNG KHÁC. Thứ tự do `kiem_tra_bai_tho` điều khiển.
#      Nhờ vậy đổi thứ tự hay bỏ một tầng không làm gãy các tầng còn lại.
#
#   3. LUÔN NỘP BẰNG CHỨNG, kể cả khi đạt. `bang_chung` là một câu người đọc
#      kiểm lại được bằng mắt; `chi_tiet` là số liệu máy đọc được. Yêu cầu của
#      chủ dự án: "từng bài thơ cần thể hiện rõ xem vượt qua từng tầng thế nào".
#
#   4. GHI CÔNG KHAI ĐIỀU KHÔNG KIỂM ĐƯỢC (nguyên tắc N3). Điều nào đòi ý đồ tác
#      giả hoặc ngữ nghĩa thì ghi thẳng khoá `<mã>_khong_kiem_duoc` vào
#      `chi_tiet`, thay vì lặng lẽ cho qua và để người đọc tưởng đã kiểm.
#
# Tầng trượt thì `kiem_tra_bai_tho` DỪNG; các tầng sau nhận `da_chay=False` qua
# `_bo_qua()`, nghĩa là CHƯA KIỂM — khác hẳn "đã kiểm và đạt".
# ══════════════════════════════════════════════════════════════════════════════


def _tang1_hinh_thuc(cac_dong: list[str]) -> KetQuaTang:
    """TẦNG 1 — HÌNH THỨC VÀ SỐ DÒNG. Điều luật: H3, H4.

    HAI PHÉP KIỂM, cả hai đều CỨNG và đều chặn:

        H3  *"Văn bản phải được phân dòng, từ 4 dòng trở lên."*  ->  n >= 4
        H4  *"Số dòng trong bài phải là bội của 4."*             ->  n % 4 == 0

    Gộp lại: số dòng phải thuộc {4, 8, 12, 16, ...}.

    H3 NÂNG TỪ 2 LÊN 4 ngày 18/09/2026 theo chủ dự án: *"sửa H3 phải có đầy đủ
    số dòng phải từ 4 trở lên"*. Ngưỡng 2 cũ đã thành thừa sau khi có H4 — bài
    nhỏ nhất thoả bội-của-4 vốn đã là 4 dòng.

    Vẫn cần CẢ HAI điều: `0 % 4 == 0` nên H4 một mình cho lọt bài rỗng; còn H3
    một mình cho lọt bài 5, 6, 7 dòng.

    ════ H4 BỔ SUNG 18/09/2026 ════

    Nguyên văn yêu cầu: *"số dòng trong mỗi bài thơ là bội của 4 (đây là Rule
    cứng không có ngoại lệ)"*.

    H4 thoạt nhìn chọi với F5 *"không giới hạn số dòng"* và S16 *"số dòng không
    hạn định"*. Chủ dự án đã cho **hợp nhất** cả ba thay vì để bên nào ghi đè
    bên nào — vì hai vế nói về hai chuyện khác nhau:

        F5, S16   về LƯỢNG      không có trần, không có sàn cố định
        H4        về HÌNH DẠNG  phải chia hết cho 4

    Tập số dòng hợp lệ là {4, 8, 12, 16, ...}: vừa vô hạn, vừa là bội của 4. Vì
    vậy F5 và S16 KHÔNG nằm trong `GHI_DE_BOI_QUYET_DINH` — không có mâu thuẫn
    nào để ghi.

    Hệ quả: H4 là ràng buộc CỨNG nên nó vào cả cờ `thuoc_the`, không chỉ `dat`.
    Một bài 6 dòng nay không còn "thuộc thể" nữa.

    Vì sao tầng này đứng đầu: mọi tầng sau đều nói về quan hệ GIỮA các dòng —
    độ dài dòng, khuôn thanh, sơ đồ vần, khổ. Không có dòng thì không có gì để
    nói. Và số dòng sai bội 4 thì bài hỏng bất kể phần còn lại hay đến đâu, nên
    chặn sớm là đúng.

    Bằng chứng: số dòng đếm được, và phần dư khi chia 4.
    """
    t = TANG_THEO_SO[1]
    n = len(cac_dong)
    du = n % 4

    co_phan_dong = n >= 4
    boi_cua_bon = du == 0

    vi_pham: list[ViPham] = []
    if not co_phan_dong:
        vi_pham.append(
            ViPham(
                ma="H3", dong=None,
                ky_vong="văn bản có phân dòng, từ 4 dòng trở lên",
                thuc_te=f"{n} dòng",
                goi_y="Luật cứng — bài không đủ 4 dòng thì không thuộc thể. "
                      "KHÔNG viết thêm dòng để ép qua: nội dung thơ phải giữ nguyên.",
            )
        )
    if not boi_cua_bon:
        # ⛔ KHÔNG GỢI Ý THÊM HAY BỚT DÒNG.
        #
        # Bản trước ghi "bớt 2 dòng để về 4, hoặc thêm 2 dòng để lên 8". Đó là
        # bảo người ta XOÁ một câu thơ, hoặc VIẾT THÊM một câu không có trong bài.
        # Chủ dự án bác thẳng: "không được sửa nội dung cho thêm hay xóa nội dung
        # thơ, phải giữ nguyên nội dung thơ" và "đây là luật cứng không thể sửa
        # để cho bài thơ pass".
        #
        # H4 là luật CỨNG: số dòng không phải bội của 4 thì bài KHÔNG thuộc thể,
        # và đó là phán quyết cuối. Không có "cách sửa" nào cả — sửa được nghĩa là
        # luật mềm. Nguyên tắc chung của bộ kiểm cũng nói vậy: bộ kiểm PHÁN, mô
        # hình viết; gợi ý câu chữ là bộ kiểm đang viết thơ hộ.
        #
        # Với thơ do mô hình SINH RA, ràng buộc này thuộc về ĐỀ BÀI ("viết N dòng,
        # N là bội của 4"), không phải về vòng sửa một bản nháp đã có.
        vi_pham.append(
            ViPham(
                ma="H4", dong=None,
                ky_vong="số dòng là bội của 4",
                thuc_te=f"{n} dòng, dư {du} khi chia 4",
                goi_y="Luật cứng, không có ngoại lệ — bài không thuộc thể. "
                      "KHÔNG thêm hay bớt dòng để ép qua: nội dung thơ phải giữ nguyên.",
            )
        )

    dat = co_phan_dong and boi_cua_bon
    if dat:
        bang_chung = f"{n} dòng — có phân dòng, và {n} = 4 × {n // 4}"
    elif not co_phan_dong:
        bang_chung = f"chỉ {n} dòng — không đủ để coi là có phân dòng"
    else:
        bang_chung = f"{n} dòng — không phải bội của 4 (dư {du})"

    return KetQuaTang(
        so=1, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=bang_chung,
        chi_tiet={
            "so_dong": n,
            "du_khi_chia_4": du,
            "la_boi_cua_4": boi_cua_bon,
            "co_phan_dong": co_phan_dong,
        },
        vi_pham=tuple(vi_pham),
    )


def _tang2_do_dai(bao_cao: tuple[BaoCaoDong, ...]) -> KetQuaTang:
    """TẦNG 2 — ĐỘ DÀI DÒNG. Điều luật: H1, H2.

    Trích luật: *"Mỗi dòng phải có đúng 7 tiếng. Ràng buộc này áp dụng cho toàn
    bộ các dòng của bài, không có ngoại lệ."*

    TIÊU CHÍ CHẶN: **mọi** dòng phải có đúng 7 tiếng. Chỉ một dòng lệch là cả
    bài trượt — đây là chỗ chủ dự án đã đính chính rõ: *"Chỉ cần một dòng 6 đến
    8 tiếng sẽ làm hỏng cả bài thơ nên là bài này hỏng."*

    ════ CHỈ TÍNH TIẾNG — DẤU CÂU KHÔNG TÍNH ════

    Đây là quy tắc quan trọng nhất của tầng này, và cũng là chỗ đã trả giá.

    Đếm tiếng KHÔNG phải đếm từ cách nhau bởi dấu cách. Theo §2.1 tài liệu:

        1. DẤU CÂU KHÔNG TÍNH LÀ TIẾNG
           "Chiều rơi chậm xuống, mái rêu xanh!"  ->  7 tiếng, không phải 9
           Dấu phẩy và dấu than bị loại trước khi đếm.

        2. GẠCH NỐI TÁCH TIẾP, VÌ NÓ MANG THÔNG TIN ÂM TIẾT
           "ra-đi-ô"  ->  3 tiếng
           Đây là NGOẠI LỆ DUY NHẤT: mọi dấu khác đều bị loại, riêng "-" thì
           tách. Xem `_la_dau_cau` ở §3.

        3. CHỮ SỐ QUY VỀ CÁCH ĐỌC RỒI MỚI ĐẾM
           "năm 1975"  ->  năm + một nghìn chín trăm bảy mươi lăm  =  8 tiếng

    🩸 LỖI ĐÃ TRẢ GIÁ — ghi lại để không lặp.

    Bản đầu nhận diện dấu câu bằng DANH SÁCH LIỆT KÊ TAY, và danh sách ấy thiếu
    gạch ngang dài "—" với gạch ngang ngắn "–". Hậu quả:

        "Chiều rơi — chậm xuống mái rêu"     6 tiếng thật
                                          -> bản cũ đếm thành 7
                                          -> LỌT qua H1, bài sai luật được coi
                                             là ĐẠT

    Đây là sai theo hướng nguy hiểm nhất: không phải loại oan bài đúng, mà là
    nhận nhầm bài sai. Nguyên nhân gốc không phải quên một ký tự, mà là chọn sai
    cách: **danh sách liệt kê thì luôn thiếu**. Nay nhận diện theo PHÂN LOẠI
    UNICODE (`category` bắt đầu bằng "P" hoặc "S"), nên mọi dấu câu và ký hiệu
    đều bị bắt kể cả dấu chưa từng gặp.

    Test `test_gach_ngang_dai_va_ngan_KHONG_duoc_tinh_la_tieng` ghim bốn ca:
    "—", "–", "«»", "…".

    Vì sao đứng trước tầng 4: P2/P4/P6 chỉ có nghĩa trên dòng đủ 7 tiếng. Tính
    khuôn thanh cho dòng 6 tiếng là gán cho tác giả một lựa chọn phong cách mà
    họ chưa hề thực hiện.

    Bằng chứng: số tiếng từng dòng, dòng nào lệch và lệch bao nhiêu, cùng số ký
    tự dấu câu đã bị loại — để người đọc kiểm được rằng phép đếm có trừ dấu.
    """
    t = TANG_THEO_SO[2]
    hong = [bc for bc in bao_cao if bc.so_tieng != SO_TIENG_MOI_DONG]
    do_dai = [bc.so_tieng for bc in bao_cao]

    vi_pham = []
    for bc in hong:
        lech = bc.so_tieng - SO_TIENG_MOI_DONG
        goi_y = f"bỏ {lech} tiếng" if lech > 0 else f"thêm {-lech} tiếng"
        if bc.tieng:
            goi_y += f'; giữ vần "{bc.van_cuoi}" ở tiếng cuối nếu dòng này đang gánh vần'
        vi_pham.append(
            ViPham(ma="H1", dong=bc.so, ky_vong="7 tiếng",
                   thuc_te=f"{bc.so_tieng} tiếng", goi_y=goi_y)
        )

    # Đếm ký tự dấu câu bị loại trên toàn bài. Gạch nối KHÔNG tính vào đây vì nó
    # không bị loại mà được dùng để tách tiếp — xem `_la_dau_cau`.
    so_dau_loai = sum(
        1 for bc in bao_cao for ky_tu in bc.van_ban if _la_dau_cau(ky_tu)
    )

    n = len(bao_cao)
    dat = not hong
    return KetQuaTang(
        so=2, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=(
            f"{n}/{n} dòng đúng 7 tiếng; nhỏ nhất = lớn nhất = 7" if dat
            else f"{len(hong)}/{n} dòng sai số tiếng: "
                 + ", ".join(f"D{bc.so}={bc.so_tieng}" for bc in hong[:6])
                 + ("…" if len(hong) > 6 else "")
        ),
        chi_tiet={
            "so_tieng_tung_dong": do_dai,
            "so_tieng_nho_nhat": min(do_dai) if do_dai else 0,
            "so_tieng_lon_nhat": max(do_dai) if do_dai else 0,
            # Bằng chứng rằng phép đếm CÓ trừ dấu câu. Nói "dấu không tính" mà
            # không đưa số thì người đọc phải tin suông; đưa số thì kiểm được.
            "so_dau_cau_da_loai": so_dau_loai,
            "quy_tac_dem": "chỉ tính tiếng; dấu câu loại theo phân loại Unicode "
                           "(P*, S*); riêng gạch nối '-' thì TÁCH tiếp vì mang "
                           "thông tin âm tiết; chữ số quy về cách đọc (§2.1)",
        },
        vi_pham=tuple(vi_pham),
    )


def _tang3_loai_tru_duong_luat(bao_cao: tuple[BaoCaoDong, ...]) -> KetQuaTang:
    """TẦNG 3 — ĐỐI CHIẾU ĐƯỜNG LUẬT. Điều luật: F1–F5. **KHÔNG CHẶN.**

    Trích luật (§3): *"Việc một bài thất ngôn tự do vẫn có niêm, có đối, có độc
    vận là **được phép**. Nhưng đó là **lựa chọn của tác giả, không phải tiêu chí
    nhận diện thể**."* · F5: *"Không giới hạn số dòng ở con số 4 hoặc 8."*

    TẦNG NÀY KHÔNG ĐÁNH TRƯỢT BÀI NÀO. Nó ghi nhận `nghi_duong_luat` để báo cáo,
    rồi cho đi tiếp.

    ════ SỬA LỖI 18/09/2026 — ghi lại để không ai khôi phục nhầm ════

    Bản trước đặt tầng này là `muc="chan"` và loại 4.288 bài. Đó là tôi đọc
    NGƯỢC tài liệu, và chủ dự án đã chỉ ra: *"là thể thơ tự do thì không bị ràng
    buộc về số dòng, bao nhiêu dòng cũng được"*.

    Đọc sai ở đâu: §3 mang tiêu đề "Điều bị loại bỏ khỏi thể". F1–F5 là những
    RÀNG BUỘC ĐÃ ĐƯỢC GỠ BỎ — thể này *không đòi* niêm, *không đòi* đối, *không
    đòi* độc vận, *không giới hạn* số dòng ở 4 hoặc 8. Tôi đã hiểu thành "có các
    thứ đó thì bị loại", tức là biến một câu nới thành một câu cấm.

    Câu chốt của §3 bác bỏ thẳng cách hiểu cũ: có niêm/đối/độc vận là *được
    phép*, và *không phải tiêu chí nhận diện thể*.

    HAI PHẦN TÀI LIỆU MÂU THUẪN NHAU — nói rõ chứ không giấu:

        §3        có niêm/đối/độc vận là được phép, không phải tiêu chí nhận diện
        §9 Bước 2 nếu 4 hoặc 8 dòng + độc vận + niêm + đối thì thuộc Đường luật

    Chọn theo §3 vì ba lẽ: (1) §3 nói thẳng về *tiêu chí nhận diện thể*, đúng câu
    hỏi đang đặt ra; (2) F5 phủ định trực tiếp con số 4/8 mà §9 Bước 2 dựa vào;
    (3) chủ dự án — tác giả của tài liệu — đã xác nhận cách đọc này.

    Ngay cả khi theo §9 Bước 2 thì tầng cũng KHÔNG ĐƯỢC chặn, vì tài liệu đòi
    **bốn** vế mà máy chỉ kiểm được **ba**: phép đối là quan hệ từ loại và ngữ
    nghĩa giữa hai dòng. Chặn dựa trên ba phần tư điều kiện nghĩa là loại oan.
    `nghi_la_duong_luat()` vì vậy giữ chữ *nghi*, và F2, F4 được ghi thẳng vào
    `chi_tiet` là không kiểm được.

    Bằng chứng: số dòng, và bài có khớp ba vế kiểm được hay không.
    """
    t = TANG_THEO_SO[3]
    nghi = nghi_la_duong_luat(bao_cao)
    n = len(bao_cao)
    # KHÔNG dựng ViPham. Tầng này không đánh trượt, nên không có "vi phạm" nào để
    # ghi: theo §3, có niêm và độc vận là quyền của tác giả. Bản trước dựng một
    # ViPham(ma="F3") ở đây, và nó chảy thẳng vào `v.vi_pham` khiến 4.288 bài mang
    # tiếng vi phạm một điều luật mà thật ra chỉ nói rằng điều đó KHÔNG bắt buộc.
    vi_pham: tuple[ViPham, ...] = ()
    return KetQuaTang(
        # `dat=True` LUÔN LUÔN. Tầng ghi nhận không có khái niệm trượt: nó quan
        # sát rồi cho đi tiếp. Kết quả quan sát nằm ở `chi_tiet["nghi_duong_luat"]`.
        so=3, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=True,
        trich_luat=t.trich_luat,
        bang_chung=(
            f"{n} dòng — không đủ ba vế số dòng + độc vận + niêm"
            if not nghi
            else f"{n} dòng, độc vận và có niêm — giống khuôn Đường luật, "
                 "nhưng §3 cho phép nên KHÔNG loại"
        ),
        chi_tiet={
            "so_dong": n,
            "nghi_duong_luat": nghi,
            "F2_khong_kiem_duoc": "phép đối đòi so từ loại và ngữ nghĩa giữa hai dòng",
            "F4_khong_kiem_duoc": "bố cục Khai–Thừa–Chuyển–Hợp đòi hiểu nội dung",
        },
        vi_pham=vi_pham,
    )


def _tang4_thanh_luat(
    bao_cao: tuple[BaoCaoDong, ...],
    van_lung: tuple[tuple[int, int], ...] = (),
) -> KetQuaTang:
    """TẦNG 4 — THANH LUẬT. Điều luật: S1, S2, S3.

    Trích luật (S2): *"P2, P4, P6 **nên** luân phiên bằng – trắc để tạo nhạc
    tính."*

    TIÊU CHÍ CHẶN: **mọi** dòng phải khớp một trong hai khuôn —
    khuôn bằng `B T B` hoặc khuôn trắc `T B T` ở vị trí P2/P4/P6.
    Dòng không khớp khuôn nào gọi là *phá khuôn*.

    HAI CHỖ DỰ ÁN CHẶT HƠN TÀI LIỆU, ghi ra để mã và tài liệu không nói hai
    điều khác nhau (xem §6.5 docs/Plan_Rule_Phan_Tang.md):

        QĐ-1  Tài liệu dùng chữ "nên" và nói ở mức dòng. Chủ dự án chốt:
              *"phải áp dụng lên toàn bộ dòng của một bài thơ"* — thành bắt buộc.
        QĐ-2  Không cho phá khuôn: *"Không được phá khuôn phải tuân thủ toàn bộ
              Rule đã có"*.

    QĐ-2 NAY KHÔNG CÒN GHI ĐÈ ĐIỀU NÀO. Trước 18/09 nó ghi đè S4 *"có thể phá
    khuôn khi dụng ý biểu đạt đòi hỏi"*, và mâu thuẫn ấy phải ghi vào
    `GHI_DE_BOI_QUYET_DINH`. Chủ dự án đã XOÁ S4 và S5 khỏi bảng luật, nên không
    còn điều nào cho phép phá khuôn — QĐ-2 thành tiêu chí thẳng, không phải một
    quyết định đi ngược tài liệu. Đây là bớt mâu thuẫn, không phải bớt chặt chẽ:
    tiêu chí không đổi một chữ, chỉ căn cứ của nó gọn lại.

    ĐÂY LÀ TẦNG LOẠI NHIỀU BÀI NHẤT trong corpus — 30.571 bài, gấp 4,65 lần
    tầng đứng thứ hai. Con số đó là hệ quả trực tiếp của QĐ-1 và QĐ-2, không
    phải do thước đo hỏng.

    Số cũ ghi ở đây là 33.775 và CHƯA TỪNG ĐƯỢC ĐO — nó tồn tại vì docstring
    không nằm trong vùng quét của doi_soat_tai_lieu.py. Nguồn thật: tong_hop.json.

    🔶 KHÔNG KIỂM ĐƯỢC: S3 *"P7 cần chọn có chủ đích"* đòi ý đồ tác giả.

    S1 LÀ QUYỀN, KHÔNG BAO GIỜ ĐÁNH TRƯỢT (N2). Hai vế của nó được thi hành theo
    hai cách khác nhau, và cả hai đều đúng:
        "P1, P3, P5 có thể tự do"  -> bằng SỰ VẮNG MẶT của mã: không dòng nào
                                      trong tệp này đọc P1/P3/P5 để phán quyết.
        "có thể dùng vần lưng"     -> ĐO rồi ghi vào chi_tiet, không phán quyết.
                                      Vế này gộp từ S7 ngày 18/09.

    Bằng chứng: khuôn của từng dòng, và dòng nào phá khuôn kèm P2/P4/P6 thực tế.
    """
    t = TANG_THEO_SO[4]
    pha = [bc for bc in bao_cao if bc.khuon == "pha"]
    n = len(bao_cao)
    vi_pham = tuple(
        ViPham(
            ma="S2", dong=bc.so,
            ky_vong="P2/P4/P6 luân phiên theo khuôn bằng (B T B) hoặc khuôn trắc (T B T)",
            thuc_te="P2/P4/P6 = " + " ".join(
                (bc.thanh[i] if i < len(bc.thanh) else "?") for i in (1, 3, 5)
            ),
            goi_y="Đổi thanh ở P2, P4 hoặc P6 để dòng khớp một trong hai khuôn",
        )
        for bc in pha
    )
    dat = not pha

    # Bảng 16 tổ hợp (§6c). Đây là MÔ TẢ, không phải tiêu chí thứ hai: bảng là tập
    # đầy đủ 2^4 nên "mọi cụm có mã" và "mọi dòng khớp khuôn" là cùng một điều.
    # Ghi ra để biên bản nói được cụm nào theo tổ hợp nào, thay vì chỉ nói đạt.
    cum = chia_cum_bon_dong(tuple(bc.khuon for bc in bao_cao))
    ma_cum = [ma_phoi_khuon_cua_cum(c) for c in cum]

    if dat:
        bang_chung = (
            f"{n}/{n} dòng khớp khuôn; 0 dòng phá khuôn; "
            f"{len(cum)} cụm 4 dòng theo tổ hợp "
            + " ".join(f"#{m}" for m in ma_cum)
        )
    else:
        bang_chung = (
            f"{len(pha)}/{n} dòng phá khuôn: "
            + ", ".join(f"D{bc.so}" for bc in pha[:8])
            + ("…" if len(pha) > 8 else "")
        )

    return KetQuaTang(
        so=4, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=bang_chung,
        chi_tiet={
            "khuon_tung_dong": [bc.khuon for bc in bao_cao],
            "so_dong_pha_khuon": len(pha),
            # None = cụm chứa dòng phá khuôn; khi `dat` thì mọi phần tử đều có số.
            "ma_phoi_khuon_tung_cum": ma_cum,
            "so_cum_bon_dong": len(cum),
            "bang_16_la_tap_day_du": True,
            # S1 — cả hai vế đều là QUYỀN, đo rồi ghi, không bao giờ phán quyết.
            "S1_p1_p3_p5_khong_bi_kiem": True,
            "so_vi_tri_van_lung": len(van_lung),
            "vi_tri_van_lung": list(van_lung),
            "S3_khong_kiem_duoc": "P7 cần chọn có chủ đích — đòi ý đồ tác giả",
        },
        vi_pham=vi_pham,
    )


def _tang5_van(
    so_do_theo_kho: tuple[tuple[str, ...], ...],
    cuoi_moi_dong: tuple[str, ...],
    lech_thanh: tuple[tuple[int, int], ...],
) -> KetQuaTang:
    """QĐ-3 (bảng vần theo ngữ âm) và QĐ-7 (tiêu chí chặn).

    QĐ-5: bảng vần thông lấy từ Trần Trọng Kim, "Việt thi" I-6 — `CAP_VAN_THONG`.

    QĐ-7 — quét cửa sổ bốn dòng liên tiếp suốt cả bài; chỉ cần MỘT cửa sổ đạt là
    tầng đạt. Nguyên văn: *"trong bài phải có ít nhất là 4 dòng liên tiếp có cấu
    trúc như thế ở cuối"*.

    QĐ-7b — TIÊU CHÍ CỦA CỬA SỔ, sửa 18/09/2026. Nguyên văn chủ dự án:

        "vần chân sẽ là như vậy trong phạm vi 4 câu
         (Nếu không có vần chân nào thì trượt)"

    Cửa sổ đạt khi có ÍT NHẤT MỘT CẶP HIỆP VẦN ở P7 — không cần khớp sơ đồ nào
    trong danh sách. Cụm duy nhất bị loại là `xxxx`.

    THAY ĐỔI SO VỚI BẢN TRƯỚC. Bản trước đòi cửa sổ khớp ĐÚNG một trong bốn sơ
    đồ §5.2, nên loại cả `aaaa` (độc vận), `axax`, `xaxa`… Chủ dự án nêu danh
    sách mở *"aabb, abab, abba, aaxa, aaaa, aaba, ..."* rồi chốt bằng câu trong
    ngoặc — câu ấy mới là luật. Đo được: tầng 5 từ 18.150 lên 24.366 bài đạt.

    (`aaba` không phải sơ đồ riêng: nhãn 'b' đòi ít nhất hai dòng cùng lớp vần,
    nên dòng lẻ loi luôn nhận 'x'. `aaba` chính là `aaxa`.)

    Vì sao chỉ đòi MỘT cửa sổ: §5.2 kết bằng "**Vần hỗn hợp**: phối nhiều sơ đồ
    trên trong cùng một bài". Đòi cả bài theo một sơ đồ duy nhất là cấm vần hỗn
    hợp, tức là chặt hơn tài liệu ở chỗ tài liệu cho phép.

    S8 ĐÃ XOÁ KHỎI BẢNG LUẬT cùng ngày. S8 nói *"Bài có thể không gieo vần"*,
    trong khi tiêu chí này loại đúng những bài không gieo vần — giữ cả hai là tự
    mâu thuẫn. Chủ dự án chọn xoá S8 thay vì ghi nó vào `GHI_DE_BOI_QUYET_DINH`.

    HỆ QUẢ PHẢI NÓI RÕ: bài dưới bốn dòng không thể có cửa sổ nào, nên trượt
    tầng 5. Nay H3 đòi ≥4 dòng và H4 đòi bội của 4 nên nhánh đó không còn với
    tới được qua đường chạy thường.
    """
    t = TANG_THEO_SO[5]
    co_van = cua_so_co_van_chan(cuoi_moi_dong)
    dat = bool(co_van)
    # Bảng tên: cụm nào khớp một sơ đồ §5.2 thì gọi đúng tên tài liệu đặt.
    khop = cua_so_khop_so_do(cuoi_moi_dong)
    ten_theo_dong = dict(khop)

    if dat:
        dong_dau, so_do = co_van[0]
        bon_dong = cuoi_moi_dong[dong_dau - 1:dong_dau + 3]
        ten = SO_DO_KHO_TAI_LIEU.get(ten_theo_dong.get(dong_dau, ""))
        bang_chung = (
            f"dòng {dong_dau}–{dong_dau + 3} có vần chân, sơ đồ {so_do}"
            + (f" ({ten})" if ten else "")
            + f": {' / '.join(bon_dong)}"
            + (f"; tổng {len(co_van)} cụm có vần" if len(co_van) > 1 else "")
        )
        vi_pham: tuple[ViPham, ...] = ()
    else:
        # Nêu ra bài THỰC SỰ vần thế nào, để người đọc đối chiếu được với bốn sơ
        # đồ — nói "không khớp" mà không nói khớp cái gì thì không phải bằng chứng.
        thuc_te = (
            "; ".join(
                f"dòng {i + 1}–{i + 4}: {''.join(suy_so_do_van(cuoi_moi_dong[i:i + 4]))}"
                for i in range(min(3, max(0, len(cuoi_moi_dong) - 3)))
            )
            or f"bài chỉ có {len(cuoi_moi_dong)} dòng, không đủ một cụm bốn dòng"
        )
        bang_chung = f"không cụm bốn dòng liên tiếp nào có vần chân — {thuc_te}"
        vi_pham = (
            ViPham(
                ma="S11", dong=None,
                ky_vong="ít nhất 4 dòng liên tiếp có vần chân — trong cụm đó phải "
                        "có ít nhất một cặp tiếng cuối hiệp vần",
                thuc_te=thuc_te,
                goi_y="Sửa tiếng cuối của hai dòng trong cùng một cụm bốn dòng "
                      "cho hiệp vần; sơ đồ nào cũng được, không bắt buộc aabb/abab",
            ),
        )

    return KetQuaTang(
        so=5, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=bang_chung,
        vi_pham=vi_pham,
        chi_tiet={
            "so_do_van_theo_kho": ["".join(k) for k in so_do_theo_kho],
            "cum_co_van_chan": [
                {
                    "dong_bat_dau": d,
                    "so_do": so_do,
                    # `ten` chỉ có khi cụm tình cờ khớp một sơ đồ §5.2; None
                    # KHÔNG nghĩa là cụm hỏng — nó chỉ là cụm không có tên riêng.
                    "ten": SO_DO_KHO_TAI_LIEU.get(ten_theo_dong.get(d, "")),
                }
                for d, so_do in co_van
            ],
            "so_cum_co_van_chan": len(co_van),
            "so_cum_khop_so_do_tai_lieu": len(khop),
            "so_cap_van_lech_thanh": len(lech_thanh),
            "so_kho_khong_co_so_do_xac_dinh": sum(
                1 for k in so_do_theo_kho if "?" in k
            ),
            "nguon_bang_van": "Trần Trọng Kim, Việt thi, I-6 — "
                              "docs/Nguon_Bang_Van_Thong.md",
        },
    )


def _tang6_nhip(
    bao_cao: tuple[BaoCaoDong, ...], nhip_khai_bao: Sequence[str | None] | None
) -> KetQuaTang:
    """TẦNG 6 — NHỊP. Điều luật: S13–S15.

    Trích luật (S14): *"Nên có một nhịp chủ đạo để bài có xương sống âm thanh."*

    TIÊU CHÍ CHẶN, hai bước:
        6a  mỗi dòng phải ngắt được theo ít nhất một trong **bảy** kiểu nhịp
            của §6 tài liệu (QĐ-6b)
        6b  phải tồn tại **một** kiểu tương thích với **mọi** dòng — *nhịp chủ
            đạo* (QĐ-4b). Về mặt cài đặt, đó là GIAO của các tập nhịp khả dĩ.

    Tập bảy kiểu là tập ĐÓNG: `4/3, 3/4, 2/2/3, 2/5, 5/2, 1/6, 3/2/2`. QĐ-6 chốt
    lấy đúng §6 tài liệu, không tra thêm nguồn ngoài.

    Cách dùng giao thay vì "đa số dòng" là cố ý: nói "đa số" thì phải định nghĩa
    đa số là bao nhiêu, mà tài liệu không nói — đặt con số ở đó là tự chế luật,
    điều nguyên tắc N1 cấm. Phép giao là kiểm nhị phân, không có chỗ cho ngưỡng.

    ⚠️ CẢNH BÁO BẮT BUỘC ĐỌC — TẦNG NÀY HIỆN RỖNG NGHĨA VỚI THƠ KHÔNG KHAI BÁO.
    Ngắt nhịp là ngắt theo RANH GIỚI TỪ, không phải theo vị trí tiếng. Chưa có
    bộ tách từ tiếng Việt thì mọi dòng 7 tiếng đều "cắt được" thành 4/3, 3/4,
    2/5… vì phép cắt chỉ là đếm số. Hệ quả: `nhip_kha_di_cua_dong` trả về cả bảy
    kiểu cho mọi dòng đủ 7 tiếng, giao khác rỗng, tầng luôn đạt.

    Đo trên corpus: tầng này chặn **0/16.391** bài — và đó KHÔNG phải vì thơ đạt
    nhịp. `chi_tiet["nguon_nhip"]` ghi `"khong_khai_bao"` để biên bản nói thật.
    Tầng chỉ chặn được thật khi `nhip_khai_bao` có giá trị, tức là với thơ do mô
    hình sinh ra kèm khai báo nhịp từng dòng.

    🔶 KHÔNG KIỂM ĐƯỢC: S15 *"đổi nhịp nên trùng chỗ chuyển ý"* đòi ngữ nghĩa.

    Bằng chứng: nhịp chủ đạo, nguồn nhịp, và tập nhịp khả dĩ của từng dòng.
    """
    t = TANG_THEO_SO[6]
    khai = list(nhip_khai_bao) if nhip_khai_bao else [None] * len(bao_cao)
    if len(khai) < len(bao_cao):
        khai += [None] * (len(bao_cao) - len(khai))

    kha_di = tuple(
        nhip_kha_di_cua_dong(bc.so_tieng, khai[i]) for i, bc in enumerate(bao_cao)
    )
    chu_dao = nhip_chu_dao(kha_di)
    co_khai_bao = any(x is not None for x in khai[: len(bao_cao)])

    dat = chu_dao is not None
    vi_pham = () if dat else (
        ViPham(
            ma="S14", dong=None,
            ky_vong="tồn tại một kiểu nhịp phủ mọi dòng",
            thuc_te="không kiểu nào trong bảy kiểu phủ hết bài",
            goi_y="Ngắt lại các dòng lệch để cả bài cùng một nhịp chủ đạo",
        ),
    )
    return KetQuaTang(
        so=6, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=(
            f"nhịp chủ đạo {chu_dao} phủ cả {len(bao_cao)}/{len(bao_cao)} dòng"
            + ("" if co_khai_bao else " — KHÔNG có khai báo nhịp nên chỉ kiểm được số học")
            if dat else "không tồn tại kiểu nhịp nào phủ mọi dòng"
        ),
        chi_tiet={
            "nhip_chu_dao": chu_dao,
            "nguon_nhip": "khai_bao" if co_khai_bao else "khong_khai_bao",
            "nhip_kha_di_tung_dong": [sorted(k) for k in kha_di],
            "S15_khong_kiem_duoc": "đổi nhịp trùng chỗ chuyển ý — đòi ngữ nghĩa",
        },
        vi_pham=vi_pham,
    )


def _tang7_kho_bo_cuc(kho: tuple[tuple[str, ...], ...]) -> KetQuaTang:
    """TẦNG 7 — KHỔ VÀ BỐ CỤC. Điều luật: S16–S21.

    Trích luật (S16): *"Số dòng trong bài không hạn định; có thể viết liên hoàn,
    không chia khổ."*

    TIÊU CHÍ CHẶN: không có khổ rỗng. Chỉ vậy thôi — và điều đó là ĐÚNG, không
    phải thiếu sót.

    VÌ SAO TẦNG NÀY GẦN NHƯ LUÔN ĐẠT: trong sáu điều S16–S21, phần lớn là QUYỀN
    (*"không hạn định"*, *"có thể"*). Theo nguyên tắc N2 của plan, điều loại
    quyền KHÔNG BAO GIỜ được dùng làm tiêu chí đánh trượt — đánh trượt một bài
    vì tác giả dùng đúng cái quyền tài liệu cho phép là mâu thuẫn tự thân. Test
    `test_khong_dieu_QUYEN_nao_lam_tieu_chi_chan` cưỡng chế điều này.

    Nên đừng đọc "tầng 7 chặn 0 bài" là tầng thừa. Nó vẫn chạy, vẫn nộp bằng
    chứng về cấu trúc khổ, và vẫn bắt được khổ rỗng — thứ duy nhất ở đây thực sự
    sai chứ không phải lựa chọn phong cách.

    🔶 KHÔNG KIỂM ĐƯỢC: S19 mạch cảm xúc / mạch tự sự đòi hiểu nội dung.

    Bằng chứng: số khổ và kích thước từng khổ.
    """
    t = TANG_THEO_SO[7]
    kich_thuoc = [len(k) for k in kho]
    rong = [i + 1 for i, k in enumerate(kho) if not k]
    dat = not rong
    return KetQuaTang(
        so=7, ten=t.ten, ma_luat=t.ma_luat, muc=t.muc, da_chay=True, dat=dat,
        trich_luat=t.trich_luat,
        bang_chung=(
            f"{len(kho)} khổ, kích thước {kich_thuoc}, không khổ rỗng" if dat
            else f"có khổ rỗng ở vị trí {rong}"
        ),
        chi_tiet={
            "so_kho": len(kho),
            "kich_thuoc_tung_kho": kich_thuoc,
            "S19_khong_kiem_duoc": "mạch cảm xúc hoặc mạch tự sự đòi hiểu nội dung",
        },
        vi_pham=(),
    )


def kiem_tra_bai_tho(
    van_ban: str, *, nhip_khai_bao: Sequence[str | None] | None = None
) -> PoemVerdict:
    """Kiểm một bài thơ, chạy TUẦN TỰ qua bảy tầng.

    Bài phải qua tầng N mới sang tầng N+1. Dừng sớm không phải để nhanh mà để
    đúng: tính khuôn trên một dòng 6 tiếng là gán cho tác giả một lựa chọn phong
    cách mà họ chưa hề thực hiện.

    Hai cờ phán quyết, CỐ Ý không gộp:
        `thuoc_the`  chỉ H1–H3 — câu trả lời của TÀI LIỆU LUẬT (§2)
        `dat`        qua toàn bộ tầng — câu trả lời của DỰ ÁN (QĐ-1 → QĐ-6)

    `nhip_khai_bao` là nhịp do người viết hoặc mô hình khai cho từng dòng. Corpus
    có sẵn không có trường này nên để None — khi đó tầng 6 chỉ kiểm được số học.
    """
    kho = tach_kho(van_ban)
    cac_dong_tho = [d for k in kho for d in k]
    ghi_chu: list[str] = []
    bao_cao = tuple(_phan_tich_dong(i, d) for i, d in enumerate(cac_dong_tho, start=1))

    # ---- Mô tả lựa chọn mềm, tính trước để các tầng dùng chung ----
    cuoi_theo_kho: list[tuple[str, ...]] = []
    khuon_theo_kho: list[tuple[Khuon, ...]] = []
    chi_so = 0
    for k in kho:
        cuoi_theo_kho.append(
            tuple(
                bao_cao[chi_so + i].tieng[-1] if bao_cao[chi_so + i].tieng else ""
                for i in range(len(k))
            )
        )
        khuon_theo_kho.append(tuple(bao_cao[chi_so + i].khuon for i in range(len(k))))
        chi_so += len(k)

    so_do_theo_kho = list(suy_so_do_van_toan_bai(tuple(cuoi_theo_kho)))
    phoi_khuon = tuple(phoi_khuon_cua_kho(k) for k in khuon_theo_kho)
    # §6c: chia theo CỤM 4 dòng liên tiếp — khác `phoi_khuon` vốn chia theo KHỔ.
    # Hai cách chia trùng nhau khi bài chia khổ đều 4 dòng, lệch nhau khi không.
    ma_phoi_khuon_cum = tuple(
        ma_phoi_khuon_cua_cum(c)
        for c in chia_cum_bon_dong(tuple(bc.khuon for bc in bao_cao))
    )

    # Tỷ lệ tính trên các dòng CÓ khuôn xác định. Đưa dòng sai số tiếng vào mẫu số
    # sẽ trộn hai chuyện khác nhau: sai luật cứng và lựa chọn phong cách.
    dong_co_khuon = [bc for bc in bao_cao if bc.khuon != "khong_xac_dinh"]
    theo_khuon = sum(1 for bc in dong_co_khuon if bc.khuon != "pha")
    ty_le = round(theo_khuon / len(dong_co_khuon), 3) if dong_co_khuon else 0.0

    van_lung = tuple(
        (bc.so, vi_tri) for bc in bao_cao for vi_tri in van_lung_cua_dong(bc.tieng)
    )

    # Ghi nhận các cặp hiệp vần lệch lớp thanh (Đ3)
    lech_thanh: list[tuple[int, int]] = []
    chi_so = 0
    for k, so_do in zip(kho, so_do_theo_kho, strict=True):
        for i in range(len(k)):
            for j in range(i + 1, len(k)):
                if so_do[i] != "x" and so_do[i] == so_do[j]:
                    a, b = bao_cao[chi_so + i], bao_cao[chi_so + j]
                    if a.tieng and b.tieng and not hiep_van(a.tieng[-1], b.tieng[-1]).dong_thanh:
                        lech_thanh.append((a.so, b.so))
        chi_so += len(k)

    # ══════════════════════════════════════════════════════════════════════════
    # CHẠY TUẦN TỰ BẢY TẦNG. Tầng chặn nào trượt thì DỪNG, các tầng sau mang
    # da_chay=False chứ không giả vờ đã kiểm.
    # ══════════════════════════════════════════════════════════════════════════
    ket_qua_tang: list[KetQuaTang] = []
    tang_dung_lai: int | None = None

    def _chay(kq: KetQuaTang) -> bool:
        """Ghi kết quả một tầng. Trả False nếu tầng chặn này trượt."""
        nonlocal tang_dung_lai
        ket_qua_tang.append(kq)
        if kq.muc == "chan" and not kq.dat:
            tang_dung_lai = kq.so
            return False
        return True

    thu_tu = (
        lambda: _tang1_hinh_thuc(cac_dong_tho),
        lambda: _tang2_do_dai(bao_cao),
        lambda: _tang3_loai_tru_duong_luat(bao_cao),
        lambda: _tang4_thanh_luat(bao_cao, van_lung),
        lambda: _tang5_van(
            tuple(so_do_theo_kho),
            tuple(bc.tieng[-1] if bc.tieng else "" for bc in bao_cao),
            tuple(lech_thanh),
        ),
        lambda: _tang6_nhip(bao_cao, nhip_khai_bao),
        lambda: _tang7_kho_bo_cuc(kho),
    )
    for lam in thu_tu:
        if not _chay(lam()):
            break
    for t in TANG[len(ket_qua_tang):]:
        ket_qua_tang.append(_bo_qua(t, tang_dung_lai or 0))

    # `thuoc_the` chỉ hỏi tài liệu luật: tầng 1 và tầng 2, tức H1–H3.
    thuoc_the = all(
        kq.dat for kq in ket_qua_tang if kq.so in (1, 2) and kq.da_chay
    ) and ket_qua_tang[1].da_chay
    # CHỈ tầng CHẶN mới góp vào phán quyết. Tầng loại `ghi_nhan` có thể trả
    # `dat=False` để biên bản nói thật rằng nó phát hiện điều gì, nhưng phát hiện
    # ấy KHÔNG được loại bài — nếu không thì "ghi nhận" và "chặn" là một.
    dat = all(kq.dat for kq in ket_qua_tang if kq.muc == "chan")
    vi_pham = tuple(vp for kq in ket_qua_tang for vp in kq.vi_pham)

    nghi = ket_qua_tang[2].da_chay and not ket_qua_tang[2].dat
    if nghi:
        ghi_chu.append(
            "Bài có số dòng, độc vận và niêm giống Đường luật. "
            "Chưa kiểm được phép đối nên phần này chỉ dựa trên ba vế đo được."
        )
    if lech_thanh:
        ghi_chu.append(
            f"Có {len(lech_thanh)} cặp hiệp vần lệch lớp thanh — được phép theo S9, ghi nhận để tham khảo."
        )
    if tang_dung_lai:
        ghi_chu.append(f"Dừng ở tầng {tang_dung_lai}; các tầng sau chưa được kiểm.")

    return PoemVerdict(
        dat=dat,
        thuoc_the=thuoc_the,
        tang=tuple(ket_qua_tang),
        tang_dung_lai=tang_dung_lai,
        vi_pham=vi_pham,
        dong=bao_cao,
        so_dong=len(bao_cao),
        so_kho=len(kho),
        so_do_van_theo_kho=tuple(so_do_theo_kho),
        phoi_khuon_theo_kho=phoi_khuon,
        ma_phoi_khuon_theo_cum=ma_phoi_khuon_cum,
        ty_le_theo_khuon=ty_le,
        van_lech_thanh=tuple(lech_thanh),
        van_lung=van_lung,
        nghi_duong_luat=nghi,
        ghi_chu=tuple(ghi_chu),
    )


# ══════════════════════════════════════════════════════════════════════════════
# §10. BẢNG HÀM KIỂM  —  cưỡng chế sự tương ứng giữa bảng luật và mã nguồn
#
# Mỗi mã luật CỨNG phải có một mục ở đây. Test kiến trúc đối chiếu `MA_CUNG` với
# tập khoá của bảng này: thêm luật cứng mà quên viết hàm kiểm thì test đỏ ngay.
# ══════════════════════════════════════════════════════════════════════════════

HAM_KIEM_CUNG: dict[str, str] = {
    "H1": "kiem_tra_bai_tho -> ViPham(ma='H1') cho từng dòng lệch 7 tiếng",
    "H2": "kiem_tra_bai_tho duyệt TOÀN BỘ dòng, không có nhánh bỏ qua",
    "H3": "_tang1_hinh_thuc -> ViPham(ma='H3') khi văn bản dưới 4 dòng",
    "H4": "_tang1_hinh_thuc -> ViPham(ma='H4') khi số dòng không chia hết cho 4",
}


def mo_ta_luat(ma: str) -> str:
    """Tra nội dung một điều luật theo mã, dùng khi dựng thông báo cho người dùng."""
    d = MA_LUAT.get(ma)
    return f"{d.ma} ({d.thanh_phan}): {d.noi_dung}" if d else f"{ma}: không có trong bảng luật"
