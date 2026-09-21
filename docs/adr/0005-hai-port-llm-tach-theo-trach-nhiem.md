# ADR-0005 — G1b đổi hình dạng: tách port theo trách nhiệm, không hợp nhất

Ngày: 21/09/2026 · Trạng thái: ✅ **ĐÃ CHẤP NHẬN VÀ THI CÔNG** · Thay thế phần "hợp nhất port" của ADR-0002

## Bối cảnh

ADR-0002 và `Plan_Thi_Cong_DeepAgent.md` (G1b) đều nói: repo có hai định nghĩa
"gọi mô hình là gì", và phải **hợp nhất** chúng.

| | `ports/llm_client.py` — `LLMClient` | `ports/llm.py` — `LlmPort` |
|---|---|---|
| Phương thức | `generate` · `stream` · `embed` | `reply` · `cheap` |
| Kiểu lượt | `contracts.chat.Message` (Pydantic) | tagged union `LlmMessage` |
| Lỗi | ngoại lệ | `Result[T, BotError]` |
| Nơi dùng | RAG (`embed`), ingest (`embed`), chat router (`stream`) | đường thơ, vòng ReAct |

Khi thi công phần **gọi tool** (21/09/2026), tôi phải sửa cả hai bên và phát hiện
một điều không thấy được từ trên giấy.

## Điều phát hiện được khi làm

Ba nơi dùng `LLMClient` KHÔNG phải là hội thoại:

- `rag/retriever.py` gọi `embed()` — biến văn bản thành vector. Không có lượt, không
  có tool, không có hội thoại.
- `ingest/{batch,enricher}.py` gọi `embed()` và `generate()` một phát, không trạng thái.
- `routers/chat.py` gọi `stream()` — phát từng mẩu, ngược hẳn với `reply()` vốn trả
  một lượt trọn vẹn kèm `tool_calls`.

Nói cách khác: **hai port này không phải hai cách nói về cùng một việc.** Chúng là
hai việc khác nhau tình cờ cùng đi tới một nhà cung cấp.

Ép chúng vào một `Protocol` sẽ cho ra một giao diện mà mọi hiện thực đều phải khai
những phương thức nó không dùng: một bộ nhúng phải có `reply()`, một bộ hội thoại
phải có `embed()`. Đó là interface segregation bị vi phạm, và cái giá trả bằng
`NotImplementedError` rải khắp adapter.

## Quyết định

**Không hợp nhất. Tách theo TRÁCH NHIỆM**, và đặt lại tên cho đúng việc:

| Port | Trách nhiệm | Ai dùng |
|---|---|---|
| `LlmPort` | hội thoại nhiều lượt + gọi tool + `Result` | đường thơ, vòng ReAct, pipeline |
| `EmbeddingPort` | văn bản → vector | `rag/`, `ingest/` |
| `StreamingPort` | phát từng mẩu | `routers/chat.py` |

`LLMClient` hiện tại bị **tách ba**, không bị xoá. Mỗi adapter provider hiện thực
port nào nó thật sự phục vụ.

## Hệ quả với `adapters/llm/chat_port.py`

Tôi đã gọi file này là *"nợ kỹ thuật có chủ ý, gỡ khi G1b xong"*. **Đánh giá đó
nay sai một nửa và phải đính chính:**

- Phần **lossy** đúng là nợ, và đã trả xong hôm nay: `ToolMessage` từng bị hạ
  xuống vai `user` làm mất `tool_call_id`; `tools` từng bị vứt. Cả hai đã sửa.
- Phần **bắc cầu** thì không phải nợ. Sau khi tách ba port, vẫn cần một chỗ dịch
  giữa tagged union của `LlmPort` và DTO Pydantic của provider. Đó là **việc đúng
  của tầng adapter**, không phải thứ chờ xoá.

Vì vậy `chat_port.py` sẽ **ở lại**, và docstring của nó cần bỏ câu "khi G1b xong
thì xoá file này".

## Vì sao ghi ADR thay vì lặng lẽ đổi plan

Plan trước nói một hướng, việc làm ra lại chỉ ra hướng khác. Sửa plan mà không ghi
lý do thì sáu tháng nữa không ai biết vì sao "hợp nhất port" biến mất — và rất có
thể sẽ có người đề xuất lại đúng nó.

## Đã thi công — 21/09/2026

| Việc | Kết quả |
|---|---|
| Tách `LLMClient` thành ba cổng | `ports/{embedding,streaming,generation}.py` |
| `LLMClient` giữ lại làm cổng gộp | kế thừa cả ba `Protocol`; chỉ `bootstrap/` + `adapters/` được dùng |
| `rag/retriever.py` | `llm_client: LLMClient` → `embedder: EmbeddingPort` |
| `ingest/{batch,enricher}.py` | → `EmbeddingPort` |
| `routers/chat.py` | `default_llm.stream` → `streamer.stream`; `.generate` → `generator.generate` |
| `AppContainer` | thêm ba khung nhìn hẹp `embedder` · `streamer` · `generator` |
| `adapters/llm/chat_port.py` | bỏ câu "gỡ file này khi G1b xong" |

**Cưỡng chế bằng máy** — `tests/architecture/test_port_hep.py`, ba test:

1. `application/` và `entrypoints/` KHÔNG được import `LLMClient` (quét AST)
2. cả ba cổng hẹp đều phải có nơi dùng thật — port chết thì test đỏ
3. dựng được `HybridRetriever` bằng một object CHỈ có `embed()`, không có
   `reply`/`stream`/`generate` — đây chính là khả năng mà việc tách bảo vệ

Không dùng hợp đồng `import-linter` như dự kiến ban đầu: `import-linter` làm việc ở
mức *module*, mà ràng buộc ở đây là mức *tên được import* (`LLMClient` so với
`EmbeddingPort`, cùng nằm trong `application.ports`). Test AST diễn đạt đúng điều
cần cưỡng chế; hợp đồng import thì không.
