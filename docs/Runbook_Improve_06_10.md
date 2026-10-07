# Vận hành thay đổi Plan Improve 06/10

## Trạng thái

Nền tảng job/search/validation đã triển khai. Adaptive và line-framing mặc định tắt; chưa có kết quả A/B thật. Key Google hiện bị provider từ chối HTTP 400. Không ghi khóa/DSN thật vào artifact và không tự sửa `.env`.

## Chạy local an toàn (PowerShell)

Chạy ở gốc repo, trong môi trường Python của dự án:

```powershell
python -m pip install -e ".[api,worker,sql,postgres,dev]"
$env:PYTHONPATH = 'src'
$env:ENV = 'dev'
$env:DEFAULT_PROVIDER = 'mock'
$env:DEFAULT_MODEL = 'mock-gpt'
$env:STORAGE_TYPE = 'sqlite'
$env:DATABASE_URL = ''
$env:POEM_EMBEDDED_WORKER = 'true'
python -X utf8 -m entrypoints.cli.main config-check
python -m alembic upgrade head
python -m uvicorn entrypoints.api.app:app --host 127.0.0.1 --port 8000
```

Các biến trên chỉ đổi tiến trình terminal, không đổi `.env`. Mock dùng để kiểm wiring và hỏi lại, không phải chứng minh chất lượng sinh thơ. Khi có DB cũ, sao lưu trước migration. `create_all` lúc startup chỉ tạo bảng thiếu, không thay thế Alembic cho thay đổi schema.

Frontend ở terminal khác:

```powershell
Set-Location frontend
npm.cmd run typecheck
npm.cmd run build
npm.cmd run dev
```

BFF giữ key backend phía server; cấu hình `BACKEND_URL` và API key theo `frontend/.env.example`. Không đưa key vào biến `NEXT_PUBLIC_*`. Với CORS trực tiếp, khai báo origin cụ thể; BFF same-origin không cần CORS.

## Worker riêng / production

API và worker phải có cùng `STORAGE_TYPE=sql`, `DATABASE_URL`, provider/model và cờ thử nghiệm. API đặt `POEM_EMBEDDED_WORKER=false`; worker chạy:

```powershell
python -X utf8 -m entrypoints.cli.main model-check
python -m alembic upgrade head
python -X utf8 -m entrypoints.worker.poem_jobs
```

`ENV=production` đọc `configs/production.yaml`, hoặc `prod.yaml` nếu không có file đó. Phải đặt rõ `DEFAULT_PROVIDER`/`DEFAULT_MODEL` phù hợp catalog và bật xác thực `API_KEYS` theo môi trường triển khai. Không dùng kho `in_memory` cho nhiều tiến trình hoặc phục hồi lịch sử. Không log biến môi trường chứa DSN/key.

Compose phát triển dùng mock/Postgres, không phải cấu hình production:

```powershell
docker compose -f infra/docker/docker-compose.yml config --quiet
docker compose -f infra/docker/docker-compose.yml build api worker
```

Không tự chạy `up` trong bước nghiệm thu này. Khi triển khai thật phải giữ volume PostgreSQL, thay credential demo, chạy migration có kiểm soát. Image có corpus mẫu; để chống chép trên kho đầy đủ, mount chỉ mục `datalake/hf/chi_muc_dong.bin` đã kiểm chứng dạng read-only. Không đồng nhất fallback corpus mẫu với chỉ mục 547.181 dòng.

## API và giới hạn

| Thao tác | Đường dẫn |
|---|---|
| Tạo job | `POST /v1/poem/jobs`, header `Idempotency-Key`, trả 202 |
| Đọc trạng thái | `GET /v1/poem/jobs/{id}` |
| Theo dõi | `GET /v1/poem/jobs/{id}/events` |
| Hủy | `DELETE /v1/poem/jobs/{id}` |
| Job đang chạy của hội thoại | `GET /v1/poem/jobs?conversation_id=...` |
| Tìm kiếm | `GET /v1/conversations?q=...&limit=50&cursor=...` |

HTTP 409: key idempotency đã dùng cho body khác. HTTP 429 lúc admission: vượt active job tenant. Kết quả job có `result_status=422` là không đạt kiểm định, không phải lỗi hạ tầng; GET trạng thái vẫn trả 200. SSE có `progress`/`done`, chỉ metadata hoặc kết quả cuối. Cursor tiếp theo ở header `x-next-cursor`; lọc tiêu đề tại repository, không tìm nội dung tin nhắn.

Mặc định: deadline tổng 300s (bao gồm chờ queue), active limit 2/tenant, lease 30s, TTL terminal 86.400s, tối đa 80 lượt model logic/job. Có thể đặt `POEM_JOB_DEADLINE`, `POEM_JOB_ACTIVE_LIMIT`, `POEM_JOB_LEASE`, `POEM_JOB_TTL`, `POEM_JOB_MAX_CALLS`. Quota ngày của SQL limiter dùng chung; retry provider có thể tốn thêm request/chi phí. Chưa có trần token theo độ dài.

## Baseline / A-B

Trước hết `model-check` phải qua bằng key hợp lệ; metadata check chưa chứng minh generate/quota. Chạy smoke ít đề trước lô tốn phí. Không thay model hoặc concurrency giữa control và treatment.

```powershell
# Chuẩn bị, KHÔNG gọi model:
python -X utf8 evals/baseline.py --size 40 --prepare-only --out evals/ket_qua/prepared40.jsonl
python -X utf8 evals/baseline.py --size 200 --prepare-only --out evals/ket_qua/prepared200.jsonl

# Chỉ khi đã có key/quota hợp lệ; các lệnh này có tính phí:
python -X utf8 evals/baseline.py --size 40 --profile fixed --out evals/ket_qua/control40.jsonl
python -X utf8 evals/baseline.py --size 40 --profile adaptive --out evals/ket_qua/adaptive40.jsonl
python -X utf8 evals/baseline.py --compare evals/ket_qua/control40.jsonl evals/ket_qua/adaptive40.jsonl --out evals/ket_qua/ab40.jsonl
```

Sau 40 đề có tín hiệu tốt mới lặp `--size 200`; dùng tên `--out` mới để tránh ghi đè raw. Profile `line` đo riêng khung thanh; không bật cùng adaptive trong phép đo một yếu tố. Runner ghi commit + source/dataset/corpus/model-price hashes, concurrency, trần gọi và deadline; manifest `prepared` không phải live. Source hash ghi nhận cả thay đổi chưa commit; commit SHA riêng không đại diện đầy đủ worktree.

JSONL chỉ chứa bài thành công, không phát nháp sai. Chi phí ước tính gồm usage `reply`/`cheap` và cached/thinking output từ adapter; lượt lỗi không có usage không thể tính chính xác. Reviewer chưa có nhãn người chấm, nên không gọi điểm LLM là chất lượng đã chứng minh.

Manifest còn ghi hash runner, luật và chỉ mục chống chép nếu có; so sánh A/B từ chối khác ngân sách, corpus, index, giá, seed hoặc run chưa đủ đề. Thiếu key ở staging/production phải fail sớm, không lùi về mock âm thầm.

Artifact lịch sử 200 đề là gpt-4o-mini zero-shot, 20% đạt, 14,81 USD/1.000 đề chưa tính cheap. Không so trực tiếp với pipeline/model mới rồi kết luận treatment tốt hơn.

## Kiểm chứng / rollback

```powershell
python -m pytest -q
$env:PYTHONPATH = 'src'
lint-imports
```

Frontend: `npm.cmd run typecheck`, `npm.cmd run build`; khi API đang chạy: `npm.cmd run gen:types`. Cần browser E2E cho reload, đổi hội thoại, hủy sớm, mất SSE; cần PostgreSQL và load test trước production.

Lần thực thi này đã build hai image nhưng chưa chạy smoke container: hệ thống duyệt quyền hết hạn mức, không phải từ chối vì rủi ro thao tác. Có thể tiếp tục kiểm tra container tạm khi quyền thực thi hoạt động lại; không dùng DB production cho các test có `drop_all`.

Cập nhật 07/10: lượt rebuild sau đó bị chặn bởi ổ đĩa đầy; hiện test offline đã chạy lại xanh sau khi dung lượng ghi phục hồi. Nghiệm thu runtime Docker/PostgreSQL vẫn chưa hoàn tất.

Ma trận PostgreSQL dùng `TEST_DATABASE_URL`, không dùng `DATABASE_URL` từ `.env`. Database phải có tên `poem_improve_test_*` và hoàn toàn là dữ liệu test, vì fixture reset bảng ứng dụng và `alembic_version`. Khi chưa cấu hình, 17 trường hợp PostgreSQL được skip. Ví dụ chỉ chạy sau khi tự tạo DB test riêng:

```powershell
$env:TEST_DATABASE_URL = 'postgresql+asyncpg://test_user:test_password@127.0.0.1:5432/poem_improve_test_local'
python -m pytest -q tests/integration
```

Rollback thử nghiệm: đặt `POEM_ADAPTIVE_CANDIDATES=false`, `POEM_LINE_FRAMING=false`, chờ job cũ kết thúc rồi restart đồng bộ API/worker. Giữ schema/job/history; không chạy downgrade trên DB thật khi chưa sao lưu và kiểm dữ liệu. Endpoint `/v1/poem` cũ vẫn còn cho client tương thích.
