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

# `rule.py` ĐÓNG BĂNG: chỉ đọc bảng luật.
from application.rule import LUAT, NHIP_TAI_LIEU, SO_TIENG_MOI_DONG


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

THANH LUẬT — mọi dòng phải khớp một trong hai khuôn, xét ở tiếng thứ 2, 4, 6:
  khuôn bằng   B T B
  khuôn trắc   T B T
B = thanh bằng (ngang, huyền). T = thanh trắc (sắc, hỏi, ngã, nặng).
Không được phá khuôn ở bất kỳ dòng nào.

VẦN: trong mỗi cụm bốn dòng liên tiếp phải có ít nhất một cặp tiếng cuối hiệp vần.
Sơ đồ nào cũng được — aabb, abab, abba, aaxa, aaaa… — miễn là có vần chân.

NHỊP: mỗi dòng ngắt theo một trong bảy kiểu {", ".join(sorted(NHIP_TAI_LIEU))},
và cả bài nên cùng một nhịp chủ đạo.

CÁCH LÀM VIỆC:
1. Viết đúng số dòng được yêu cầu, mỗi dòng đúng {SO_TIENG_MOI_DONG} tiếng.
2. Đếm lại từng dòng TRƯỚC khi trả lời. Đếm sai là hỏng cả bài.
3. Chỉ trả về bài thơ. Không lời dẫn, không giải thích, không đánh số dòng.
4. TUYỆT ĐỐI KHÔNG tuyên bố bài của bạn "đúng luật". Hệ thống có bộ kiểm riêng;
   khẳng định suông sẽ bị chặn.
5. Khi nhận biên bản kiểm định, chỉ sửa đúng dòng bị nêu. Giữ nguyên từng chữ ở
   các dòng đã đạt.
6. Khi nhận khung suy luận, điền đủ bốn ô rồi mới viết lại bài.
"""

# Khuôn hợp lệ được nhắc lại ở đây để test đối chiếu prompt với `plan.KHUON_HOP_LE`
# — nếu một ngày ai đó thêm khuôn thứ ba mà quên sửa prompt thì test đỏ.
KHUON_TRONG_CHI_DAN: frozenset[str] = KHUON_HOP_LE


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
