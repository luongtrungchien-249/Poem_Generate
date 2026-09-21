"""Chỉ dẫn sinh thơ — §25 tài liệu đích.

HAI TẦNG, ĐÚNG KỶ LUẬT ĐÃ CÓ (`plan-tang-agents.md` §5.2):

    tầng 1+2  CHỈ_DAN_SINH_THO   hằng số, KHÔNG nội suy trạng thái động
    tầng 3    dung_luot_yeu_cau  dữ liệu của lượt này, bọc thẻ XML

Tầng 1+2 phải là hằng số để prefix cache còn hiệu lực: nhét tên người dùng hay
dấu thời gian vào đó là phá cache của mọi yêu cầu.

════ VÌ SAO DỰNG TỪ BẢNG `LUAT` CHỨ KHÔNG GÕ TAY ════

Phần luật cứng trong chỉ dẫn được SINH RA từ `rule.LUAT` lúc import, không chép
tay. Chép tay thì đến một ngày bảng luật đổi mà prompt không đổi, và mô hình được
dạy một luật khác với luật dùng để chấm nó — kiểu lệch âm thầm và rất khó thấy.

Đây vẫn là hằng số: `LUAT` là dữ liệu đóng băng, nên chuỗi sinh ra tất định và
giống nhau ở mọi tiến trình.
"""

from __future__ import annotations

from application.poetry.plan import KHUON_HOP_LE
from application.poetry.requirement import PoetryRequirement
from application.prompting.builder import wrap_xml_tag
from application.prompting.instructions import CACH_LAM_VIEC, CHI_DAN_CHAT_LUONG

# `rule.py` ĐÓNG BĂNG: chỉ đọc bảng luật.
from application.rule import LUAT, NHIP_TAI_LIEU


def _bang_luat_cung() -> str:
    return "\n".join(
        f"  {d.ma}  {d.noi_dung}." for d in LUAT if d.loai == "cung"
    )


CHI_DAN_SINH_THO: str = f"""Bạn là người làm thơ thất ngôn tự do tiếng Việt.

RÀNG BUỘC CỨNG — vi phạm thì bài KHÔNG thuộc thể, không có ngoại lệ nào:
{_bang_luat_cung()}

Cách đếm tiếng: dấu câu KHÔNG tính là tiếng; gạch nối thì tách tiếp
("ra-đi-ô" = 3 tiếng); chữ số phải quy về cách đọc rồi mới đếm
("năm 1975" = năm + một nghìn chín trăm bảy mươi lăm = 8 tiếng).

THANH LUẬT — ĐÂY LÀ CHỖ HỎNG NHIỀU NHẤT, đọc kỹ phần này.

Chỉ xét tiếng thứ 2, 4, 6 của mỗi dòng. Mỗi dòng phải khớp ĐÚNG một trong hai:
  khuôn bằng   tiếng 2 = B, tiếng 4 = T, tiếng 6 = B
  khuôn trắc   tiếng 2 = T, tiếng 4 = B, tiếng 6 = T

Phân lớp thanh theo DẤU trên tiếng — tra bảng này, đừng nghe theo cảm giác:
  B (bằng)  không dấu  hoặc  dấu huyền        ma · mà
  T (trắc)  dấu sắc · dấu hỏi · dấu ngã · dấu nặng   má · mả · mã · mạ

Tiếng 1, 3, 5, 7 muốn thanh gì cũng được — luật không đụng tới chúng.

CÁCH VIẾT ĐỂ KHÔNG PHÁ KHUÔN (làm theo đúng thứ tự này):
  1. Chọn khuôn cho dòng: bằng (B T B) hay trắc (T B T).
  2. Chọn TRƯỚC ba tiếng ở vị trí 2, 4, 6 sao cho dấu của chúng khớp khuôn.
  3. Sau đó mới lấp bốn tiếng còn lại (1, 3, 5, 7) cho thành câu có nghĩa.
  4. Đọc lại dòng vừa viết, đếm tới tiếng 2, 4, 6, tra bảng dấu ở trên, đối
     chiếu với khuôn đã chọn. Lệch một chỗ thì viết lại dòng đó.

Viết câu trước rồi mới sửa thanh là cách chắc chắn hỏng: đổi một tiếng cho đúng
thanh thường làm gãy nghĩa, rồi sửa nghĩa lại làm lệch thanh.

Hai dòng khác nhau được dùng hai khuôn khác nhau — không bắt buộc cả bài một khuôn.

VẦN: trong mỗi cụm bốn dòng liên tiếp phải có ít nhất một cặp tiếng cuối hiệp vần.
Sơ đồ nào cũng được — aabb, abab, abba, aaxa, aaaa… — miễn là có vần chân.

NHỊP: mỗi dòng ngắt theo một trong bảy kiểu {", ".join(sorted(NHIP_TAI_LIEU))},
và cả bài nên cùng một nhịp chủ đạo.

{CHI_DAN_CHAT_LUONG}
{CACH_LAM_VIEC}"""


# 🔴 SỬA 21/09/2026 — BẢN TRƯỚC LÀ MỘT LỜI HỨA SUÔNG.
#
# Bản trước viết `KHUON_TRONG_CHI_DAN = KHUON_HOP_LE` kèm chú thích "để test đối
# chiếu prompt với plan.KHUON_HOP_LE". Hai chuyện sai cùng lúc:
#
#   1. Test đó KHÔNG TỒN TẠI. `grep` toàn cây chỉ ra đúng một chỗ nhắc tên hằng
#      số này: chính dòng khai báo nó. Đúng ca `instructions.py` đặt luật để cấm —
#      hằng số không ai đọc chỉ làm bản kiểm kê trông đầy đủ.
#   2. Kể cả có test, nó vẫn vô dụng: gán bí danh rồi so bí danh với bản gốc là so
#      một giá trị với CHÍNH NÓ. Luôn xanh, không bao giờ bắt được sự lệch giữa
#      bảng khuôn và chữ trong prompt — đúng thứ nó tự nhận là để bắt.
#
# Nay nó ĐỌC THẬT chuỗi prompt. Thêm một khuôn thứ ba vào `KHUON_HOP_LE` mà quên
# sửa prompt thì tập rút ra thiếu phần tử, và test đối chiếu đỏ.
# Mã khuôn viết KHÔNG DẤU (`bang`, `trac`) vì nó là khoá dữ liệu; chỉ dẫn gửi cho
# mô hình viết CÓ DẤU ("khuôn bằng") vì nó là tiếng Việt cho người và cho mô hình
# đọc. Nhịp cầu giữa hai cách viết phải khai báo ra ở đây — phép ghim đầu tiên viết
# ngày 21/09/2026 quên mất chuyện này và đỏ ngay lần chạy đầu, đúng như mong muốn:
# một phép ghim thật thì phải bắt được cả sự lệch của chính nó.
#
# Thêm khuôn thứ ba vào `KHUON_HOP_LE` mà quên khai ở đây, hoặc khai rồi mà quên
# viết vào prompt — cả hai đều làm tập rút ra thiếu phần tử và test đối chiếu đỏ.
_CHU_CUA_KHUON: dict[str, str] = {"bang": "bằng", "trac": "trắc"}


def _khuon_duoc_nhac_trong_chi_dan() -> frozenset[str]:
    """Rút những khuôn THẬT SỰ có mặt trong chỉ dẫn gửi cho mô hình."""
    return frozenset(
        ma
        for ma in KHUON_HOP_LE
        if (chu := _CHU_CUA_KHUON.get(ma)) and f"khuôn {chu}" in CHI_DAN_SINH_THO
    )


KHUON_TRONG_CHI_DAN: frozenset[str] = _khuon_duoc_nhac_trong_chi_dan()


def dung_luot_yeu_cau(
    req: PoetryRequirement, khoi_vi_du: str = "", khoi_ke_hoach: str = ""
) -> str:
    """Tầng 3 — dữ liệu của riêng lượt này, bọc thẻ để mô hình phân biệt nguồn.

    Chỉ đưa vào những trường CÓ giá trị. Nhồi "chưa rõ" vào prompt là dạy mô hình
    rằng thiếu thông tin vẫn cứ viết — trong khi cổng B1 đã chặn đúng điều đó.
    """
    dong: list[str] = []
    if req.chu_de.co_gia_tri:
        dong.append(f"Chủ đề: {req.chu_de.gia_tri}")
    if req.so_dong_int:
        n = req.so_dong_int
        dong.append(f"Số dòng: {n} (= 4 × {n // 4}, bắt buộc đúng con số này)")
    if req.cam_xuc.co_gia_tri:
        dong.append(f"Cảm xúc: {req.cam_xuc.gia_tri}")
    if req.phong_cach.co_gia_tri:
        dong.append(f"Phong cách: {req.phong_cach.gia_tri}")
    if req.rang_buoc_van.co_gia_tri:
        dong.append(f"Vần: {req.rang_buoc_van.gia_tri}")
    if req.rang_buoc_thanh.co_gia_tri:
        dong.append(f"Thanh: {req.rang_buoc_thanh.gia_tri}")

    phan = [CHI_DAN_SINH_THO]
    if khoi_vi_du:
        # Ví dụ bọc thẻ RIÊNG để mô hình phân biệt "bài của người khác, để nhìn
        # khuôn" với "yêu cầu dành cho bài của bạn". Trộn chung một khối là cách
        # nhanh nhất khiến mô hình chép lại ví dụ thay vì học khuôn từ nó.
        phan.append(wrap_xml_tag("vi_du_dung_luat", khoi_vi_du))
    if khoi_ke_hoach:
        # Kế hoạch là RÀNG BUỘC của bài này, khác ví dụ (bài của người khác) và
        # khác yêu cầu (lời người dùng). Ba nguồn, ba thẻ — trộn lại thì mô hình
        # không biết cái nào được phép đi chệch, cái nào không.
        phan.append(wrap_xml_tag("ke_hoach_bat_buoc", khoi_ke_hoach))
    phan.append(wrap_xml_tag("yeu_cau_bai_tho", "\n".join(dong)))
    phan.append("Viết bài thơ. Chỉ bài thơ.")
    return "\n".join(phan)
