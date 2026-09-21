# PLAN THI CÔNG — DeepAgent Thất Ngôn Tự Do

**Ngày lập:** 21/09/2026
**Tài liệu đích:** `docs/DeepAgent_That_Ngon_Tu_Do_Architecture.md` (1.923 dòng, 38 mục)
**Repo thi công:** cây hiện tại (`src/` kiến trúc 4 vòng), **không** dựng `poetry-agent/` mới
**Trạng thái:** ✅ ĐÃ CHỐT QĐ-D1 → QĐ-D5 · ✅ **G0 → G14 ĐÃ THI CÔNG XONG (21/09/2026)** — 788 test xanh + 9 skip (chờ Postgres)

> **Đã thi công — 530 test xanh, mypy sạch, 4 hợp đồng import-linter KEPT:**
>
> | Tệp | Thi hành chỉ thị |
> |---|---|
> | `src/application/poetry/requirement.py` | 5 — cổng thông tin đầy đủ, 5 ca hỏi lại |
> | `src/application/poetry/plan.py` | 1, 2 — kế hoạch phải hợp luật trước khi viết |
> | `src/application/poetry/quality.py` | 3 — bảy chiều chất lượng, 5 đo được / 2 không |
> | `src/application/poetry/cot.py` | 3 — khung suy luận bốn ô |
> | `src/application/poetry/reasoning.py` | 2 — sáu bước suy luận, dừng ở bước trượt đầu |
> | `src/application/poetry/verifier.py` | 1–5 — cổng chặn đầu ra, hai cờ tách rời |
> | `src/domain/guardrails/output/verification_claim.py` | §19.4 |
> | `src/adapters/tools/poem_quality.py` | 3 — Tool `danh_gia_chat_luong_tho` |
> | `tests/architecture/test_rule_dong_bang.py` | **1 — ghim SHA-256 của `rule.py`** |
>
> **G1 đã xong** — `POST /v1/poem` chạy được, 9 test hợp đồng HTTP:
>
> | Tệp | Việc |
> |---|---|
> | *(đã xoá)* `application/agent/{graph,state,nodes}` | thi hành ADR-0002 |
> | `adapters/llm/chat_port.py` | cầu `LLMClient` → `LlmPort` (nợ có chủ ý, gỡ ở G1b) |
> | `adapters/tools/executor.py` | `ToolPort` trên sổ đăng ký |
> | `adapters/rate_limit/memory.py` | `RateLimitPort` in-memory |
> | `application/poetry/prompt.py` | chỉ dẫn sinh thơ, **dựng từ bảng `LUAT`** |
> | `application/poetry/sinh_tho.py` | use case: cổng B1 → prompt → vòng ngoài |
> | `contracts/poem.py` · `entrypoints/api/routers/poem.py` | hợp đồng + router mỏng |
> | `bootstrap/container.py` | 4 trường mới, bỏ `agent_graph` |
>
> **Bổ sung 21/09/2026 — ba việc nữa đã xong:**
>
> | Việc | Tệp |
> |---|---|
> | **Ca 5** — không nói số dòng thì hỏi lại (bội của 4) | `application/poetry/requirement.py` |
> | **Gọi tool đã thông** — sửa đủ 5 tầng từng chặn nó | `ports/llm_client.py` · `adapters/llm/{openai,anthropic,mock,chat_port}.py` |
> | **G6a — vá lỗ streaming bỏ qua output rails** 🔴 | `domain/guardrails/output/streaming.py` · `routers/chat.py` |
>
> **Lượt 3, 21/09/2026 — G1b và G6 xong:**
>
> | Việc | Kết quả |
> |---|---|
> | **G1b** — tách ba port theo trách nhiệm | `ports/{embedding,streaming,generation}.py`; xem **ADR-0005** |
> | cưỡng chế cổng hẹp | `tests/architecture/test_port_hep.py` — quét AST, cấm `application/`+`entrypoints/` import `LLMClient` |
> | **G6b** — nối topic filter, ba mức SAFE/REVIEW/BLOCK | `domain/guardrails/input/topic.py`, nối vào cả `/v1/chat` lẫn `/v1/poem` |
> | input rails cho đường thơ | `/v1/poem` trước đây KHÔNG có rào đầu vào nào |
> | bảng đe doạ §20 | `tests/unit/domain/test_threat_matrix.py`, dataset 3 → 13 ca |
>
> **Hai lỗi thật phát hiện khi làm**, đều có test hồi quy:
> 1. mẫu `hack ngân hàng` không bắt được chính ca `adv-003` của dataset mình
> 2. `check_forbidden_topics` tồn tại từ lâu nhưng **không đường nào gọi tới**
>
> **Lượt 4, 21/09/2026 — G3 (Knowledge / few-shot) xong:**
>
> | Việc | Kết quả |
> |---|---|
> | Lược đồ chuẩn §9.2 | `application/poetry/dataset.py` — **chạy lại `rule.py`, không tin nhãn trong dữ liệu** |
> | Cổng kho thơ | `ports/poem_corpus.py` + `adapters/persistence/corpus/jsonl.py` |
> | Bộ chọn §26–28 | `application/poetry/fewshot.py` — zero/one/few-shot theo SỐ ràng buộc người dùng nêu |
> | Tập tuyển commit được | `datalake/corpus_tuyen/tho_mau.jsonl` — 300 bài, 149 KB, sinh bằng `datalake/scripts/tuyen_tho_mau.py` |
> | Nối vào prompt | ví dụ bọc thẻ `<vi_du_dung_luat>` riêng, tách khỏi `<yeu_cau_bai_tho>` |
>
> **Bất biến trung tâm, giữ bởi KIỂU DỮ LIỆU chứ không bởi kỷ luật:** `MauTho` chỉ
> dựng được từ bài đã qua `kiem_tra_bai_tho`, nên không có đường nào đưa một bài
> sai luật vào prompt. 25 test, trong đó một test quét **toàn bộ** tập tuyển.
>
> **Đối sách R2 đã thi hành:** bộ chọn ưu tiên bài **cùng số dòng** trước khi xét
> chủ đề — vì cổng 4 (thanh luật) chặn 55,29% corpus còn chủ đề không chặn bài nào.
>
> **Lượt 5, 21/09/2026 — G2 · G4 · G5 · G7 · G8, hết plan:**
>
> | GĐ | Việc | Tệp |
> |---|---|---|
> | **G2** | Requirement Analyzer §7.2 — **bắt trích dẫn, rồi kiểm trích dẫn có thật** | `poetry/phan_tich_yeu_cau.py` |
> | **G4** | Planner §10 (tất định) · State Machine §31 (14 trạng thái, bảng chuyển được cưỡng chế) | `poetry/planner.py` · `poetry/state.py` |
> | **G5** | evidence: `duong_di`, `che_do_vi_du`, `id_vi_du`, `quyet_dinh_hitl` vào response | `contracts/poem.py` |
> | **G7** | HITL §22 (5 quyết định) · Feedback §24 (**van chặn giữa lời khen và kho mẫu**) | `domain/policy/hitl.py` · `poetry/feedback.py` |
> | **G8** | Benchmark §33, 6 nhóm, chạy offline | `evals/run_poetry.py` · `evals/metrics/{poetry,safety_hitl}.py` |
>
> **Ba lỗi thật phát hiện khi thi công, đều có test hồi quy:**
> 1. **B3 chặn vì số khổ** — vi phạm N2, vì S18 cho phép viết liên hoàn. B3 nay chỉ kiểm tổng số dòng.
> 2. **Bộ trích đọc nhầm khung JSON mẫu** (`"..."`) thành dữ liệu khi provider lặp lại prompt.
> 3. **Gọi mô hình vô ích** khi thứ duy nhất còn thiếu là `so_dong` — vốn do regex tất định lo.
>
> **Ba nhóm metric §33.1/2/4 được ghi rõ là CHƯA đo được offline** (đòi provider
> thật hoặc người chấm) thay vì để trống — nguyên tắc N3.

> **Năm chỉ thị của chủ dự án, 21/09/2026 — nguyên văn:**
>
> 1. *"Rule của tôi phải là không được thay đổi."*
> 2. *"Cần tuân thủ quy định về bằng trắc của tôi: chi tiết từng bước tạo thơ cần có kiểm
>    tra từng bước suy luận của Agent và kiểm tra Output trước khi trả cho người dùng."*
> 3. *"Giữ nguyên file Rule này, thiết kế cho tôi một Tool cho phần này, cần kiểm tra đầy
>    đủ chất lượng của LLM; nếu không đạt được thì cần Chain-of-thought trước khi trả ra
>    kết quả."*
> 4. *"Lấy ý tưởng tách node, bỏ cây thư mục."*
> 5. *"Cần thỏa mãn đầy đủ mọi thông tin trước khi cho thơ cho người dùng."*
>
> Hệ quả trực tiếp: **`src/application/rule.py` bị ĐÓNG BĂNG.** Không một dòng nào của tệp
> đó được sửa trong toàn bộ plan này. Mọi thứ mới đều *cộng thêm bên ngoài*, gọi vào
> `kiem_tra_bai_tho()` như một hộp đen. Có test kiến trúc cưỡng chế điều này (xem §5.5).

> Plan này KHÔNG phải bản dịch tài liệu đích sang danh sách việc. Nó là bản **đối chiếu**:
> tài liệu đòi gì, repo đã có gì, chỗ nào hai bên nói ngược nhau, và thi công theo thứ tự
> nào để mỗi giai đoạn đều cho ra thứ chạy được.

---

## 0. Kết luận một trang

**Tin tốt:** tài liệu đích đòi 38 hạng mục; repo **đã có sẵn khoảng 55%**, và phần đã có
lại đúng là phần khó nhất — bộ kiểm luật tất định (`rule.py`, bảy tầng, 453 test) và vòng
sinh–kiểm–sửa bắt buộc (`verify_output.py`, 7 chặn cứng G1–G7).

**Tin xấu:** phần đã có **chưa nối vào bất kỳ entrypoint nào**. `generate_with_verification`
và `PoemVerifier` hiện chỉ được gọi trong test. Gọi `POST /v1/chat` xin một bài thơ hôm nay
thì không có cổng kiểm nào chạy.

**Vì vậy thứ tự thi công đảo so với §37 của tài liệu.** Tài liệu xếp Phase 1 = Requirement,
Phase 3 = DeepAgent, Phase 4 = Tools. Plan này đặt **G1 = nối lõi đã có vào một API thật**,
vì đó là việc nhỏ nhất cho ra giá trị lớn nhất, và vì mọi giai đoạn sau đều cần một đường
dây end-to-end để đo.

| | Tài liệu §37 | Plan này |
|---|---|---|
| Việc đầu tiên | PoetryRequest Schema | **Nối `PoemVerifier` vào `POST /v1/poem`** |
| Lý do | theo thứ tự luồng dữ liệu | theo thứ tự **rủi ro giảm nhanh nhất** |

**Tám giai đoạn G0 → G7.** G0 không viết code. Sau G1 đã có sản phẩm dùng được. G5 trở đi
là phần làm cho nó đáng tin, không phải làm cho nó chạy.

---

## 1. Sáu nguyên tắc thi công

Kế thừa N1–N4 của `Plan_Rule_Phan_Tang.md`, thêm sáu điều riêng cho tầng agent.

| # | Nguyên tắc | Vì sao |
|---|---|---|
| **P1** | **Một nguồn luật duy nhất.** Mọi phép kiểm thơ, ở mọi tool, mọi node, mọi test, đều gọi `application.rule.kiem_tra_bai_tho`. Không viết lại phép đếm tiếng ở chỗ thứ hai. | Hai bộ luật song song là cách chắc chắn nhất để hai nơi nói hai điều khác nhau. Đây cũng là chỗ plan này **từ chối** §12.2 của tài liệu — xem QĐ-D3. |
| **P2** | **Bộ kiểm phán, mô hình sửa.** Không dòng code nào được sửa văn bản thơ. | Sửa bằng code là âm thầm thay đổi tác phẩm rồi ghi lại như thể mô hình viết ra như thế. |
| **P3** | **Fail closed.** Hết lượt sửa thì trả lỗi, không trả bài "gần đúng". Không có evidence thì không được tuyên bố "đúng luật" (§19.4). | Một bài sai luật lọt ra nguy hiểm hơn một lỗi 422. |
| **P4** | **Mỗi giai đoạn phải cho ra thứ chạy được và đo được.** Không có giai đoạn nào chỉ "dựng khung, giai đoạn sau mới dùng". | Repo này đã có sẵn bài học: `agent/graph`, `pipeline/handle_message` đều dựng xong rồi nằm im trong test. |
| **P5** | **Node mới phải là hàm thuần + tiêm phụ thuộc qua tham số**, trả `Result[T, BotError]` hoặc tagged union, so khớp bằng `isinstance`. | Đúng quy ước đang chạy (`plan-tang-agents.md` §1.3, §1.4, §1.6). Đừng đem kiểu thứ hai vào. |
| **P6** | **Cưỡng chế bằng máy, không bằng review.** Mỗi ràng buộc kiến trúc phải có một test hoặc một hợp đồng `import-linter` giữ nó. | Bốn hợp đồng hiện tại đang KEPT. Thêm code mà không thêm hợp đồng là làm loãng dần. |

---

## 2. ĐỐI CHIẾU — tài liệu đòi gì, repo có gì

Đọc bảng này trước khi đọc phần giai đoạn. Cột "Còn thiếu" chính là toàn bộ khối lượng công việc.

### 2.1. Đã có, dùng được ngay (không phải viết lại)

| Tài liệu | Repo hiện có | Ghi chú |
|---|---|---|
| §3.4 Verification-first | `pipeline/stages/verify_output.py` | Đủ và hơn: 7 chặn cứng G1–G7 |
| §14 Verification Loop + `MAX_REVISION` | `max_repair_rounds`, `_chien_luoc_cho_luot` | Có thêm phát hiện không-tiến-bộ (G5) và phát hiện lặp bằng hash (G6) |
| §15 Revision Agent "không viết lại cả bài nếu chỉ một dòng sai" | thang `sua_dong → sinh_lai_kho → sinh_lai_ca_bai` | Tài liệu nói nguyên tắc, repo đã có cả thang leo thang |
| §12.2 Tool 2/3/4/5/6 (syllable, rhyme, tone, structure, rules) | `adapters/tools/poem_check.py` → `rule.py` | Một tool tổng thay vì năm tool — xem QĐ-D3 |
| §17 Input Rails | `domain/guardrails/input/{injection,length,pii,topic}.py` | Có sẵn cả bốn, `topic.py` chưa được nối |
| §19 Output Rails | `domain/guardrails/output/{citation,policy,schema,toxicity}.py` | Thiếu đúng §19.4 (verification claim) |
| §9 Retrieval | `application/rag/{retriever,reranker,context_builder}.py` + `ingest/` | Hybrid BM25+dense+RRF, đã có |
| §30 Memory (short-term / session) | `application/memory/{session,profile}.py` | Knowledge & feedback memory còn thiếu |
| §24 Feedback record | `contracts/feedback.py` + `routers/feedback.py` | Schema hẹp hơn §24 |
| §32 Failure Handling | `domain/common/errors.py`, `is_retryable`, `is_silent`, `FallbackManager` | Đã phân loại lỗi tạm/vĩnh viễn |
| §33 Evaluation | `evals/run.py`, `evals/metrics/`, 3 dataset | Thiếu metric thơ |
| §5.2 State | `PoemVerdict`, `ContextEnvelope`, `PipelineDeps` | State hẹp hơn, chưa có trạng thái xuyên node |

### 2.2. Chưa có — khối lượng công việc thật

| Tài liệu | Còn thiếu | Giai đoạn |
|---|---|---|
| §7.2 Requirement Analyzer | toàn bộ | **G2** |
| §8 Clarification Gate | toàn bộ | **G2** |
| §10 Planner (`PoetryPlan`) | toàn bộ | **G4** |
| §11 Writer chuyên thơ | có `generate_react_loop` nhưng chưa có prompt/plan thơ | **G4** |
| §9.2 Canonical schema + adapter dataset thơ | toàn bộ | **G3** |
| §26–28 Zero/One/Few-shot selector | toàn bộ | **G3** |
| §19.4 Cấm tuyên bố "đúng luật" không evidence | toàn bộ | **G5** |
| §16 Guardrails cho **streaming** | **đang là lỗ hổng** — nhánh stream bỏ qua output rails | **G6** |
| §20 Safety Threat Matrix (bộ test đối kháng) | một phần (`adversarial.jsonl` chưa nối) | **G6** |
| §21–23 HITL (3 chế độ, decision engine, review interface) | toàn bộ | **G7** |
| §24 Feedback → Quality Review → Validated Example | toàn bộ | **G7** |
| §31 State Machine 14 trạng thái | toàn bộ | **G4** (dựng), **G7** (đủ) |
| §33.3–33.6 metric thơ / agent / safety / HITL | toàn bộ | **G8** |
| Nối bất kỳ thứ gì ở trên vào API | **toàn bộ** | **G1** |

---

## 3. NĂM QUYẾT ĐỊNH — ✅ ĐÃ CHỐT 21/09/2026

Cả năm đều là chỗ tài liệu đích nói ngược với thứ đang chạy. Chủ dự án đã chốt **giữ
`rule.py` nguyên vẹn ở cả năm chỗ**. Mỗi mục dưới đây nêu: tài liệu nói gì, repo nói gì,
và quyết định cuối cùng.

---

### QĐ-D1 — Số tiếng mỗi dòng: cứng hay mềm? ✅

**Tài liệu §10 (Planner), nguyên văn:**

> *"Mỗi dòng hướng tới 7 tiếng, nhưng cho phép biến đổi nếu user không yêu cầu ràng buộc cứng."*

**`rule.py` H1 + H2:**

> *"Mỗi dòng phải có đúng 7 tiếng. Ràng buộc này áp dụng cho toàn bộ các dòng, không có ngoại lệ."*

Và chủ dự án đã đính chính rõ, ghi trong docstring `_tang2_do_dai`:
*"Chỉ cần một dòng 6 đến 8 tiếng sẽ làm hỏng cả bài thơ nên là bài này hỏng."*

Hai câu này **không thể cùng đúng**. Nếu 7 tiếng "cho phép biến đổi" thì H1 không còn là
luật cứng, và bảy tầng sụp từ tầng 2.

**Đề nghị: giữ H1/H2 là cứng tuyệt đối, bỏ vế "cho phép biến đổi" của §10.**

Lý do: H1 là *điều kiện nhận diện thể*. Bỏ nó thì sản phẩm không còn là "thất ngôn tự do"
nữa, chỉ là thơ tự do. Ngoài ra §10 tự mâu thuẫn với chính §3.4 của tài liệu
("LLM không tự tuyên bố đúng luật") — nếu số tiếng co giãn thì không có gì để verify.

> ✅ **CHỐT: giữ H1/H2 cứng tuyệt đối.** Chỉ thị 1 — *"Rule của tôi phải là không được
> thay đổi."* Vế *"cho phép biến đổi"* của §10 bị **loại bỏ** khỏi phạm vi thi công.
> `PoetryPlan.line_plan` không được mang trường số tiếng linh hoạt.

---

### QĐ-D2 — Thanh luật và vần: tài liệu đích **nới**, dự án đang **siết** ✅

**Tài liệu §3.3:**

> *"Không mặc định mọi dòng phải theo cùng một mô hình bằng/trắc cố định."*
> *"Không ép một mô hình vần duy nhất nếu yêu cầu thuộc thơ tự do."*

**Dự án, QĐ-1 + QĐ-2 (đã chốt 18/09):** tầng 4 đòi **mọi** dòng khớp một trong hai khuôn
`B T B` / `T B T` ở P2/P4/P6, **không cho phá khuôn**. Đây là cổng chặn khắt khe nhất —
chặn 30.571/55.297 bài, tức **55,29%**.

**Dự án, QĐ-7b:** tầng 5 đòi mỗi bài phải có ít nhất một cụm 4 dòng liên tiếp có vần chân.
S8 *"bài có thể không gieo vần"* đã bị **xoá khỏi bảng luật** vì lý do này.

Tức là tài liệu đích nói "đừng ép", còn bộ luật đang chạy thì **đang ép**, và đã đo được
cái giá: hơn một nửa corpus bị loại ở đúng chỗ tài liệu bảo đừng ép.

**Đề nghị: giữ QĐ-1, QĐ-2, QĐ-7b; đọc §3.3 là nói về *thể loại*, không phải về *chuẩn sinh*.**

Phân biệt hai câu hỏi khác nhau — đây chính là chỗ `PoemVerdict` đã tách sẵn hai cờ:

| Câu hỏi | Cờ | Ai trả lời | Áp cho |
|---|---|---|---|
| "Bài này có thuộc thể thất ngôn tự do không?" | `thuoc_the` | tài liệu luật (H1–H4) | **kiểm** thơ có sẵn |
| "Bài này có đạt chuẩn dự án không?" | `dat` | QĐ-1 → QĐ-7b | **sinh** thơ mới |

§3.3 đúng cho cột trên, QĐ-1/QĐ-2 đúng cho cột dưới. DeepAgent **sinh** thơ, nên dùng `dat`.
Hai cờ đã tồn tại sẵn trong code, không phải thêm gì.

> ✅ **CHỐT: giữ QĐ-1, QĐ-2, QĐ-7b nguyên vẹn.** Chỉ thị 2 — *"Cần tuân thủ quy định về
> bằng trắc của tôi."* Chuẩn sinh của DeepAgent là cờ `dat` (cả bảy tầng), không phải
> `thuoc_the`.
>
> Hệ quả đã được chấp nhận: vòng sửa sẽ chạy nhiều lượt hơn vì mô hình phải khớp khuôn
> B/T ở **mọi** dòng. Rủi ro R2 (§6) vì vậy **không còn là câu hỏi mở về luật** — nó trở
> thành bài toán kỹ thuật: làm cho mô hình đạt được chuẩn đó, chứ không phải hạ chuẩn.
> Ba đối sách còn lại của R2 (prompt có bảng khuôn, few-shot cùng phối khuôn, tăng lượt
> sửa) đều được thi hành; đối sách thứ tư (nới QĐ-2) **đã bị loại bỏ vĩnh viễn**.

---

### QĐ-D3 — Bảy tool riêng lẻ hay một tool tổng? ✅

**Tài liệu §12.2** liệt kê 7 tool, trong đó 5 tool kiểm thơ tách rời: `count_syllables`,
`check_rhyme`, `check_tone`, `check_structure`, `check_poetry_rules`.

**Repo** có đúng một tool `kiem_tra_tho`, gọi thẳng `kiem_tra_bai_tho()`.

Tách năm tool là đi ngược nguyên tắc trung tâm của `rule.py`, ghi ở §9b quy ước 1:

> *"phân tích làm một lần ở `kiem_tra_bai_tho` rồi dùng chung, để bảy tầng không thể hiểu
> khác nhau về cùng một dòng thơ."*

Năm tool riêng nghĩa là năm chỗ tự tách tiếng. Đến một ngày `count_syllables` và
`check_rhyme` sẽ bất đồng về việc "ra-đi-ô" là mấy tiếng, và không ai biết.

Hệ quả kéo theo: **§22.3 Human Tiebreaker mất đối tượng.** Tài liệu định nghĩa tiebreaker là
lúc *"Rule Checker A ≠ Rule Checker B"*. Với một nguồn luật tất định, tình huống đó **không
bao giờ xảy ra**. Giữ nguyên định nghĩa ấy là dựng một nhánh code chết.

**Đề nghị:**

1. **Giữ một tool tổng**, nhưng cho nó tham số `pham_vi` để trả về **lát cắt** thay vì cả biên bản:
   ```
   kiem_tra_tho(van_ban, pham_vi=["so_tieng"])       ≈ count_syllables
   kiem_tra_tho(van_ban, pham_vi=["van"])            ≈ check_rhyme
   kiem_tra_tho(van_ban, pham_vi=["thanh"])          ≈ check_tone
   kiem_tra_tho(van_ban, pham_vi=["kho"])            ≈ check_structure
   kiem_tra_tho(van_ban)                             ≈ check_poetry_rules
   ```
   Mô hình có đúng trải nghiệm §13 (Tool Decision Policy: gọi cái cần, không gọi máy móc
   tất cả), còn hệ thống vẫn có một nguồn luật. Chi phí gọi không đổi — `rule.py` thuần và
   chạy trong mili-giây.
2. **Giữ `evaluate_poetry_quality` (Tool 7) tách riêng thật**, vì nó là phán đoán ngữ nghĩa,
   khác hẳn loại. Đúng như tài liệu dặn: *"Không dùng điểm quality để thay thế các rule
   checker có thể kiểm chứng bằng thuật toán."*
3. **Định nghĩa lại Human Tiebreaker** (§22.3) thành: *luật cứng đạt, nhưng
   `evaluate_poetry_quality` thấp hoặc chủ đề nhạy cảm*. Đó mới là mâu thuẫn có thật giữa
   hai loại bằng chứng khác loại.

> ✅ **CHỐT cả ba ý.** Chỉ thị 3 — *"Giữ nguyên file Rule này, thiết kế cho tôi một Tool
> cho phần này."* Thiết kế đầy đủ của Tool đó ở **§5.5** (mới). Tool thứ hai
> (`danh_gia_chat_luong_tho`) cũng ở §5.5, kèm cơ chế Chain-of-thought.

---

### QĐ-D4 — `agent/graph/` của §36 chọi với ADR-0002 ✅

**Tài liệu §36** đề xuất cây mới `poetry-agent/` với `agent/graph/main_graph.py`, `state.py`,
`routing.py`.

**ADR-0002** (17/09, trạng thái *đề xuất*) đề nghị **gỡ bỏ** `application/agent/graph.py`,
`state.py`, `nodes/` — vì chúng dùng Pydantic khả biến, ném exception thay vì `Result`, phụ
thuộc trực tiếp thay vì qua port, và `while not state.is_finished` không có trần ngân sách.

Làm theo §36 nguyên văn = khôi phục đúng thứ ADR-0002 đang đề nghị vứt.

**Đề nghị: lấy *ý tưởng* §36, bỏ *cây thư mục* §36.**

Cái đúng của §36 là **tách node theo trách nhiệm**. Cái sai là gợi ý một kiến trúc graph
khả biến song song với 4 vòng đang chạy. Ánh xạ ở §4 dưới đây giữ nguyên ý tưởng, đặt vào
đúng vòng.

Kèm theo: **thi hành ADR-0002 trong G1** (gỡ `agent/{graph,state,nodes}`, bỏ `agent_graph`
khỏi `AppContainer`), và hợp nhất `ports/llm.py` với `ports/llm_client.py` — hiện đang có
hai định nghĩa "gọi mô hình là gì" trong một hệ thống.

> ✅ **CHỐT: lấy ý tưởng tách node, bỏ cây thư mục.** Chỉ thị 4, nguyên văn. Bảng ánh xạ
> 17 dòng ở §4 là bản thi hành của quyết định này.

---

### QĐ-D5 — H4 (bội của 4) không có trong tài liệu đích ✅

Tài liệu DeepAgent **không nhắc H4 một lần nào**. §10 chỉ nói *"Structure: 4 khổ"*, §7.2 chỉ
có trường `length`.

Nhưng H4 là luật **cứng, không ngoại lệ** (18/09): số dòng phải là bội của 4, và bài không
thoả thì *không thuộc thể*. Tầng 1 chặn 4.668 bài vì điều này.

Hệ quả bắt buộc cho Requirement Analyzer: **nếu người dùng xin "6 dòng" thì đó là một yêu
cầu không thể đáp ứng**, phải vào Clarification Gate chứ không được im lặng làm 8 dòng.

Và `_tang1_hinh_thuc` đã dặn sẵn cách xử lý đúng:

> *"Với thơ do mô hình SINH RA, ràng buộc này thuộc về ĐỀ BÀI ('viết N dòng, N là bội của
> 4'), không phải về vòng sửa một bản nháp đã có."*

Tức là H4 phải được chặn ở **tầng yêu cầu**, không phải ở vòng sửa — sửa H4 nghĩa là thêm
hoặc xoá câu thơ, điều P2 cấm.

**Đề nghị:** thêm trường hợp 4 vào §8.2 Clarification Gate:

> *"Bạn yêu cầu 6 dòng, nhưng thể thất ngôn tự do của hệ thống này đòi số dòng là bội của 4.
> Bạn muốn 4 dòng hay 8 dòng?"*

> ✅ **CHỐT: H4 giữ nguyên, chặn ở tầng yêu cầu.** Chỉ thị 1 + chỉ thị 5 — *"Cần thỏa mãn
> đầy đủ mọi thông tin trước khi cho thơ cho người dùng."* Xin 6 dòng là yêu cầu không
> thể đáp ứng, phải hỏi lại, **không được im lặng làm 8 dòng**.

---

## 4. ÁNH XẠ §36 VÀO KIẾN TRÚC 4 VÒNG

§36 đề xuất một cây phẳng. Đặt nguyên cây đó vào repo sẽ phá bốn hợp đồng `import-linter`
đang KEPT. Bảng dưới là bản dịch, giữ nguyên trách nhiệm từng thành phần.

| §36 đề xuất | Đặt vào đâu trong repo | Vòng | Vì sao |
|---|---|---|---|
| `agent/graph/state.py` | `application/poetry/state.py` | 2 | State thuần, frozen dataclass, không I/O |
| `agent/graph/main_graph.py` + `routing.py` | `application/poetry/workflow.py` | 2 | Orchestrator tường minh, đánh số bước — theo mẫu `handle_message.py`, **không** dùng graph khả biến (QĐ-D4) |
| `agent/nodes/input_validator.py` | *(đã có)* `domain/guardrails/input/` | 1 | Luật thuần, không cần node riêng |
| `agent/nodes/requirement_analyzer.py` | `application/poetry/requirement.py` | 2 | Cần LLM → qua `LlmPort` |
| `agent/nodes/clarification.py` | `application/poetry/clarification.py` | 2 | Hàm thuần trên `PoetryRequirement` |
| `agent/nodes/researcher.py` | *(đã có)* `application/rag/` + `poetry/fewshot.py` | 2 | Tái dùng retriever hiện có |
| `agent/nodes/planner.py` | `application/poetry/planner.py` | 2 | |
| `agent/nodes/writer.py` | `application/poetry/writer.py` | 2 | Bọc `generate_react_loop` |
| `agent/nodes/verifier.py` + `reviser.py` | *(đã có)* `pipeline/stages/verify_output.py` | 2 | Đã gộp sẵn hai vai, đúng §14+§15 |
| `agent/nodes/reviewer.py` | `application/poetry/review.py` | 2 | Tool 7 quality |
| `agent/prompts/*.md` | *(đã có)* `adapters/prompts/templates/` | 3 | Registry YAML đã có versioning |
| `tools/*.py` | *(đã có)* `adapters/tools/poem_check.py` + `poem_quality.py` mới | 3 | Theo QĐ-D3 |
| `safety/*.py` | *(đã có)* `domain/guardrails/` + `domain/policy/` | 1 | |
| `hitl/decision_engine.py` | `domain/policy/hitl.py` | **1** | Hàm thuần trên số liệu — thuộc vòng trong cùng |
| `hitl/human_review.py` | `entrypoints/admin/` + `application/poetry/review_queue.py` | 4 + 2 | Giao diện thuộc entrypoint |
| `knowledge/data/poetry_dataset.json` | `datalake/` *(đã có corpus)* | — | Xem G3 |
| `knowledge/ingestion.py` + `retriever.py` | *(đã có)* `application/ingest/` + `rag/` | 2 | |
| `evaluation/` | *(đã có)* `evals/` | — | |

**Một hợp đồng `import-linter` mới cần thêm ở G2** (cưỡng chế P1):

```ini
[importlinter:contract:mot-nguon-luat-tho]
name = Chi rule.py duoc dinh nghia luat tho
type = forbidden
source_modules =
    application.poetry
    adapters.tools
forbidden_modules =
    re
# ngoại lệ: các module được phép dùng regex cho việc khác
ignore_imports =
    ...
```

> Ghi chú: hợp đồng trên là *phác thảo ý định*, cách cưỡng chế cụ thể cần thử — nhiều khả
> năng một test AST quét `application/poetry/` tìm chuỗi tách tiếng sẽ hiệu quả hơn hợp đồng
> import. Chốt cách làm ở đầu G2.

---

## 5. TÁM GIAI ĐOẠN

Mỗi giai đoạn có: **mục tiêu · tệp đụng tới · nghiệm thu · ước lượng**.

Ước lượng tính theo *phiên làm việc* (≈ nửa ngày tập trung), không phải ngày lịch.

---

### G0 — Chốt quyết định, đặt lại trạng thái tài liệu ⬜ *(0 code)*

**Mục tiêu:** hết mơ hồ trước khi tốn công.

| Việc | Đầu ra |
|---|---|
| Chủ dự án trả lời QĐ-D1 → QĐ-D5 | 5 dòng gật/bác, ghi thẳng vào §3 của plan này |
| Thêm khối trạng thái vào đầu `DeepAgent_..._Architecture.md` | *"ĐÍCH — chưa thi công. Thi công theo `Plan_Thi_Cong_DeepAgent.md`. Các chỗ đã bị QĐ-D1→D5 ghi đè: §3.3, §10, §12.2, §22.3, §36."* |
| Commit file đó (hiện đang untracked) | git tracked |
| ADR-0002 → *chấp nhận* hoặc *bác bỏ* | không để ở "đề xuất" nữa |
| Viết ADR-0004: "Thi công DeepAgent trong cây hiện tại, không dựng `poetry-agent/`" | `docs/adr/0004-*.md` |
| Sửa `plan-tang-agents.md`: thêm cảnh báo tên module thuộc dự án tiền thân | tránh người mới đi tìm `agents/ports/` |

**Nghiệm thu:** không còn tài liệu nào trong `docs/` mô tả một cây thư mục không tồn tại
mà không ghi rõ điều đó.

**Ước lượng:** 1 phiên (chủ yếu là chủ dự án quyết).

---

### G1 — Nối lõi đã có vào API thật ⭐ *(giai đoạn quan trọng nhất)*

**Mục tiêu:** `POST /v1/poem` trả về một bài thơ **đã qua bảy tầng**, hoặc lỗi có chẩn đoán.
Không thêm tính năng mới nào — chỉ thu hoạch P1→P3b đang nằm im.

**Vì sao đặt đầu tiên:** mọi giai đoạn sau đều cần một đường dây end-to-end để đo. Không có
nó thì G2–G7 lại tiếp tục là code chỉ chạy trong test — đúng vết xe của `agent/graph`.

**Việc:**

1. **Thi hành ADR-0002** (theo QĐ-D4):
   - xoá `application/agent/{graph.py,state.py,nodes/}`
   - bỏ trường `agent_graph` khỏi `AppContainer`, bỏ import trong `container.py`
   - hợp nhất `ports/llm_client.py` vào `ports/llm.py` (giữ `LlmPort`, chuyển `rag/`,
     `ingest/`, adapters sang dùng nó)
2. **Ba adapter cầu còn thiếu** — hiện `verify_output` cần 3 port mà container chưa dựng:
   - `adapters/llm/chat_port.py` — hiện thực `LlmPort.reply()` trên provider hiện có
   - `adapters/tools/executor.py` — hiện thực `ToolPort` trên `tool_registry`
   - `adapters/rate_limit/memory.py` — hiện thực `RateLimitPort` in-memory
3. **`AppContainer` thêm:** `verifier: OutputVerifier`, `chat_llm: LlmPort`, `tools: ToolPort`,
   `rate_limiter: RateLimitPort`
4. **Contract mới** `contracts/poem.py`:
   ```
   PoemRequest   : yeu_cau, so_dong?, chu_de?, max_repair_rounds
   PoemResponse  : poem, dat, so_luot_sua, chien_luoc_cuoi,
                   bang_chung_bay_tang[], mo_ta_mem[], trace_id
   ```
   `bang_chung_bay_tang` lấy thẳng `KetQuaTang.bang_chung` + `chi_tiet` — đây chính là
   *Evidence* mà §3.4 và §19.2 đòi, và nó đã có sẵn.
5. **Router** `entrypoints/api/routers/poem.py` → gọi `generate_with_verification`
6. **Ánh xạ lỗi:** `OutputKhongDat` → HTTP 422 kèm `chan_doan`. Không trả bài sai (P3).

**Nghiệm thu:**

- `curl POST /v1/poem` với provider `mock` trả 200 kèm bảy khối bằng chứng, hoặc 422 kèm chẩn đoán
- Test contract mới trong `tests/contract/test_poem_api.py`: **không đường nào trả 200 với
  bài mà `kiem_tra_bai_tho(poem).dat == False`** — đây là test quan trọng nhất của cả plan
- `make check` xanh (lint + mypy + `lint-imports` + 453 test cũ vẫn xanh)
- `grep -rn "generate_with_verification" src/` có kết quả **ngoài** `tests/`

**Ước lượng:** 3–4 phiên. Phần lớn là mục 1 và 2.

**Rủi ro:** hợp nhất hai `LlmPort` đụng vào `rag/`, `ingest/`, 4 adapter LLM. Nếu quá rộng,
tách thành G1a (dựng adapter cầu + router, giữ nguyên hai port) và G1b (hợp nhất port).

---

### G2 — Requirement Analyzer + Clarification Gate

**Mục tiêu:** hệ thống biết hỏi lại thay vì đoán (§3.2, §7.2, §8).

**Tệp mới:**

```
application/poetry/requirement.py   PoetryRequirement (frozen) + trích xuất qua LlmPort
application/poetry/clarification.py danh_gia_du_thong_tin() -> Du | CanHoi   (hàm THUẦN)
domain/poetry/__init__.py           từ vựng miền: ChuDe, CamXuc, PhongCach
```

**Thiết kế `PoetryRequirement`** — mở rộng §7.2, thêm hai trường tài liệu thiếu:

| Trường | Nguồn | Ghi chú |
|---|---|---|
| `the_tho` | §7.2 `form` | cố định `that_ngon_tu_do` ở bản đầu |
| `chu_de`, `cam_xuc`, `phong_cach` | §7.2 | |
| `so_dong` | §7.2 `length` | **phải là bội của 4** — QĐ-D5 |
| `rang_buoc_van`, `rang_buoc_thanh` | §7.2 | |
| `so_kho`, `rang_buoc_rieng` | §7.2 `custom_constraints` | |
| **`nguon_tung_truong`** | *thêm* | mỗi trường ghi rõ: người dùng nói, hay hệ thống mặc định |

Trường cuối là bổ sung của plan, không có trong tài liệu, và cần thiết: §3.2 cấm "tự suy
đoán khi thông tin quan trọng bị thiếu" — nhưng nếu không ghi lại trường nào là suy đoán thì
không ai kiểm được là đã tuân thủ hay chưa. Đây là nguyên tắc N3 (*ghi công khai điều không
kiểm được*) áp cho tầng yêu cầu.

**Clarification Gate — bốn ca**, ba ca đầu từ §8.2, ca 4 từ QĐ-D5:

| Ca | Kích hoạt | Câu hỏi |
|---|---|---|
| 1 | thiếu chủ đề | "Bạn muốn bài thơ viết về chủ đề nào?" |
| 2 | mâu thuẫn thể loại (xin tự do + đòi luật bát cú) | "Ưu tiên đặc trưng tự do hay luật bằng-trắc bát cú?" |
| 3 | ràng buộc mơ hồ ("vần thật chặt") | "Vần chân theo mô hình cố định hay liên kết vần tự nhiên?" |
| **4** | **`so_dong` không phải bội của 4** | **"Số dòng phải là bội của 4 — bạn muốn 4 hay 8 dòng?"** |

**Nghiệm thu:**

- Bảng 4 ca chạy được bằng test, mỗi ca một test
- Test: **không ca nào Gate tự điền `chu_de`** khi người dùng không nói (cưỡng chế §3.2)
- Test: `so_dong` trả về luôn thoả `% 4 == 0` hoặc Gate hỏi lại

**Ước lượng:** 3 phiên.

---

### G3 — Knowledge Base + Few-shot selector

**Mục tiêu:** §9, §26–28.

**Điểm mạnh riêng của dự án này, phải khai thác:** `poetry_dataset.json` mà §9.1 nói tới đã
tồn tại, và **tốt hơn** một dataset thường — `datalake/analysis/bai_dat.jsonl` chứa
**24.366 bài đã được chính `rule.py` xác nhận qua bảy tầng**, kèm sơ đồ vần, phối khuôn,
và bằng chứng từng tầng.

Nghĩa là few-shot example đưa vào prompt **được bảo đảm đúng luật** — điều gần như không
dataset thơ nào có.

**Việc:**

1. `application/poetry/dataset.py` — adapter schema hiện tại → canonical §9.2, **không sửa
   dữ liệu gốc** (đúng như §9.2 dặn)
2. Metadata mở rộng: ngoài §9.2, thêm `so_do_van`, `phoi_khuon_theo_cum`, `so_dong`, `so_kho`
3. `application/poetry/fewshot.py` — chọn ví dụ theo §28 (form/topic/style/mood/structure),
   **cộng thêm**: ưu tiên bài có cùng `so_do_van` với `PoetryPlan`
4. Ba chế độ §26–28: `zero_shot | one_shot | few_shot`, chọn theo độ phức tạp yêu cầu
5. Xử lý bản quyền/đạo văn: §9.4 dặn *"Không copy nguyên bài thơ nếu không cần thiết"* —
   thêm rail ở G6 chặn đầu ra trùng >60% với ví dụ đã đưa vào prompt

**Nghiệm thu:**

- ⛔ **Test cưỡng chế:** mọi ví dụ few-shot đưa vào prompt phải thoả
  `kiem_tra_bai_tho(vi_du).dat == True`. Đưa một bài sai luật vào làm mẫu là dạy mô hình sai.
- Corpus thiếu (gitignored) thì selector phải lùi về zero-shot, không được ném lỗi
- Test: retrieval trả rỗng → zero-shot, đúng §32 Retrieval Failure

**Ước lượng:** 3 phiên.

**Ghi chú rủi ro:** `datalake/dataraw/` và `bai_dat.jsonl` đều bị gitignore. Cần quyết định
nơi lưu dataset đã chuẩn hoá cho môi trường chạy thật — đề nghị một tệp nhỏ
(~500 bài tuyển) commit được, phần còn lại sinh lại bằng script.

---

### G4 — Planner + Writer + Prompt Architecture + State Machine

**Mục tiêu:** §10, §11, §25, §29, §31.

**Tệp mới:**

```
application/poetry/planner.py        PoetryPlan (frozen) + sinh plan
application/poetry/writer.py         bọc generate_react_loop cho thơ
application/poetry/state.py          TrangThai (14 trạng thái §31)
application/poetry/workflow.py       orchestrator tường minh, đánh số bước
adapters/prompts/templates/poem_write/v1.yaml
adapters/prompts/templates/poem_plan/v1.yaml
```

**`PoetryPlan`** theo §10, với hai ràng buộc cứng thêm vào:

- `stanza_plan` phải cho **tổng số dòng là bội của 4** (QĐ-D5)
- `line_plan` **không** được mang trường "số tiếng linh hoạt" (QĐ-D1)

**Prompt (§25):** theo đúng kỷ luật đã có ở `plan-tang-agents.md` §5.2 —
tầng 1 (system) và tầng 2 (instruction) là **hằng số, không nội suy**; chỉ tầng 3
(conversation + retrieval context) mới mang dữ liệu động, và phải bọc thẻ XML.

**§18 LLM Rails — 10 điều** đưa thẳng vào system prompt, trong đó điều 4
(*"Never claim verification without tool evidence"*) sẽ được **cưỡng chế bằng code** ở G5,
không chỉ bằng câu chữ trong prompt. Prompt không phải là bảo đảm — đó là câu mở đầu của
`verify_output.py`.

**§31 State Machine:** dựng đủ 14 trạng thái ngay ở G4, kể cả những trạng thái mà G4 chưa
dùng (`HITL_DECISION`, `TIEBREAKER`) — nhưng đánh dấu rõ `chua_thi_hanh`, không để mã chết
trông như mã chạy.

**Nghiệm thu:**

- Sinh được bài thơ theo plan, qua bảy tầng, với provider mock
- Test: `PoetryPlan` có `stanza_plan` tổng dòng không chia hết 4 → bị từ chối ngay ở planner
- Test: system prompt là hằng số — không có f-string, không `.format()`

**Ước lượng:** 4 phiên.

---

### G5 — Verification Gate + Evidence + cấm tuyên bố suông

**Mục tiêu:** §14, §15, §19.4. Phần lớn đã có — giai đoạn này **hoàn thiện**, không dựng mới.

**Việc:**

1. **Evidence vào response** — `PoemResponse.bang_chung_bay_tang` đã thêm ở G1, nay bổ sung
   `chi_tiet` máy đọc được và `trich_luat` của từng tầng
2. **Rail mới `domain/guardrails/output/verification_claim.py`** — §19.4:
   quét đầu ra tìm các khẳng định kiểu *"đúng luật"*, *"đã kiểm tra"*, *"chuẩn thất ngôn"*;
   nếu có mà `verdict.dat` không đúng hoặc không có verdict → **chặn**.
   Đây là rail duy nhất của cả hệ thống chặn *lời nói về kết quả* chứ không chặn *kết quả*.
3. **Escalate thay vì chỉ Err** — §14: `MAX_REVISION` vượt thì `OutputKhongDat` hiện tại
   trả thẳng lỗi. Nay thêm nhánh: nếu HITL bật thì đẩy sang hàng đợi review (G7), nếu tắt
   thì giữ nguyên hành vi 422.
4. **`revision_count` và lịch sử sửa** vào `PoemResponse` — §23 đòi reviewer thấy
   *"Agent Revision History"*.

**Nghiệm thu:**

- Test: mô hình trả *"Bài thơ trên đã đúng luật thất ngôn tự do"* kèm bài 6 tiếng → **bị chặn**
- Test: biên bản kiểm định **không bao giờ** xuất hiện ở lượt `system` (kiểm bằng AST)
- Test: hết lượt → không có đường nào trả bài ra ngoài

**Ước lượng:** 2 phiên.

---

### G6 — GuardianRails đầy đủ + vá lỗ streaming 🔴

**Mục tiêu:** §16–20.

**🔴 Việc số 1 — lỗ hổng đang tồn tại, không phải tính năng mới:**
`routers/chat.py` nhánh `req.stream` yield thẳng `chunk.delta` ra SSE;
`enforce_output_guardrails` **chỉ chạy ở nhánh non-streaming**. Bật stream = tắt rào chắn
đầu ra. Đây là việc phải làm bất kể DeepAgent có được thi công hay không.

Cách vá: đệm theo cửa sổ trượt, chạy rail trên từng khối hoàn chỉnh trước khi phát; rail nào
cần cả bài (citation, verification claim) thì giữ lại khối cuối cho tới khi đủ.

**Việc còn lại:**

| § | Việc |
|---|---|
| §17.3 | Nối `domain/guardrails/input/topic.py` vào luồng, phân loại SAFE/REVIEW/BLOCK |
| §19.2 | Grounding — đã có `citation.py`, nối vào luồng thơ |
| §19.3 | Format check: poem only / poem + explanation / markdown / json |
| §20 | Sáu mối đe doạ → bộ test đối kháng, dùng `evals/datasets/adversarial.jsonl` |
| §9.4 | Rail chống copy nguyên bài từ few-shot (xem G3) |

**Nghiệm thu:**

- Test: bật `stream=true` → output rails **vẫn chạy**; có test cho đúng ca này
- Sáu dòng của bảng §20 đều có ít nhất một test đối kháng
- Tỉ lệ chặn injection đo được trên `adversarial.jsonl`, ghi số vào báo cáo

**Ước lượng:** 3 phiên (riêng streaming 1,5).

---

### G7 — HITL + Feedback Loop

**Mục tiêu:** §21–24.

**Việc:**

1. `domain/policy/hitl.py` — decision engine **thuần**, 6 đầu vào §22 → 5 đầu ra:
   `AUTO_RESPOND | ASK_USER | HUMAN_REVIEW | HUMAN_TIEBREAKER | REJECT`
2. Ba chế độ §21: on-the-loop (giám sát), in-the-loop (duyệt), as-tiebreaker
3. **Tiebreaker theo định nghĩa mới của QĐ-D3** — luật cứng đạt nhưng quality thấp hoặc chủ
   đề nhạy cảm, **không phải** "hai rule checker bất đồng" (tình huống đó không tồn tại)
4. `entrypoints/admin/` — màn hình review §23: request → plan → poem → evidence → tool
   results → violations → revision history; bốn hành động APPROVE / EDIT / REJECT / REQUEST REVISION
5. Feedback §24: mở rộng `contracts/feedback.py` cho đủ trường, và thêm bước **Quality
   Review** — *"Feedback không tự động trở thành training data"*

**Nghiệm thu:**

- Ma trận quyết định: mỗi trong 5 đầu ra có ít nhất 2 test (một ca vào, một ca biên)
- Test: không đường nào để feedback thô chảy thẳng vào tập few-shot mà không qua Quality Review
- Test: hàng đợi review không mất bài khi tiến trình restart *(chờ Bước 5 — lưu trữ thật;
  tới đó thì đây là hạn chế phải ghi rõ, không được giấu)*

**Ước lượng:** 4 phiên.

---

### G8 — Evaluation / Benchmark

**Mục tiêu:** §33, sáu nhóm metric.

`evals/` đã có khung + 3 dataset. Thêm:

```
evals/metrics/poetry.py    §33.3 — syllable/rhyme/tone/structure accuracy, đo bằng rule.py
evals/metrics/agent.py     §33.4 — mở rộng: tool selection, argument accuracy, revision success rate
evals/metrics/safety.py    §33.5
evals/metrics/hitl.py      §33.6 — escalation precision/recall, human agreement
evals/datasets/poetry_golden.jsonl
```

**Điểm tựa sẵn có:** §33.3 không cần gán nhãn tay — `rule.py` đã là ground truth tất định.
Đây là lợi thế hiếm; hầu hết hệ thống sinh văn bản không có thước đo khách quan nào.

**Metric quan trọng nhất, phải theo dõi từ G1:**

| Metric | Định nghĩa | Vì sao |
|---|---|---|
| **Tỉ lệ đạt lượt đầu** | % bài `dat=True` ngay ở `so_luot=0` | Đo chất lượng prompt + few-shot |
| **Số lượt sửa trung bình** | trung bình `so_luot` của bài đạt | Đo chi phí thật mỗi bài |
| **Tỉ lệ kiệt lượt** | % request kết thúc bằng `OutputKhongDat` | Đo mức QĐ-D2 có khả thi không |

Ba số này nên được ghi từ **ngay G1**, không đợi G8 — chúng là thứ cho biết QĐ-D2
(siết khuôn B/T) có chạy nổi trong thực tế hay không.

**Ước lượng:** 3 phiên.

---

## 5.5. THIẾT KẾ TOOL — thi hành chỉ thị 2, 3 và 5 ⭐

Mục này là bản thiết kế chi tiết cho ba chỉ thị:

> **Chỉ thị 2** — *"chi tiết từng bước tạo thơ cần có kiểm tra từng bước suy luận của Agent
> và kiểm tra Output trước khi trả cho người dùng"*
> **Chỉ thị 3** — *"Giữ nguyên file Rule này, thiết kế cho tôi một Tool cho phần này, cần
> kiểm tra đầy đủ chất lượng của LLM; nếu không đạt được thì cần Chain-of-thought"*
> **Chỉ thị 5** — *"Cần thỏa mãn đầy đủ mọi thông tin trước khi cho thơ cho người dùng"*

### 5.5.0. `rule.py` ĐÓNG BĂNG — cưỡng chế bằng máy

Chỉ thị 1 không phải lời dặn, nó là một ràng buộc kiểm được. Thi hành bằng ba lớp:

| Lớp | Cách |
|---|---|
| 1 | Không module mới nào `import` thứ gì từ `rule` ngoài các tên **chỉ đọc**: `kiem_tra_bai_tho`, `PoemVerdict`, `KetQuaTang`, `ViPham`, `BaoCaoDong`, `mo_ta_luat`, `TANG`, `LUAT`, `SO_TIENG_MOI_DONG` |
| 2 | Test `test_rule_dong_bang.py` ghim **SHA-256 của `rule.py`**. Đổi một ký tự → test đỏ, kèm thông báo nhắc rằng sửa luật phải đo lại corpus và cập nhật ba báo cáo |
| 3 | Test quét AST: không tệp nào ngoài `rule.py` được định nghĩa hàm tên `tach_tieng`, `dem_tieng`, `thanh_cua`, `van_cua` — chặn việc cài lại phép đếm ở chỗ thứ hai (P1) |

> Lớp 2 cố ý *khó chịu*. Nó không cấm sửa `rule.py` — nó buộc người sửa phải nhìn thấy
> cái giá trước khi sửa.

### 5.5.1. Hai Tool, hai thẩm quyền khác nhau

Chỉ thị 3 đòi một Tool kiểm **chất lượng**. Nhưng chất lượng và luật là hai loại phán quyết
khác hẳn nhau, và **không được trộn**:

| | `kiem_tra_tho` *(đã có)* | `danh_gia_chat_luong_tho` *(mới)* |
|---|---|---|
| Nguồn phán quyết | `rule.py` — tài liệu luật | Chuẩn dự án, ngoài tài liệu luật |
| Tính chất | **tất định**, cùng vào → cùng ra | tất định, nhưng ngưỡng do dự án đặt |
| Quyền | loại bài khỏi thể | **không bao giờ** đụng `thuoc_the` |
| Khi trượt | dựng biên bản có địa chỉ dòng | **bật Chain-of-thought** |

Trộn hai thứ này là cách chắc chắn để một ngày nào đó một bài bị loại vì "thiếu hình ảnh"
rồi được ghi lại như thể nó sai luật thơ. Vì vậy `KetQuaKiemDinh` của bộ kiểm đầy đủ mang
**hai cờ tách rời**, đúng tinh thần hai cờ `dat` / `thuoc_the` của `PoemVerdict`:

```
dat_luat        <- rule.py, không ai được ghi đè
dat_chat_luong  <- chuẩn dự án
dat             <- dat_luat AND dat_chat_luong   (cờ tổng, dùng để chặn đầu ra)
```

### 5.5.2. Tool mới — `danh_gia_chat_luong_tho`

**Bảy chiều**, lấy từ §12.2 Tool 7 của tài liệu đích. Điều quan trọng: **năm chiều đo được
bằng thuật toán, hai chiều thì không** — và hai chiều không đo được thì **ghi công khai**
là không kiểm được, đúng nguyên tắc N3, chứ không chấm điểm bừa.

| Chiều | §12.2 | Đo bằng gì | Ngưỡng |
|---|---|---|---|
| `lap_tieng` | repetition | tỷ lệ tiếng khác nhau / tổng tiếng | ≥ 0,55 |
| `lap_dong` | repetition | số cặp dòng trùng nhau hoàn toàn | = 0 |
| `bam_chu_de` | theme_alignment | giao giữa tiếng trong bài và từ khoá chủ đề | ≥ 1 tiếng, chỉ kiểm khi có chủ đề |
| `nhac_tinh` | rhythm | `verdict.ty_le_theo_khuon` *(đọc từ rule.py)* | = 1,0 |
| `da_dang_van` | rhythm | số lớp vần khác nhau trong bài | ≥ 1 |
| `mach_lac` | semantic_coherence | 🔶 **KHÔNG ĐO ĐƯỢC** bằng thuật toán | — |
| `hinh_anh` | imagery | 🔶 **KHÔNG ĐO ĐƯỢC** bằng thuật toán | — |

> **Vì sao không dùng LLM để chấm hai chiều cuối ngay tại Tool này.** Port `OutputVerifier`
> quy định hiện thực phải **đồng bộ và thuần, không I/O** — *"cổng chặn không được phép
> trượt vì mạng"* — và **tất định**, vì *"nếu không, vòng sửa sẽ dao động"*. Một LLM-judge
> vi phạm cả hai. Nó thuộc về node Reviewer ở G7, nơi nó chỉ **tư vấn** cho HITL chứ không
> chặn đầu ra. Hai chiều này vì vậy trả về `khong_kiem_duoc` và đi vào phần *tham khảo*
> của biên bản.

**Nguồn gốc các ngưỡng — nói thẳng, không giấu.** `Plan_Rule_Phan_Tang.md` §1.1 ghi lại một
sai lầm đã trả giá: chọn ngưỡng 0,5 *vì nó giữ lại 84,82% số bài*, tức nắn luật cho vừa dữ
liệu. Để không lặp:

- `nhac_tinh = 1,0` và `lap_dong = 0` **không phải ngưỡng tự chọn** — chúng suy ra trực tiếp
  từ QĐ-2 (không cho phá khuôn) và từ nghĩa của "trùng dòng".
- `bam_chu_de ≥ 1 tiếng` là ngưỡng nhỏ nhất có nghĩa, và chỉ kiểm khi người dùng có nêu chủ đề.
- ~~`lap_tieng ≥ 0,55`~~ **ĐÃ GỠ 21/09/2026** — cùng với `lap_dong = 0`. Cả hai vi phạm
  nguyên tắc **N2**: S20 (loại *quyền*) nói *"có thể dùng điệp dòng, điệp khổ, điệp cấu
  trúc"*, nên phạt sự lặp là đánh trượt vì tác giả dùng đúng quyền tài liệu cho phép.

  Đo trên 6.000 bài người viết đã đạt luật:
  - `lap_tieng` **thiên vị theo độ dài** — trung vị 0,929 (bài 4–8 dòng) tụt còn 0,638
    (bài 56 dòng). Nguyên nhân là số học: kho âm tiết tiếng Việt hữu hạn, hư từ lặp tự
    nhiên, nên bài càng dài thì tỉ lệ *khác nhau/tổng* càng buộc phải giảm.
  - `lap_dong` bắt 164 bài, **toàn bộ là điệp có chủ ý** (điệp khúc, kết cấu vòng tròn).

  Thay bằng `dong_phan_biet ≥ 2` (số nguyên, chỉ bắt ca suy biến tuyệt đối) và
  `so_dong_lap` (**không chặn** — tín hiệu cho HITL). **Hệ thống nay không còn ngưỡng
  tuỳ ý nào**, có test `test_KHONG_con_nguong_tuy_y_nao` cưỡng chế.

### 5.5.3. Chain-of-thought — bật khi nào, và là loại CoT nào

Chỉ thị 3: *"nếu không đạt được thì cần Chain-of-thought trước khi trả ra kết quả"*.

Loại CoT ở đây là **Structured Reasoning theo §29 của tài liệu đích**, không phải private
chain-of-thought. §29 nói rõ: *"Không yêu cầu Agent xuất Chain-of-Thought"*, và các artifact
có cấu trúc là *"operational state, không phải private chain-of-thought"*. Hai điều đó không
mâu thuẫn với chỉ thị 3 — chỉ thị đòi mô hình **phải suy luận có kỷ luật trước khi viết lại**,
chứ không đòi phơi dòng suy nghĩ nội tại.

**Khi nào bật:**

```
luật trượt          -> biên bản có địa chỉ dòng, KHÔNG bật CoT
                       (lỗi cụ thể, đã chỉ rõ chỗ; bắt suy luận thêm là tốn tiền vô ích)

chất lượng trượt    -> BẬT CoT
                       (lỗi khuếch tán, không có "dòng 3 sai"; phải suy luận mới sửa được)

cả hai trượt        -> biên bản luật trước, CoT sau
                       (sửa cái có địa chỉ trước, đó là cái rẻ)

lặp / không tiến bộ -> BẬT CoT bất kể loại lỗi
                       (G5/G6 của verify_output đã phát hiện được hai trạng thái này)
```

**Khung CoT bắt buộc điền** — bốn ô, mô hình phải điền trước khi được viết lại:

```
<khung_suy_luan>
1. CHIỀU CHƯA ĐẠT      : <tên chiều, số đo, ngưỡng>
2. NGUYÊN NHÂN         : <vì sao bài hiện tại không đạt chiều đó>
3. HƯỚNG SỬA           : <cách sửa — KHÔNG viết câu thơ ở ô này>
4. DÒNG PHẢI GIỮ NGUYÊN: <danh sách dòng đã đạt>
</khung_suy_luan>
```

Ô 3 cấm viết thơ là có chủ đích: tách *quyết định sửa gì* khỏi *viết câu chữ*. Ô 4 chống
đúng kiểu hỏng đã biết — mô hình viết lại cả bài rồi làm hỏng dòng đang đúng.

### 5.5.4. Kiểm **từng bước suy luận** — thi hành chỉ thị 2

Chỉ thị 2 đòi kiểm *từng bước*, không chỉ kiểm kết quả cuối. Sáu bước, mỗi bước **chặn**:

| Bước | Tên | Kiểm gì | Chặn khi |
|---|---|---|---|
| **B1** | YÊU CẦU | Requirement đủ thông tin *(chỉ thị 5)* | còn trường bắt buộc trống |
| **B2** | KẾ HOẠCH | `PoetryPlan` hợp lệ | tổng dòng không bội 4; lệch `so_dong` người dùng xin; khuôn khai báo không thuộc `{bang, trac}` |
| **B3** | BẢN NHÁP ↔ KẾ HOẠCH | Bài viết ra có đúng bài đã hoạch định | số dòng / số khổ lệch plan |
| **B4** | LUẬT | `kiem_tra_bai_tho().dat` | bất kỳ tầng chặn nào trượt |
| **B5** | CHẤT LƯỢNG | năm chiều đo được | chiều nào dưới ngưỡng |
| **B6** | TUYÊN BỐ | §19.4 — không khẳng định "đúng luật" thiếu căn cứ | có khẳng định mà `dat_luat = False` |

Bốn tính chất bắt buộc, sao chép đúng kỷ luật bảy tầng của `rule.py`:

1. **Dừng ở bước trượt đầu tiên.** Bước sau mang `da_chay=False` — *chưa kiểm*, khác hẳn
   *đã kiểm và đạt*.
2. **Luôn nộp bằng chứng**, kể cả khi đạt.
3. **Bước không kiểm được thì ghi công khai**, không lặng lẽ cho qua.
4. **Không bước nào gọi bước khác.** Thứ tự do một orchestrator điều khiển.

B3 là bước mà tài liệu đích **không có**, và nó cần thiết: không có B3 thì Planner có thể
lập kế hoạch 8 dòng còn Writer viết 12 dòng, cả hai vẫn "đạt" phần của mình, và không ai
phát hiện rằng kế hoạch đã bị bỏ qua.

### 5.5.5. Chỉ thị 5 — cổng thông tin đầy đủ

*"Cần thỏa mãn đầy đủ mọi thông tin trước khi cho thơ cho người dùng."*

Thi hành ở **B1**, và nó là cổng **chặn**: thiếu thông tin thì hệ thống **hỏi lại**, không
sinh thơ. Bốn ca:

| Ca | Kích hoạt | Hỏi |
|---|---|---|
| 1 | thiếu chủ đề | "Bạn muốn bài thơ viết về chủ đề nào?" |
| 2 | mâu thuẫn thể loại (xin tự do + đòi luật bát cú) | "Ưu tiên đặc trưng tự do hay luật bằng-trắc bát cú?" |
| 3 | ràng buộc mơ hồ ("vần thật chặt") | "Vần chân theo mô hình cố định hay liên kết vần tự nhiên?" |
| 4 | `so_dong` không phải bội của 4 *(QĐ-D5)* | "Số dòng phải là bội của 4 — bạn muốn 4 hay 8 dòng?" |

Kèm một ràng buộc chống "đoán bừa": mỗi trường của `PoetryRequirement` mang theo
`nguon` thuộc `{nguoi_dung, mac_dinh, suy_doan}`. **Không trường nào được mang `suy_doan`**
khi đi qua B1 — có test cưỡng chế. Không ghi nguồn thì không ai kiểm được là hệ thống đã hỏi
hay đã tự đoán.

---

## 5.6. G9 · G10 · G11 — ba giai đoạn bổ sung (21/09/2026)

Bổ sung sau khi G0→G8 xong, gom đúng bốn mục còn tồn ở §8 *"cái plan này cố ý không làm"*
mà chủ dự án yêu cầu đưa vào thi công.

---

### G9 — Bền vững hoá dữ liệu · sửa lỗi cô lập tenant

**Vấn đề 1 — mất dữ liệu khi restart.** Toàn bộ lưu trữ nằm trong RAM. Hàng đợi HITL,
bộ đếm rate-limit và lịch sử hội thoại biến mất mỗi lần khởi động lại; chạy nhiều
uvicorn worker thì mỗi tiến trình giữ một bản riêng.

**Vấn đề 2 — 🔴 LỖI ĐANG TỒN TẠI, cô lập tenant hỏng.** `routers/chat.py` lọc
`{"tenant_id": ...}` trên `chunk.metadata`, nhưng `tenant_id` là **field của `Chunk`**,
không nằm trong `metadata`. Hệ quả: **mọi chunk đều bị loại, RAG luôn trả rỗng.**

Lỗi này nguy hiểm gấp đôi vì nó hỏng theo hướng *im lặng*: RAG rỗng trông như "không
tìm thấy tài liệu", không như "bộ lọc sai". Và nếu một ngày ai đó sửa nhầm thành
không lọc gì, nó lật sang hướng ngược lại — rò dữ liệu giữa các tenant.

#### Quyết định: SQLite trước, Postgres sau — và nói rõ vì sao

| | SQLite (làm ở G9) | Postgres (vẫn là Bước 5) |
|---|---|---|
| Phụ thuộc | `sqlite3` — **thư viện chuẩn** | `sqlalchemy` · `asyncpg` · `alembic` |
| Chạy được ngay | ✅ mọi máy, không cần Docker | ❌ cần hạ tầng |
| Kiểm chứng được | ✅ test thật, có ca restart | ❌ chỉ chạy được nơi có DB |
| Nhiều tiến trình | ⚠️ một tệp, khoá ghi | ✅ |

Tôi **không** viết adapter Postgres ở G9. Viết vài trăm dòng SQLAlchemy không chạy
được ở đâu trong repo này là tạo ra thứ *trông như đã xong*: nó qua được review, nằm
trong bản kiểm kê, và không ai biết nó có hoạt động hay không cho tới lần deploy đầu.

SQLite đóng đúng vấn đề đã nêu (mất khi restart), kiểm chứng được bằng test thật, và
**chứng minh cổng lưu trữ thật sự thay thế được** — thứ mà Postgres sau này chỉ cần
cắm vào cùng chỗ.

#### Việc

| # | Việc | Nghiệm thu |
|---|---|---|
| G9.1 | `TenantScope` thành tham số **đầu tiên, bắt buộc** của mọi phương thức port chạm dữ liệu | test kiến trúc quét AST |
| G9.2 | Sửa lỗi lọc tenant | test: hai tenant không thấy dữ liệu của nhau |
| G9.3 | `adapters/persistence/sqlite/` hiện thực `RelationalRepository` + `CacheRepository` | test: ghi → đóng → mở lại → dữ liệu còn |
| G9.4 | `_build_storage` nhận `storage.kind = "sqlite"` | container dựng được |

> **Ràng buộc G9.1 là phần quan trọng nhất**, không phải phần lưu trữ. ADR-0003 nói
> rõ: cô lập tenant phải được bảo đảm **bằng chữ ký hàm**, không bằng review. Một
> `tenant_id` nằm trong `dict` filter thì gõ sai là lọt; một tham số bắt buộc thì
> quên là không biên dịch nổi.

---

### G10 — Xác thực và multi-tenant thật

Hiện `tenant_id` và `user_id` lấy thẳng từ **thân request** — nghĩa là bất kỳ ai cũng
tự khai mình thuộc tenant nào. Cô lập tenant có chặt đến đâu ở tầng dưới cũng vô
nghĩa nếu danh tính do chính người gọi tự nhận.

| # | Việc | Nghiệm thu |
|---|---|---|
| G10.1 | Middleware xác thực bằng API key, khoá → tenant | thiếu/sai khoá → 401 |
| G10.2 | `tenant_id` **chỉ** lấy từ khoá, KHÔNG lấy từ thân request | test: thân request khai tenant khác vẫn bị ép về tenant của khoá |
| G10.3 | Đường công khai (`/healthz`, `/metrics`, `/docs`) khai báo tường minh | test: danh sách đóng |

> Chỗ dễ sai nhất: để `req.tenant_id` ghi đè tenant của khoá "cho tiện khi test".
> Có test riêng ghim điều đó.

---

### ✅ ĐÃ THI CÔNG — G9 · G10 · G11, 21/09/2026

| Việc | Tệp | Nghiệm thu |
|---|---|---|
| `TenantScope` — kiểu riêng, không có mặc định ngầm | `domain/conversation/tenant.py` | `TenantScope()` không gọi được |
| `scope` thành tham số ĐẦU của mọi port lưu trữ | `ports/repositories.py` | test AST quét chữ ký |
| 🩸 Sửa lỗi lọc tenant | `persistence/memory/vector.py` | RAG trả kết quả; A không thấy dữ liệu B |
| SQLite bền vững | `persistence/sqlite/` | ghi → xoá object → mở lại → còn dữ liệu |
| Xác thực API key, tenant từ khoá | `api/middleware/auth.py` | thân request KHÔNG ghi đè được tenant |
| Ngưỡng ra cấu hình | `configs/base.yaml` | sửa ngưỡng không cần sửa mã |

**mypy đã làm phần lớn việc**: đổi chữ ký port xong, **mọi nơi quên tenant đều
thành lỗi biên dịch**. Đó chính là điều ADR-0003 muốn — cô lập tenant bảo đảm bằng
chữ ký hàm, không bằng review.

**Một test tự bắt lỗi của chính nó:** bản đầu của
`test_KHONG_con_noi_nao_loc_tenant_qua_dict_filters` tìm chuỗi thô, nên nó bắt luôn
các docstring **cố ý nhắc lại** cách viết cũ để ghi nhớ. Cách sửa duy nhất khi đó là
xoá lời cảnh báo — tức test buộc người ta phá thứ nó định bảo vệ. Nay soi bằng AST.

---

### G11 — Ngưỡng tuỳ ý ra cấu hình

`NGUONG_TUY_Y_LAP_TIENG = 0,55` là con số **duy nhất** trong hệ thống do người viết
code đặt tuỳ ý. Nó đang nằm trong mã nguồn, nên sửa nó là sửa code.

Đưa ra `configs/base.yaml` để chủ dự án chỉnh được mà không đụng mã — và quan trọng
hơn, để con số ấy **nằm cạnh các cấu hình khác thay vì lẩn trong một module**.

Vẫn giữ nguyên hai tính chất đã có: tên hằng số tự khai là tuỳ ý, và có test khẳng
định nó chưa được duyệt.

---
### G12 — Bước 5 THẬT: một adapter SQL, hai dialect

**Tôi đã sai về một ràng buộc, và nói lại cho rõ.**

Ở G9 tôi từ chối viết adapter Postgres với lý do: *"vài trăm dòng SQLAlchemy không
chạy được ở đâu trong repo này"*. Lý do ấy dựa trên một kiểm tra: `sqlalchemy`,
`asyncpg` chưa được cài.

Kiểm lại thì **cài được cả hai**. Điều đó làm đổ lập luận cũ, vì:

> Một adapter **SQLAlchemy async** chạy trên **cả** `sqlite+aiosqlite` lẫn
> `postgresql+asyncpg`. Cùng một mã, cùng một câu SQL. Nên nó **test được ngay
> hôm nay** bằng SQLite trong CI, và phần chưa kiểm chứng thu lại chỉ còn phương
> ngữ Postgres — thứ SQLAlchemy lo.

Đó không còn là "mã trông như đã xong". Đó là mã chạy thật trong test thật.

#### Hệ quả: adapter `sqlite3` thuần viết ở G9 bị THAY THẾ

Tôi viết nó cách đây một lượt. Nay nó bị thay, vì giữ cả hai nghĩa là **hai hiện
thực của cùng một port** — đúng thứ duplication mà cả plan này cảnh báo. Sửa một
lỗi ở một bên rồi quên bên kia là chuyện sẽ xảy ra, không phải có thể xảy ra.

Giữ lại đúng một: `adapters/persistence/sql/`.

#### Việc

| # | Việc | Nghiệm thu |
|---|---|---|
| G12.1 | `adapters/persistence/sql/` — SQLAlchemy Core async, hai dialect | test chạy thật trên `sqlite+aiosqlite` |
| G12.2 | `RateLimitPort` bền vững, **dùng chung giữa các tiến trình** | hai instance khác nhau cùng thấy một bộ đếm |
| G12.3 | Gỡ adapter `sqlite3` thuần | không còn hai hiện thực cùng port |
| G12.4 | Test tích hợp Postgres, **skip khi không có DB** | có `DATABASE_URL` thì chạy thật |

> **G12.2 mới là phần đóng đúng khoảng trống còn lại.** Kho quan hệ đã bền vững từ
> G9; thứ vẫn hỏng khi chạy nhiều worker là **bộ đếm rate-limit** — mỗi tiến trình
> một bản, nên hạn mức thực tế bị nhân lên bằng số worker. Đó là lỗ kiểm soát chi
> phí, không phải lỗ tiện nghi.

---

### ✅ ĐÃ THI CÔNG — G12 · G13, 21/09/2026

| Việc | Tệp | Nghiệm thu |
|---|---|---|
| Adapter SQL, hai dialect | `persistence/sql/` | test chạy THẬT trên `sqlite+aiosqlite` |
| Bộ đếm dùng chung giữa tiến trình | `sql/rate_limit.py` | hai instance + hai engine + một tệp = MỘT bộ đếm |
| Gỡ adapter `sqlite3` thuần | *(đã xoá)* | không còn hai hiện thực cùng port |
| Vòng đời khoá API | `domain/policy/api_key.py` · `sql/api_key.py` | thu hồi có hiệu lực NGAY |
| Khoá lưu dạng băm | `bam_khoa()` | quét mọi byte trên đĩa không thấy khoá nguyên văn |

**🩸 Một test tự phát hiện mình đúng-một-cách-rỗng.** `test_KHOA_NGUYEN_VAN_KHONG_duoc_luu`
bản đầu chỉ đọc tệp `.sqlite3`. Ở chế độ WAL, dữ liệu vừa ghi nằm trong tệp `-wal`,
nên khẳng định "không có khoá nguyên văn" xanh **trong khi không kiểm gì cả** — và sẽ
xanh vĩnh viễn kể cả khi có người chuyển sang lưu khoá nguyên văn.

Phát hiện được là nhờ **khẳng định đối chứng dương** (`băm phải có mặt`) đi kèm: nó đỏ.
Đó là lý do một test phủ định luôn cần một đối chứng dương.

---

### G13 — Bước 6: vòng đời khoá API

Hiện bảng khoá nạp một lần lúc khởi động. **Thu hồi một khoá đòi restart** — nghĩa
là khi một khoá bị lộ, cửa vẫn mở cho tới lần deploy tiếp theo.

| # | Việc | Nghiệm thu |
|---|---|---|
| G13.1 | `domain/policy/api_key.py` — luật thuần: hết hạn, thu hồi | test thuần, không I/O |
| G13.2 | Kho khoá bền vững | khoá sống qua restart |
| G13.3 | Thu hồi **có hiệu lực ngay**, không restart | thu hồi xong request kế tiếp nhận 401 |
| G13.4 | Khoá lưu dạng **BĂM**, không lưu nguyên văn | đọc được cả bảng cũng không dùng lại được khoá |

> **G13.4 là điều dễ bỏ qua nhất.** Bảng khoá nay nằm trong DB; lưu nguyên văn thì
> một bản sao lưu rò rỉ là mọi khoá rò theo. Băm thì bản sao lưu vô dụng với kẻ lấy
> được nó.

---
### G14 — ba việc cuối, ngoài plan gốc

Bốn mục ở §8 *"cố ý không làm"* nay còn đúng một: **§33.1/2/4 đòi khoá API thật**.

| # | Việc | Kết quả |
|---|---|---|
| G14.1 | 🩸 **Kho vector bền vững** — đính chính lập luận sai của chính tôi | `sql/vector.py` |
| G14.2 | **Alembic** — migration thật, upgrade + downgrade đã chạy | `migrations/` |
| G14.3 | **Test tích hợp hai dialect** — một bộ kiểm, `parametrize` theo dialect | `tests/integration/` |

#### 🩸 G14.1 — tôi đã lập luận sai ở G12

Tôi từ chối làm kho vector trên SQL với lý do *"quét toàn bảng — chép lại in-memory
nhưng chậm hơn"*. Vế "chậm hơn" đúng; vế **"chép lại in-memory" thì sai**:

    in-memory   MẤT khi restart · MỖI TIẾN TRÌNH một bản
    SQL         BỀN VỮNG        · DÙNG CHUNG giữa các tiến trình

Đó đúng là hai vấn đề tôi đã bỏ công sửa cho kho quan hệ (G9) và bộ đếm (G12.2).
Bỏ qua chúng ở kho vector chỉ vì tốc độ là **đánh đổi sai hạng**: tài liệu đã nạp
biến mất sau mỗi lần restart, và hai worker thấy hai kho khác nhau.

`pgvector`/Qdrant giải bài toán KHÁC — tìm gần đúng (ANN) ở quy mô triệu vector.
Đó là tối ưu cho QUY MÔ, không phải sửa lỗi đúng-sai. Ngưỡng cần đổi hướng đã ghi
trong `sql/vector.py`: ~10⁵ chunk mỗi tenant.

#### G14.2 — bài học về tệp cấu hình

`alembic.ini` phải là **ASCII thuần**: Alembic đọc nó bằng encoding LOCALE (cp1252
trên Windows), không phải UTF-8, nên chú thích tiếng Việt làm vỡ ngay lệnh đầu
tiên. Phần giải thích đầy đủ nằm ở `migrations/env.py`, nơi được đọc bằng UTF-8.

#### G14.3 — một bộ kiểm, hai dialect

Viết riêng cho Postgres thì trong vài tháng nó sẽ lệch khỏi bộ SQLite — và bên bị
quên luôn là Postgres, vì nó không chạy trong CI. Nên chỉ có MỘT bộ, `parametrize`
theo dialect: SQLite luôn chạy, Postgres tự skip khi không có `DATABASE_URL`.

---

## 6. RỦI RO — bốn điều có thể làm hỏng plan

| # | Rủi ro | Dấu hiệu sớm | Cách xử lý |
|---|---|---|---|
| **R1** | **Hợp nhất hai `LlmPort` ở G1 lan rộng** hơn dự tính (đụng `rag/`, `ingest/`, 4 adapter) | G1 quá 4 phiên mà chưa xong mục 1 | Tách G1a/G1b như đã nêu; G1a không cần hợp nhất port |
| **R2** ⚠️ | **QĐ-D2 quá khắt khe cho mô hình.** Tầng 4 loại 55,29% thơ **người viết**. Không có cơ sở nào để tin mô hình làm tốt hơn người ở đúng ràng buộc đó. Nếu tỉ lệ đạt lượt đầu < 5%, mỗi bài sẽ tốn 3–4 lượt gọi model, hoặc kiệt lượt | Đo ngay ở cuối G1 với 20 request mock + 20 request thật | **Đo trước khi tranh luận.** Nếu quá thấp: (a) tăng `max_repair_rounds`, (b) đưa khuôn B/T vào prompt dưới dạng bảng mẫu cụ thể, (c) few-shot chọn bài **cùng phối khuôn** (G3 đã có dữ liệu này), (d) cuối cùng mới xét nới QĐ-2 — và đó là quyết định của chủ dự án, không phải của người thi công |
| **R3** | **Tầng 6 (Nhịp) rỗng nghĩa** — chặn 0/16.391 bài vì chưa có bộ tách từ tiếng Việt | đã biết, đã ghi trong docstring | DeepAgent **sinh** thơ nên có thể khai báo nhịp từng dòng → `nhip_khai_bao` có giá trị → tầng 6 chặn được thật. Đưa `nhip` vào `line_plan` ở G4. Đây là chỗ DeepAgent làm được điều mà phân tích corpus không làm được |
| **R4** | **Dataset gitignored** — `bai_dat.jsonl` và corpus gốc không có trên checkout sạch | người mới clone không chạy được G3 | Commit một tệp tuyển ~500 bài; ghi rõ trong README cách sinh lại phần còn lại |

---

## 7. ĐƯỜNG GĂNG VÀ THỨ TỰ

```
G0 ──► G1 ──┬──► G2 ──┬──► G4 ──► G5 ──► G7 ──► G8
            │         │
            └──► G3 ──┘
                      
            G6 ──────────────────────────► (chạy song song, không phụ thuộc G2–G5)
```

- **G0 → G1** là đường găng tuyệt đối. Không chốt QĐ-D4 thì G1 phải đi đường vòng.
- **G2 và G3 chạy song song được** — Requirement không cần Knowledge, và ngược lại.
- **G6 tách rời** — riêng phần vá streaming nên làm **ngay sau G1**, không đợi, vì đó là lỗ
  hổng đang tồn tại chứ không phải tính năng mới.
- **G8 nên bắt đầu sớm một phần** — ba metric ở §5/G8 phải ghi từ G1.

| Giai đoạn | Phiên | Cộng dồn | Cho ra gì |
|---|---:|---:|---|
| G0 | 1 | 1 | Hết mơ hồ |
| G1 | 3–4 | 5 | ⭐ **API sinh thơ đúng luật chạy được** |
| G6a (streaming) | 1,5 | 6,5 | 🔴 Vá lỗ hổng |
| G2 | 3 | 9,5 | Biết hỏi lại |
| G3 | 3 | 12,5 | Few-shot đảm bảo đúng luật |
| G4 | 4 | 16,5 | Plan + Writer + State Machine |
| G5 | 2 | 18,5 | Evidence + cấm tuyên bố suông |
| G6b | 1,5 | 20 | Rails đầy đủ |
| G7 | 4 | 24 | HITL + Feedback |
| G8 | 3 | 27 | Benchmark 6 nhóm |

**≈ 27 phiên ≈ 13–14 ngày tập trung.** Con số này là *ước lượng*, không phải cam kết — và
nó giả định QĐ-D1→D5 được chốt ở G0 và không đảo lại giữa chừng.

---

## 8. CÁI PLAN NÀY CỐ Ý KHÔNG LÀM

Ghi ra để sau này không ai tưởng là bỏ sót.

| Không làm | Vì sao |
|---|---|
| Dựng cây `poetry-agent/` của §36 | QĐ-D4 — phá 4 hợp đồng import-linter đang KEPT, và khôi phục đúng thứ ADR-0002 đề nghị gỡ |
| Tách 5 tool kiểm thơ riêng lẻ | QĐ-D3 — P1, một nguồn luật |
| Human Tiebreaker theo nghĩa "hai checker bất đồng" | QĐ-D3 — với luật tất định, tình huống đó không tồn tại; giữ lại là dựng nhánh code chết |
| Adapter lưu trữ thật (Postgres/Redis/pgvector) | Thuộc **Bước 5** của README + ADR-0003, không thuộc plan này. Hệ quả phải ghi rõ: hàng đợi HITL mất khi restart, cho tới khi Bước 5 xong |
| Xác thực, multi-tenant thật | Bước 6 |
| Sửa `rule.py` | Trừ khi QĐ-D1/D2/D5 bị bác. Sửa luật thì phải đo lại corpus và cập nhật 3 báo cáo đã đối soát — là một dự án riêng |
| Fine-tuning / training | §24 nói rõ feedback không tự thành training data. Ngoài phạm vi |

---

## 9. NGHIỆM THU TOÀN PLAN

Plan coi là xong khi **tất cả** các điều sau đúng:

1. `make check` xanh: `ruff` + `mypy` + `lint-imports` (≥4 hợp đồng) + toàn bộ test
2. ⛔ **Không tồn tại đường nào** từ HTTP trả về một bài thơ có
   `kiem_tra_bai_tho(poem).dat == False` — có test cưỡng chế, và đây là điều kiện nghiệm thu
   duy nhất không được thương lượng
3. Mọi response chứa thơ đều kèm bằng chứng bảy tầng
4. Không có khẳng định "đúng luật" nào thoát ra mà không có verdict chống lưng
5. Bốn ca Clarification chạy được, đều có test
6. Mọi few-shot example đưa vào prompt đều `dat == True`
7. Output rails chạy ở **cả hai** nhánh streaming và non-streaming
8. Sáu nhóm metric §33 có số đo, ghi vào một báo cáo trong `docs/`
9. Ba metric vận hành (đạt lượt đầu / lượt sửa TB / kiệt lượt) có số đo trên ≥100 request
10. `python datalake/scripts/doi_soat_tai_lieu.py` vẫn xanh — mọi con số mới trong docs truy được về nguồn

---

## 10. VIỆC TIẾP THEO NGAY

1. Chủ dự án đọc **§3**, trả lời QĐ-D1 → QĐ-D5
2. Chốt xong thì bắt đầu **G0** (1 phiên, không code)
3. Rồi **G1** — và đo ngay ba metric vận hành để biết R2 có thành vấn đề thật không

> Một câu cho người đọc vội: **repo này đã có phần khó nhất của tài liệu đích rồi. Việc còn
> lại phần lớn là nối dây và hỏi đúng câu hỏi — trừ QĐ-D2, chỗ duy nhất có thể khiến cả
> hướng đi phải xem lại.**
