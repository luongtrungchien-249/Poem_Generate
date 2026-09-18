# AI Platform

Nền tảng AI production theo **kiến trúc 4 vòng** (hexagonal): phụ thuộc chỉ đi từ ngoài vào trong,
và ranh giới giữa các vòng do máy cưỡng chế chứ không dựa vào review.

```
entrypoints ──► bootstrap ──► adapters ──► application ──► domain
   (HTTP,        (ráp phụ      (httpx, DB,   (use case,      (thuần Python,
    worker,       thuộc,        Prometheus)   port/Protocol)   không I/O)
    admin, CLI)   đọc env)
```

## Cấu trúc

```
src/
├── domain/          # Vòng 1 — thuần. Không I/O, không thư viện ngoài
│   ├── common/          Result, cây lỗi nghiệp vụ
│   ├── conversation/    ThreadScope, các loại tin nhắn bất biến
│   ├── knowledge/       RetrievedChunk, cosine similarity
│   ├── policy/          mention, command, injection, access, output guard
│   ├── guardrails/      luật input (injection, PII, độ dài) & output (citation, toxicity)
│   └── llm/             đếm token, cắt ngữ cảnh theo ngân sách
│
├── application/     # Vòng 2 — use case. Chỉ import domain
│   ├── rule.py          LUẬT THƠ thất ngôn tự do — đặc tả thi hành được
│   ├── poem_verifier.py nối rule.py vào cổng kiểm định, dựng biên bản sửa
│   ├── ports/           Protocol ra thế giới ngoài: llm, memory, repositories, tools,
│   │                    rate_limit, channel, logger, tracer, verifier
│   ├── pipeline/        đường đi 11 stage + vòng ngoài kiểm định đầu ra
│   ├── prompting/       lắp ngữ cảnh, ngân sách, chỉ dẫn hệ thống
│   ├── rag/             truy hồi lai (BM25 + dense + RRF), rerank, lắp ngữ cảnh
│   ├── ingest/          load → chunk → enrich → embed
│   ├── memory/          bộ nhớ phiên và hồ sơ người dùng
│   └── agent/           vòng lặp ReAct, sổ đăng ký tool (graph/ sẽ gỡ — xem ADR-0002)
│
├── adapters/        # Vòng 3 — hiện thực port bằng công nghệ cụ thể
│   ├── llm/             openai · anthropic · vllm · mock · router · resilience · caching
│   ├── persistence/     memory/ (dev & test); postgres · vector · redis thêm ở Bước 5
│   ├── prompts/         registry YAML + templates
│   ├── tools/           http_call · sql_query · search_kb · kiem_tra_tho
│   └── observability/   tracing · metrics · cost
│
├── bootstrap/       # Vòng 4 — nơi DUY NHẤT đọc biến môi trường
│   ├── settings.py      base.yaml ← <env>.yaml ← ENV
│   └── container.py     build_container(settings) -> AppContainer
│
└── entrypoints/     # Cửa vào: api · worker · admin · cli
```

Ngoài `src/`: `configs/` (cấu hình đa môi trường), `tests/` (unit · contract · integration ·
architecture), `evals/`, `infra/` (docker · helm · terraform), `docs/adr/` (quyết định kiến trúc).

## Bắt đầu

```bash
pip install -e ".[api,worker,dev]"     # hoặc: make install
cp .env.example .env                   # điền khoá nếu cần; mặc định chạy provider mock
make run                               # uvicorn entrypoints.api.app:app --reload
```

- Swagger: http://localhost:8000/docs
- Metrics: http://localhost:8000/metrics

## Kiểm tra chất lượng

```bash
make test        # toàn bộ test
make test-unit   # chỉ test thuần — không mạng, không Docker
make arch        # kiểm tra ranh giới tầng (import-linter)
make check       # lint + types + arch + test
```

Test **không bao giờ** chạm mạng: `tests/conftest.py` xoá mọi khoá API khỏi môi trường và ép
provider về `mock`. `tests/architecture/` quét AST toàn bộ `src/` để chặn import sai chiều.

## Đầu ra có ràng buộc

Khi yêu cầu kèm một `OutputSpec` (ví dụ làm thơ thất ngôn tự do), đầu ra **không đi thẳng
ra người dùng**. Nó phải qua hai vòng:

```
vòng trong   generate_react_loop   mô hình tự chủ, có thể gọi tool kiem_tra_tho để tự soi
vòng ngoài   verify_output         đường ống LUÔN chạy, mô hình không bỏ qua được
```

Cùng một bộ luật (`application/rule.py`), hai chỗ gọi, hai thẩm quyền khác nhau. Chưa đạt
thì hệ thống dựng biên bản có địa chỉ dòng rồi bắt soạn lại; hết lượt sửa thì trả lỗi
`OutputKhongDat` — **không bao giờ** trả ra bài sai luật.

## Cấu hình

Thứ tự ưu tiên: `configs/base.yaml` → `configs/<ENV>.yaml` → biến môi trường.
Bí mật (khoá API, DSN) **chỉ** ở biến môi trường hoặc `.env`, không bao giờ trong YAML.
Mọi truy cập `os.environ` nằm trong `bootstrap/settings.py` — không nơi nào khác.

## Trạng thái và việc còn lại

| Bước | Nội dung | Trạng thái |
|---|---|---|
| 0 | Vá an toàn: `.gitignore`, `.env.example`, tách bí mật | ✅ |
| 1 | Dựng kiến trúc 4 vòng, chuyển toàn bộ mã, cưỡng chế ranh giới | ✅ |
| 2 | Chọn một lõi agent duy nhất, gỡ `agent/graph` | ⬜ ADR-0002 |
| P1+P2 | Luật thơ thất ngôn tự do: `application/rule.py` + 33 test | ✅ |
| P3a | Khe cắm kiểm định: tách `respond`, port `OutputVerifier`, lỗi `OutputKhongDat` | ✅ |
| P3b | Vòng ngoài `verify_output.py` (G1–G7) + tool tự soi `kiem_tra_tho` | ✅ |
| 3 | Nối use case vào API, sửa bug lọc tenant, guardrails cho streaming | ⬜ |
| 4 | Siết mypy, gỡ `contracts` khỏi `domain` | ⬜ |
| 5 | Adapter thật: Postgres · pgvector/Qdrant · Redis | ⬜ ADR-0003 |
| 6 | Worker thật, xác thực, multi-tenant, CI đầy đủ | ⬜ |
