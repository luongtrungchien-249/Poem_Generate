# Poem Generate — hướng dẫn cài đặt, chạy và triển khai

Thực hiện theo thứ tự: chuẩn bị môi trường → cài đặt → cấu hình → tạo database → chạy backend/frontend → kiểm thử → dùng model thật → benchmark → chuẩn bị triển khai.

Lệnh chính dùng **Windows PowerShell**, phù hợp môi trường phát triển của dự án. Chạy tại thư mục gốc repository, trừ khi có chỉ dẫn đổi thư mục. Không cần Docker hoặc API key để bắt đầu bằng mock.

## 1. Chuẩn bị môi trường

- Git để lấy source.
- Python 3.11, phiên bản đang dùng trong CI và Dockerfile.
- Node.js đáp ứng yêu cầu Next.js của dự án: `>=20.9.0`, kèm npm.
- Docker Engine/Desktop và Docker Compose nếu chạy stack container; không bắt buộc cho SQLite local.
- API key có quyền dùng model nếu muốn sinh thơ thật; mock chỉ kiểm tra luồng ứng dụng.

Kiểm tra sau khi cài và mở lại terminal:

```powershell
git --version
python --version
node --version
npm.cmd --version
# Chỉ cần nếu sử dụng Docker:
docker --version
docker compose version
```

Nếu Windows không nhận `python`, thử `py -3.11 --version` và dùng `py -3.11` ở bước tạo virtual environment.

## 2. Lấy source và cài backend

Nếu đã mở repository trong IDE, bỏ qua clone và chuyển tới thư mục dự án đang có.

```powershell
git clone https://github.com/luongtrungchien-249/Poem_Generate.git
Set-Location Poem_Generate
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[api,worker,sql,postgres,dev]"
$env:PYTHONPATH = 'src'
$env:PYTHONUTF8 = '1'
```

Các extras cài API, worker, SQLite/PostgreSQL và công cụ kiểm thử. SQLAlchemy dùng extra `asyncio` để cài cả `greenlet` cần cho SQL async.

Nếu PowerShell chặn `Activate.ps1`, không cần đổi policy toàn hệ thống: dùng `.\.venv\Scripts\python.exe` thay `python`; công cụ khác nằm trong `.venv\Scripts`.

Linux/macOS dùng:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[api,worker,sql,postgres,dev]"
export PYTHONPATH=src
```

Ở các bước tiếp theo, đổi `Set-Location` thành `cd`, `Copy-Item` thành `cp`, `npm.cmd` thành `npm`, và `$env:TEN = 'gia-tri'` thành `export TEN='gia-tri'` khi dùng Bash.

## 3. Tạo cấu hình backend

Chỉ sao chép khi chưa có `.env`, không ghi đè file đang dùng:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Mở `.env` và kiểm tra/chỉnh các dòng sau. Đây là nội dung cấu hình, không phải lệnh PowerShell:

```dotenv
ENV=dev
HOST=127.0.0.1
PORT=8000
WORKERS=1
DEFAULT_PROVIDER=mock
DEFAULT_MODEL=mock-gpt
DEFAULT_TIER=cheap
STORAGE_TYPE=sqlite
DATABASE_URL=
POEM_EMBEDDED_WORKER=true
POEM_JOB_DEADLINE=300
POEM_JOB_ACTIVE_LIMIT=2
POEM_JOB_LEASE=30
POEM_JOB_TTL=86400
POEM_JOB_MAX_CALLS=80
POEM_ADAPTIVE_CANDIDATES=false
POEM_LINE_FRAMING=false
SO_SONG_SONG=2
```

SQLite mặc định lưu tại `data/app.sqlite3`. Không chọn `in_memory` nếu cần giữ lịch sử sau restart. Hai cờ thử nghiệm giữ `false` đến khi có kết quả A/B phù hợp.

Ưu tiên cấu hình: `configs/base.yaml` → `configs/<ENV>.yaml` → `.env` → biến môi trường của terminal/container. `ENV=production` dùng `configs/prod.yaml` nếu không có `production.yaml`. Biến đã đặt bằng `$env:...` thắng `.env`; mở terminal mới khi muốn bỏ override cũ.

Không commit `.env`, API key hoặc DSN thật. Backend và frontend có file môi trường riêng.

## 4. Kiểm tra cấu hình và tạo database local

Trong terminal Python tại gốc repo:

```powershell
# Ép lượt đầu về mock/SQLite, không dùng DSN đã có trong .env:
$env:ENV = 'dev'
$env:DEFAULT_PROVIDER = 'mock'
$env:DEFAULT_MODEL = 'mock-gpt'
$env:STORAGE_TYPE = 'sqlite'
$env:DATABASE_URL = ''
$env:POEM_EMBEDDED_WORKER = 'true'
python -X utf8 -m entrypoints.cli.main config-check
New-Item -ItemType Directory -Force data | Out-Null
python -m alembic upgrade head
python -m alembic current
```

`config-check` phải báo `Config OK: mock/mock-gpt`. Migration phải hoàn tất và `alembic current` hiển thị revision hiện tại.

**Sao lưu trước nếu database đã có dữ liệu.** Với SQLite, dừng API/worker rồi backup; nếu có file `-wal`/`-shm`, dùng quy trình backup SQLite nhất quán, không chỉ sao chép file chính khi đang ghi.

Alembic đọc `DATABASE_URL` của tiến trình hoặc `-x dsn=...`, **không tự nạp `.env` như ứng dụng**. Khi dùng PostgreSQL, phải cung cấp DSN cho terminal migration; nếu không, lệnh có thể chạy vào SQLite mặc định. Không đưa mật khẩu thật vào dòng lệnh/log chia sẻ.

Startup có `create_all` để tạo bảng thiếu, nhưng không thay thế migration cho schema cũ.

## 5. Chạy backend

Giữ terminal bước 4 và chạy:

```powershell
python -m uvicorn entrypoints.api.app:app --host 127.0.0.1 --port 8000 --reload
```

API tự chạy worker nhúng trong cấu hình dev này; chưa cần terminal worker riêng. Chỉ dùng `--reload` cho phát triển.

| Địa chỉ | Mục đích |
|---|---|
| `http://127.0.0.1:8000/docs` | Swagger, xem schema và thử API |
| `http://127.0.0.1:8000/healthz` | Kiểm tra API trả lời |
| `http://127.0.0.1:8000/readyz` | Endpoint readiness hiện có |
| `http://127.0.0.1:8000/metrics` | Metrics Prometheus |

`/readyz` hiện trả trạng thái khai báo, chưa thực sự ping từng dependency. Không coi HTTP 200 ở đây là chứng minh database/model hoạt động; cần smoke test bên dưới.

## 6. Cài và chạy giao diện

Mở terminal thứ hai tại gốc repo:

```powershell
Set-Location frontend
npm.cmd ci
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
```

Kiểm tra `frontend/.env.local`:

```dotenv
BACKEND_URL=http://127.0.0.1:8000
BACKEND_API_KEY=
```

Chạy:

```powershell
npm.cmd run typecheck
npm.cmd run dev
```

Mở `http://localhost:3000`. Cổng 8000 là API, không phải giao diện.

Frontend gọi backend qua BFF của Next.js; key backend chỉ nằm phía server. Không đặt key vào `NEXT_PUBLIC_*`. Đổi `.env.local` cần restart Next.js. Nếu backend bật `API_KEYS`, đặt `BACKEND_API_KEY` bằng key hợp lệ trong bảng đó.

## 7. Smoke test ứng dụng

### 7.1 Qua giao diện

Tạo hội thoại → gửi yêu cầu thơ → xem tiến độ → tải lại trang khi job đang chạy → thử hủy job. Với mock, yêu cầu đủ thông tin có thể không đạt luật và trả chẩn đoán; yêu cầu thiếu thông tin có thể hỏi lại. Mock không chứng minh chất lượng generation.

### 7.2 Qua API

Mở terminal thứ ba. Ví dụ dùng dev không xác thực; chuỗi không dấu trong request để tránh vấn đề encoding của Windows PowerShell cũ:

```powershell
$apiBase = 'http://127.0.0.1:8000'
$apiHeaders = @{}
# Nếu bật xác thực, thêm x-api-key vào $apiHeaders bằng key của bạn.
Invoke-RestMethod "$apiBase/healthz"

$conversationBody = @{ tieu_de = 'Thu nghiem local' } | ConvertTo-Json
$conversation = Invoke-RestMethod "$apiBase/v1/conversations" -Method Post `
    -Headers $apiHeaders -ContentType 'application/json' -Body $conversationBody

$jobHeaders = $apiHeaders.Clone()
$jobHeaders['Idempotency-Key'] = [guid]::NewGuid().ToString()
$jobBody = @{
    yeu_cau = 'Viet bai tho ve que huong'
    chu_de = 'que huong'
    so_dong = 4
    session_id = $conversation.conversation_id
} | ConvertTo-Json
$job = Invoke-RestMethod "$apiBase/v1/poem/jobs" -Method Post `
    -Headers $jobHeaders -ContentType 'application/json' -Body $jobBody
$job.job_id

# Chạy lại để đọc tiến độ/kết quả:
Invoke-RestMethod "$apiBase/v1/poem/jobs/$($job.job_id)" -Headers $apiHeaders
```

POST tạo job trả HTTP 202. GET trạng thái trả 200 kể cả job không đạt; đọc `status`, `result_status`, `result` và `error`, không chỉ mã HTTP của GET.

```powershell
# Hủy job chưa kết thúc:
Invoke-RestMethod "$apiBase/v1/poem/jobs/$($job.job_id)" -Method Delete -Headers $apiHeaders
# Xem lịch sử:
Invoke-RestMethod "$apiBase/v1/conversations/$($conversation.conversation_id)" -Headers $apiHeaders
```

SSE dùng `GET /v1/poem/jobs/{job_id}/events`, có event `progress`/`done`. Đóng SSE không hủy job; hủy bằng DELETE. Retry POST cần cùng idempotency key và cùng body để nhận lại job.

| Kết quả | Ý nghĩa / hành động |
|---|---|
| `completed`, `result_status=200` | Bài thơ đạt kiểm định hoặc câu hỏi làm rõ |
| `failed`, `result_status=422` | Không đạt kiểm định; không phát bài sai luật |
| HTTP 401 | Thiếu/sai key backend |
| HTTP 409 | Idempotency key đã dùng với body khác |
| HTTP 429 khi tạo job | Vượt active job/tenant; chờ hoặc hủy job cũ |
| `expired` | Hết deadline tổng, gồm cả chờ queue |

Endpoint đồng bộ `POST /v1/poem` vẫn dùng được trong Swagger. Luồng job thích hợp cho tiến độ và phục hồi khi reload. Số dòng phải là bội của 4; hệ thống hỏi lại thay vì tự làm tròn.

## 8. Chuyển sang model thật

Dừng backend, mở terminal mới và kích hoạt `.venv` để bỏ override mock của bước 4. Chỉnh `.env` với provider/model trong [configs/models.yaml](configs/models.yaml). Ví dụ theo cấu hình Google hiện có của repository:

```dotenv
DEFAULT_PROVIDER=google
DEFAULT_MODEL=gemini-3.5-flash-lite
GOOGLE_API_KEY=<dien-key-cua-ban>
SO_SONG_SONG=2
```

Placeholder phải thay trước khi chạy. Provider khác dùng `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`; vLLM dùng `VLLM_BASE_URL` và model server đang phục vụ. Có tên trong catalog không đảm bảo tài khoản được cấp quyền truy cập.

```powershell
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = 'src'
python -X utf8 -m entrypoints.cli.main config-check
python -X utf8 -m entrypoints.cli.main model-check
python -m uvicorn entrypoints.api.app:app --host 127.0.0.1 --port 8000 --reload
```

`config-check` kiểm catalog/giá cấu hình. `model-check` gọi metadata, không sinh thơ; vẫn cần request sinh thật để kiểm quyền generation/quota. Generation và benchmark có thể tính phí. Kiểm tra giá/quota của tài khoản trước khi chạy lô lớn; giá catalog là cấu hình ước tính, không phải cam kết hóa đơn.

Dev có thể fallback mock khi thiếu key; staging/production thiếu key phải fail. Không coi dev không báo lỗi là bằng chứng đang dùng model thật: xem provider/model trong CLI và job.

## 9. Bật xác thực

Thêm vào `.env` backend và restart API:

```dotenv
API_KEYS=<key-ngau-nhien-cua-ban>:tenant_local
```

Đặt `BACKEND_API_KEY` trong `frontend/.env.local` bằng phần key trước dấu `:`, rồi restart frontend. API trực tiếp cần header `x-api-key`. Tenant được tra từ key, không lấy từ body client.

Không để bảng key rỗng khi public backend: cấu hình rỗng hiện tắt xác thực, kể cả khi đổi `ENV`. Key chung trong BFF không thay thế đăng nhập người dùng: trước khi public frontend, cần kiểm soát frontend/session để người ngoài không sử dụng quyền tenant của key đó.

## 10. Kiểm thử và kiểm tra chất lượng

Terminal Python ở gốc repo:

```powershell
python -m ruff check src tests evals
python -m mypy src
$env:PYTHONPATH = 'src'
lint-imports
python -m pytest -q -W error::pytest.PytestUnhandledThreadExceptionWarning
python -X utf8 datalake/scripts/doi_soat_tai_lieu.py
python -X utf8 evals/run_poetry.py
```

`evals/run_poetry.py` kiểm offline tập mẫu/luật/an toàn, không đo tỷ lệ generation model thật. Tests ép provider mock và vô hiệu key LLM; ma trận PostgreSQL chỉ dùng DSN test riêng khi bạn chủ động cấp.

Terminal frontend:

```powershell
npm.cmd run typecheck
npm.cmd run build
# Backend phải đang chạy nếu cập nhật kiểu từ OpenAPI:
npm.cmd run gen:types
```

`gen:types` có thể sửa file tracked: xem diff trước commit. Không dùng `npm run lint` làm cổng nghiệm thu hiện tại: script ESLint có trong package nhưng chưa khai báo dependency/config hoàn chỉnh.

Để chạy như CI, tách `python -m pytest -q tests/unit tests/architecture` và `python -m pytest -q tests/contract`. CI còn kiểm Ruff, mypy, import-linter, đối soát tài liệu và evaluation gate.

`src/application/rule.py` đóng băng. Không sửa rule hoặc đổi hash để làm test xanh. `.gitattributes` cố định CRLF cho riêng file để hash nhất quán Windows/Linux.

### PostgreSQL integration — chỉ DB test riêng

Tự tạo DB rỗng có tên bắt đầu `poem_improve_test_`, rồi cấu hình terminal test:

```powershell
# Ví dụ minh họa; thay bằng credential của DB test riêng đã tạo:
$env:TEST_DATABASE_URL = 'postgresql+asyncpg://test_user:test_password@127.0.0.1:5432/poem_improve_test_local'
python -m pytest -q tests/integration
```

Fixture **xóa/reset bảng ứng dụng và `alembic_version`**. Không trỏ vào DB đang dùng/production. Không dùng `DATABASE_URL` thay `TEST_DATABASE_URL`. Thiếu DSN test thì PostgreSQL cases skip; xanh có skip không chứng minh PostgreSQL runtime đã nghiệm thu.

## 11. Dữ liệu và baseline/A-B

`datalake/corpus_tuyen` chứa corpus mẫu đủ khởi động local. Không cần tải toàn kho để cài ứng dụng. Dữ liệu thô/chỉ mục đầy đủ không đưa lên Git.

Nếu cần toàn kho đối chiếu/chống chép, đọc [Plan PoeTone](docs/Plan_PoeTone.md) và hướng dẫn trong `datalake/scripts/nhap_kho_hf.py` trước khi tải/nhập. Nguồn dự án sử dụng: `phamson02/vietnamese-poetry-corpus` trên HuggingFace, ghi nhận CC-BY-4.0; giữ attribution khi sử dụng/phân phối. Corpus mẫu không tương đương chỉ mục đầy đủ `datalake/hf/chi_muc_dong.bin`.

Chuẩn bị artifact, không gọi model:

```powershell
python -X utf8 evals/baseline.py --size 40 --prepare-only --out evals/ket_qua/local_prepared40.jsonl
```

Chỉ khi model-check và smoke generation qua, có quota/ngân sách phù hợp, mới chạy các lệnh **có thể tính phí**:

```powershell
python -X utf8 evals/baseline.py --size 40 --profile fixed --out evals/ket_qua/local_control40.jsonl
python -X utf8 evals/baseline.py --size 40 --profile adaptive --out evals/ket_qua/local_adaptive40.jsonl
python -X utf8 evals/baseline.py --compare evals/ket_qua/local_control40.jsonl evals/ket_qua/local_adaptive40.jsonl --out evals/ket_qua/local_ab40.jsonl
```

Dùng tên output mới mỗi lần; runner không cho ghi đè raw run. `--max-calls 80 --timeout 300` giới hạn gọi logic/deadline mỗi đề, không phải trần tiền/token; retry có thể thêm request.

Giữ nguyên model, concurrency, dataset, corpus và ngân sách giữa control/treatment. Profile `line` đo line-framing riêng. Sau 40 đề có tín hiệu tốt mới lặp `--size 200` với output mới.

Runner tạo raw JSONL, manifest và báo cáo tổng hợp truy vết source/cấu hình. Artifact prepared không phải live. Chưa có baseline live mới chứng minh adaptive/line-framing tốt hơn; không lấy tỷ lệ lịch sử khác model/pipeline làm kết luận cho bản hiện tại. Chỉ bật cờ sau nghiệm thu, đồng bộ API/worker. Chi tiết tại [Runbook Improve 06/10](docs/Runbook_Improve_06_10.md).

## 12. API và worker riêng với PostgreSQL

Đây là bước rời local SQLite, chưa phải xác nhận production-ready. Chuẩn bị PostgreSQL riêng, credential phù hợp và backup.

API/worker dùng cùng DB, provider/model và cờ thử nghiệm. Cấu hình:

```dotenv
ENV=production
STORAGE_TYPE=sql
DATABASE_URL=<DSN-PostgreSQL-cua-ban>
DEFAULT_PROVIDER=<provider-trong-catalog>
DEFAULT_MODEL=<model-trong-catalog>
POEM_EMBEDDED_WORKER=false
API_KEYS=<key-ngau-nhien-cua-ban>:tenant_production
POEM_ADAPTIVE_CANDIDATES=false
POEM_LINE_FRAMING=false
```

Thay placeholder và cấp key LLM tương ứng. Không dùng credential demo Compose cho production.

Ở terminal migration có `DATABASE_URL` đúng được cấp qua môi trường an toàn:

```powershell
python -X utf8 -m entrypoints.cli.main config-check
python -X utf8 -m entrypoints.cli.main model-check
python -m alembic upgrade head
python -m alembic current
```

Không migration đồng thời từ nhiều replica. Xác nhận đúng DB và backup trước thay đổi; terminal mới giúp tránh override SQLite/mock từ local.

Terminal API, gốc repo trong `.venv`:

```powershell
python -m uvicorn entrypoints.api.app:app --host 0.0.0.0 --port 8000 --workers 1
```

Terminal worker, cùng môi trường:

```powershell
python -X utf8 -m entrypoints.cli.main worker
```

Nếu tách máy/container, cấp cùng cấu hình cho cả hai. Poem queue hiện nằm ở SQL, không cần Redis cho riêng luồng job này. Worker claim/heartbeat, API đọc trạng thái; tắt worker nhúng khi vận hành worker riêng.

Frontend bản build, tại `frontend/`:

```powershell
npm.cmd ci
npm.cmd run typecheck
npm.cmd run build
npm.cmd run start
```

Next.js cần chạy server cho BFF, không static export. Nếu frontend chạy container, `BACKEND_URL` phải là địa chỉ backend truy cập được từ container; `127.0.0.1` không trỏ đến container API khác.

## 13. Docker dev (tùy chọn)

Compose có API, worker, PostgreSQL, Redis, Qdrant; **không có frontend**, mặc định mock. Dừng backend local để tránh trùng cổng 8000; kiểm dung lượng đĩa trước build.

```powershell
docker compose -f infra/docker/docker-compose.yml config --quiet
docker compose -f infra/docker/docker-compose.yml build api worker
docker compose -f infra/docker/docker-compose.yml up -d postgres redis qdrant
# Migration một lần bằng môi trường service api:
docker compose -f infra/docker/docker-compose.yml run --rm --no-deps api python -m alembic upgrade head
docker compose -f infra/docker/docker-compose.yml up -d api worker
docker compose -f infra/docker/docker-compose.yml ps
docker compose -f infra/docker/docker-compose.yml logs --tail 100 api worker
```

Chạy smoke bước 7 và frontend local bước 6. Compose không tự cấp key/model trong `.env` root cho services; provider/model demo đang ghi trong YAML. Model thật cần override riêng, cấp secrets cho **cả API và worker**, không commit key.

Compose hiện **chưa khai báo volume bền vững cho PostgreSQL**. Trước khi giữ dữ liệu quan trọng, bổ sung named volume/mount, backup và thử restore. Filesystem container không phải chiến lược lưu dữ liệu. Không chạy `down -v` với dữ liệu cần giữ.

Tạm dừng mà không xóa container:

```powershell
docker compose -f infra/docker/docker-compose.yml stop
```

Image có corpus mẫu; toàn kho chống chép cần chỉ mục đã kiểm chứng qua read-only mount. Build thành công chưa chứng minh runtime: kiểm API/worker/DB và restart recovery thực tế.

## 14. Checklist trước khi public / bàn giao

- Cài được từ môi trường sạch, backend/frontend build và các cổng kiểm tra pass.
- API/worker chung SQL, đúng model/config, migration đúng DB.
- Key model hợp lệ, smoke generation qua; có quota/ngân sách.
- Backend bật `API_KEYS`; frontend có kiểm soát đăng nhập/truy cập; không lộ key browser.
- HTTPS/reverse proxy; SSE không buffer/timeout quá sớm; BFF same-origin không cần CORS wildcard.
- Volume bền vững, backup và thử restore; không dùng DB thật cho test.
- Browser test: reload, đổi hội thoại, mất SSE, hủy sớm, restart API/worker, job recovery.
- PostgreSQL integration/load test, đo latency/chi phí/tỷ lệ đạt theo cấu hình phát hành.
- Giám sát queue/job lỗi, 429, timeout, DB và chi phí; không chỉ dựa vào `/readyz` hiện tại.

Worker có lease/fencing nhưng là **at-least-once**: crash sau gọi provider có thể chạy lại và phát sinh phí lặp; không cam kết exactly-once billing. `POEM_JOB_MAX_CALLS` không phải trần tuyệt đối HTTP retry/token.

[deploy.yaml](.github/workflows/deploy.yaml) hiện là scaffold, lệnh deploy bị comment: **không tự deploy production**. Merge/CI xanh không đồng nghĩa đã phát hành; cần hạ tầng, registry, secrets và rollout/rollback phù hợp.

Rollback thử nghiệm: đặt hai cờ `POEM_ADAPTIVE_CANDIDATES=false`, `POEM_LINE_FRAMING=false`, chờ job cũ kết thúc rồi restart đồng bộ API/worker. Không downgrade DB thật hoặc xóa lịch sử để rollback code khi chưa backup và kiểm tính tương thích schema.

## 15. Lỗi thường gặp

| Hiện tượng | Kiểm tra / xử lý |
|---|---|
| Không import `entrypoints`/`domain` | Đúng `.venv`, đã editable install, ở gốc repo; đặt `PYTHONPATH=src` |
| Thiếu `greenlet`/`aiosqlite`/`asyncpg` | Cài lại extras bước 2 trong đúng Python |
| Đổi `.env` vẫn mock | Biến terminal cũ thắng `.env`; mở terminal mới, config/model-check |
| Provider HTTP 400/401/403 | Kiểm key, quyền service/model; không chia sẻ key/log bí mật |
| Provider 429 | Kiểm quota, giảm concurrency, chờ theo policy; không retry lô lớn vô hạn |
| Frontend 502 | Backend chưa chạy hoặc URL sai; kiểm healthz, restart Next.js sau đổi env |
| API/frontend 401 | Key/header không khớp `API_KEYS` |
| Job giữ `queued` | Worker chưa chạy, worker nhúng tắt hoặc khác DSN; xem log worker |
| Job `expired` | Queue/generation quá deadline; kiểm backlog/quota trước khi tăng thời gian |
| Kết quả 422 với mock | Không sinh được bài đạt; dùng model thật để kiểm generation |
| Migration nhầm DB | Alembic không đọc `.env`; kiểm DSN terminal migration |
| Cổng 8000/3000 đang dùng | Dừng tiến trình trùng hoặc đổi cổng và `BACKEND_URL` tương ứng |
| Docker build hết đĩa | Kiểm dung lượng, không xóa volume DB để chữa lỗi build |
| Hash rule khác máy | Giữ `.gitattributes`, checkout đúng EOL; không sửa rule/hash để bỏ test |

## 16. Tài liệu đọc tiếp

- [Plan Improve 06/10](docs/Plan_Improve_06_10.md): phạm vi, tiến độ, việc còn lại.
- [Runbook Improve 06/10](docs/Runbook_Improve_06_10.md): worker, giới hạn, benchmark, rollback.
- [Báo cáo phân tích và kế hoạch cải thiện](docs/Bao_Cao_Phan_Tich_Va_Ke_Hoach_Cai_Thien.md): cơ sở đánh giá.
- [Plan PoeTone](docs/Plan_PoeTone.md): dữ liệu và phép đo generation lịch sử.
- [Plan Rule phân tầng](docs/Plan_Rule_Phan_Tang.md): luật và bảo vệ rule.
- [ADR](docs/adr): quyết định kiến trúc.

Khi sửa code, giữ chiều phụ thuộc `entrypoints → bootstrap → adapters → application → domain`; kiểm bằng test/import-linter. Hướng dẫn này không thay thế các hạng mục nghiệm thu còn mở trong plan/runbook.
