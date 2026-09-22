"""Tầng 3 — gom bối cảnh vào lượt hỏi.

════ MỘT CHỖ DỰNG KHỐI, HAI ĐƯỜNG DÙNG ════

`dung_khoi_boi_canh` là nơi DUY NHẤT quyết định bối cảnh được gói ra sao: khối nào
trước khối nào, bọc thẻ gì, cắt theo trần token nào. Hai đường gọi nó:

    /v1/chat                 → dựng nội dung cho lượt `user` cuối
    assemble_context_envelope → dựng lượt `user` cuối của chuỗi hội thoại

Trước 21/09/2026 `/v1/chat` tự dựng lấy, và thiếu đúng phần quan trọng nhất: TRẦN
TOKEN. Một tài liệu dài bất kỳ đi thẳng vào prompt, đẩy lượt hỏi ra ngoài cửa sổ
ngữ cảnh hoặc làm lời gọi bị từ chối — lỗi chỉ xuất hiện với tài liệu lớn, tức là
đúng lúc khó tái hiện nhất.

════ VÌ SAO KHÔNG GỘP HẲN HAI ĐƯỜNG VỀ `assemble_context_envelope` ════

`LlmMessage` chỉ có ba vai: user, assistant, tool. KHÔNG có vai system. Đường chat
cần vai đó — nó là ranh giới giữa "lệnh của hệ thống" và "dữ liệu người ngoài
kiểm soát", và đánh mất ranh giới ấy là trao quyền ra lệnh cho bất kỳ ai ghi được
vào kho tài liệu.

Nên phần dùng chung là phần dựng KHỐI, không phải phần dựng CHUỖI TIN NHẮN.
"""

from dataclasses import dataclass

from application.ports.llm import AssistantMessage, LlmMessage, UserMessage
from domain.conversation.message import StoredMessage

from .budget import enforce_layer_budget
from .builder import wrap_xml_tag


@dataclass(frozen=True, slots=True)
class KhoiBoiCanh:
    """Nội dung lượt hỏi cuối, đã gói và đã cắt theo trần."""

    noi_dung: str
    tokens: int
    co_tai_lieu: bool


def dung_khoi_boi_canh(
    question: str,
    *,
    retrieved_knowledge: str | None = None,
    user_facts: str | None = None,
    summary: str | None = None,
) -> KhoiBoiCanh:
    """Gói bối cảnh + câu hỏi thành nội dung của MỘT lượt `user`.

    THỨ TỰ KHỐI: tóm tắt → thông tin người dùng → tài liệu → câu hỏi.
    Câu hỏi đặt CUỐI cùng vì mô hình bám phần cuối prompt chặt hơn phần giữa; đặt
    nó trước một khối tài liệu dài là để nó bị chìm.

    Mỗi khối đi qua trần token riêng: một khối phình to không được phép ăn hết chỗ
    của các khối khác, và nhất là không được đẩy câu hỏi ra ngoài cửa sổ.
    """
    khoi: list[str] = []
    tokens = 0
    co_tai_lieu = False

    if summary:
        b = enforce_layer_budget(summary, "summary")
        khoi.append(wrap_xml_tag("tom_tat", b.text))
        tokens += b.tokens

    if user_facts:
        b = enforce_layer_budget(user_facts, "facts")
        khoi.append(wrap_xml_tag("thong_tin_nguoi_dung", b.text))
        tokens += b.tokens

    if retrieved_knowledge:
        b = enforce_layer_budget(retrieved_knowledge, "knowledge")
        khoi.append(wrap_xml_tag("tai_lieu", b.text))
        tokens += b.tokens
        co_tai_lieu = True

    q = enforce_layer_budget(question, "question")
    tokens += q.tokens

    noi_dung = "\n\n".join([*khoi, f"[Câu hỏi]\n{q.text}"]) if khoi else q.text
    return KhoiBoiCanh(noi_dung=noi_dung, tokens=tokens, co_tai_lieu=co_tai_lieu)


@dataclass(frozen=True, slots=True)
class ContextEnvelope:
    messages: tuple[LlmMessage, ...]
    tokens_used: int
    has_knowledge: bool


def assemble_context_envelope(
    question: str,
    recent_history: tuple[StoredMessage, ...],
    retrieved_knowledge: str | None = None,
    user_facts: str | None = None,
    summary: str | None = None,
) -> ContextEnvelope:
    """Dựng chuỗi hội thoại xen kẽ thật.

    Nguyên tắc: KHÔNG bao giờ ép lịch sử hội thoại thành một khối duy nhất hay một
    lượt assistant giả. Mô hình đọc nhịp hỏi–đáp để biết ai đã nói gì; gộp lại là
    xoá thông tin đó đi.
    """
    turn_list: list[LlmMessage] = []

    # Bỏ bản trùng với chính câu đang hỏi: nó sắp được thêm ở cuối.
    for msg in recent_history:
        if msg.text.strip() == question.strip():
            continue
        if msg.role == "user":
            turn_list.append(UserMessage(content=msg.text))
        elif msg.role == "assistant":
            turn_list.append(AssistantMessage(content=msg.text))

    khoi = dung_khoi_boi_canh(
        question,
        retrieved_knowledge=retrieved_knowledge,
        user_facts=user_facts,
        summary=summary,
    )
    turn_list.append(UserMessage(content=khoi.noi_dung))

    # 🔴 `tokens_used` TRƯỚC 21/09/2026 LUÔN BẰNG 0: biến đếm được khởi tạo rồi
    # không bao giờ cộng vào. Trường này có mặt trong kiểu trả về, có tên đúng, và
    # không mang thông tin nào — ai đọc nó để quyết định đều đang đọc một số bịa.
    return ContextEnvelope(
        messages=tuple(turn_list),
        tokens_used=khoi.tokens,
        has_knowledge=khoi.co_tai_lieu,
    )
