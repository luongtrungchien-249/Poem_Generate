"""Dựng prompt — bốn tầng, trần token, và khử thẻ ranh giới.

════════════════════════════════════════════════════════════════════════════
BỐN TẦNG, XẾP THEO MỨC ĐỘ THAY ĐỔI
════════════════════════════════════════════════════════════════════════════

Thứ tự không phải để cho gọn mắt — nó quyết định tiền:

    tầng 1  nền          `system.py`        hằng số, không bao giờ đổi
    tầng 2  loại việc    `instructions.py`  hằng số theo loại việc
    tầng 3  bối cảnh     `context.py`       đổi theo lượt: tài liệu, tóm tắt
    tầng 4  lượt hiện tại                   câu hỏi của người dùng

Prefix cache chỉ ăn phần ĐẦU giống nhau giữa các yêu cầu. Đặt một thứ đổi theo
lượt lên trước một thứ bất biến là làm hỏng cache của mọi yêu cầu phía sau nó —
mỗi lượt lại trả tiền cho cùng một khối chữ. Nên tầng 1 và 2 vào vai `system`,
tầng 3 và 4 vào vai `user`.

Tầng 3 vào vai `user` còn vì một lý do nặng hơn tiền: tài liệu và văn bản dán vào
là DỮ LIỆU do người ngoài kiểm soát. Vai `system` là vai ra lệnh; đặt dữ liệu vào
đó là trao quyền ra lệnh cho bất kỳ ai ghi được vào kho tài liệu.

════════════════════════════════════════════════════════════════════════════
HAI ĐƯỜNG SINH, HAI BỘ PROMPT — CỐ Ý KHÔNG GỘP
════════════════════════════════════════════════════════════════════════════

    /v1/chat  →  SYSTEM_PROMPT_V1  +  mẫu `rag_answer`  (gói này)
    /v1/poem  →  CHI_DAN_SINH_THO                       (`application/poetry/`)

Đường thơ có chỉ dẫn riêng vì phần luật của nó SINH RA từ bảng `rule.LUAT`, nên
prompt không lệch được khỏi bộ chấm bài. Gói này KHÔNG chép lại một chữ nào của
luật thơ — chép là tạo nguồn thứ hai, và đến ngày bảng luật đổi thì mô hình được
dạy hai luật khác nhau tuỳ đường nó đi qua. Có test chặn điều đó.

════════════════════════════════════════════════════════════════════════════
BA LỖ HỔNG ĐÃ VÁ 21/09/2026 — ĐỀU CÙNG MỘT LOẠI
════════════════════════════════════════════════════════════════════════════

Thứ được viết ra trông đầy đủ, nhưng đường đi tới mô hình đứt ở giữa chừng. Không
phép kiểm nào về NỘI DUNG prompt bắt được chúng:

    1. `SYSTEM_PROMPT_V1` không đường nào gọi tới. Lượt chat tắt RAG chạy mà
       không có chỉ dẫn hệ thống nào.

    2. Tài liệu RAG không bao giờ tới mô hình. `template.render()` trả cặp
       (system, user); khối `[CONTEXT]` nằm ở phần user, mà mã viết
       `rendered_sys, _ =`. Mô hình nhận mệnh lệnh "chỉ trả lời theo [CONTEXT]"
       và không hề nhận [CONTEXT] — nên trả lời "tài liệu không đề cập" với mọi
       câu hỏi. Response thì VẪN kèm `citations`.

    3. Bộ khử thẻ bảo vệ 1 trong 9 thẻ ranh giới. Tám vùng dữ liệu thoát ra
       được, kể cả vùng chứa văn bản người dùng gõ vào.

Nên các test của gói này kiểm ĐƯỜNG ĐI, không kiểm câu chữ —
`tests/contract/test_tang_prompt_day_du.py`.
"""

from .budget import CHARS_PER_TOKEN, TOKEN_BUDGET, BudgetLayer, enforce_layer_budget
from .builder import THE_RANH_GIOI, sanitize_tag_lookalikes, wrap_xml_tag
from .context import ContextEnvelope, assemble_context_envelope
from .system import SYSTEM_PROMPT_V1

__all__ = [
    "SYSTEM_PROMPT_V1",
    "THE_RANH_GIOI",
    "sanitize_tag_lookalikes",
    "wrap_xml_tag",
    "BudgetLayer",
    "enforce_layer_budget",
    "CHARS_PER_TOKEN",
    "TOKEN_BUDGET",
    "ContextEnvelope",
    "assemble_context_envelope",
]
