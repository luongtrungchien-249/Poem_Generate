"""HƯỚNG DẪN GIỌNG ĐỌC — chủ dự án chốt 22/09/2026.

Nhập từ `compare_prompt.py` (`TTS_STYLE_SYSTEM_PROMPT` + `TTS_STYLE_USER_TEMPLATE`),
là phần duy nhất của khối TTS bản cũ còn dùng được ở hệ thống này.

════ ĐỪNG NHẦM VỚI QĐ-TTS-1 ════

QĐ-TTS-1 đóng phần PHIÊN ÂM để đếm tiếng ("Vinfast" -> "Vin Phát"), và đóng vì nó
đụng thẳng vào luật: phiên âm làm đổi số tiếng, tức đổi đúng thứ H1 đo. Quyết định
ấy chốt "để nguyên từ ngoại lai, đếm tiếng theo luật".

File này KHÔNG đụng luật một chữ nào. Nó nói cách ĐỌC một bài đã viết xong và đã
qua cổng — hai chuyện khác nhau, và QĐ-TTS-1 không phủ chuyện thứ hai.

════ RẬP KHUÔN `tieu_de.py` ════

Cùng một hình dạng bài toán, nên cùng một khuôn, và hai bất biến cũng y hệt:

  1. **Không đi qua luật thơ.** Hướng dẫn đọc không phải một dòng thơ: không đếm
     tiếng, không khuôn thanh, không vần. Không hàm nào ở đây gọi `rule.py`.

  2. **Hỏng thì trả rỗng, không trả lỗi.** Bài đã qua cổng trước khi hàm này chạy.
     Để một lượt gọi phụ đánh hỏng một bài đã đạt là đổi thứ chắc chắn lấy thứ
     trang trí. Mọi nhánh lỗi — mạng, hết giờ, mô hình trả rác — đều về chuỗi rỗng,
     và người gọi hiểu rỗng là "bài này không có hướng dẫn đọc".
"""

from __future__ import annotations

from application.ports.llm import CallContext, LlmPort, UserMessage
from application.prompting.builder import wrap_xml_tag
from application.prompting.system import CHI_DAN_HUONG_DAN_DOC
from domain.common.result import Ok

# Trần độ dài, đo bằng TIẾNG — cùng đơn vị với chỉ dẫn ("hai đến bốn câu"). Bốn
# câu tiếng Việt hiếm khi vượt 120 tiếng; vượt xa thế thì thứ trả về gần như chắc
# chắn là một bài phân tích, không phải một hướng dẫn đọc.
#
# Đây KHÔNG phải một luật thơ. Nó là rào chắn đọc kết quả, và nó CẮT BỎ thay vì
# đánh trượt: hướng dẫn quá dài trở thành không có hướng dẫn, bài vẫn nguyên.
SO_TIENG_TOI_DA = 120

# Ký tự mô hình hay bọc quanh đoạn văn dù đã bị dặn đừng.
_KY_TU_BAO = "\"'“”‘’`*_#"


def loc_huong_dan(van_ban: str) -> str:
    """Rút hướng dẫn đọc từ câu trả lời thô. Rỗng nghĩa là không dùng được.

    THUẦN và TẤT ĐỊNH — tách khỏi lời gọi mạng để test được mà không cần mô hình.

    Khác `tieu_de.loc_tieu_de` ở một chỗ: tiêu đề là MỘT dòng nên lấy dòng đầu,
    còn hướng dẫn đọc là một đoạn văn xuôi nên phải gộp các dòng lại. Lấy dòng đầu
    ở đây sẽ cắt cụt đúng phần nội dung.
    """
    dong = [d.strip().strip(_KY_TU_BAO).strip() for d in van_ban.strip().splitlines()]
    doan = " ".join(d for d in dong if d)
    if not doan:
        return ""
    # Dài quá thì bỏ, ĐỪNG cắt ngắn: cắt giữa chừng cho ra một mẩu cụt mà trông
    # như có chủ ý — cùng lý do `tieu_de.py` bỏ thay vì cắt.
    return "" if len(doan.split()) > SO_TIENG_TOI_DA else doan


async def huong_dan_doc(
    van_ban_tho: str,
    *,
    llm: LlmPort,
    ctx: CallContext,
    default_model: str | None = None,
) -> str:
    """Một lượt gọi, trả hướng dẫn đọc. Rỗng khi không lấy được — KHÔNG ném lỗi.

    Bài thơ bọc thẻ riêng để mô hình phân biệt "văn bản để đọc" với "lệnh cho
    bạn" — và bài do mô hình viết ra nên càng phải bọc.
    """
    if not van_ban_tho.strip():
        return ""

    loi_nhac = f"{CHI_DAN_HUONG_DAN_DOC}\n{wrap_xml_tag('bai_tho', van_ban_tho)}"
    try:
        r = await llm.reply(
            messages=(UserMessage(content=loi_nhac),),
            tools=(),
            ctx=ctx,
            model=default_model,
        )
    except Exception:
        # Bài đã qua cổng rồi. Không lỗi nào ở đây đáng để đánh hỏng nó.
        return ""
    return loc_huong_dan(r.value.text) if isinstance(r, Ok) else ""
