# KẾ HOẠCH CẢI THIỆN DỰ ÁN POEM_GENERATE

**Ngày lập:** 06/10/2026

**Phạm vi:** Backend Python, frontend Next.js, pipeline sinh thơ, kiểm định, dữ liệu đánh giá và tài liệu dự án.

**Mục tiêu:** Tăng độ ổn định và tỷ lệ sinh thơ đạt luật, đồng thời giảm độ trễ và chi phí vận hành mà không thay đổi bộ luật đã đóng băng tại `src/application/rule.py`.

---

## 1. Kết luận điều hành

Dự án đã có nền tảng tốt: kiến trúc phân lớp rõ, bộ luật tất định, cơ chế fail-closed, cô lập tenant, tập test lớn và dữ liệu đánh giá thực tế. Điểm nghẽn hiện nay không nằm ở việc thiếu thêm một tầng kiến trúc AI, mà nằm ở bốn vấn đề cụ thể:

1. Đường sinh thơ là tác vụ dài nhưng vẫn chạy trong một HTTP request đồng bộ.
2. Chiến lược sinh mặc định `k=32` tạo chi phí lớn cho cả yêu cầu dễ lẫn khó.
3. Một số số liệu, cấu hình và hợp đồng kiến trúc chưa đồng bộ với trạng thái source hiện tại.
4. Các hướng cải tiến chất lượng chưa có một quy trình A/B thống nhất để chứng minh hiệu quả.

Ba ưu tiên cao nhất là:

- Chuyển sinh thơ sang mô hình job nền, có tiến trình thật và khả năng phục hồi.
- Chốt một baseline đánh giá có thể tái lập trên 200 đề.
- Thay `k=32` cố định bằng chiến lược sinh thích nghi và dừng sớm.

Fine-tuning/LoRA chỉ được xem xét sau khi hoàn tất các tối ưu trên và xác nhận dữ liệu huấn luyện đủ sạch.

---

## 2. Nguyên tắc bất biến

Mọi thay đổi trong kế hoạch phải tuân thủ các nguyên tắc sau:

1. **Không sửa `src/application/rule.py`.** Hash SHA-256 đã chốt phải được giữ nguyên.
2. **Fail-closed.** Không trả bài thơ sai luật hoặc bản nháp chưa kiểm định cho người dùng.
3. **Bộ kiểm phán, mô hình sửa.** Code kiểm định không tự sửa câu thơ.
4. **Không tối ưu bằng cảm giác.** Thay đổi prompt, model hoặc chiến lược sinh phải có A/B test.
5. **Đo theo bài hoàn chỉnh.** Không dùng tỷ lệ đúng từng dòng thay thế cho tỷ lệ bài đạt.
6. **Cô lập tenant xuyên suốt.** Job, hội thoại, hạn mức và dữ liệu đều phải mang tenant scope.
7. **Không để dữ liệu bí mật vào Git.** `.env` chỉ dùng cục bộ; tài liệu không ghi khóa hoặc DSN thật.
8. **Không biến đánh giá ngữ nghĩa không ổn định thành cổng chặn cứng** khi chưa đo được sai số.

---

## 3. Baseline hiện tại

Các số liệu dưới đây là mốc tham chiếu trước triển khai. Kết quả 200 đề thuộc lần đo lịch sử `baseline_775b225.jsonl`, gpt-4o-mini, zero-shot; không phải tỷ lệ đạt của pipeline one-shot hiện tại:

| Chỉ số | Giá trị hiện tại |
|---|---:|
| Test được thu thập | 1.179 |
| Kết quả chạy toàn bộ test | 1.170 passed, 9 skipped |
| Thời gian chạy test quan sát được | 15,27 giây |
| Tập đánh giá chính | 200 đề |
| Tỷ lệ đạt toàn bài trên baseline | 20,0% |
| Tỷ lệ kiệt lượt sửa | 80,0% |
| Thời gian trung bình | 26,0 giây/bài |
| Lượt gọi `reply` trung bình | 21,8 lượt/bài |
| Chi phí đã đo | 14,81 USD/1.000 bài, chưa tính lượt `cheap` |
| Số ứng viên mặc định mỗi khổ | 32 |
| Corpus đạt bảy tầng | 24.366 bài |
| Tầng nhịp trên corpus hiện tại | 0/24.366 bài bị chặn |

Baseline phải được đóng gói thành một báo cáo máy đọc được, có commit, provider, model, cấu hình, thời gian chạy và raw result đi kèm. Không so sánh kết quả giữa hai lần chạy nếu khác tập đề hoặc khác cách tính.

---

## 4. Chỉ số thành công

### 4.1. Chỉ số vận hành

- P50 và P95 thời gian hoàn thành job.
- Tỷ lệ request tạo job thành công.
- Tỷ lệ job hoàn thành, thất bại, hết hạn và bị hủy.
- Tỷ lệ lỗi 429, timeout và lỗi provider.
- Số lượt gọi model trung bình trên mỗi bài.
- Token vào/ra và chi phí trên mỗi bài.
- **Chi phí trên một bài đạt:** `tổng chi phí / số bài thực sự đạt`.

### 4.2. Chỉ số chất lượng

- Tỷ lệ bài đạt luật tổng thể.
- Tỷ lệ đạt theo độ dài 4, 8, 12, 16 và 20 dòng.
- Tỷ lệ bài chết tại từng tầng.
- Tỷ lệ đạt ngay lượt đầu và sau sửa.
- Số lượt sửa trung bình của bài đạt.
- Tỷ lệ trùng dòng với corpus.
- Điểm tư vấn về mạch lạc và hình ảnh; không dùng làm cổng chặn cứng.

### 4.3. Mục tiêu sau hai giai đoạn đầu

- Không còn phụ thuộc vào kết nối HTTP dài để giữ tác vụ sinh thơ sống.
- Có thể tải lại trang và tiếp tục theo dõi job.
- P95 API tạo job dưới 1 giây, không tính thời gian worker xử lý.
- Giảm ít nhất 25% lượt gọi model trung bình mà không làm giảm tỷ lệ đạt baseline.
- Không tăng tỷ lệ bài sai lọt qua cổng; mục tiêu bắt buộc vẫn là 0.

---

## 5. Lộ trình thực hiện

## Giai đoạn 0 — Đồng bộ sự thật của dự án

**Ưu tiên:** P0

**Mục đích:** Loại bỏ sai lệch giữa code, cấu hình, tài liệu và phép đo trước khi phát triển thêm.

### 0.1. Sửa tài liệu và số liệu

- Đổi số liệu Tầng 6 từ mốc lịch sử `0/16.391` sang số hiện tại `0/24.366`; nếu giữ số cũ phải ghi rõ đó là mốc lịch sử.
- Ghi chi phí baseline đúng là 14,81 USD/1.000 bài, chưa tính lượt `cheap`.
- Phân biệt rõ 1.179 test được thu thập với 1.170 test passed và 9 skipped.
- Thay link `file:///c:/...` bằng link tương đối trong Markdown.
- Đánh dấu các dự báo như “giảm 80% chi phí” hoặc “dưới 5 giây” là mục tiêu thử nghiệm, không phải kết quả đã chứng minh.

### 0.2. Chuẩn hóa model

- Xác minh model mặc định thực sự tồn tại trong API của provider.
- Xác minh giá input, output, cached input và token suy luận.
- Bổ sung smoke test model trước khi dùng cho eval hoặc production.
- Khi khởi động, cấu hình model không hợp lệ phải báo lỗi rõ ràng thay vì chờ tới lượt gọi đầu tiên.
- Không hard-code một model thay thế trong kế hoạch; lựa chọn phải dựa trên availability, quota, giá và benchmark.

### 0.3. Sửa entry point CLI

`pyproject.toml` hiện khai báo `entrypoints.cli.main:main`, trong khi module tương ứng chưa tồn tại. Chọn một trong hai cách:

- Tạo CLI tối thiểu có lệnh health/eval phù hợp; hoặc
- Xóa project script nếu dự án không còn hỗ trợ CLI.

### 0.4. Đóng gói baseline

- Tạo một lệnh duy nhất để chạy baseline 40 đề và 200 đề.
- Ghi kết quả JSONL và bản tổng hợp JSON/Markdown.
- Ghi commit SHA, provider, model, seed nếu có, số ứng viên, số vòng sửa và concurrency.
- Không ghi API key hoặc dữ liệu bí mật vào artifact.

### Nghiệm thu Giai đoạn 0

- Tài liệu không còn link tuyệt đối theo máy cá nhân.
- Model mặc định vượt qua smoke test hoặc hệ thống fail sớm với lỗi cấu hình rõ ràng.
- Project script CLI không còn trỏ tới module thiếu.
- Baseline 40/200 đề chạy bằng lệnh được tài liệu hóa và tạo artifact có thể đối chiếu.

---

## Giai đoạn 1 — Tách tác vụ sinh thơ khỏi HTTP request

**Ưu tiên:** P0

**Mục đích:** Chống timeout, cho phép tải lại trang, hủy tác vụ và hiển thị tiến trình thật.

### 1.1. Kiến trúc đề xuất

```text
POST /v1/poem/jobs
        │
        ├── kiểm tra input, auth, quota
        ├── tạo job theo tenant
        └── trả 202 + job_id
                    │
                    ▼
              Worker xử lý
                    │
          planning / generating
          verifying / repairing
                    │
                    ▼
GET /v1/poem/jobs/{job_id}
GET /v1/poem/jobs/{job_id}/events  (SSE)
DELETE /v1/poem/jobs/{job_id}      (hủy)
```

SSE chỉ là kênh truyền trạng thái. Worker và trạng thái bền vững mới là phần giải quyết timeout thực sự.

### 1.2. Trạng thái job

Tập trạng thái tối thiểu:

```text
queued
planning
generating
verifying
repairing
completed
failed
cancelled
expired
```

Mỗi job cần lưu:

- `job_id`, `tenant_id`, `conversation_id`.
- Thời điểm tạo, bắt đầu, cập nhật và kết thúc.
- Trạng thái hiện tại và tiến trình theo khổ.
- Provider/model và cấu hình sinh quan trọng.
- Kết quả cuối hoặc lỗi đã chuẩn hóa.
- Cờ hủy và deadline tổng.

Không lưu hoặc phát bản nháp sai luật ra client. Event tiến trình chỉ chứa metadata an toàn.

### 1.3. An toàn và độ bền

- Tenant được lấy từ API key, không lấy từ body.
- `Idempotency-Key` ngăn tạo job trùng khi client retry.
- Giới hạn job đồng thời và ngân sách theo tenant.
- Worker phải kiểm tra cờ hủy giữa các khổ và giữa các lượt sửa.
- Job được cập nhật heartbeat để phát hiện worker chết.
- Có TTL cho job đã hoàn thành và job bị bỏ quên.
- Retry chỉ áp dụng với lỗi tạm thời; không retry lỗi luật hoặc input.

### 1.4. Frontend

- Thay tiến trình `setInterval` ước lượng bằng trạng thái thật từ SSE.
- Khi mất SSE, chuyển sang polling có backoff.
- Lưu `job_id` theo conversation để tải lại trang vẫn theo dõi được.
- Cho phép hủy job.
- Phân biệt rõ trạng thái “không đạt luật” với lỗi hạ tầng.

### Nghiệm thu Giai đoạn 1

- `POST /v1/poem/jobs` trả nhanh với `202` và `job_id`.
- Tải lại trình duyệt không làm mất job.
- Mất kết nối SSE không làm hủy tác vụ.
- Client không nhận nội dung bản nháp chưa đạt.
- Test bao phủ auth, tenant isolation, idempotency, cancel, timeout và worker recovery.

---

## Giai đoạn 2 — Dọn nợ kiến trúc và hoàn thiện chức năng nền

**Ưu tiên:** P1

### 2.1. Tách Contracts khỏi Domain

- Thay `contracts.chat.Message` trong `domain/llm/token.py` bằng kiểu thuần Domain hoặc Protocol tối thiểu.
- Gỡ whitelist tương ứng trong `.importlinter`.
- Kiểm tra lại các Application Port đang phụ thuộc trực tiếp vào DTO mạng.
- Adapter chịu trách nhiệm chuyển đổi giữa DTO và kiểu nghiệp vụ.

### 2.2. Tìm kiếm hội thoại phía server

Frontend hiện đã gửi `?q=...`, nhưng backend chưa nhận và thực thi tham số này.

- Bổ sung `q` vào `GET /v1/conversations`.
- Lọc theo tenant và tiêu đề; cân nhắc cả nội dung tin nhắn ở giai đoạn sau.
- Thêm phân trang cursor thay cho giới hạn danh sách cố định.
- Escape ký tự đặc biệt của `LIKE`, hoặc dùng FTS5 khi dữ liệu đủ lớn.
- Thêm index phù hợp và test cô lập tenant.

### 2.3. Tài liệu kiến trúc

- Phân biệt “kiến trúc mục tiêu” và “ngoại lệ hiện hữu”.
- Cập nhật ADR khi thay đổi mô hình chạy từ request đồng bộ sang job nền.
- Không di chuyển các file đối chiếu chỉ vì chúng nằm ngoài `src`; architecture test hiện đang kiểm soát vai trò của chúng.

### Nghiệm thu Giai đoạn 2

- Domain không còn import `contracts`.
- Hợp đồng import-linter tương ứng được gỡ whitelist và vẫn `KEPT`.
- `GET /v1/conversations?q=...` lọc thật ở repository.
- Tìm kiếm và phân trang không làm lộ hội thoại giữa các tenant.

---

## Giai đoạn 3 — Giảm chi phí và tăng tỷ lệ đạt

**Ưu tiên:** P1

**Nguyên tắc:** Mỗi thay đổi chạy 40 đề trước; chỉ chạy đủ 200 đề khi có tín hiệu tốt.

### 3.1. Sinh thích nghi thay cho `k=32` cố định

Chiến lược đề xuất:

```text
k=8
 ├── có khổ đạt       → dừng ngay
 ├── có ứng viên gần  → sửa ứng viên tốt nhất
 └── còn quá xa       → tăng lên k=16
                         ├── đạt → dừng
                         └── chưa đạt → k=32 hoặc fail theo ngân sách
```

Điểm cần thực hiện:

- Sinh theo batch nhỏ để có thể dừng sớm.
- Không sinh lại ứng viên đã có khi tăng từ 8 lên 16/32.
- Dùng `diem_tuan_thu` để chọn ứng viên gần đích.
- Đặt ngân sách token/lượt gọi cho từng job.
- Có giới hạn riêng cho bài 4, 8, 12, 16 và 20 dòng.

### 3.2. Khung thanh cấp dòng

- Đưa mục tiêu `B-T-B` hoặc `T-B-T` của từng dòng vào prompt sinh khổ.
- Dùng chung ở luồng sinh mới, `sinh_lai_kho` và `sinh_lai_ca_bai`.
- Không đưa bảng quá dài làm tăng token không cần thiết.
- A/B test với cùng model, tập đề và ngân sách.

### 3.3. Rhyme Bank theo chủ đề

- Trích các nhóm vần từ kho đã kiểm định.
- Rerank theo chủ đề và ngữ cảnh khổ trước.
- Chỉ đưa một số gợi ý nhỏ vào prompt, không ép model sao chép câu nguồn.
- Mọi dòng sinh ra vẫn phải qua chỉ mục chống chép.
- Ghi ID nguồn gợi ý vào evidence phục vụ truy vết.

### 3.4. Cache và tái sử dụng

- Cache kết quả phân tích yêu cầu khi nội dung không đổi.
- Cache phần system prompt bất biến nếu provider hỗ trợ.
- Không gọi lại reviewer/title/TTS khi bài chưa qua luật.
- Không chạy lại các bước đã có kết quả hợp lệ sau một sửa đổi cục bộ nếu hợp đồng cho phép.

### 3.5. Ma trận A/B bắt buộc

Mỗi thử nghiệm phải báo cáo:

| Chỉ số | Control | Treatment | Chênh lệch |
|---|---:|---:|---:|
| Tỷ lệ đạt toàn bài | | | |
| Tỷ lệ đạt 16–20 dòng | | | |
| Lượt gọi trung bình | | | |
| Token trung bình | | | |
| Chi phí/1.000 bài | | | |
| Chi phí trên một bài đạt | | | |
| P50/P95 thời gian | | | |
| Tỷ lệ 429/timeout | | | |

Không nhận thay đổi nếu tỷ lệ đạt tăng nhưng chi phí trên một bài đạt xấu đi quá mức chưa được chấp thuận.

### Nghiệm thu Giai đoạn 3

- Giảm ít nhất 25% lượt gọi trung bình so với baseline, không giảm tỷ lệ đạt.
- Hoặc tăng tỷ lệ đạt có ý nghĩa với chi phí trên một bài đạt tốt hơn baseline.
- Kết quả có raw artifact, commit và cấu hình tái lập được.
- Không thay đổi hash `rule.py`.

---

## Giai đoạn 4 — Hoàn thiện đánh giá nhịp và chất lượng ngôn ngữ

**Ưu tiên:** P2

### 4.1. Tầng nhịp chạy ở chế độ quan sát

Tầng 6 không loại bài nào trong corpus đã đo (0/24.366). Đây là dấu hiệu cần khảo sát sức phân biệt; chưa đủ để kết luận mọi văn bản đều qua hoặc tokenizer là nguyên nhân duy nhất. Không đưa tokenizer mới thành cổng chặn ngay.

Lộ trình:

1. So sánh `underthesea`, một FST/tokenizer nhẹ và cách khai báo nhịp từ planner.
2. Chạy trên 24.366 bài ở chế độ shadow/observe.
3. Lấy mẫu bài bị đánh dấu và đánh giá thủ công.
4. Đo false-positive, false-negative và độ ổn định giữa các phiên bản.
5. Chỉ đề xuất thành cổng chặn sau khi có ngưỡng nghiệm thu được phê duyệt.

Nếu phải bổ sung tầng kiểm định ngoài `rule.py`, tầng đó phải có evidence riêng và không được giả danh là kết quả từ bộ luật đóng băng.

### 4.2. Reviewer ngữ nghĩa

- Giữ `mach_lac` và `hinh_anh` ở vai trò tư vấn/HITL.
- Ghi model, phiên bản prompt và độ tin cậy.
- Không dùng một lần chấm LLM để loại bài tự động.
- Xây tập mẫu có người chấm trước khi so sánh reviewer hoặc model.

### Nghiệm thu Giai đoạn 4

- Có báo cáo sai số của tokenizer/nhịp trên tập được gắn nhãn.
- Không có thay đổi âm thầm làm 24.366 bài corpus đổi phán quyết.
- Reviewer không trở thành cổng chặn cứng nếu chưa có đánh giá với người chấm.

---

## Giai đoạn 5 — Chuẩn bị Fine-tuning/LoRA

**Ưu tiên:** P3

**Điều kiện bắt đầu:** Giai đoạn 0–3 hoàn thành và tối ưu prompt/rerank đã chạm trần.

### 5.1. Làm sạch dữ liệu

Tập 24.366 bài đạt luật không mặc nhiên là tập SFT tốt. Cần:

- Khử trùng lặp cấp bài, khổ và dòng.
- Loại bài đạt luật nhưng chất lượng ngôn ngữ thấp.
- Kiểm tra quyền sử dụng và lưu nguồn dữ liệu.
- Gắn metadata: chủ đề, cảm xúc, độ dài, vần, khuôn thanh và nguồn.
- Chia train/validation/test theo tác giả hoặc nguồn để tránh rò rỉ.
- Giữ một test set bất biến, không dùng trong chọn dữ liệu hay tinh chỉnh prompt.

### 5.2. Thiết kế tập huấn luyện

- **SFT:** yêu cầu có cấu trúc → bài đạt luật và có chất lượng.
- **DPO:** cùng yêu cầu, `chosen` là bài tốt hơn và `rejected` chứa lỗi được chẩn đoán rõ.
- Không tạo cặp DPO chỉ bằng cách gắn nhãn mọi bài trượt là xấu; lỗi phải cùng loại và đủ gần để mô hình học được khác biệt.
- Cân bằng theo độ dài, đặc biệt không để bài 4 dòng lấn át bài 16–20 dòng.

### 5.3. Cổng quyết định fine-tuning

Chỉ tiếp tục nếu thử nghiệm nhỏ chứng minh:

- Tỷ lệ đạt cao hơn model gốc trên test set bất biến.
- Chi phí trên bài đạt giảm.
- Không tăng sao chép corpus.
- Không làm giảm chất lượng chủ đề và mạch lạc.
- Tổng chi phí huấn luyện, phục vụ và vận hành hợp lý hơn giải pháp API hiện tại.

Các mục tiêu “giảm 80% chi phí” và “dưới 5 giây” là mục tiêu nghiên cứu, không phải Definition of Done mặc định.

---

## 6. Thứ tự backlog đề xuất

| ID | Công việc | Ưu tiên | Phụ thuộc |
|---|---|---|---|
| IMP-001 | Sửa số liệu và link trong báo cáo | P0 | Không |
| IMP-002 | Xác minh model, giá và thêm startup validation | P0 | Không |
| IMP-003 | Sửa hoặc bỏ CLI entry point bị thiếu | P0 | Không |
| IMP-004 | Chuẩn hóa runner baseline 40/200 đề | P0 | Không |
| IMP-005 | Thiết kế schema và API poem job | P0 | IMP-004 |
| IMP-006 | Worker, trạng thái bền vững, cancel và deadline | P0 | IMP-005 |
| IMP-007 | SSE tiến trình thật và polling fallback | P0 | IMP-006 |
| IMP-008 | Frontend theo dõi/phục hồi job | P0 | IMP-007 |
| IMP-009 | Tách `contracts` khỏi Domain | P1 | Không |
| IMP-010 | Tìm kiếm hội thoại server-side và cursor | P1 | Không |
| IMP-011 | Sinh thích nghi k=8→16→32 | P1 | IMP-004 |
| IMP-012 | A/B khung thanh cấp dòng | P1 | IMP-004 |
| IMP-013 | Rhyme Bank có truy vết nguồn | P1 | IMP-004 |
| IMP-014 | Shadow evaluation cho nhịp | P2 | IMP-004 |
| IMP-015 | Chuẩn bị dataset SFT/DPO | P3 | IMP-011–014 |
| IMP-016 | Thử nghiệm LoRA nhỏ | P3 | IMP-015 |

---

## 7. Rủi ro và biện pháp kiểm soát

| Rủi ro | Tác động | Kiểm soát |
|---|---|---|
| SSE bị hiểu nhầm là giải pháp timeout | Job vẫn chết khi request mất | Tách worker và trạng thái job trước, SSE chỉ truyền event |
| Job bị chạy trùng | Tốn chi phí và lưu hai kết quả | Idempotency key và unique constraint theo tenant |
| Adaptive `k` làm giảm tỷ lệ đạt | Chất lượng đi xuống | A/B theo độ dài, giữ ngân sách fallback tới 32 |
| Rhyme Bank làm tăng sao chép | Vi phạm tính nguyên bản | Chỉ gợi ý từ/vần, giữ cổng chống chép và evidence nguồn |
| Tokenizer nhịp đánh sai | Loại nhầm bài | Chạy observe-only trước, đo với người chấm |
| Eval bị nhiễu bởi 429/provider | So sánh sai | Ghi retry, concurrency, model và loại run không hợp lệ |
| Fine-tune học dữ liệu kém | Đạt luật nhưng thơ dở | Curate thủ công, test set bất biến, đo ngữ nghĩa riêng |
| Tài liệu lệch code trở lại | Quyết định sai | Kiểm tra số liệu tài liệu bằng script trong CI khi khả thi |

---

## 8. Definition of Done chung

Mọi thay đổi được xem là hoàn thành khi:

1. `python -m pytest` chạy xanh; test cần hạ tầng chỉ được skip với lý do rõ ràng.
2. `tests/architecture/test_rule_dong_bang.py` xác nhận hash `rule.py` không đổi.
3. Hợp đồng import-linter vẫn `KEPT`.
4. `npm run typecheck` chạy xanh cho frontend.
5. Thay đổi API có contract test và cập nhật OpenAPI/types frontend.
6. Thay đổi prompt/model/chiến lược sinh có A/B artifact tái lập được.
7. Không có khóa, DSN hoặc dữ liệu nhạy cảm trong commit và log.
8. Không trả bản nháp chưa đạt qua REST, SSE, log người dùng hoặc lịch sử hội thoại.
9. Tài liệu mô tả đúng trạng thái đã triển khai, phân biệt rõ phần “đã có”, “đang làm” và “đề xuất”.

---

## 9. Quyết định đề xuất

Trong chu kỳ triển khai tiếp theo, chỉ nên cam kết ba epic:

1. **Baseline và cấu hình đáng tin cậy.**
2. **Poem Job + tiến trình thật + phục hồi tác vụ.**
3. **Sinh thích nghi để giảm chi phí trên mỗi bài đạt.**

Tách từ tiếng Việt, Rhyme Bank nâng cao và fine-tuning tiếp tục ở nhánh nghiên cứu cho tới khi ba epic trên hoàn thành. Cách sắp xếp này xử lý trước rủi ro vận hành, tạo thước đo đáng tin cậy, rồi mới tối ưu chất lượng bằng dữ liệu thực.

---

## 10. Nhật ký thực thi — 06/10/2026

Đã thực thi phần nền tảng và chuẩn bị nhánh thử nghiệm; **chưa hoàn thành toàn bộ plan**. Việc chạy baseline thật và bật tối ưu mặc định đang chờ API key hợp lệ. Không thay `.env`, không chạy huấn luyện và không triển khai production.

| ID | Trạng thái | Bằng chứng / phần còn thiếu |
|---|---|---|
| IMP-001 | Đã cập nhật | Báo cáo sửa link, số liệu lịch sử và các khẳng định chưa được chứng minh. |
| IMP-002 | Đã triển khai; live bị chặn | Catalog giá Google, validation khởi động, CLI `model-check`. Key hiện tại bị provider từ chối HTTP 400; chưa xác nhận quota/generate smoke. |
| IMP-003 | Đã triển khai | CLI có `config-check`, `model-check`, `worker`; dùng chung composition root. |
| IMP-004 | Runner đã kiểm thử; baseline mới chưa có | `evals/baseline.py`: prepare 40/200, JSONL/JSON/Markdown, manifest, chi phí bài đạt, P50/P95, retry và so sánh cùng cấu hình. |
| IMP-005 | Đã triển khai | Schema/migration, API 202, idempotency theo tenant, conflict 409, giới hạn active job. |
| IMP-006 | Đã triển khai và kiểm thử SQLite | Worker độc lập, lease + owner fencing, heartbeat, cancel, deadline, TTL, trần gọi model và quota tenant. SQL completion/history cùng transaction. PostgreSQL production và load test còn cần kiểm tra. |
| IMP-007 | Đã triển khai | SSE chỉ metadata/kết quả cuối, polling backoff khi mất SSE; không phát bản nháp sai. |
| IMP-008 | Đã triển khai; cần nghiệm thu trình duyệt | UI theo dõi job, lưu ID/yêu cầu để reload, phục hồi active job theo conversation, hủy cả khi admission chưa xong. Typecheck/build xanh; chưa có browser E2E. |
| IMP-009 | Hoàn tất phạm vi `domain/llm/token.py` | Protocol thuần Python, gỡ whitelist Domain → Contracts, import-linter xanh. Các port Application khác chưa được refactor đồng loạt. |
| IMP-010 | Đã triển khai | Repository lọc tiêu đề, tenant, escape LIKE, cursor keyset trước limit; BFF chuyển q/cursor; Sidebar tải trang tiếp. |
| IMP-011 | Nhánh thử nghiệm, mặc định tắt | Batch 8→16→32, sửa gần đích, giữ trần 32; trần lượt gọi/job. Chưa có ngân sách token/độ dài riêng, A/B chưa chạy. |
| IMP-012 | Nhánh thử nghiệm, mặc định tắt | Khung cấp dòng dùng chung cho sinh khổ và ngữ cảnh sinh/sửa cả bài; cần A/B để quyết định. |
| IMP-013 | Chưa thực hiện | Rhyme Bank truy vết nguồn chờ baseline/A-B; không thêm prompt chưa đo. |
| IMP-014 | Chưa thực hiện | Cần tập nhãn thủ công và thiết kế shadow; không sửa phán quyết nhịp. |
| IMP-015 | Chưa đủ điều kiện | Chờ nghiệm thu 0–3 và khảo sát quyền/chất lượng dữ liệu. |
| IMP-016 | Chưa đủ điều kiện | Không chạy LoRA khi chưa qua các cổng dữ liệu và benchmark. |

### Artifact và vận hành

- [Runbook](Runbook_Improve_06_10.md): cài dependency, cấu hình SQL, chạy worker/API, migration, benchmark và rollback.
- [ADR-0006](adr/0006-durable-poem-jobs.md): queue SQL, delivery at-least-once và lưu kết quả có fencing.
- [Manifest 40 đề](../evals/ket_qua/improve_06_10_40.manifest.json), [200 đề](../evals/ket_qua/improve_06_10_200.manifest.json): `mode=prepared`, không phải kết quả chạy thật.
- [Tổng hợp baseline lịch sử](../evals/ket_qua/improve_06_10_historical.summary.md): giữ raw JSONL gốc; chi phí chưa bao gồm `cheap`.

### Giới hạn nghiệm thu còn mở

Chưa chứng minh P95 admission <1 giây, giảm ≥25% lượt gọi, tăng tỷ lệ đạt hoặc giảm chi phí/bài đạt. Metadata model check không thay thế generate smoke. Job phục hồi sau worker chết có thể gọi lại provider, nhưng owner cũ không được ghi kết quả/lịch sử lần thứ hai. UI sử dụng SQL mới bảo toàn cả lịch sử sau restart; `in_memory` chỉ là chế độ dev, dù queue job vẫn nằm trong SQLite.

Hash bất biến của `src/application/rule.py`: `0a0b2488f2ab10562b8a42a78f7550189664d69c05031f83c4aa4702f1321975`.

### Kết quả kiểm chứng

- Toàn bộ pytest: **1.230 passed, 9 skipped**, 28,55 giây; đã chạy với cảnh báo thread SQLite nâng thành lỗi, không còn cảnh báo đó. 9 trường hợp PostgreSQL skip vì không cấu hình DB test chuyên dụng.
- Import-linter: **4 kept, 0 broken**; Ruff xanh trên các file Python thay đổi.
- Frontend: typecheck và production build thành công. Contract test đối chiếu các trường trong `frontend/scripts/gen-types.mjs` với OpenAPI backend.
- Alembic: upgrade head trên SQLite tạm, `alembic check` không có schema drift. Test vòng đời API thực xác nhận worker nhúng hoàn tất job làm rõ và lưu đủ lịch sử SQL.
- Docker Compose config hợp lệ; hai image API/worker build thành công. Đây là xác minh build, **không phải xác minh chạy container/PostgreSQL**. Smoke container chưa chạy vì hệ thống duyệt quyền báo hết hạn mức; không có quyết định rằng thao tác đó không an toàn và không vượt qua cơ chế duyệt.
- Sau thay đổi manifest hash, 6 test runner/baseline liên quan chạy lại đều passed. Manifest 40/200 được tạo lại từ source cuối, vẫn `mode=prepared`.

Chưa chạy stack, chưa đổi `.env`, chưa dùng DB của người dùng để migration/test và chưa có kết quả live mới.

## 11. Chuẩn bị Pull Request — 07/10/2026

Đẩy thay đổi lên nhánh hiện tại `tat-fewshot-va-doi-chieu-rule3`, dùng PR #2 đang mở vào `main` để giữ lịch sử review và tránh PR trùng.

Kiểm chứng tại thời điểm chuẩn bị PR: **1.230 passed, 17 skipped**, 28,14 giây, không có cảnh báo thread SQLite; import-linter **4 kept, 0 broken**; Ruff trên các file Python thay đổi và frontend typecheck xanh. Số skip tăng từ 9 lên 17 vì job/migration đã tham gia ma trận SQLite/PostgreSQL dùng chung, chưa có `TEST_DATABASE_URL`.

Fixture PostgreSQL mới chỉ nhận `TEST_DATABASE_URL` với database tên `poem_improve_test_*`, không dùng `DATABASE_URL` trong `.env`. Các test này có reset bảng, nên chỉ chạy trên database test riêng, không dùng dữ liệu thật.

Lượt rebuild Docker tiếp theo ngày 06/10 gặp ổ đĩa đầy và thất bại; không thay thế kết quả build thành công của lượt trước bằng tuyên bố runtime thành công. Ngày 07/10 dung lượng ghi đã phục hồi và test offline chạy lại xanh. Chưa nghiệm thu PostgreSQL runtime, browser E2E hoặc A/B model thật; các cờ tối ưu vẫn mặc định tắt. Không commit `.env`, key, DB cục bộ hoặc corpus thô.
