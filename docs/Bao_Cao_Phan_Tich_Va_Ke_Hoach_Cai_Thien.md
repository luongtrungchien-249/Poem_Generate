# BÁO CÁO PHÂN TÍCH TOÀN BỘ HỆ THỐNG & KẾ HOẠCH CẢI THIỆN
**Dự án:** Poem_Generate (AI Platform v2.0)

**Tác giả phân tích:** Antigravity AI Assistant

**Ngày lập:** Tháng 10/2026

**Phạm vi:** Toàn bộ Source Code (`src/`, `frontend/`), Hệ thống Tài liệu (`docs/`), Ngữ liệu & Thực nghiệm (`datalake/`, `evals/`), Bộ kiểm thử (`tests/`).

---

## MỤC LỤC
1. [Tổng Quan Dự Án & Triết Lý Thiết Kế Cốt Lõi](#1-tổng-quan-dự-án--triết-lý-thiết-kế-cốt-lõi)
2. [Kiến Trúc Phần Mềm (4 Vòng Hexagonal)](#2-kiến-trúc-phần-mềm-4-vòng-hexagonal)
3. [Bộ Luật Thơ Thất Ngôn Tự Do & Hệ Thống Kiểm Định 7 Tầng](#3-bộ-luật-thơ-thất-ngôn-tự-do--hệ-thống-kiểm-định-7-tầng)
4. [Bản Chất Toán Học & Cơ Chế Sáng Tác Thơ Đột Phá](#4-bản-chất-toán-học--cơ-chế-sáng-tác-thơ-đột-phá)
5. [Phân Tích Chi Tiết Cấu Trúc Toàn Bộ Mã Nguồn](#5-phân-tích-chi-tiết-cấu-trúc-toàn-bộ-mã-nguồn)
6. [Đánh Giá Hiện Trạng, Điểm Nghẽn & Nợ Kỹ Thuật](#6-đánh-giá-hiện-trạng-điểm-nghẽn--nợ-kỹ-thuật)
7. [Kế Hoạch Hành Động Cải Thiện Toàn Diện (Action Plan 4 Giai Đoạn)](#7-kế-hoạch-hành-động-cải-thiện-toàn-diện-action-plan-4-giai-đoạn)
8. [Tiêu Chí Nghiệm Thu (Definition of Done)](#8-tiêu-chí-nghiệm-thu-definition-of-done)

---

## 1. TỔNG QUAN DỰ ÁN & TRIẾT LÝ THIẾT KẾ CỐT LÕI

### 1.1. Bản chất hệ thống
**Poem_Generate** là một nền tảng **Enterprise AI Platform** chuyên sâu cho bài toán **sáng tác và kiểm định tự động thơ Thất Ngôn Tự Do Việt Nam**, đồng thời đóng vai trò trợ lý AI hội thoại đa năng với RAG (Retrieval-Augmented Generation), quản lý phiên bộ nhớ, bảo mật guardrails và cô lập multi-tenant bằng khóa API.

### 1.2. Bốn triết lý kỹ thuật bất biến
1. **Verification-First (Kiểm định là trên hết):** Mô hình sinh ngôn ngữ lớn (LLM) không bao giờ được tin cậy tuyệt đối. Mọi đầu ra bắt buộc phải đi qua bộ thẩm định ngữ âm/toán học tất định trước khi trả cho người dùng.
2. **Fail-Closed (Hỏng thì đóng, không trả ẩu):** Nếu mô hình không thể sửa bài đạt luật sau số vòng quy định, hệ thống trả về mã lỗi HTTP `422 Unprocessable Entity` kèm biên bản chẩn đoán chi tiết; **tuyệt đối không bao giờ trả ra một bài thơ sai luật**.
3. **Bộ kiểm phán, mô hình sửa (Không sửa hộ):** Không một dòng code nào trong hệ thống được can thiệp sửa văn bản thơ của tác giả hay mô hình. Sửa bằng code là làm sai lệch tác phẩm.
4. **Luật thơ đóng băng (`rule.py` FROZEN):** Bộ luật tại `src/application/rule.py` được ghim chặt bằng mã băm SHA-256 (`tests/architecture/test_rule_dong_bang.py`), ngăn chặn mọi hành vi nới lỏng hoặc sửa đổi luật tùy tiện lúc runtime.

---

## 2. KIẾN TRÚC PHẦN MỀM (4 VÒNG HEXAGONAL)

Dự án tuân thủ nghiêm ngặt **Kiến trúc 4 vòng (Hexagonal Architecture / Clean Architecture)** theo quyết định kiến trúc [ADR-0001](adr/0001-kien-truc-4-vong.md):

```
entrypoints ──► bootstrap ──► adapters ──► application ──► domain
  (FastAPI,      (Dependency   (OpenAI, DB,   (Use cases,    (Thuần Python,
   Workers,       Injection,    Prometheus,    Pipelines,     không I/O,
   Next.js BFF)   đọc ENV)      pgvector)      Protocols)     Result/Error)
```

### 2.1. Phân tầng & Chiều phụ thuộc
- **Vòng 1 — Domain (`src/domain/`):** Lõi nghiệp vụ thuần túy, không có I/O, không import thư viện ngoài. Định nghĩa các kiểu `Result[T, E]`, cây lỗi `BotError`, chính sách bảo mật, guardrails đầu vào/đầu ra, cấu trúc thread và tenant.
- **Vòng 2 — Application (`src/application/`):** Chứa các Use Case, đường ống xử lý (Pipeline), luật thơ (`rule.py`), bộ lập kế hoạch (`planner.py`), và định nghĩa các giao diện trừu tượng (`typing.Protocol`) tại `ports/`.
- **Vòng 3 — Adapters (`src/adapters/`):** Hiện thực hóa các `ports/` bằng công nghệ cụ thể: gọi API (OpenAI, Gemini, Anthropic, vLLM), cơ sở dữ liệu (SQLite, PostgreSQL), kho lưu trữ vector, observability (Prometheus, OpenTelemetry).
- **Vòng 4 — Bootstrap (`src/bootstrap/`):** Nơi **duy nhất** được đọc biến môi trường (`settings.py`) và ráp toàn bộ phụ thuộc vào container (`container.py`).
- **Cửa vào — Entrypoints (`src/entrypoints/`):** Giao diện bên ngoài: HTTP REST API (FastAPI), Worker định kỳ, CLI.

### 2.2. Phân rã Port theo trách nhiệm ([ADR-0005](adr/0005-hai-port-llm-tach-theo-trach-nhiem.md))
Thay vì gom mọi thao tác gọi model vào một Interface cồng kềnh, hệ thống tách thành 4 port chuyên biệt:
- `LlmPort`: Hội thoại nhiều lượt, hỗ trợ gọi tool và trả về kiểu `Result[T, BotError]`.
- `EmbeddingPort`: Biến văn bản thành vector nhúng (chỉ phục vụ RAG và nạp tài liệu).
- `StreamingPort`: Bắn token theo luồng SSE thời gian thực cho chat.
- `OutputVerifier`: Cổng kiểm định đầu ra đồng bộ, tất định, không chạm I/O.

---

## 3. BỘ LUẬT THƠ THẤT NGÔN TỰ DO & HỆ THỐNG KIỂM ĐỊNH 7 TẦNG

Đặc tả chuẩn hóa tại [docs/Luat_Tho_That_Ngon_Tu_Do.md](Luat_Tho_That_Ngon_Tu_Do.md) và thực thi trong code tại [src/application/rule.py](../src/application/rule.py).

### 3.1. Các nhóm điều luật
- **Ràng buộc cứng (Hard Rules - H1 đến H4):** Vi phạm lập tức bị loại khỏi thể loại:
  - `H1`: Mỗi dòng có đúng 7 tiếng.
  - `H2`: Áp dụng cho mọi dòng, không có ngoại lệ.
  - `H3`: Có phân dòng rõ ràng, tối thiểu 4 dòng.
  - `H4`: Số dòng trong bài **bắt buộc phải là bội của 4** (tập hợp lệ: 4, 8, 12, 16, 20,...).
- **Điều loại bỏ (Forbidden - F1 đến F5):** Gỡ bỏ các ràng buộc niêm luật của Đường luật (không bắt buộc niêm, không bắt buộc đối, không bắt buộc độc vận, không hạn định số dòng).
- **Ràng buộc mềm (Soft Rules - S1 đến S21):** Định hình phong cách, nhạc tính, bố cục, vần và nhịp.

### 3.2. Bảy tầng kiểm tra tuần tự (Sequential Tiers)
Bài thơ phải qua tầng $N$ mới được xét tầng $N+1$. Nếu một tầng chặn bị trượt, hệ thống dừng ngay và các tầng sau mang trạng thái `da_chay=False`:

| Tầng | Tên Tầng | Điều luật | Cơ chế & Tiêu chí phán quyết | Loại tầng |
| :--- | :--- | :--- | :--- | :--- |
| **Tầng 1** | Hình thức & Số dòng | `H3, H4` | Kiểm tra văn bản $\ge 4$ dòng và số dòng chia hết cho 4. | **Chặn (Block)** |
| **Tầng 2** | Độ dài dòng | `H1, H2` | Đếm chính xác âm tiết tiếng Việt (xử lý từ ghép, gạch nối, đọc số học chuẩn miền Bắc). Mọi dòng phải đúng 7 tiếng. | **Chặn (Block)** |
| **Tầng 3** | Đối chiếu Đường luật | `F1 - F5` | Nhận diện xem bài viết có trùng với Đường luật không. | **Ghi nhận (Observe)** |
| **Tầng 4** | Thanh luật (Bằng/Trắc) | `S1, S2, S3` | Xét vị trí **P2, P4, P6** của từng dòng: bắt buộc phải theo **Khuôn Bằng (`B-T-B`)** hoặc **Khuôn Trắc (`T-B-T`)**. Cấm phá khuôn (QĐ-1, QĐ-2). Khổ 4 dòng đối chiếu **16 tổ hợp nhị phân**. | **Chặn (Block)** |
| **Tầng 5** | Hiệp vần | `S6, S9-S12` | Quét cửa sổ 4 dòng liên tiếp: **bắt buộc có ít nhất 1 cặp hiệp vần chân ở vị trí P7** (tra bảng vần thông chuẩn ngữ âm của học giả Trần Trọng Kim). | **Chặn (Block)** |
| **Tầng 6** | Nhịp điệu | `S13 - S15` | Xét 7 kiểu nhịp: `4/3, 3/4, 2/2/3, 2/5, 5/2, 1/6, 3/2/2`. Tìm giao tập hợp để xác định **nhịp chủ đạo** phủ toàn bài. | **Chặn (Block)** |
| **Tầng 7** | Khổ & Bố cục | `S16 - S21` | Xác định số khổ, độ dài khổ; cấm khổ rỗng. | **Chặn (Block)** |

### 3.3. Đánh giá chất lượng & Chống đạo văn
- **5 Chiều chất lượng tự động ([quality.py](../src/application/poetry/quality.py)):** Nhạc tính (`nhac_tinh`), Bám chủ đề (`bam_chu_de`), Đa dạng vần (`da_dang_van`), Dòng phân biệt (`dong_phan_biet`), Số dòng lặp.
- **2 Chiều thẩm mỹ ngữ nghĩa (`mach_lac`, `hinh_anh`):** Được chuyển sang module [reviewer.py](../src/application/poetry/reviewer.py) để mô hình LLM thứ hai chấm điểm tư vấn (không can thiệp vào cổng chặn).
- **Chặn trùng lặp nguyên văn (QĐ-P2):** Hệ thống lập chỉ mục bộ nhớ [chi_muc_dong.bin](../datalake/hf/chi_muc_dong.bin) chứa **547.181 dòng thơ 7 chữ** từ kho di sản và kho mẫu. Bất kỳ dòng nào bị LLM chép nguyên văn sẽ bị định danh số dòng và đánh trượt ngay lập tức.

---

## 4. BẢN CHẤT TOÁN HỌC & CƠ CHẾ SÁNG TÁC THƠ ĐỘT PHÁ

Nghiên cứu thực nghiệm tại [docs/Do_That_21-09_R2.md](Do_That_21-09_R2.md) và [docs/Plan_PoeTone.md](Plan_PoeTone.md) chỉ ra:

### 4.1. Lũy thừa tiêu diệt xác suất ($p^n$)
- Xác suất một dòng thơ thỏa mãn cả độ dài 7 tiếng và khuôn thanh Bằng/Trắc là $p \approx 0.30 - 0.56$.
- Khi sinh nguyên bài thơ $n$ dòng trong một lượt, xác suất thành công giảm theo lũy thừa:
  $P(\text{bài đạt}) \approx p^n$
  Đây là mô hình minh họa giả định các dòng độc lập và cùng xác suất; chưa bao quát vần, nhịp, chất lượng và tương quan giữa dòng. Không phải dự báo tỷ lệ đạt thực tế.
  - Bài 4 dòng: $0.56^4 \approx 10\%$
  - Bài 8 dòng: $0.56^8 \approx 1\%$
  - Bài 12 dòng: $0.56^{12} \approx 0.1\%$
  - Bài 20 dòng: $\approx 0\%$
- Một số thực nghiệm lịch sử chưa cho thấy lợi ích rõ từ model mạnh hơn. Không thể suy ra mọi model đều không cải thiện hoặc kết luận tokenizer là nguyên nhân duy nhất; phải đo lại theo model và prompt.

### 4.2. Giải pháp kiến trúc của hệ thống
1. **Sinh từng khổ độc lập (Stanza-wise Generation - [sinh_theo_kho.py](../src/application/poetry/sinh_theo_kho.py)):**
   Cố định $n=4$ (sinh từng khổ 4 dòng). Mỗi khổ sinh đồng thời `k` ứng viên ($k=32$, gọi song song theo lô):
   $$P(\text{khổ đạt}) = 1 - (1 - p^4)^k \approx 1 - (1 - 0.10)^{32} \approx 96.5\%$$
   Khổ sinh xong được nối tích lũy vào phần trước và kiểm tra tính hợp lệ toàn cục.
2. **ReAct Self-Correction Cứu khổ:**
   Nếu sinh 32 ứng viên mà chưa khổ nào đạt, hệ thống chọn ứng viên gần đích nhất theo `diem_tuan_thu` và cho LLM chạy 1 vòng ReAct với tool `kiem_tra_tho` để tự soi lỗi và sửa.
3. **One-Shot Learning (QĐ-P4):**
   Đưa 1 bài thơ mẫu chuẩn luật vào lời nhắc. Kết quả đo A/B thực tế: tỉ lệ dòng đủ 7 tiếng tăng từ $58.7\%$ lên **$98.7\%$**, đưa $p$ từ $22.5\%$ lên **$46.6\%$**.
4. **Vòng lặp sửa sai ngoài (Escalation Ladder - [verify_output.py](../src/application/pipeline/stages/verify_output.py)):**
   Đường lùi dự phòng nếu sinh từng khổ thất bại:
   $$\text{sua\_dong} \longrightarrow \text{sinh\_lai\_kho} \longrightarrow \text{sinh\_lai\_ca\_bai}$$

---

## 5. PHÂN TÍCH CHI TIẾT CẤU TRÚC TOÀN BỘ MÃ NGUỒN

```
Poem_Generate/
├── configs/               # Cấu hình đa môi trường (base.yaml, dev.yaml, models.yaml)
├── src/
│   ├── domain/            # Entities, Result/Error, Policies (HITL, API Key), Guardrails
│   ├── application/       # Use Cases (sinh_tho, pipeline), Rule Engine (rule.py), Ports
│   ├── adapters/          # LLM Adapters, SQL Dual-Dialect, Vector, Tools, Observability
│   ├── bootstrap/         # Settings (nơi duy nhất đọc ENV) & Container DI
│   ├── contracts/         # Schemas DTOs Pydantic dùng cho API & Network
│   └── entrypoints/       # FastAPI Routers, Worker tasks, CLI
├── frontend/              # Next.js 16 App Router, Tailwind v4, Zustand Store, BFF Proxy
├── evals/                 # Benchmark datasets (200 đề), đo đạc p, chi phí
├── datalake/              # Ngữ liệu 198k bài thơ HuggingFace, binary line index 547k dòng
└── tests/                 # 1.170+ Unit, Contract, Integration & Architecture tests
```

### Các tệp nguồn cốt lõi:
- [src/application/rule.py](../src/application/rule.py) (117 KB): Bộ phân tích ngữ âm học tiếng Việt, tra vần thông, kiểm tra thanh điệu, đếm âm tiết, phân tách khổ và chạy tuần tự 7 tầng.
- [src/application/poetry/sinh_tho.py](../src/application/poetry/sinh_tho.py): Đầu mối điều phối toàn bộ luồng sinh thơ: Cổng làm rõ B1 $\to$ Lập kế hoạch B2 $\to$ Sinh theo khổ $\to$ Thẩm định $\to$ Đặt tiêu đề $\to$ Tạo chỉ dẫn TTS.
- [src/application/pipeline/stages/verify_output.py](../src/application/pipeline/stages/verify_output.py): Vòng ngoài kiểm định với 7 chốt chặn bảo vệ (G1: Trần số lượt, G2: Timeout deadline, G3: Ngân sách ngày, G4: Hủy yêu cầu, G5: Không tiến bộ, G6: Lặp vòng, G7: Fail-closed).
- [src/entrypoints/api/routers/poem.py](../src/entrypoints/api/routers/poem.py): Endpoint `POST /v1/poem` xử lý 3 mã trạng thái: `200 + PoemResponse` (đạt kèm bằng chứng 7 tầng), `200 + CanLamRo` (thiếu dữ kiện $\to$ hỏi lại), `422 + PoemKhongDat` (hết lượt sửa $\to$ trả chẩn đoán, giấu bài sai).
- [src/entrypoints/api/middleware/auth.py](../src/entrypoints/api/middleware/auth.py): Xác thực API key và **suy ra Tenant trực tiếp từ khóa**, triệt tiêu nguy cơ giả mạo tenant (IDOR).
- [frontend/app/api/_backend.ts](../frontend/app/api/_backend.ts): Lớp BFF phía server bảo vệ API key tuyệt đối khỏi trình duyệt client.

---

## 6. ĐÁNH GIÁ HIỆN TRẠNG, ĐIỂM NGHẼN & NỢ KỸ THUẬT

### 6.1. Điểm mạnh vượt trội
- **Kỷ luật kiểm thử cực cao:** Có **1.179 test được thu thập trước triển khai: 1.170 passed, 9 skipped, trong 15,27 giây ở máy đo**, bảo vệ toàn bộ ranh giới module, không phụ thuộc mạng.
- **Toán học hóa AI:** Giải quyết thành công bài toán $p^n$ bằng sinh theo khổ kết hợp ReAct tự soi.
- **Fail-Closed tuyệt đối:** Không bao giờ để lọt bài thơ rác hoặc sai thể loại ra ngoài.

### 6.2. Các điểm nghẽn & Nợ kỹ thuật cần xử lý
1. **Nút thắt bài dài (16–20 câu):** Baseline lịch sử `baseline_775b225.jsonl` (gpt-4o-mini, zero-shot) đạt 15% cho 16 dòng và 7,5% cho 20 dòng, phần lớn chết ở Tầng 4 (Thanh luật).
2. **Chi phí và thời gian gọi LLM cao:** Trung bình tốn $21.8$ lượt gọi model, $26$ giây/bài, chi phí lịch sử 14,81 USD/1.000 bài, chưa tính lượt `cheap` do tham số $k=32$ ứng viên mỗi khổ.
3. **Nguy cơ Timeout HTTP 504:** Endpoint `/v1/poem` cũ vẫn chạy đồng bộ để tương thích. Luồng UI mới dùng `/v1/poem/jobs`, worker SQL độc lập và SSE trạng thái; cần SQL chung để phục hồi cả lịch sử.
4. **Tầng 6 (Nhịp) rỗng nghĩa:** Chưa có bộ tách từ tiếng Việt nên mọi dòng 7 tiếng đều cắt được theo số học $\to$ Tầng 6 chặn $0/24.366$ bài (luôn đạt nhưng chưa có giá trị ngữ nghĩa).
5. **Cấu hình Model Google Gemini chưa đồng bộ:** Tên `gemini-3.5-flash-lite` đã được xác minh qua tài liệu Google. Catalog đã sửa giá Standard paid-tier input/output/cached input thành 0,30/2,50/0,03 USD mỗi triệu token. Kiểm tra bằng key cục bộ ngày 06/10 trả HTTP 400 với lỗi key/quyền dịch vụ; benchmark thật đang bị chặn. Giá ước tính không thay thế hóa đơn hoặc xác nhận quota.
6. **Nợ kiến trúc Bước 4:** [src/domain/llm/token.py](../src/domain/llm/token.py) đã chuyển sang Protocol thuần Python; whitelist đã được gỡ và import-linter vẫn giữ đủ hợp đồng.
7. **Frontend Web UI:** Trước triển khai, thanh tiến trình dùng timer giả lập và Next.js BFF lọc tiêu đề trên 200 bản tải từ backend (không phải trình duyệt lọc). Hiện UI theo job/SSE/polling; tìm kiếm và cursor đã xuống repository, lọc tenant trước giới hạn.

---

## 7. KẾ HOẠCH HÀNH ĐỘNG CẢI THIỆN TOÀN DIỆN (ACTION PLAN 4 GIAI ĐOẠN)

Phần dưới giữ định hướng đề xuất ban đầu; thứ tự thực thi và trạng thái hiện tại xem [Plan_Improve_06_10.md](Plan_Improve_06_10.md). Các nghiên cứu không được coi là đã nghiệm thu.

### GIAI ĐOẠN 1: ỔN ĐỊNH HẠ TẦNG, CHỐNG TIMEOUT & DỌN NỢ KIẾN TRÚC (Ưu tiên cao nhất)

#### 1.1. Chuẩn hóa Model Google Gemini & Bảng giá
- **Công việc:** Giữ model được người vận hành chọn nếu có availability hợp lệ; kiểm tra API, quota và đơn giá chuẩn vào [configs/models.yaml](../configs/models.yaml). Cập nhật điều tiết rate-limit cho key Free Tier.
- **Tệp sửa:** `configs/models.yaml`, `src/bootstrap/model_validation.py`, `src/adapters/llm/google.py`. Không tự đổi `.env` hoặc khóa của người dùng.

#### 1.2. Thêm luồng SSE Streaming cho `/v1/poem`
- **Cập nhật thực thi:** Dùng `POST /v1/poem/jobs` trả 202 và `GET /v1/poem/jobs/{id}/events`. Worker và SQL giữ tác vụ sống; SSE chỉ phát trạng thái:
  - `event: progress` (`{"kho": 1, "tong_kho": 4, "ung_vien": 8, "trang_thai": "sinh_ung_vien"}`)
  - `event: progress` (`{"trang_thai": "tu_soi_react", "msg": "Đang dùng ReAct tự sửa khổ 2..."}`)
  - `event: done` (Toàn bộ `PoemResponse` hoặc `PoemKhongDat`).
- **Tệp sửa:** `src/entrypoints/api/routers/poem.py`, `src/application/poetry/sinh_tho.py`.

#### 1.3. Cập nhật Web UI nhận tiến trình thật
- **Công việc:** Nối luồng SSE vào [frontend/app/api/_backend.ts](../frontend/app/api/_backend.ts) và cập nhật thanh tiến trình [PoemEvidence.tsx](../frontend/components/poem/PoemEvidence.tsx) hiển thị chính xác trạng thái thực.
- **Tệp sửa:** `frontend/components/poem/PoemEvidence.tsx`, `frontend/hooks/useChat.ts`.

#### 1.4. Hoàn thành Bước 4: Tách Contracts khỏi Domain
- **Công việc:** Thay thế `contracts.chat.Message` trong `src/domain/llm/token.py` bằng Protocol thuần túy; gỡ whitelist trong [.importlinter](../.importlinter); giữ các script đối chiếu theo architecture test, không di chuyển chỉ vì chúng nằm ngoài `src`.
- **Tệp sửa:** `src/domain/llm/token.py`, `.importlinter`.

---

### GIAI ĐOẠN 2: ĐỘT PHÁ TẦNG 4 & NÂNG TỈ LỆ ĐẠT BÀI DÀI (Kỹ thuật cốt lõi)

#### 2.1. Khung cấp dòng (Line-level Framing - GĐ2.2 Plan PoeTone)
- **Công việc:** Khi lập kế hoạch khổ thơ (`planner.py`), định hướng mục tiêu khuôn thanh từng dòng cụ thể vào lời nhắc (ví dụ: `Dòng 1: [B-T-B]`, `Dòng 2: [T-B-T]`), giúp LLM tập trung từ ngữ ngay từ đầu.
- **Tệp sửa:** `src/application/poetry/prompt.py`, `src/application/poetry/sinh_theo_kho.py`, `src/application/prompting/system.py`.

#### 2.2. Kho thi liệu gợi ý vần theo chủ đề (Rhyme Bank - GĐ2.3)
- **Công việc:** Trích xuất các cụm vần chuẩn từ kho thơ mẫu và gợi ý tham khảo 3–4 cặp từ hiệp vần theo chủ đề trong prompt, giúp LLM không bị bí từ dẫn đến bẻ gãy khuôn thanh.
- **Tệp sửa:** `src/application/poetry/fewshot.py`.

#### 2.3. Đo kiểm A/B trên 40 đề & 200 đề
- **Công việc:** Chạy lại `evals/do_that.py` trên tập 200 đề để đối soát tỉ lệ đạt luật trên bài 16–20 câu (mục tiêu nghiên cứu >50%; mốc lịch sử là 15%/7,5% cho 16/20 dòng, chưa phải baseline hiện tại).

---

### GIAI ĐOẠN 3: HOÀN THIỆN NGÔN NGỮ HỌC & TÍNH NĂNG WEB (Trải nghiệm)

#### 3.1. Tách từ tiếng Việt cho Tầng 6 (Nhịp)
- **Công việc:** Tích hợp bộ tách từ nhẹ (`underthesea` hoặc FST tokenizer) vào cổng kiểm định bổ trợ [verifier.py](../src/application/poetry/verifier.py) (giữ nguyên `rule.py` đóng băng) để quan sát ranh giới từ thật ở chế độ shadow. Chỉ đề xuất cổng chặn sau khi có nhãn thủ công và đo false-positive/false-negative.

#### 3.2. Tìm kiếm hội thoại phía Server & Quản lý User
- **Công việc:** Bổ sung tham số tìm kiếm `?q=...` vào `GET /v1/conversations` (SQLite LIKE hoặc FTS5); cập nhật Sidebar gọi API tìm kiếm; bổ sung modal Cài đặt (Settings) trên giao diện Web.
- **Tệp sửa:** `src/entrypoints/api/routers/conversations.py`, `frontend/components/sidebar/Sidebar.tsx`.

---

### GIAI ĐOẠN 4: TỐI ƯU CHI PHÍ DÀI HẠN (FINE-TUNING / LoRA)

#### 4.1. Xây dựng Dataset SFT / DPO
- **Nguồn dữ liệu:** $24.366$ bài thơ đạt 7 tầng tại `datalake/analysis/bai_dat.jsonl` và các bài trượt tại `bai_truot.jsonl`.
- **Công việc:** Đóng gói cặp dữ liệu Prompt $\to$ Poem đạt chuẩn (SFT) và cặp Chosen/Rejected đối chiếu lỗi thanh điệu P2/P4/P6 (DPO).

#### 4.2. Huấn luyện LoRA trên mô hình nền
- **Công việc:** Fine-tune LoRA trên mô hình mã nguồn mở cỡ nhỏ (Qwen 2.5 7B hoặc Gemma 2 9B). Giả thuyết nghiên cứu: có thể giảm số ứng viên, chi phí và thời gian. Các mục tiêu 1–2 ứng viên, giảm 80% và dưới 5 giây chưa được chứng minh; chỉ bắt đầu sau baseline/A-B, kiểm quyền dữ liệu và chia tập tránh rò rỉ.

---

## 8. TIÊU CHÍ NGHIỆM THU (DEFINITION OF DONE)

Mọi thay đổi khi tiến hành bắt buộc phải thỏa mãn:
1. `make arch` (hoặc `PYTHONPATH=src lint-imports`): 100% hợp đồng ranh giới 4 vòng phải xanh (`KEPT`).
2. `tests/architecture/test_rule_dong_bang.py`: SHA-256 của `rule.py` không bị thay đổi một byte nào.
3. `pytest tests/unit tests/contract`: Toàn bộ 1.170+ test tự động phải PASS, chạy hoàn toàn offline không chạm mạng.
4. Mọi thử nghiệm cải tiến prompt bắt buộc đo A/B chứng minh hiệu quả và không làm giảm tỉ lệ đạt luật hiện tại.


## 9. Cập nhật thực thi ngày 06/10/2026

Đã triển khai nền tảng job, CLI/validation, runner baseline và tìm kiếm repository. Các nhánh adaptive và line-framing chỉ là thử nghiệm, mặc định tắt. `rule.py` không đổi. Xem [hướng dẫn vận hành](Runbook_Improve_06_10.md) và [ADR-0006](adr/0006-durable-poem-jobs.md).

Số 20% đạt, 26 giây và 14,81 USD/1.000 bài là **lịch sử zero-shot**, không phải kết quả đo pipeline one-shot hiện tại. [Tổng hợp lịch sử](../evals/ket_qua/improve_06_10_historical.summary.md) tách khỏi manifest chuẩn bị 40/200; chưa sinh kết quả benchmark giả.

Nguồn xác minh model/giá: [model Google](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), [bảng giá Google](https://ai.google.dev/gemini-api/docs/pricing). Kiểm tra metadata không bảo đảm quota hoặc chất lượng sinh; cần lượt sinh smoke/A-B bằng key hợp lệ.
