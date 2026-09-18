# ADR-0003 — Lộ trình adapter lưu trữ thật

Ngày: 17/09/2026 · Trạng thái: **đề xuất**

## Bối cảnh

Toàn bộ dữ liệu hiện nằm trong RAM (`adapters/persistence/memory/`), trong khi Terraform đã dựng
RDS và ElastiCache, `.env` khai báo `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL`. Khởi động lại API
là mất sạch hội thoại; chạy nhiều uvicorn worker thì mỗi tiến trình giữ một bản dữ liệu riêng.

## Quyết định

`bootstrap/container.py::_build_storage()` là điểm rẽ nhánh duy nhất, hiện ném
`NotImplementedError` cho mọi `storage.kind` khác `in_memory`. Bước 5 sẽ thêm:

- `adapters/persistence/postgres/` — SQLAlchemy async, Alembic, `UnitOfWork`
- `adapters/persistence/vector/` — `pgvector.py` hoặc `qdrant.py`
- `adapters/persistence/redis/` — `cache.py`, `rate_limiter.py`

Ràng buộc kèm theo: mọi phương thức port chạm dữ liệu phải nhận `TenantScope` ở tham số đầu
tiên, để việc cô lập tenant được bảo đảm bằng chữ ký hàm chứ không bằng review.

## Lỗi hiện tại mà quyết định này chặn dứt điểm

`entrypoints/api/routers/chat.py` lọc `{"tenant_id": ...}` trên `chunk.metadata`, trong khi
`tenant_id` là field của `Chunk` chứ không nằm trong `metadata`. Mọi chunk đều bị loại nên RAG
luôn trả về rỗng. Khi `TenantScope` là tham số bắt buộc của port, kiểu dữ liệu sẽ không cho phép
viết sai như vậy. Sửa ở Bước 3.
