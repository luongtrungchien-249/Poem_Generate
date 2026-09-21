"""Sổ đăng ký tool của agent.

LỊCH SỬ — đọc trước khi định thêm lại một lõi agent thứ hai vào đây.

Gói này từng chứa `graph.py`, `state.py` và `nodes/` — một lõi agent thứ hai chạy
song song với `application/pipeline/`. ADR-0002 đã cho gỡ ngày 21/09/2026. Lý do,
chép lại để không ai khôi phục nhầm:

    | | agent/graph (đã gỡ) | pipeline/handle_message (giữ) |
    |---|---|---|
    | Kiểu dữ liệu | Pydantic, khả biến | frozen dataclass |
    | Xử lý lỗi | ngoại lệ | Result[T, BotError] |
    | Phụ thuộc ngoài | trực tiếp | qua port |

`AgentGraph` lặp `while not state.is_finished` trên trạng thái khả biến, không có
trần ngân sách, và không phân biệt lỗi tạm thời với lỗi vĩnh viễn. Bản tương đương
có đủ chặn cứng nằm ở `application/pipeline/stages/generate.py`.

§36 của `docs/DeepAgent_That_Ngon_Tu_Do_Architecture.md` đề xuất dựng lại một
`agent/graph/` mới. QĐ-D4 đã bác: lấy ý tưởng tách node, bỏ cây thư mục. Các node
của tài liệu đích nằm ở `application/poetry/`, xem §4 của `Plan_Thi_Cong_DeepAgent.md`.
"""

from .tools import ToolRegistry, tool_registry

__all__ = [
    "ToolRegistry",
    "tool_registry",
]
