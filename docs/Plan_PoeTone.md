# PLAN — Nâng chất thơ và giảm chi phí cho đường sinh thất ngôn tự do

**Ngày lập:** 26/09/2026 · **Viết lại** từ bản nháp cùng ngày để khớp với hệ thống đang chạy
**Tệp mục tiêu:** `src/application/poetry/` · `src/application/prompting/system.py` · `evals/` · `datalake/scripts/`
**Tệp KHÔNG được đụng:** `src/application/rule.py` (ĐÓNG BĂNG, băm `0a0b2488…`)
**Trạng thái:** ✅ GĐ−1, GĐ0, GĐ1.1, GĐ1.3, GĐ3.2, GĐ3.4 (một phần), QĐ-P2/P4/P9 xong (26/09) · 🟡 tiếp theo: đo lại 40 đề sau one-shot, rồi các A/B GĐ2.

---

## 0. Đọc trước — vì sao phải viết lại

Bản nháp đầu được viết cho **một hệ thống khác**. Đối chiếu từng tên trong bản nháp với repo này
(`grep` toàn bộ, trừ `datalake/`) cho kết quả: **không tên nào tồn tại**, trừ chính file plan.

| Bản nháp nói | Repo này thật sự có |
|---|---|
| `pipeline_v2_0`: Composer → Finalizer → Repair | `poetry/sinh_tho.py`: cổng B1 → `planner.py` → `sinh_tung_kho` (k = 32, dừng sớm) → cứu khổ bằng ReAct → `PoemVerifierDayDu` → đường lùi `generate_with_verification` |
| Effort `fast / standard / studio` | Không có. Hai núm: `so_ung_vien_moi_kho` (mặc định 32) và `max_repair_rounds` (mặc định 3) |
| `REPAIR_STRATEGIES` 4 bước | `THANG_LEO_THANG` **3 bước**: `sua_dong` → `sinh_lai_kho` → `sinh_lai_ca_bai` (`prompting/system.py:713`) |
| `checker_ver2.py` | `application/rule.py`, 7 tầng, **đóng băng**, có test ghim SHA-256 |
| Hai thể: lục bát + 7 chữ | **Một thể duy nhất**: thất ngôn tự do. Lục bát nằm ngoài phạm vi (`Plan_TTS_Tieu_De_Reviewer.md` §Phạm vi) |
| 12.000 bài, đạt 99,95%, 2,02 lượt gọi/bài | Không có lô nào như vậy. Số thật ở §1 |
| Kho mẫu 7 chữ chỉ 34 bài | `datalake/corpus_tuyen/tho_mau.jsonl` **300 bài** + `bai_dat.jsonl` **24.366 bài** đạt luật. Few-shot **đang TẮT** theo quyết định 22/09 |
| `stock_phrases`, phạt lặp | `quality.py` **đã gỡ** phạt lặp ngày 21/09 vì phạm S20 (quyền điệp) và G11 (không ngưỡng tuỳ ý) |
| `_composer_rank_key`, `verbalized_probability` | Không xếp hạng: `_chon_mot_kho` nhận **ứng viên ĐẦU TIÊN** đạt luật |
| `judge.py`, `PRIMER_MODEL_NAME` | `poetry/reviewer.py` chấm `mach_lac`, `hinh_anh` thang 1–10, **chỉ tư vấn**. Đường rẻ là `LlmPort.cheap` + tier `cheap` trong `configs/models.yaml` |
| `batch_generate.py`, `llm_call_stats.py` | `evals/do_that.py` (12 đề), `datalake/scripts/do_ab_prompt.py` (A/B có p-value), trường `so_ung_vien_da_dung` |
| `data/topic/topic.jsonl` | Không có. Chủ đề nằm trong `do_that.py`, `do_ab_prompt.py::_chu_de_cua`, và trường `topic` của `datalake/generate/generate_poem.jsonl` |
| `db.py` bảng `evaluations`, `Evaluate.jsx` | Adapter SQL hai dialect + Alembic (`migrations/`); `routers/feedback.py` + `poetry/feedback.py`; frontend Next.js/TSX (`components/poem/PoemEvidence.tsx`) |
| `llm_endpoints.py` | `adapters/llm/vllm.py` + `configs/models.yaml` |
| `van_gom_nhom_*.json` | `CAP_VAN_THONG`, `van_cua`, `hiep_van` trong `rule.py` |
| `export_sft_data.py` | Không có |
| "Qwen3.5 hay Gemma?" | `.env` thật (26/09/2026): `DEFAULT_PROVIDER=openai`, `DEFAULT_MODEL=gpt-4o-mini`. Adapter Google (Gemma/Gemini) đã có nhưng chưa phải mặc định |

**Khác biệt quan trọng nhất không nằm ở tên file mà ở chẩn đoán.** Bản nháp giả định LLM yếu nhất ở
**lập kế hoạch vần**. Ở hệ thống này số đo nói khác:

| Tầng | % chặn trên corpus 55.297 bài vào tầng | Nguồn |
|---|---:|---|
| 4 — Thanh luật (S2, P2/P4/P6) | **55,29 %** | `datalake/analysis/TONG_HOP.md` |
| 5 — Vần (S11) | 1,46 % | cùng nguồn |

Trên thơ máy sinh cũng vậy: 163/199 bài trượt chết ở tầng 4 (`docs/analysis_generate.md`). **Nút thắt
là thanh điệu ở P2/P4/P6, không phải vần.** Mọi cải tiến bộ sinh trong plan này nhắm vào tầng 4 trước.

---

## 1. Hiện trạng đo được

| Chỉ số | Giá trị | Điều kiện đo | Nguồn |
|---|---:|---|---|
| Sinh cả bài một lần, đạt luật | 8,3 % | gpt-4o-mini, 12 đề (4/8/12 dòng) | `docs/Do_That_21-09_R2.md` |
| Sinh từng khổ + chọn ứng viên, đạt luật | 83,3 % | cùng 12 đề, k = 16, hai lần chạy độc lập | cùng nguồn |
| `p` — một dòng khớp khuôn thanh | ≈ 0,56 | gpt-4o-mini | cùng nguồn |
| Thời gian mỗi bài | 7,4–10,3 s | k = 16 | cùng nguồn |
| Lô 199 bài 20 dòng, đạt luật | **1/199** | bộ sinh ngoài hệ thống, chưa rõ mô hình | `docs/analysis_generate.md` |
| Few-shot → dòng đủ 7 tiếng | 55,62 % → 62,69 % (p = 0,0044) | gpt-4o-mini, 25 chủ đề × 8 ứng viên | chú thích `sinh_tho.py` |
| Test | 1129 xanh · 9 skip; ruff, mypy, import-linter sạch | sau GĐ−1, 26/09/2026 | `make check` |

**Những gì CHƯA đo — và là lý do plan này tồn tại:**

1. **Tỉ lệ đạt ở k = 32, bài dài (16–20 dòng).** Con số 86% trong `sinh_theo_kho.py` là **tính** từ
   `p = 0,56`, chưa phải đo.
2. **`p` của mô hình đang dùng thật.** Nếu chuyển sang Gemma thì mọi phép tính `k` phải làm lại.
3. **Chất thơ.** Reviewer có sẵn nhưng chưa ai chạy nó trên một lô để biết điểm có ổn định không.
4. **Bám đề.** `quality.py` chỉ kiểm "có ≥ 1 tiếng của chủ đề xuất hiện".
5. **Chép thơ có sẵn.** Chưa có phép kiểm nào.
6. **Chi phí thật mỗi bài.** Chưa có số, dù đã có `so_ung_vien_da_dung` và `observability/cost.py`.
7. **Mô hình hiểu luật hay chỉ nhớ mẫu.** Chưa có probe nào.

---

## 2. Tám ràng buộc — plan không được phá

Mỗi ràng buộc là một quyết định **đã chốt** của chủ dự án, có test hoặc chú thích ghim trong mã.

| # | Ràng buộc | Hệ quả cho plan |
|---|---|---|
| R1 | `rule.py` đóng băng | Điểm liên tục (GĐ1) nằm ở **file mới**, chỉ **gọi** hàm công khai của `rule.py`, không viết lại phép đếm hay phép tách thanh |
| R2 | Không ngưỡng tuỳ ý (G11) | Mọi ngưỡng mới hoặc là số nguyên có nghĩa, hoặc là một QĐ có người chốt. Trọng số 0,4/0,3/0,3 của PoeTone **không được chép sang** mà không có QĐ |
| R3 | LLM không bao giờ vào cổng chặn (`test_reviewer_khong_noi_vao_cong_chan`) | Điểm Reviewer chỉ được dùng để **chọn giữa các bài đã đạt**, không bao giờ để loại bài |
| R4 | Bộ kiểm phán, mô hình sửa, **không gợi ý câu chữ** (`poem_verifier.dung_bien_ban`, tính chất 3) | Gợi ý tiếng vần cụ thể trong prompt là vùng xám → QĐ-P5 |
| R5 | Fail closed — không trả bài sai | Không cải tiến nào được thêm đường trả bài chưa qua `PoemVerifierDayDu` |
| R6 | Mọi đổi prompt phải đo A/B (`do_ab_prompt.py`) với chỉ số **"ứng viên dùng được thật"** (đạt luật ∧ không chép ∧ qua chất lượng) | Không dùng "đạt luật" trơn làm chỉ số chính |
| R7 | S20 cho phép điệp dòng, điệp khổ | Không phạt lặp. Lặp chỉ được là tín hiệu HITL hoặc số mô tả |
| R8 | Kiến trúc 4 vòng, `import-linter` KEPT | Logic mới ở `application/`; gọi mô hình qua `LlmPort`; script đo ở `evals/` hoặc `datalake/scripts/` |

---

## 3. Mục tiêu

**Nguyên tắc:** đo baseline trước, rồi chủ dự án chốt đích dựa trên số đo. Các cột "Đích đề xuất"
dưới đây là **đề xuất**, không phải cam kết — theo R2, một con số không có nguồn thì không được
thành ngưỡng.

| Mục tiêu | Chỉ số | Hiện tại | Đích đề xuất |
|---|---|---|---|
| Đúng luật | % yêu cầu trả `200 + PoemResponse` trên tập 200 đề | chưa đo ở quy mô này | ≥ baseline, và 100% bài trả ra qua cổng (R5, bất biến) |
| Ít phải cứu | % bài đi đường lùi `bo_sinh = "mot_lan"` · % khổ cần cứu ReAct | chưa đo | giảm so với baseline |
| Rẻ hơn | lượt gọi mỗi bài (`so_ung_vien_da_dung` + tiêu đề + TTS + Reviewer) | chưa đo | giảm ≥ 30% sau GĐ2, không đổi tỉ lệ đạt |
| Đầu vào của `k` | `p` (tỉ lệ dòng khớp khuôn) theo từng mô hình | 0,56 (gpt-4o-mini) | có số cho mọi mô hình ứng viên |
| Thơ hay | Reviewer `mach_lac`, `hinh_anh` (1–10) | chưa đo | có baseline; +0,5 điểm sau GĐ2 |
| Bám đề | % đoán đúng nhóm chủ đề khi chỉ xem bài | chưa đo | có baseline |
| Không chép | % bài có ≥ 1 dòng trùng nguyên văn một dòng trong kho | chưa đo | QĐ-P2 |
| Hiểu luật thật | chênh điểm probe giữa tập lịch sử và tập OOS | chưa đo | có số đo |

---

## 4. Bảy quyết định chủ dự án phải chốt

| Mã | Câu hỏi | Khuyến nghị | Chặn giai đoạn |
|---|---|---|---|
| **QĐ-P1** | Điểm tuân thủ liên tục: gộp thành một số bằng trọng số 0,4/0,3/0,3 (của PoeTone, đo trên Songci Trung Quốc) hay báo **ba số rời**? | **Ba số rời.** Trọng số kia không có nguồn cho thể này; `reviewer.py` đã chọn cách tương tự | GĐ1 |
| **QĐ-P2** | Phát hiện bài có dòng trùng nguyên văn thơ có sẵn thì **chặn** hay **chỉ báo HITL**? | Chặn khi trùng **nguyên một dòng 7 tiếng**: đó là số nguyên có nghĩa ("chép một câu"), không phải ngưỡng dò | GĐ1 |
| **QĐ-P3** | Có đổi luật chọn khổ từ "ứng viên đạt ĐẦU TIÊN" sang "sinh tới **m** ứng viên đạt rồi để Reviewer chọn" không? | Chỉ sau khi GĐ1 chứng minh Reviewer ổn định. Giá: khoảng m lần số lượt gọi mỗi khổ. Đề xuất m = 2, bật bằng tham số, mặc định tắt | GĐ1.6 |
| **QĐ-P4** | **Bật lại** ví dụ mẫu (one-shot), đảo quyết định tắt few-shot ngày 22/09? | Bật **one-shot** (1 ví dụ, không phải 3): số đo 22/09 ủng hộ (p = 0,0044), và một ví dụ giữ được phần lớn mức tiết kiệm token | GĐ2 |
| **QĐ-P5** | Khung bài có được **gợi ý tiếng vần cụ thể** cho P7 không, hay chỉ ghi nhóm vần và khuôn thanh? | Chỉ khuôn thanh + nhóm vần. Gợi ý tiếng cụ thể là bộ kiểm viết thơ hộ (R4) | GĐ2.2 |
| **QĐ-P6** | Nhập kho HF (CC-BY-4.0) vào `datalake/` — chấp nhận nghĩa vụ ghi nguồn trong README và mọi báo cáo? | Có. Không commit dữ liệu thô, chỉ commit script và bản thống kê | GĐ0.2 |
| **QĐ-P7** | Có đầu tư GĐ6 (LoRA, cần GPU ≥ 24 GB hoặc thuê) không? | Quyết **sau GĐ5**, khi có bảng chi phí từng mô hình | GĐ6 |

---

## Giai đoạn −1 — Dọn nền · ✅ XONG 26/09/2026

1. ✅ **`test_file_doi_chieu_khong_chay` xanh lại.** Bản `compare_rule.py` trong working tree là bản
   gốc trước 22/09, có dòng rác `Rule.py` ở đầu nên **không import được** (`NameError`). Hệ quả là
   `chay_doi_chieu_rule2.py` và `chay_doi_chieu_rule3.py` cũng hỏng theo. Đã khôi phục bản HEAD: bản này
   có nhãn "KHÔNG CHẠY", phần lõi đã bù và phần nới luật rule3. Bản hỏng được sao lưu ngoài repo.
2. ✅ **Sửa 6 lỗi mypy** trong các file đang sửa dở. Không lỗi nào đổi hành vi:
   - `verify_output.py`: biến `them` bị dùng cho hai kiểu (`Mapping` rồi `str`), tách thành `bo_sung`;
   - `sinh_theo_kho.py`: `_NganSachLuonMo` hiện thực đủ `RateLimitPort` (thêm `check`, `should_warn`);
   - `sinh_tho.py`: bổ sung chú thích kiểu.
3. ✅ **Commit toàn bộ phần đang dở** trên nhánh `tat-fewshot-va-doi-chieu-rule3`.
4. ✅ **Mô hình đang chạy thật:** `openai` / `gpt-4o-mini` (đọc từ `.env`).

⚠️ Còn lại: `make arch` gọi `lint-imports` trần, và lệnh này báo *"Could not find package 'domain'"*
nếu `src` không nằm trên `PYTHONPATH`. Chạy `PYTHONPATH=src lint-imports` thì 4/4 hợp đồng KEPT.

**Nghiệm thu:** ruff, mypy, import-linter, pytest đều sạch; baseline chạy trên commit của bước 3.

---

## Giai đoạn 0 — KẾT QUẢ · ✅ XONG 26/09/2026 (QĐ-P6 đã chốt: nhập kho HF)

Commit đo: `775b225` · `openai` / `gpt-4o-mini` · k = 32 · 4 phương án mỗi lượt.

| Bàn giao | Tệp |
|---|---|
| Tập 200 đề, ghim bằng test | `evals/datasets/de_danh_gia.jsonl` · `evals/dung_tap_de.py` · `tests/unit/application/test_tap_de.py` |
| Kho HF đã lọc qua `rule.py` | `datalake/scripts/nhap_kho_hf.py` → `datalake/hf/tong_hop.json` (dữ liệu thô gitignore) |
| Script chấm chung | `evals/cham_diem.py` |
| Baseline có chi phí | `evals/do_that.py --de …` → `evals/ket_qua/baseline_775b225.{jsonl,log}` |
| Đo `p` | `datalake/scripts/do_p.py` |

### 0.A. Baseline 200 đề

| Độ dài | Đạt | Lượt gọi TB | Thời gian TB |
|---:|---:|---:|---:|
| 4 | 12/40 (30 %) | 17,1 | 18 s |
| 8 | 10/40 (25 %) | 19,7 | 22 s |
| 12 | 9/40 (22,5 %) | 22,0 | 26 s |
| 16 | 6/40 (15 %) | 24,2 | 29 s |
| 20 | 3/40 (7,5 %) | 25,9 | 36 s |
| **Tổng** | **40/200 (20 %)** | 21,8 | 26 s |

- Chi phí **2,96 USD / 200 bài = 14,81 USD / 1.000 bài** (chưa tính lượt `cheap`).
- 39/40 bài đạt đến từ `tung_kho`. **Đường lùi sinh–sửa cứu được 1/161 bài.**
- Trong 160 bài trượt, chẩn đoán đầu tiên: S2 (thanh) ≈ 93, H3 (không đủ 4 dòng / không phân dòng) 35,
  H1 (số tiếng) ≈ 16, H4 9. H3 ở đường lùi gợi ý mô hình trả văn bản không phải bài thơ — soi ở GĐ3.4.
- **248 lần gặp 429** trong lô, đã được bộ đo tự thử lại. Xem 0.C.

### 0.B. `p` hôm nay thấp hơn một nửa con số 21/09

12 chủ đề × 16 ứng viên khổ đầu mỗi nhánh (`do_p.py`, chạy ngày 26/09):

| Phương án / lượt | Dòng đủ 7 tiếng | **`p`** (đủ 7 tiếng **và** khớp khuôn) | Khổ đạt luật | Lượt gọi |
|---:|---:|---:|---:|---:|
| 1 | 71,2 % | **32,3 %** | 1/192 | 192 |
| 4 (mặc định hiện tại) | 67,7 % | **27,0 %** | 3/192 | 48 |

- `sinh_theo_kho.py` tính `k` từ **p = 0,56**. Với p ≈ 0,3 thì một khổ đạt ≈ p⁴ ≈ 1 %, và k = 32
  cho mỗi khổ ≈ 30–50 %. Đây là lý do tỉ lệ đạt tụt theo độ dài ở bảng trên.
- Lượt đo lặp trước đó (6 chủ đề) cho 82,8 % → 72,9 % dòng đủ tiếng. **Xin 4 phương án một lượt làm
  giảm độ đủ tiếng 3–10 điểm** (mô hình hay viết dòng 6 tiếng khi viết nhiều phương án). Đổi lại số
  lượt gọi giảm 4 lần. Chênh ở "khổ đạt" (1 vs 3) nằm trong nhiễu. → **QĐ-P8** dưới đây.
- Chưa rõ vì sao `p` giảm so với 21/09. Hai nghi phạm: prompt đã đổi nhiều trên nhánh này (`system.py`
  +880 dòng, few-shot tắt), hoặc phép đo 21/09 định nghĩa `p` khác. **Việc đầu tiên của GĐ2:**
  chạy `do_p.py` ở commit `d09b8cb` (trước các thay đổi prompt) để tách hai khả năng.

### 0.C. Lỗ hổng sản phẩm phát hiện được: không thử lại khi gặp 429

`ChatLlmAdapter.reply` bọc mọi lỗi provider thành `UpstreamError` và **không thử lại**. Tài khoản
hiện có trần 200.000 token/phút; một bài 20 dòng gửi tới 8 lượt song song. Lượt chạy thử đầu tiên
**không** có retry: 8/20 đề trượt oan vì 429. Người dùng `/v1/poem` sẽ gặp đúng lỗi đó.

Bộ đo đã có retry riêng (`evals/do_that.py::_DemLuotGoi`, ghi `lan_thu_lai_429`). Sản phẩm thì chưa:
đề xuất nối `adapters/llm/resilience.py` vào đường `/v1/poem` — xem QĐ-P9.

### 0.D. Kho HF

| Kho | Đạt `rule.py` | Trượt | Trùng `final_data_7_chu` |
|---|---:|---:|---:|
| `bay_chu` (43.565 bài không trùng) | **20.445** (46,9 %) | 23.120 | 22.887 (52,5 %) |
| `duong_luat` (2.549 bài) | 2.051 | 498 | 69 |

- Khoảng một nửa kho HF trùng với `final_data_7_chu.jsonl`, nên việc khử trùng là cần thiết (đã gắn cờ).
- 80 % thơ Đường luật qua được `rule.py`, đúng thiết kế: tầng 3 chỉ ghi nhận, không chặn. Probe đoán
  thể ở GĐ4.3 vì vậy **không** được dùng `rule.py` làm đáp án; phải dùng nhãn `specific_genre`.

### Hai quyết định mới phát sinh

| Mã | Câu hỏi | Khuyến nghị |
|---|---|---|
| **QĐ-P8** | Giữ `SO_UNG_VIEN_MOI_LUOT = 4` hay về 1? | Đo lại bằng `do_p.py` với 24+ chủ đề trước khi đổi. Nếu "khổ đạt" không khác biệt có ý nghĩa thì giữ 4 (rẻ hơn 4 lần lượt gọi) |
| **QĐ-P9** | Thêm retry có backoff cho 429 vào đường sản phẩm? | Có. Không đổi luật, không đổi prompt; chỉ ngừng biến giới hạn tần suất thành bài "không đạt" |

### 0.E. Sau GĐ0 — đã làm ngày 26/09/2026

Chủ dự án chốt theo khuyến nghị: **QĐ-P1** ba số rời · **QĐ-P8** giữ 4 phương án/lượt ·
**QĐ-P9** thêm retry cho sản phẩm.

1. ✅ **QĐ-P9 — retry trong `ChatLlmAdapter.reply`.** Chỉ thử lại 429, 5xx và lỗi mạng (tối đa 6
   lần, tôn trọng `Retry-After`, chờ tối đa 60 s). 400/401/404/422 không thử lại. `UpstreamError`
   nay mang `status_code`. Bộ đo bỏ retry riêng của nó. Test: `tests/unit/adapters/test_chat_port_thu_lai.py`.
2. ✅ **`p` KHÔNG giảm vì prompt.** Đo `p` bằng hàm dựng lời nhắc của từng commit (zero-shot, 1 phương
   án/lượt, 12 chủ đề):

   | Commit | Lời nhắc | `p` |
   |---|---:|---:|
   | `168c0e6` (sáng 21/09) | 1.661 ký tự | 0,22 |
   | `9572aeb` (tối 21/09) | 3.972 | 0,33 |
   | `9594e41` (22/09) | 4.484 | 0,28 |
   | HEAD | 8.369 | 0,35 |

   Con số `p = 0,56` ngày 21/09 **không tái lập được** theo định nghĩa này ở commit nào. Khác biệt duy
   nhất còn lại giữa lượt đo 21/09 (83,3 %) và baseline hôm nay (20 %) là **few-shot** (bật ngày 21/09,
   tắt ngày 22/09). QĐ-P4 vì vậy là việc có giá trị cao nhất tiếp theo, và phải A/B trước khi bật.
3. ✅ **GĐ1.1 — `application/poetry/diem_tuan_thu.py`.** Ba số rời `cau_truc`, `thanh`, `van` cộng
   `hinh_thuc` và `so_dong_can_sua`. Đối chiếu với `rule.py`: 3.000/3.000 bài đạt đều trọn vẹn;
   0/23.120 bài trượt của kho HF được trọn vẹn. `van` là 0/1 (tầng 5 đạt khi có MỘT cụm có vần), không
   phải tỉ lệ.
4. ✅ **GĐ3.2 — `_chon_mot_kho` chọn ứng viên cứu theo `khoa_xep_hang()`** (hình thức → số dòng phải
   viết lại → vần), không còn theo `len(v.vi_pham)`.

### 0.F. Đã làm tiếp, 26/09/2026 — không tốn lượt gọi API

Chủ dự án chốt theo khuyến nghị: **QĐ-P2** chặn dòng chép nguyên văn · **QĐ-P3** tắt mặc định ·
**QĐ-P4** bật one-shot · **QĐ-P5** chỉ khuôn + nhóm vần · **QĐ-P7** để sau GĐ5.

1. ✅ **QĐ-P4 — one-shot cho mọi yêu cầu** (commit `090c03c`). A/B khổ đầu, 192 ứng viên mỗi nhánh:
   `p` 22,5 % → **46,6 %**, dòng đủ 7 tiếng 58,7 % → **98,7 %**, 0 ứng viên chép bài mẫu, token vào
   +10 %. Ba ví dụ không tốt hơn một. Trước đây tool `sinh_tho` của chat **không truyền kho mẫu**
   nên luôn chạy zero-shot; nay container dùng một kho chung cho cả hai đường.
   ⚠️ **Chưa đo tỉ lệ đạt cả bài sau thay đổi này** (lượt 200 đề dừng ở đề 7/200 theo yêu cầu chủ
   dự án: 3/7 đạt, 0,12 USD). Lệnh đo lại: `python evals/do_that.py --de evals/datasets/de_danh_gia.jsonl --gioi-han 40`.
2. ✅ **QĐ-P2 / GĐ1.3 — phát hiện và chặn chép.**
   - Cổng `ChiMucDongThoPort` · chuẩn hoá `application/poetry/doi_chieu_chep.py` · adapter
     `adapters/persistence/corpus/chi_muc_dong.py` · dựng sẵn bằng `datalake/scripts/dung_chi_muc_dong.py`.
   - 547.181 dòng 7 tiếng (tho_mau + bai_dat + kho HF). Dựng từ JSONL mất 190 s, nên chỉ mục được
     **dựng sẵn** (34 s, offline) và nạp trong 0,26 s. Thiếu tệp dựng sẵn thì lùi về `tho_mau.jsonl`.
   - `PoemVerifierDayDu` thêm lỗi mã `CHEP` có địa chỉ dòng. Bài chép vẫn `dat_luat = True`, chỉ
     `dat = False`. `_chon_mot_kho` loại khổ có dòng chép ngay ở bước chọn.
   - Hiện trạng: 1/40 bài đạt của baseline có một dòng trùng nguyên văn («Những chiếc lá vàng
     rơi lả tả», từ kho `bai_dat`).
3. ✅ **GĐ3.4 — mổ xẻ đường lùi** (160 bài trượt của baseline):
   S2 97 bài · H4 44 · **H3 35** · CL1 31 · CL4 22 · H1 18. **35 bài có bản nháp cuối chỉ 1 dòng**: bản
   nháp là đoạn văn cuối của vòng ReAct, nên hoặc mô hình trả một câu dẫn, hoặc vòng lặp trả chuỗi
   cứng `"Đã hoàn thành các bước suy luận."` (`generate.py`). Chưa phân biệt được vì bản nháp
   trượt chưa từng được lưu. **Đã thêm** `OutputKhongDat.ban_nhap_cuoi` (ẩn khỏi `repr`, API không
   đọc, có test ghim) và `do_that.py` ghi nó ra — lượt đo kế tiếp sẽ trả lời.
   ✅ **Đã sửa kịch bản khả dĩ nhất:** mô hình đưa bài vào tham số `van_ban` của `kiem_tra_tho` rồi
   kết thúc bằng một câu dẫn. `generate_react_loop` nhận thêm `la_ban_nhap` (chỉ đường thơ truyền:
   `verify_output.co_dang_bai_tho`, ≥ 4 dòng); khi lời cuối không phải bài thơ, vòng trả bản nháp
   gần nhất lấy từ văn bản hoặc tham số tool. Kết quả vẫn qua cổng kiểm đầy đủ. Đường chat
   thường không đổi. Test: `test_react_giu_ban_nhap.py`. Hiệu quả thật cần lượt đo kế tiếp.
4. ✅ `Makefile`: `arch` chạy `PYTHONPATH=src lint-imports`. README cập nhật số đo thật.

**Còn lại, đều cần A/B trả tiền trước khi bật (R6):** khung cấp dòng (GĐ2.2, QĐ-P5), thi liệu (GĐ2.3),
bảng soi toàn khổ khi sửa (GĐ3.1), tính lại `k` từ `p` mới (≈ 0,47).

---

## Giai đoạn 0 — Dữ liệu và công cụ đo (kế hoạch gốc)

### 0.1. Tập đề cố định — `evals/datasets/de_danh_gia.jsonl`

- **200 đề**, mỗi đề gồm `chu_de` và `so_dong ∈ {4, 8, 12, 16, 20}`, 40 đề mỗi độ dài. Bài dài phải có
  mặt: đó là nơi `pⁿ` cắn mạnh nhất, và cũng là nơi con số 86% chưa được kiểm.
- Chủ đề lấy từ trường `topic` của `generate_poem.jsonl` cộng danh sách trong `do_that.py`, trộn
  bằng seed cố định ghi trong file.
- **Không bao giờ** dùng 200 đề này để chọn ví dụ mẫu, dựng thi liệu hay huấn luyện. Có test ghim:
  chủ đề trong tập đề không được xuất hiện trong kho ví dụ đã lọc.

### 0.2. Nhập kho HF — `datalake/scripts/nhap_kho_hf.py` · cần QĐ-P6

Nguồn: [`phamson02/vietnamese-poetry-corpus`](https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus),
198.598 bài, cột `content, title, url, genre, period, specific_genre, author`, giấy phép CC-BY-4.0
(đã đối chiếu trang dataset ngày 26/09/2026).

- Lọc `specific_genre == "bảy chữ"` làm **kho chính**. Giữ riêng `thất ngôn tứ tuyệt`,
  `thất ngôn bát cú`, `thất ngôn cổ phong` làm **kho đối chiếu Đường luật**. Kho này dùng cho probe
  đoán thể ở GĐ4 và cho tầng 3, **không** dùng làm ví dụ.
- Chạy `kiem_tra_bai_tho` trên mọi bài, **không tin nhãn `specific_genre`**. Ghi ra
  `datalake/hf/{bay_chu,duong_luat}_{dat,truot}.jsonl`, giữ `author` và `url` để ghi nguồn.
- **Khử trùng với `datalake/dataraw/final_data_7_chu.jsonl`** bằng băm nội dung đã chuẩn hoá. Hai kho
  có thể cùng gốc; không khử trùng thì phép kiểm chép ở 1.3 đếm đôi.
- Thêm `datalake/hf/` vào `.gitignore`. Commit script và `datalake/hf/tong_hop.json` (chỉ số liệu).

### 0.3. Script chấm chung — `evals/cham_diem.py`

- Đầu vào: JSONL có trường bài thơ và đề. Đầu ra: cùng file, thêm cột điểm. Các cột được bổ sung dần
  qua GĐ1 và GĐ4.
- **Dựng trên `evals/metrics/poetry.py`**, không viết bộ đếm thứ hai. Đơn vị phán quyết vẫn là BÀI,
  như docstring của `DoLuongTho` đã chốt.
- In bảng tổng hợp theo độ dài bài.

### 0.4. Baseline

- Mở rộng `evals/do_that.py`: đọc `de_danh_gia.jsonl` và ghi ra mỗi bài các trường `bo_sinh`,
  `so_ung_vien_da_dung`, `so_luot_sua`, `chien_luoc_cuoi`, thời gian, token vào/ra, chi phí
  (`observability/cost.py`), và `duong_di`.
- Đo `p` của mô hình hiện tại bằng `do_ab_prompt.py`, cho hai nhánh giống hệt nhau (A/A). Phép chạy
  này kiểm luôn độ nhiễu của bộ đo.
- ⚠️ **Ước chi phí trước khi chạy.** Trường hợp xấu nhất của một bài 20 dòng là
  5 khổ × 8 lượt × (1 + cứu ReAct), cộng đường lùi. Chạy thử 20 đề trước, nhân lên, rồi mới chạy
  cả 200.

**Nghiệm thu:** có `evals/ket_qua/baseline_<commit>.jsonl`; có `p` của mô hình hiện tại; có kho HF đã
lọc với số bài đạt từng nhóm; bảng baseline tách theo độ dài bài.

---

## Giai đoạn 1 — Chấm nhiều chiều (1 tuần)

### 1.1. Điểm tuân thủ liên tục — `application/poetry/diem_tuan_thu.py` · cần QĐ-P1

`kiem_tra_bai_tho` **dừng ở tầng chặn đầu tiên**, nên các tầng sau mang `da_chay = False`. Muốn có
điểm liên tục thì phải tính **ba chiều độc lập**, bằng hàm công khai của `rule.py` (R1: gọi, không
viết lại):

| Chiều | Định nghĩa | Hàm của `rule.py` |
|---|---|---|
| `cau_truc` | tỉ lệ dòng đủ 7 tiếng, và số dòng có phải bội của 4 | `dem_tieng`, `tach_kho` |
| `thanh` | tỉ lệ dòng khớp một trong hai khuôn ở P2/P4/P6 | `tach_tieng`, `khuon_cua_dong` |
| `van` | tỉ lệ cụm 4 dòng có ít nhất một cặp vần chân | `cua_so_co_van_chan` |

- Thuần, tất định, không gọi mô hình.
- **Không bao giờ** thay `PoemVerdict.dat`. Test: bài đạt thì được (1, 1, 1); bài sai đúng một dòng
  thanh thì `thanh` giảm đúng 1/n.
- Test đối chiếu: trên `bai_dat.jsonl`, 100% bài phải có cả ba chiều bằng 1,0. Lệch là dấu hiệu file
  mới hiểu luật khác `rule.py`.

**Dùng ngay được, không cần chờ gì thêm:** `_chon_mot_kho` hiện chọn ứng viên để cứu bằng
`len(v.vi_pham)`. Con số này chỉ đếm vi phạm **ở tầng chết đầu tiên**, nên một ứng viên chết ở tầng 2
với 1 vi phạm có thể bị xếp "gần đích" hơn một ứng viên đã qua tầng 2 và chỉ sai 2 dòng thanh. Thay
bằng điểm liên tục (xem 3.2).

### 1.2. Lặp và sáo mòn — chỉ mô tả, không phạt

Bản nháp đề xuất phạt lặp. **Không làm**: `quality.py` đã gỡ đúng việc này ngày 21/09, vì 164/164 bài bị
bắt đều là điệp có chủ ý (R7).

Thay bằng: `cham_diem.py` thống kê 50 cụm 2–3 tiếng xuất hiện nhiều nhất trên lô máy sinh, so với tần
suất của cùng cụm đó trong kho người viết. Đây là **số mô tả** cho báo cáo và cho việc chọn thi liệu ở
2.3. Không chặn, không trừ điểm.

### 1.3. Phát hiện chép — `application/poetry/doi_chieu_chep.py` + chỉ mục ở `datalake/` · cần QĐ-P2

- Chỉ mục: băm mọi **dòng** đã chuẩn hoá (dùng `tach_tieng` của `rule.py`) từ kho HF,
  `final_data_7_chu.jsonl` và `tho_mau.jsonl`. Với thơ 7 tiếng, "7-gram trùng" gần như đồng nghĩa với
  "trùng nguyên một dòng". Thêm chỉ mục 4-gram để báo cáo mức trùng một phần.
- Ghi cho mỗi bài: `so_dong_trung_nguyen_van`, `ngram4_trung_max`, và dòng nguồn bị trùng (kèm
  `author` và `url`).
- Chạy trên `generate_poem.jsonl` và lô baseline để có số hiện trạng.
- Nếu QĐ-P2 chọn **chặn**: nối vào `PoemVerifierDayDu` như một chiều chất lượng mới. Phép kiểm tất
  định và đồng bộ nên hợp lệ với port `OutputVerifier`. Chỉ mục phải nạp qua một port, không đọc file
  trong `application/`.

### 1.4. Mở rộng Reviewer thành bộ chấm 4 chiều — sửa `poetry/reviewer.py`

- Thêm hai chiều vào hai chiều sẵn có: **trôi chảy** và **bám đề**. Vẫn thang 1–10, vẫn giữ mỏ neo hiệu
  chuẩn, vẫn **không gộp** thành điểm tổng (lý do đã ghi trong file).
- Đổi sang `LlmPort.cheap` với tier `cheap`. Nếu port chưa cho đặt `temperature` thì thêm tham số đó
  vào `CallContext` hoặc `CheapRoute`: sửa port là việc của R8, không gọi thẳng SDK.
- **Đo độ ổn định trước khi tin:** chấm lại 100 bài baseline hai lần. Báo độ lệch tuyệt đối trung bình
  từng chiều. Chiều nào lệch ≥ 1 điểm thì không được dùng để xếp hạng ở 1.6.
- Giữ nguyên bất biến R3: `test_reviewer_khong_noi_vao_cong_chan` phải còn xanh.

### 1.5. Mạch lạc giữa các dòng (tuỳ chọn)

Dùng `ports/embedding.py`: tính độ tương đồng giữa từng cặp dòng liền nhau. Chỉ là cột mô tả trong
`cham_diem.py`, dùng để đối chiếu với điểm `mach_lac` của Reviewer. Nếu hai số không tương quan thì bỏ
chiều này.

### 1.6. Xếp hạng khổ bằng chất thơ · cần QĐ-P3

- Thêm tham số `so_ung_vien_dat_can` (mặc định **1** = hành vi hiện tại) vào `sinh_tung_kho`.
- Khi > 1: tiếp tục sinh tới khi có đủ số ứng viên đạt, rồi dùng Reviewer chọn ứng viên có tổng
  `mach_lac + hinh_anh` cao hơn, chấm **trong ngữ cảnh các khổ trước**.
- Luật vẫn là cổng tuyệt đối: Reviewer chỉ thấy ứng viên **đã đạt**.
- Ghi `ly_do_chon` vào `duong_di`, để `PoemEvidence.tsx` hiển thị được.

**Nghiệm thu GĐ1:** chạy lại baseline với cột mới; tỉ lệ đạt không đổi (vì chưa đụng bộ sinh); có số
đo độ ổn định của Reviewer; có số hiện trạng về chép.

---

## Giai đoạn 2 — Cải tiến bộ sinh, nhắm tầng 4 (1,5 tuần)

Mọi thay đổi ở đây là **thay đổi prompt**, nên đều đi qua `do_ab_prompt.py` (R6).

### 2.1. One-shot · cần QĐ-P4

- Khôi phục ba dòng đã ghi sẵn trong `sinh_tho.py` (chú thích "⛔ FEW-SHOT ĐÃ TẮT"), với
  `SO_VI_DU_TOI_DA = 1`.
- Nguồn ví dụ: `tho_mau.jsonl`, cộng kho HF `bay_chu_dat` **sau** khi đã lọc chép và loại mọi bài trùng
  chủ đề với tập đề đánh giá.
- `fewshot.py` đã chọn theo **cùng số dòng và cùng phối khuôn**. Giữ nguyên tiêu chí đó: nó nhắm đúng
  tầng 4.
- Chống chép bài mẫu: phép kiểm 1.3 chạy thêm trên bài mẫu vừa đưa vào prompt.

### 2.2. Khung bài cấp dòng — mở rộng `planner.py` · cần QĐ-P5

Hiện `KhoPlan.khuon` chỉ gợi ý khuôn ở **cấp khổ**. Mở rộng xuống **cấp dòng**:

- Mỗi khổ nhận một phối khuôn 4 dòng. Mặc định là hai mẫu §4.3: **#7** (cổ điển) và **#10** (đảo). Hai
  mẫu này chiếm **94,67%** số cụm trong corpus người viết, nên đây là khuôn "tự nhiên" nhất để mô hình
  bắt chước. Các khổ luân phiên #7 và #10.
- Đưa vào prompt dưới dạng bảng:

  ```
  D1: P2=B  P4=T  P6=B   P7: vần nhóm A
  D2: P2=T  P4=B  P6=T   P7: tự do
  ...
  ```

- Nhóm vần lấy từ `van_cua` và `CAP_VAN_THONG`. Nếu QĐ-P5 cho phép, liệt kê thêm 3–5 tiếng vần hay gặp
  nhất trong corpus đạt cho nhóm đó.
- Kế hoạch vẫn **tất định**, vẫn không gọi mô hình (nguyên tắc đầu file `planner.py`).
- Bước B3 (`reasoning.py::_b3_nhap_khop_ke_hoach`) đã đối chiếu bản nháp với kế hoạch. Mở rộng nó
  để đối chiếu cấp dòng, **chỉ để mô tả**. Luật vẫn chỉ đòi mỗi dòng khớp **một trong hai** khuôn, nên
  lệch khỏi khung **không** phải trượt.

### 2.3. Thi liệu theo chủ đề — `datalake/scripts/dung_thi_lieu.py`

- Từ kho người viết đạt luật, rút các cụm danh từ và hình ảnh hay gặp, theo nhóm chủ đề (nhãn từ 4.1).
  Loại những cụm mà 1.2 đã đánh dấu là sáo mòn của máy.
- Mỗi yêu cầu lấy ngẫu nhiên 5–8 hình ảnh, **điền vào trường `hinh_anh` sẵn có của `PoetryPlan`**:
  planner đã có chỗ cho nó, chỉ chưa ai điền.

### 2.4. A/B

Mỗi nhánh chạy trên cùng danh sách chủ đề, cùng số ứng viên, cùng mô hình. Khổ đầu cố định khi đo việc
viết tiếp.

| Nhánh | Lời nhắc |
|---|---|
| A | hiện tại |
| B | A + one-shot |
| C | B + khung cấp dòng |
| D | C + thi liệu |
| E | D, rút gọn `BANG_LUAT_THO` trong `system.py` |

- **Chỉ số chính:** ứng viên dùng được thật (R6).
- **Chỉ số phụ:**
  - `p` (dòng khớp khuôn);
  - dòng đủ 7 tiếng;
  - tỉ lệ chép khổ trước;
  - token lời nhắc;
  - Reviewer 4 chiều;
  - trùng dòng với kho.
- Cỡ mẫu: tối thiểu như lượt 22/09 (25 chủ đề × 8 ứng viên mỗi nhánh). Hiệu ứng nhỏ thì tăng cỡ mẫu, đừng
  kết luận khi p-value của script ≥ 0,05.
- Nhánh thắng được làm mặc định **chỉ khi** chỉ số chính tăng có ý nghĩa **và** Reviewer không giảm.

**Sau khi có nhánh thắng:** đo lại `p` và **tính lại `SO_UNG_VIEN_MAC_DINH`** theo công thức đầu file
`sinh_theo_kho.py`. `p` tăng là cơ hội hạ `k`, và hạ `k` là nơi tiết kiệm chi phí thật sự nằm.

---

## Giai đoạn 3 — Cải tiến cứu khổ và đường lùi (3 ngày)

### 3.1. Bảng soi toàn khổ trước khi sửa

`dung_bien_ban` đã chỉ **tiếng nào, vị trí nào** sai thanh (`_chi_ro_thanh`), nhưng chỉ cho **dòng
lỗi**. Thêm vào lời nhắc của `_cuu_kho_bang_react` và của bước `sua_dong` một bảng do code dựng cho
**mọi dòng** của khổ: thanh ở P2/P4/P6, tiếng ở P7, dòng nào đạt và dòng nào hỏng.

Thêm vào `CHI_DAN_TU_SOI` yêu cầu: *xác nhận bảng này trước, rồi mới viết lại*. Neo cho việc này là
[NC]: xác định vần và đối trước khi làm thì độ chính xác tăng từ 0–3% lên 36%.

Bảng chỉ **mô tả**, không đề xuất chữ (R4).

### 3.2. Chọn ứng viên cứu bằng điểm liên tục

Thay `len(v.vi_pham)` trong `_chon_mot_kho` bằng điểm 1.1 (xem lý do ở 1.1). Đo tỉ lệ cứu thành công
trước và sau.

### 3.3. Khung bài cho đường lùi

Đưa khung cấp dòng (2.2) vào chỉ dẫn của `sinh_lai_kho` và `sinh_lai_ca_bai` trong `CHI_DAN_SUA`.

### 3.4. Mổ xẻ thất bại

- Với mọi bài trả 422 và mọi khổ không cứu được ở baseline: nhóm theo tầng chết và loại lỗi.
- Soi riêng lỗi **mô hình chú thích vào trong bài**. Đây là nguyên nhân số một ở tầng 2 trong
  `analysis_generate.md`: kiểm xem `_lay_cac_phuong_an` và `_lay_bon_dong` có lọc được không.

**Nghiệm thu:** tỉ lệ cứu ReAct thành công tăng; tỉ lệ đi đường lùi giảm; số bài 422 trên tập 200 đề
không tăng.

---

## Giai đoạn 4 — Đánh giá chuyên sâu (1,5 tuần)

### 4.1. Nhãn nhóm chủ đề

- Gán 200 đề vào 7 nhóm: tình yêu, quê hương – đất nước, thiên nhiên, hoài niệm, nỗi buồn, triết lý,
  đời thường. LLM gán, người kiểm ngẫu nhiên 50.
- Bám đề: cho LLM đoán nhóm từ bài thơ mà không thấy đề. Báo tỉ lệ đúng.

### 4.2. Chấm mù và Turing test

- **Backend:**
  - migration Alembic thêm bảng `danh_gia_mu` với các cột `bai_id`, `nguon_that ∈ {nguoi, may}`,
    `nguoi_cham`, `troi_chay`, `mach_lac`, `chat_tho`, `bam_de` (1–5), `doan_la_nguoi` (1–5);
  - router mới đi qua xác thực API key hiện có, tenant lấy từ khoá (G10).
- **Frontend:** trang chấm mù trong `frontend/app/`. Trộn thơ người (kho HF `bay_chu_dat`, **không**
  phải bài nổi tiếng dễ nhận ra) với thơ máy theo tỉ lệ 1:2, ẩn nguồn.
- **Mục tiêu:** ≥ 5 người chấm, mỗi người 30 bài. Đối chiếu điểm người với Reviewer. Nếu tương quan
  thấp thì Reviewer không được dùng ở 1.6.

### 4.3. Bộ probe — `evals/probes/`

Mọi đáp án do `rule.py` xác định, không do LLM.

| Probe | Cách dựng |
|---|---|
| Đoán thể | 4–8 dòng, chọn: thất ngôn tự do · tứ tuyệt Đường luật · bát cú Đường luật · thơ tám chữ. Nguồn: kho HF đã tách ở 0.2 |
| Điền tiếng | Che một tiếng ở P2/P4/P6 hoặc P7. Ba phương án nhiễu: cùng nghĩa sai thanh · đúng thanh sai vần · ngẫu nhiên |
| Ghép vần | Cho D1–D3, chọn D4 để cụm có vần chân và giữ phối khuôn |
| Sắp xếp | Xáo 4 dòng của một khổ, yêu cầu sắp lại. Chấm cả khớp hoàn toàn lẫn khớp từng phần (phối khuôn đúng, cặp vần đúng) |

- **Tập lịch sử:** bài người viết trong kho HF.
- **Tập OOS:** ≥ 100 bài chưa công khai, do nhóm tự viết. Kiểm rò rỉ bằng chỉ mục 1.3. Thơ máy sinh
  chỉ là OOS phụ, và phải ghi rõ trong báo cáo.
- Chạy mỗi probe **có và không có** `BANG_LUAT_THO` trong prompt.

---

## Giai đoạn 5 — So sánh mô hình (4 ngày)

Chạy cấu hình thắng của GĐ2 và GĐ3 trên tập 200 đề, qua các adapter đã có:

| Mô hình | Adapter | Vai trò |
|---|---|---|
| gpt-4o-mini | `openai.py` | baseline hiện tại |
| Gemma (qua Gemini API) | `google.py` (mới) | ứng viên rẻ |
| Qwen3-8B | `vllm.py` | ứng viên fine-tune cho GĐ6 |
| một mô hình mạnh (Claude Sonnet 5 hoặc GPT-4o) | `anthropic.py` / `openai.py` | mốc trên |

**Bảng kết quả gồm các cột sau.** Với mỗi mô hình, **tính lại `k`** để đạt cùng một tỉ lệ đạt, rồi so
chi phí ở `k` đó chứ không so ở cùng `k`. Mô hình rẻ mà `p` thấp có thể đắt hơn khi quy đổi.

| Cột | Nguồn |
|---|---|
| `p` | GĐ0.4 |
| `k` cần thiết | GĐ0.4 |
| tỉ lệ đạt | baseline |
| lượt gọi / bài | baseline |
| độ trễ | baseline |
| chi phí / 1.000 bài | `observability/cost.py` |
| Reviewer 4 chiều | GĐ1.4 |
| bám đề | GĐ4.1 |
| trùng dòng | GĐ1.3 |
| probe lịch sử / OOS / chênh | GĐ4.3 |

**Bàn giao:** bảng này + khuyến nghị cho QĐ-P7.

---

## Giai đoạn 6 — Sinh – chấm – học (LoRA) (2–3 tuần) · cần QĐ-P7

### 6.1. Dữ liệu — `datalake/scripts/xuat_sft.py` (mới)

- **Nhiệm vụ chính (yêu cầu → bài):** bài do chính hệ thống sinh, đã qua `PoemVerifierDayDu`, không
  trùng dòng với kho. Với mỗi đề, chỉ giữ bài có Reviewer cao nhất.
- **Prompt ngược [VN]:** cho LLM viết yêu cầu tự nhiên cho các bài `bay_chu_dat` của kho HF, để có cặp
  dữ liệu từ thơ người thật. Yêu cầu sinh ra phải đi qua `phan_tich_yeu_cau.py` và qua cổng B1.
- **Nhiệm vụ phụ [NC]:** 10–20% mẫu probe (điền tiếng, sắp xếp).
- Loại 200 đề đánh giá và toàn bộ tập OOS. Khử trùng.

### 6.2. Huấn luyện

Ngoài repo: LoRA rank 16, α 32, 2–3 epoch trên mô hình chọn ở GĐ5. Adapter lưu ngoài repo, phục vụ qua
vLLM và khai báo trong `configs/models.yaml`.

### 6.3. Vòng lặp (tối đa 3 vòng)

```
model_k sinh k ứng viên mỗi khổ trên đề huấn luyện
  → rule.py + chép + Reviewer chấm
  → giữ bài tốt nhất
  → huấn luyện model_{k+1}
```

Dừng khi `p` tăng < 1 điểm % giữa hai vòng, **hoặc khi Reviewer giảm**. Reviewer giảm là dấu hiệu thơ
cứng đi [PT].

### 6.4. Tích hợp

- Mô hình fine-tune làm **bộ sinh ứng viên** trong `sinh_tung_kho`, với `k` tính lại từ `p` đo được.
  Mô hình lớn giữ vai trò cứu ReAct và đường lùi.
- **Tuỳ chọn [RNN]:** ràng buộc lúc giải mã qua vLLM, chặn token làm sai thanh ở P2/P4/P6. Cần ánh xạ
  token → tiếng, việc này khó với tokenizer BPE. Phải làm thử nghiệm khả thi riêng trước khi cam kết.
- Bài vẫn đi qua `PoemVerifierDayDu` như mọi đường khác (R5).

**Nghiệm thu:** trên tập 200 đề, so với cấu hình thắng GĐ5:

- tỉ lệ đạt ≥;
- Reviewer không giảm;
- trùng dòng không tăng;
- lượt gọi mỗi bài giảm;
- chênh probe lịch sử/OOS không tăng.

---

## Giai đoạn 7 (tuỳ chọn) — Viết lại thành thơ (1–2 tuần) · [VN]

- Thêm trường `van_ban_nguon` vào `PoemRequest`. Người dùng dán văn xuôi hoặc thơ dịch; hệ thống viết lại
  thành thất ngôn tự do, giữ ý.
- `requirement.py`: khi có `van_ban_nguon` thì `chu_de` suy từ nguồn. Cổng B1 vẫn hỏi lại nếu thiếu
  `so_dong`.
- Đo độ giữ nghĩa bằng embedding giữa nguồn và bài. Luật không đổi một chữ.

---

## 5. Lịch

| Tuần | Giai đoạn | Bàn giao |
|---|---|---|
| 1 | −1, 0 | Test xanh, tập 200 đề, kho HF đã lọc, `cham_diem.py`, baseline + `p` |
| 2 | 1 | Điểm liên tục, chỉ mục chép, Reviewer 4 chiều + số ổn định, QĐ-P1/P2/P3 được chốt |
| 3 | 2 | One-shot, khung cấp dòng, thi liệu, bảng A/B, `k` tính lại |
| 4 | 3 + đầu 4 | Cứu khổ có bảng soi, nhãn chủ đề |
| 5 | 4 | Trang chấm mù, bộ probe, tập OOS |
| 6 | 5 | Bảng so sánh mô hình, khuyến nghị QĐ-P7 |
| 7–9 | 6 | Adapter LoRA, tích hợp, báo cáo cuối |
| 10+ | 7 | Viết lại thành thơ |

Từ GĐ−1 tới GĐ5 không cần GPU. GĐ5 cần GPU nếu tự host Qwen qua vLLM; có thể thuê theo giờ.

## 6. Rủi ro

| Rủi ro | Cách xử lý |
|---|---|
| Chi phí đo vượt dự kiến (k = 32 × 200 đề × 5 mô hình) | Chạy thử 20 đề trước mỗi lô; theo dõi `so_ung_vien_da_dung`; hạ `SO_SONG_SONG` khi gặp 429, **không** hạ `k` (chú thích trong `sinh_theo_kho.py`) |
| Reviewer không ổn định hoặc thiên vị | Đo ở 1.4; đối chiếu với người chấm ở 4.2; chiều nào không ổn định thì không dùng để xếp hạng |
| One-shot làm mô hình chép bài mẫu | Phép kiểm chép 1.3 chạy cả trên bài mẫu; chỉ số chính của A/B đã loại bản chép |
| Khung cấp dòng làm thơ gượng | Theo dõi Reviewer trong A/B; khung chỉ gợi ý, luật vẫn cho cả 16 phối khuôn |
| Nhãn `specific_genre` của HF sai | Không tin nhãn; mọi bài đi qua `rule.py` |
| Kho HF trùng với `final_data_7_chu.jsonl` | Khử trùng bằng băm ở 0.2 trước khi đếm bất cứ gì |
| `p` của Gemma thấp hơn hẳn | Kết luận đúng là đổi mô hình, không phải tăng `k` lên 64 (chú thích `SO_UNG_VIEN_MAC_DINH`) |
| Tập OOS nhỏ và không sạch tuyệt đối | Kiểm rò rỉ bằng chỉ mục 1.3; ghi rõ cỡ tập trong mọi báo cáo |
| Fine-tune làm thơ cứng | Dừng vòng lặp khi Reviewer giảm |
| Vi phạm giấy phép | Ghi nguồn CC-BY-4.0 trong README và báo cáo; không phát hành lại dữ liệu thô |

---

## Phụ lục A — Những gì của bản nháp bị bỏ hoặc đổi, và vì sao

| Bản nháp | Xử lý | Lý do |
|---|---|---|
| Mọi phần về lục bát | **Bỏ** | Hệ thống chỉ làm thất ngôn tự do |
| Công thức `0.4 × structure + 0.3 × tone + 0.3 × rhyme` | **Đổi** thành ba số rời, chờ QĐ-P1 | R2: trọng số lấy từ Songci không có nguồn cho thể này |
| Sửa `checker_ver2.py` để thêm điểm | **Đổi** thành file mới gọi `rule.py` | R1: `rule.py` đóng băng |
| Phạt lặp, mở rộng `stock_phrases` | **Bỏ**, thay bằng thống kê mô tả | R7: đã gỡ ngày 21/09 vì phạt nhầm điệp |
| Dựng chuỗi vần là việc LLM làm kém nhất | **Đổi trọng tâm** sang khuôn thanh | Số đo: tầng 4 chặn 55,29%, tầng 5 chặn 1,46% |
| Judge chen vào khoá xếp hạng | **Giữ ý**, nhưng chỉ xếp các ứng viên đã đạt, chờ QĐ-P3 | R3 |
| Gợi ý 2–3 chữ vần mỗi vị trí | **Chờ QĐ-P5** | R4 |
| Mục tiêu "99,95% → ≥ 99,9%", "2,02 → 1,2 lượt gọi" | **Bỏ** | Số của hệ thống khác; baseline của hệ thống này chưa đo |
| Mỗi đề sinh 1 lục bát + 1 bài 7 chữ | **Đổi** thành 5 độ dài 4–20 dòng | Độ dài mới là biến quyết định tỉ lệ đạt ở hệ thống này |
