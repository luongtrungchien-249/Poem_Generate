"""ĐẶT TIÊU ĐỀ — QĐ-TD-1, chủ dự án chốt 21/09/2026.

════ MỘT LƯỢT GỌI RIÊNG, SAU KHI BÀI ĐÃ QUA CỔNG ════

Plan ban đầu (`docs/Plan_TTS_Tieu_De_Reviewer.md` §4) đề xuất một thẻ `<tieu_de>`
đi kèm bài thơ. Đọc mã thì giả định đó sai:

    thơ được sinh THEO TỪNG KHỔ bốn dòng — mỗi ứng viên là một khổ, không phải
    một bài. Thẻ tiêu đề trong câu trả lời sẽ cho MỘT TIÊU ĐỀ MỖI KHỔ.

Và `sinh_theo_kho._lay_bon_dong` lấy bốn dòng không rỗng đầu tiên, nên một dòng
tiêu đề lọt vào là hỏng cả ứng viên — dù bài thơ bên dưới có thể đúng luật.

Nên tiêu đề đặt SAU, trên bài đã hoàn chỉnh. Đường sinh không bị đụng một dòng nào.

════ TIÊU ĐỀ KHÔNG BAO GIỜ LÀM BÀI TRƯỢT ════

Hai bất biến, và cả hai đều có test ghim:

  1. **Tiêu đề không đi qua luật thơ.** Nó không phải một dòng thơ: không đếm
     tiếng, không khuôn thanh, không vần. Không hàm nào ở đây gọi `rule.py`.

  2. **Hỏng thì trả rỗng, không trả lỗi.** Bài đã qua cổng trước khi hàm này chạy.
     Để một lượt gọi phụ đánh hỏng một bài đã đạt là đổi thứ chắc chắn lấy thứ
     trang trí. Mọi nhánh lỗi — mạng, hết giờ, mô hình trả rác — đều về chuỗi rỗng,
     và người gọi hiểu rỗng là "bài này không có tiêu đề".
"""

from __future__ import annotations

from application.ports.llm import CallContext, LlmPort, UserMessage
from application.prompting.builder import wrap_xml_tag
from application.prompting.instructions import CHI_DAN_DAT_TIEU_DE
from domain.common.result import Ok

# Trần độ dài, đo bằng TIẾNG chứ không bằng ký tự — cùng đơn vị với chỉ dẫn ("hai
# đến năm tiếng"). Cho dư hai tiếng so với chỉ dẫn: vượt xa hơn thế thì thứ trả về
# gần như chắc chắn là một câu, không phải một tiêu đề.
#
# Đây KHÔNG phải một luật thơ. Nó là rào chắn đọc kết quả, và nó CẮT BỎ thay vì
# đánh trượt: tiêu đề quá dài trở thành không có tiêu đề, bài vẫn nguyên.
SO_TIENG_TOI_DA = 7

# Ký tự mô hình hay bọc quanh tiêu đề dù đã bị dặn đừng.
_KY_TU_BAO = "\"'“”‘’`*_#-–—:.!?,;"


def loc_tieu_de(van_ban: str) -> str:
    """Rút tiêu đề từ câu trả lời thô. Rỗng nghĩa là không dùng được.

    THUẦN và TẤT ĐỊNH — tách khỏi lời gọi mạng để test được mà không cần mô hình.
    """
    for dong in van_ban.strip().splitlines():
        sach = dong.strip().strip(_KY_TU_BAO).strip()
        if not sach:
            continue
        # Nhiều tiếng quá thì đây là một câu, không phải tiêu đề. Bỏ, đừng cắt
        # ngắn: cắt giữa chừng cho ra một mẩu vô nghĩa mà trông như có chủ ý.
        if len(sach.split()) > SO_TIENG_TOI_DA:
            return ""
        return sach
    return ""


async def dat_tieu_de(
    van_ban_tho: str,
    *,
    llm: LlmPort,
    ctx: CallContext,
    default_model: str | None = None,
) -> str:
    """Một lượt gọi, trả tiêu đề. Rỗng khi không đặt được — KHÔNG ném lỗi.

    Bài thơ bọc thẻ riêng để mô hình phân biệt "văn bản để đọc" với "lệnh cho
    bạn", đúng cách `dung_luot_yeu_cau` đang làm với ví dụ và kế hoạch.
    """
    if not van_ban_tho.strip():
        return ""

    loi_nhac = f"{CHI_DAN_DAT_TIEU_DE}\n{wrap_xml_tag('bai_tho', van_ban_tho)}"
    try:
        r = await llm.reply(
            messages=(UserMessage(content=loi_nhac),),
            tools=(),
            ctx=ctx,
            model=default_model,
        )
    except Exception:
        # Bài đã qua cổng rồi. Không có lỗi nào ở đây đáng để đánh hỏng nó.
        return ""
    return loc_tieu_de(r.value.text) if isinstance(r, Ok) else ""
