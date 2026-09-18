# ADR-0002 — Chỉ giữ một lõi agent

Ngày: 17/09/2026 · Trạng thái: **đề xuất** (chưa thực hiện)

## Bối cảnh

Repo đang có song song hai kiến trúc agent, và API không dùng cái nào:

| | `application/agent/graph.py` | `application/pipeline/handle_message.py` |
|---|---|---|
| Kiểu dữ liệu | Pydantic, khả biến | `@dataclass(frozen=True, slots=True)` |
| Xử lý lỗi | ngoại lệ | `Result[T, BotError]` |
| Phụ thuộc ngoài | trực tiếp | qua port |
| Nơi được dùng | chỉ trong test | chỉ trong test |

## Quyết định đề xuất

Giữ `pipeline/handle_message.py` làm đường đi chính thức, gỡ `agent/graph.py`, `agent/state.py`
và `agent/nodes/`. Phần hữu ích của nhánh graph là vòng lặp ReAct, và bản tương đương đã có ở
`application/pipeline/stages/generate.py`.

## Lý do

Lõi bất biến cộng với `Result` buộc mọi nhánh lỗi phải được xử lý ngay tại chỗ gọi. `AgentGraph`
lặp `while not state.is_finished` trên trạng thái khả biến, không có trần ngân sách, và không
phân biệt lỗi tạm thời với lỗi vĩnh viễn.

## Việc cần làm khi thực hiện

- Xoá `agent/{graph,state,nodes}` và mục `agent_graph` trong `AppContainer`.
- Chuyển `tests/unit/application/test_agent_graph.py` sang kiểm thử `generate_react_loop`.
- Giữ `agent/tools/registry.py` (thuần) và `adapters/tools/` (có I/O).
