from typing import Literal, NamedTuple, TypeAlias

BudgetLayer: TypeAlias = Literal["system", "knowledge", "facts", "summary", "recent", "question", "tool"]

# Measured ratio: 3.6 chars per token for Vietnamese + English mix
CHARS_PER_TOKEN = 3.6

# ⚠️ BA TRONG BẢY MỤC CHƯA BAO GIỜ ĐƯỢC CƯỠNG CHẾ — ghi ra 23/09/2026.
#
# `enforce_layer_budget` chỉ được gọi cho `summary`, `facts`, `knowledge` và
# `question` (xem `context.py`). Ba mục `system`, `recent`, `tool` là con số khai
# báo, không ai kiểm. Không ghi ra thì người đọc tưởng cả bảng đều có hiệu lực.
#
# `system` ĐANG VƯỢT TRẦN và đó KHÔNG phải lỗi cần sửa:
#     khai báo   1000 token
#     thực tế    vượt xa    (SYSTEM_PROMPT_V1 nay gồm cả bảng luật và chỉ dẫn
#                             từng loại việc — gộp `instructions.py` 23/09/2026)
#
# ⛔ ĐỪNG BẬT CƯỠNG CHẾ CHO `system`. Nó là HẰNG SỐ, và `enforce_layer_budget` cắt
# bằng `text[:max_chars]` — cắt một chỉ dẫn hệ thống là âm thầm xoá mất phần cuối
# của nó.
#
# Đo thật trước khi gộp (4.643 ký tự, trần 3.600): nhát cắt nuốt trọn phần chỉ
# dẫn cuối chuỗi — trong đó có điều bắt buộc phải nói với người dùng rằng bài thơ
# viết trong khung trò chuyện CHƯA đi qua bộ kiểm luật. Gộp xong chuỗi còn dài
# hơn nữa, nên bật cưỡng chế bây giờ còn cắt sâu hơn.
#
# Không lỗi, không cảnh báo. Chỉ là trợ lý thôi không cảnh báo nữa, trong một sản
# phẩm mà điểm bán chính là thơ đúng luật.
#
# Trần chỉ an toàn với các tầng chứa DỮ LIỆU đổi theo lượt — cắt bớt tài liệu thì
# mất thông tin, còn cắt bớt mệnh lệnh thì đổi cả hành vi.
TOKEN_BUDGET: dict[BudgetLayer, int] = {
    "system": 1000,  # KHAI BÁO, không cưỡng chế — xem chú thích trên
    "knowledge": 4000,
    "facts": 1000,
    "summary": 1000,
    "recent": 3000,  # khai báo, không cưỡng chế
    "question": 1000,
    "tool": 2000,  # khai báo, không cưỡng chế
}


class BudgetCheck(NamedTuple):
    text: str
    tokens: int
    truncated_tokens: int


def enforce_layer_budget(text: str, layer: BudgetLayer) -> BudgetCheck:
    budget = TOKEN_BUDGET.get(layer, 2000)
    estimated_tokens = int(len(text) / CHARS_PER_TOKEN)

    if estimated_tokens <= budget:
        return BudgetCheck(text=text, tokens=estimated_tokens, truncated_tokens=0)

    # Exceeded budget: slice text to strictly fit within token budget
    max_chars = int(budget * CHARS_PER_TOKEN)
    truncated_text = text[:max_chars]
    truncated_tokens = estimated_tokens - budget

    return BudgetCheck(text=truncated_text, tokens=budget, truncated_tokens=truncated_tokens)
