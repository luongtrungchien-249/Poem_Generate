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
│   ├── agent/           sổ đăng ký tool (graph/ đã gỡ 21/09 — ADR-0002)
│   └── poetry/          yêu cầu · kế hoạch · chất lượng · CoT · suy luận · few-shot
│
├── adapters/        # Vòng 3 — hiện thực port bằng công nghệ cụ thể
│   ├── llm/             openai · anthropic · vllm · mock · router · resilience · caching
│   ├── persistence/     memory/ (dev & test) · sql/ (SQLite + Postgres) · corpus/
│   ├── prompts/         registry YAML + templates
│   ├── tools/           http_call · sql_query · search_kb · poem_check · poem_quality
│   ├── rate_limit/      bộ đếm in-memory (bản dùng chung ở persistence/sql/)
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
- Sinh thơ: `POST /v1/poem` — xem mục dưới
- Metrics: http://localhost:8000/metrics

## Kiểm tra chất lượng

```bash
make test             # toàn bộ test
make test-unit        # chỉ test thuần — không mạng, không Docker
make test-integration # hai dialect; nhánh Postgres tự bỏ qua khi thiếu DATABASE_URL
make arch             # kiểm tra ranh giới tầng (import-linter)
make migrate          # alembic upgrade head
make check            # lint + types + arch + test
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

### `POST /v1/poem`

Đường sinh thơ đã nối vào API (21/09/2026). Ba mã trạng thái, ba nghĩa khác nhau:

| Mã | Nghĩa |
|---|---|
| `200` + `PoemResponse` | bài qua cả luật lẫn chất lượng, **kèm bằng chứng bảy tầng** |
| `200` + `CanLamRo` | chưa đủ thông tin → hệ thống **hỏi lại**, không đoán |
| `422` + `PoemKhongDat` | hết lượt sửa → **không** trả bài sai, chỉ trả chẩn đoán |

```bash
curl -X POST localhost:8000/v1/poem -H 'content-type: application/json'   -d '{"yeu_cau":"Viết bài về quê hương","chu_de":"quê hương","so_dong":8}'
```

Xin 6 dòng thì API **không tự làm tròn** — nó hỏi *"bạn muốn 4 hay 8 dòng?"*, vì H4
(số dòng là bội của 4) là luật cứng và làm tròn im lặng là quyết định thay người dùng.

> Với provider `mock` mặc định, endpoint này trả **422** — mock không sinh thơ. Đó là
> hành vi đúng: fail closed. Cần provider thật để có bài đạt.

### `rule.py` bị ĐÓNG BĂNG

Chỉ thị chủ dự án 21/09/2026: *"Rule của tôi phải là không được thay đổi."*
`tests/architecture/test_rule_dong_bang.py` ghim SHA-256 của tệp, chặn việc cài lại
phép đếm tiếng ở chỗ thứ hai, và chặn việc ghi đè biến của nó lúc chạy. Sửa luật là
một quyết định, không phải một thao tác — thông báo lỗi của test ghi sẵn ba bước phải
làm trước khi đổi băm.

## Cấu hình

Thứ tự ưu tiên: `configs/base.yaml` → `configs/<ENV>.yaml` → biến môi trường.
Bí mật (khoá API, DSN) **chỉ** ở biến môi trường hoặc `.env`, không bao giờ trong YAML.
Mọi truy cập `os.environ` nằm trong `bootstrap/settings.py` — không nơi nào khác.

## ⚠️ Năng suất thật — cập nhật 26/09/2026

**Baseline 200 đề** (`evals/datasets/de_danh_gia.jsonl`, `gpt-4o-mini`, commit `775b225`,
zero-shot, 32 ứng viên mỗi khổ):

| Độ dài | 4 | 8 | 12 | 16 | 20 | **Tổng** |
|---|---:|---:|---:|---:|---:|---:|
| đạt luật | 30 % | 25 % | 22,5 % | 15 % | 7,5 % | **20 %** |

Chi phí ≈ 14,8 USD / 1.000 bài, trung bình 26 s mỗi bài.

Con số 83,3 % đo ngày 21/09 (12 đề, 4–12 dòng, few-shot đang bật) **không tái lập được**
trên tập đề này. Nút thắt vẫn là **tầng 4 (thanh luật)**: `p` — tỉ lệ một dòng vừa đủ 7
tiếng vừa khớp khuôn — chỉ ≈ 0,22–0,35 khi zero-shot.

**One-shot đã bật lại (commit `090c03c`)**: một bài mẫu đưa `p` từ 22,5 % lên 46,6 % và dòng
đủ 7 tiếng từ 58,7 % lên 98,7 % (A/B khổ đầu, 192 ứng viên mỗi nhánh). **Chưa đo lại tỉ lệ đạt
cả bài sau thay đổi này.**

Chi tiết và cách đo lại: [`docs/Plan_PoeTone.md`](docs/Plan_PoeTone.md) §0.A–0.F.

## Nguồn dữ liệu ngoài

- **Vietnamese Poetry Corpus**: [`phamson02/vietnamese-poetry-corpus`](https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus)
  trên HuggingFace, giấy phép **CC-BY-4.0**. Dùng làm kho đối chiếu và kho ví dụ
  ứng viên (Plan_PoeTone GĐ0.2). Dữ liệu thô **không** commit; nhập lại bằng
  `python datalake/scripts/nhap_kho_hf.py`, số liệu ở `datalake/hf/tong_hop.json`.
  Mọi báo cáo dùng dữ liệu này phải ghi nguồn như trên.

## Trạng thái và việc còn lại

| Bước | Nội dung | Trạng thái |
|---|---|---|
| 0 | Vá an toàn: `.gitignore`, `.env.example`, tách bí mật | ✅ |
| 1 | Dựng kiến trúc 4 vòng, chuyển toàn bộ mã, cưỡng chế ranh giới | ✅ |
| 2 | Chọn một lõi agent duy nhất, gỡ `agent/graph` | ✅ ADR-0002 |
| P1+P2 | Luật thơ thất ngôn tự do: `application/rule.py` + 33 test | ✅ |
| P3a | Khe cắm kiểm định: tách `respond`, port `OutputVerifier`, lỗi `OutputKhongDat` | ✅ |
| P3b | Vòng ngoài `verify_output.py` (G1–G7) + tool tự soi `kiem_tra_tho` | ✅ |
| G1 | Nối đường thơ vào API: `POST /v1/poem`, 3 adapter port, đóng băng `rule.py` | ✅ |
| G6a | Vá lỗ `stream=true` bỏ qua output guardrails | ✅ |
| — | Gọi tool: `tools` đi được cả hai chiều qua 4 adapter provider | ✅ |
| G1b | Tách port theo trách nhiệm (hội thoại · nhúng · luồng) — ADR-0005 | ✅ |
| G6b | Nối topic filter 3 mức SAFE/REVIEW/BLOCK · input rails cho `/v1/poem` · bảng đe doạ §20 | ✅ |
| G3 | Kho thơ mẫu + few-shot **đảm bảo đúng luật** (300 bài tuyển, commit được) | ✅ |
| G2 | Requirement Analyzer §7.2 — trích yêu cầu từ câu nói tự nhiên, `nguon` kiểm được | ✅ |
| G4 | Planner §10 (tất định) + State Machine §31 (14 trạng thái) | ✅ |
| G5 | Evidence đầy đủ: đường đi · nguồn ví dụ · quyết định HITL | ✅ |
| G7 | HITL §22 (5 quyết định) + Feedback §24 (van chặn trước kho mẫu) | ✅ |
| G8 | Benchmark §33 — `python evals/run_poetry.py`, chạy offline | ✅ |
| G9 | Cô lập tenant bằng chữ ký hàm · sửa lỗi lọc tenant · SQLite bền vững | ✅ |
| G10 | Xác thực API key, tenant lấy từ khoá (không từ thân request) | ✅ |
| G11 | Gỡ ngưỡng tuỳ ý cuối cùng — hệ thống **không còn ngưỡng dò được nào** | ✅ |
| G12 | Adapter SQL **một mã hai dialect** (SQLite/Postgres) · bộ đếm dùng chung giữa tiến trình | ✅ |
| G13 | Vòng đời khoá API: phát hành · hết hạn · **thu hồi tức thì** · lưu dạng băm | ✅ |
| G14 | Kho vector bền vững · Alembic migration · test tích hợp hai dialect | ✅ |
| G15 | **Đo thật với OpenAI** — trả lời rủi ro R2, xem `docs/Do_That_21-09_R2.md` | ✅ |
| 3 | Sửa bug lọc tenant | ✅ G9 |
| 4 | Siết mypy, gỡ `contracts` khỏi `domain` | ⬜ |
| 5 | Adapter SQL + kho vector + Alembic ✅ G12/G14 · pgvector/Qdrant chỉ cần khi >10⁵ vector | ✅ |
| 6 | Vòng đời khoá API ✅ G13 · còn worker thật, CI đầy đủ | 🟡 |
