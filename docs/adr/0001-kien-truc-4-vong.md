# ADR-0001 — Kiến trúc 4 vòng, ranh giới do máy cưỡng chế

Ngày: 17/09/2026 · Trạng thái: **đã áp dụng**

## Bối cảnh

Cấu trúc cũ (`packages/core`, `apps/`) trộn domain thuần với HTTP client, YAML loader và
Prometheus trong cùng một gói. Hệ quả đo được:

- `core/llm/fallback.py` import singleton Prometheus, nên không test được lõi nếu thiếu hạ tầng.
- `core/rag/retrieve/hybrid.py` import thẳng `InMemoryVectorRepository`, nên lõi phụ thuộc vào
  một hiện thực lưu trữ cụ thể.
- `apps/worker/*` import container của API, nên worker ghi dữ liệu vào RAM của chính nó.
- Đăng ký tool xảy ra như side effect lúc import, nên thứ tự import quyết định hành vi hệ thống.

## Quyết định

Bốn vòng, phụ thuộc chỉ hướng vào trong:

`entrypoints → bootstrap → adapters → application → domain`

1. `domain` thuần: không I/O, không thư viện ngoài.
2. Ra thế giới ngoài chỉ qua `application/ports/` (`typing.Protocol`).
3. `bootstrap/settings.py` là nơi duy nhất đọc `os.environ`.
4. Mọi hiện thực được ráp tại `bootstrap/container.py`; không còn singleton mức module.
5. Ranh giới kiểm bằng `.importlinter` (CI) và `tests/architecture/` (quét AST, chạy cùng pytest
   nên không cần cài thêm công cụ).

## Hệ quả

- Ngay khi bật, bộ kiểm tra bắt được 5 vi phạm thật. Cả 5 đã sửa bằng cách đảo chiều phụ thuộc:
  Protocol lưu trữ chuyển lên `application/ports/repositories.py`; `trace_span` thành `TracerPort`
  với `NullTracer` mặc định; ba tool có I/O chuyển xuống `adapters/tools/`.
- Test lõi chạy 1,6 giây và không chạm mạng.
- Nợ còn lại: `domain/llm/token.py` vẫn dùng `contracts.chat.Message` (Pydantic). Đã khai báo
  tường minh trong `.importlinter` và sẽ gỡ ở Bước 4.
