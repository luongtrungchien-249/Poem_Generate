"""NODE REVIEWER — QĐ-RV-1, chủ dự án chốt 21/09/2026.

Chấm hai chiều mà `quality.py` khai báo công khai là KHÔNG kiểm được bằng thuật
toán:

    CL6  mach_lac   semantic_coherence — đòi hiểu nội dung
    CL7  hinh_anh   imagery            — đòi hiểu nội dung

════ 🔴 BẤT BIẾN DUY NHẤT: TƯ VẤN, KHÔNG CHẶN ════

Điểm của Reviewer **không bao giờ** được đọc bởi `verify_output.py` hay
`quality.py`. Lý do đã viết sẵn ở `quality.py`: port `OutputVerifier` đòi hiện thực
ĐỒNG BỘ, THUẦN và TẤT ĐỊNH — *"cổng chặn không được phép trượt vì mạng"*, và *"nếu
không tất định, vòng sửa sẽ dao động"*. Một LLM-judge vi phạm cả hai.

Bản prompt cũ (`compare_prompt.py`) chính là hệ thống mắc đúng lỗi đó: nó để mô
hình chấm rồi sửa theo điểm mô hình vừa chấm, không có điểm tựa nào ngoài chính nó.

Có test ghim chiều import: `test_reviewer_khong_noi_vao_cong_chan`.

════ CHỈ NHẬP MỎ NEO, KHÔNG NHẬP BỘ TIÊU CHÍ ════

Thang E/L/M/I của bản cũ có một chiều **M — thi luật**, chấm bằng LLM theo luật lục
bát. Mang nguyên sang đây hỏng hai lần: sai thể, và tệ hơn, dựng một THẨM QUYỀN THỨ
HAI về luật bên cạnh `rule.py` — đúng thứ cả tầng 1 lẫn tầng 2 đang cấm mô hình tự
làm. Thi luật đã có chủ, và chủ đó không phải LLM.

Thứ đáng nhập là **mỏ neo hiệu chuẩn**: *"điểm 5 là trung bình, 8 mới là tốt, 10 là
kiệt tác"*. Neo từng mốc chống điểm phồng tốt hơn hẳn một dòng "hãy chấm khách
quan" — đó là hiệu chuẩn, không phải mệnh lệnh.

TRỌNG SỐ THÌ KHÔNG NHẬP. Bốn con số 0,25/0,25/0,35/0,15 của bản cũ không có nguồn
gốc nào; chép lại là vi phạm N1. Ở đây hai chiều đứng RIÊNG, không gộp thành một
điểm tổng — gộp thì phải có trọng số, và trọng số thì phải có người chốt.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from application.ports.llm import CallContext, LlmPort, UserMessage
from application.prompting.builder import wrap_xml_tag
from domain.common.result import Ok

# Mỏ neo hiệu chuẩn — phần duy nhất nhập từ `compare_prompt.py`.
#
# Hai chiều CỐ Ý KHÔNG có trọng số và KHÔNG gộp thành điểm tổng: gộp đòi trọng số,
# trọng số đòi một người chốt, và chưa ai chốt. Hai con số rời nói được nhiều hơn
# một con số trung bình che mất cả hai.
CHI_DAN_REVIEWER: str = """Bạn đọc bài thơ dưới đây và chấm HAI chiều.

Thang 1–10, hiệu chuẩn như sau — đây là mốc, không phải gợi ý:
  10  kiệt tác        8  tốt        5  trung bình        1  rất kém
Không nể nang, không hào phóng. Phần lớn bài thơ nằm quanh mốc 5.

MẠCH LẠC — các dòng có làm nên một bài, hay là bốn câu rời đặt cạnh nhau?
HÌNH ẢNH — bài có hình ảnh cụ thể nhìn thấy được, hay chỉ có chữ khái quát?

KHÔNG chấm thi luật. Số tiếng, thanh điệu, vần đã có bộ kiểm riêng lo, và nhận xét
của bạn về chúng sẽ bị bỏ qua.

Trả lời đúng định dạng này, không thêm gì:
<mach_lac>số</mach_lac>
<hinh_anh>số</hinh_anh>
<nhan_xet>một câu, chỉ ra chỗ cụ thể trong bài</nhan_xet>
"""

_SO = r"([0-9]+(?:[.,][0-9]+)?)"


@dataclass(frozen=True, slots=True)
class NhanXetReviewer:
    """Ý kiến tư vấn. KHÔNG có trường nào nói bài đạt hay trượt — cố ý.

    `co_y_kien=False` nghĩa là lượt gọi không cho kết quả dùng được (mạng hỏng, mô
    hình trả rác). Khi đó hai điểm là None và người đọc biết là KHÔNG CÓ ý kiến,
    khác hẳn với "có ý kiến và điểm thấp".
    """

    co_y_kien: bool
    mach_lac: float | None = None
    hinh_anh: float | None = None
    nhan_xet: str = ""


def _diem(the: str, van_ban: str) -> float | None:
    m = re.search(rf"<{the}>\s*{_SO}\s*</{the}>", van_ban, re.IGNORECASE)
    if not m:
        return None
    try:
        gt = float(m.group(1).replace(",", "."))
    except ValueError:
        return None
    # Ngoài thang thì coi như không đọc được, KHÔNG kẹp về biên: kẹp là bịa ra một
    # con số mô hình không nói, rồi trình bày nó như thể nó có nói.
    return gt if 1.0 <= gt <= 10.0 else None


def doc_nhan_xet(van_ban: str) -> NhanXetReviewer:
    """Rút ý kiến từ câu trả lời thô. THUẦN — test được mà không cần mô hình."""
    ml, ha = _diem("mach_lac", van_ban), _diem("hinh_anh", van_ban)
    if ml is None and ha is None:
        return NhanXetReviewer(co_y_kien=False)
    m = re.search(r"<nhan_xet>(.*?)</nhan_xet>", van_ban, re.IGNORECASE | re.DOTALL)
    return NhanXetReviewer(
        co_y_kien=True,
        mach_lac=ml,
        hinh_anh=ha,
        nhan_xet=m.group(1).strip() if m else "",
    )


async def xin_nhan_xet(
    van_ban_tho: str,
    *,
    llm: LlmPort,
    ctx: CallContext,
    default_model: str | None = None,
) -> NhanXetReviewer:
    """Một lượt gọi, trả ý kiến tư vấn. Hỏng thì `co_y_kien=False`, KHÔNG ném lỗi.

    Bài thơ bọc thẻ riêng: nó là DỮ LIỆU để đọc, không phải lệnh. Bài do mô hình
    viết ra nên càng phải bọc — một dòng thơ trông như chỉ dẫn sẽ bị khử ở đó.
    """
    if not van_ban_tho.strip():
        return NhanXetReviewer(co_y_kien=False)

    loi_nhac = f"{CHI_DAN_REVIEWER}\n{wrap_xml_tag('bai_tho', van_ban_tho)}"
    try:
        r = await llm.reply(
            messages=(UserMessage(content=loi_nhac),),
            tools=(),
            ctx=ctx,
            model=default_model,
        )
    except Exception:
        return NhanXetReviewer(co_y_kien=False)
    if not isinstance(r, Ok):
        return NhanXetReviewer(co_y_kien=False)
    return doc_nhan_xet(r.value.text)
