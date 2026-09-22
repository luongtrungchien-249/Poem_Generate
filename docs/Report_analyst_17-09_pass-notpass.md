# BÁO CÁO PHÂN TÍCH CORPUS — BÀI ĐẠT / BÀI KHÔNG ĐẠT LUẬT

**Tệp phân tích:** `datalake/dataraw/final_data_7_chu.jsonl` — 67.150 bản ghi
**Ngày đo:** 18/09/2026 (đo lại lần cuối sau QĐ-7b) · **Bộ luật:** `src/application/rule.py`, bảy tầng
**Sinh lại:** `python datalake/scripts/kiem_tra_toan_bo.py`

> **Lượt đo 18/09 — toàn bộ, không sót tệp nào.** Bản 17/09 đo bằng bộ luật chỉ chặn ở
> ba luật cứng H1, H2, H3 (H4 chưa ra đời, tầng 3 còn chặn oan, tầng 5 còn đòi khớp sơ
> đồ đóng). Lượt này chạy lại **mười script** — `kiem_tra_toan_bo.py` cộng chín script
> phân tích — nên **mọi tệp trong `datalake/analysis/` đều mang số liệu của bộ luật hiện
> tại**. Không con số nào được mang sang từ bản cũ.
>
> Ba chỗ số liệu đổi nhiều nhất ở lượt này, cả ba đều được ghi rõ tại chỗ:
> §5.1.1 (bài rỗng cứu được **1.244 → 673**), §6.2 (điểm mù **42 → 12**),
> §8.1 (phép so bản luật đã hỏng và đã sửa).

---

## 0. Tóm tắt cho người bận

> ### ĐƠN VỊ PHÁN QUYẾT LÀ **BÀI**, KHÔNG PHẢI DÒNG
>
> Chỉ cần **một** dòng lệch là **cả bài** trượt. Một bài 32 dòng có 31 dòng hoàn hảo
> và 1 dòng 6 tiếng là **bài hỏng**, không phải "bài đạt 97%".
>
> Hệ quả khi đọc: mọi số liệu **mức dòng** trong báo cáo này chỉ để **chẩn đoán
> nguyên nhân**, tuyệt đối không dùng làm thước đo chất lượng corpus.

### 0.1. Hai con số, cố ý không gộp

| | Số bài | Trả lời câu hỏi gì |
|---|---:|---|
| **Thuộc thể** — theo tài liệu luật (chỉ H1–H4) | **55.297** | *"Bài này có phải thất ngôn tự do không?"* — câu trả lời của `Luat_Tho_That_Ngon_Tu_Do.md` §2 |
| **Đạt** — theo chuẩn dự án (cả bảy tầng) | **24.366** | *"Bài này có tuân thủ toàn bộ Rule không?"* — câu trả lời của dự án, sau QĐ-1 → QĐ-7b |

Khoảng cách **30.931 bài** giữa hai con số **không phải lỗi**. Nó là hệ quả đo được của
các quyết định đã chốt, và sau QĐ-7b thì **gần như toàn bộ nằm ở QĐ-1 và QĐ-2** (không
cho phá khuôn thanh luật): 30.571 trong 30.931 bài, tức **98,84%**.

Tỉ lệ đạt: **24.366 / 62.034 bài có nội dung = 39,28%**.

### 0.2. Phễu bảy cổng

Bài phải qua cổng N mới sang cổng N+1. Bài bị chặn ở cổng nào thì các cổng sau **không
chạy** — bản ghi mang `da_chay: false`, nghĩa là *chưa kiểm*, **không** phải *đạt*.

| Cổng | Mức | Điều luật | Vào | Qua | % qua | Chặn | % chặn | Còn lại | Đánh dấu |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| **1. Hình thức và số dòng** | ⛔ chặn | H3, **H4** | 62.034 | 57.366 | 92,48% | **4.668** | 7,52% | 92,48% | — |
| 2. Độ dài dòng | ⛔ chặn | H1, H2 | 57.366 | 55.297 | 96,39% | 2.069 | 3,61% | 89,14% | — |
| 3. Đối chiếu Đường luật | ℹ️ ghi nhận | F1–F5 | 55.297 | 55.297 | 100,00% | 0 | 0,00% | 89,14% | 4.288 |
| **4. Thanh luật** | ⛔ chặn | S1–S3 | 55.297 | 24.726 | **44,71%** | **30.571** | **55,29%** | 39,86% | — |
| 5. Vần | ⛔ chặn | S6, S9–S12 | 24.726 | **24.366** | 98,54% | 360 | 1,46% | **39,28%** | — |
| 6. Nhịp | ⛔ chặn | S13–S15 | 24.366 | 24.366 | 100,00% | 0 | 0,00% | 39,28% | — |
| 7. Khổ và bố cục | ⛔ chặn | S16–S21 | 24.366 | 24.366 | 100,00% | 0 | 0,00% | 39,28% | — |

**Ba mẫu số khác nhau, đừng lẫn:**

- **% qua** và **% chặn** — mẫu số là số bài **đi vào cổng đó**. Trả lời *"trong những bài
  tới được cổng này, bao nhiêu phần trăm lọt?"*. Đây là độ khắt khe của **riêng** cổng.
- **Còn lại** — mẫu số là **toàn bộ 62.034 bài có nội dung**. Đường sống sót tích luỹ.
- **Đánh dấu** — số bài cổng ghi nhận có phát hiện nhưng **vẫn cho đi tiếp**.

Một cổng có thể *% qua* rất cao mà *Còn lại* vẫn thấp, nếu các cổng trước đã cắt nhiều.
Cổng 6 là ví dụ: nó cho qua 100,00% nhưng đường sống sót đã dừng ở 39,28% từ cổng 5.

Đọc theo cột *% chặn* thì thứ tự khắt khe là: **cổng 4 (55,29%)** ≫ cổng 1 (7,52%) ≫
cổng 2 (3,61%) ≫ cổng 5 (1,46%). Ba cổng còn lại không chặn bài nào.

> **Cổng 3 đã sửa 18/09.** Bản trước đặt nó là cổng CHẶN và loại 4.288 bài. Đó là đọc
> ngược tài liệu: §3 nói có niêm/đối/độc vận là **được phép**, và F5 nói **"không giới hạn
> số dòng ở con số 4 hoặc 8"**. Nay cổng 3 chỉ ghi nhận, không loại ai. Chi tiết ở
> `docs/Report_stage_of_rule.md` §7.3.

**Cổng 4 là nút cổ chai thật sự** — một mình nó loại 30.571 bài, **81,16% toàn bộ bài
trượt**, gấp **6,5 lần** cổng đứng thứ hai (cổng 1, 4.668 bài).

> **Tỉ trọng này tăng mạnh sau QĐ-7b.** Trước đó cổng 5 còn chặn 6.576 bài và cổng 4
> chiếm 69,66%. Nay cổng 5 chỉ còn 360 bài, nên phần của cổng 4 dồn lên 81,16%. Số bài
> cổng 4 chặn **không đổi một bài** — chỉ mẫu số đổi.

### 0.3. Đối soát

```
67.150 dòng đọc = 67.150 bản ghi parse được = 67.150 id duy nhất       ✅
67.150 bản ghi  = 24.366 đạt + 37.668 trượt + 5.116 không có nội dung  ✅
62.034 lần gọi rule.py = 24.366 đạt + 37.668 trượt                     ✅
```

Không bản ghi nào bị bỏ sót, trùng, hay đếm hai lần.

### 0.4. ⚠️ Ba điều phải biết trước khi dùng con số 24.366

**1. Cổng 6 chặn 0 bài, và đó KHÔNG phải vì thơ đạt nhịp.**
Ngắt nhịp là ngắt theo *ranh giới từ*. Chưa có bộ tách từ tiếng Việt nên mọi dòng 7
tiếng đều "cắt được" theo cả bảy kiểu — phép kiểm rỗng nghĩa. Bằng chứng trực tiếp:
**100,00% bài đạt được gán nhịp chủ đạo `4/3`** — không phải vì thơ Việt toàn nhịp
4/3, mà vì giao của bảy kiểu luôn khác rỗng và `4/3` đứng đầu bảng. **24.366 là con số
chưa qua kiểm nhịp thật sự.**

**2. Cổng 7 chặn 0 bài, nhưng đây là đúng.**
S16–S21 phần lớn là *quyền* (*"không hạn định"*, *"có thể"*). Nguyên tắc N2 cấm dùng
điều loại quyền để đánh trượt — loại một bài vì tác giả dùng đúng cái quyền tài liệu
cho phép là mâu thuẫn tự thân.

**3. Ba điều luật không kiểm được bằng máy, đã ghi công khai trong từng biên bản.**
S3 (*P7 chọn có chủ đích*), S15 (*đổi nhịp trùng chỗ chuyển ý*), S19 (*mạch cảm xúc*)
đòi ý đồ tác giả hoặc ngữ nghĩa. F2 (*phép đối*) và F4 (*bố cục Khai–Thừa–Chuyển–Hợp*)
cũng vậy — nên cổng 3 chỉ xét ba trong bốn vế và hàm mang tên `nghi_la_duong_luat`.

---

## 1. Phương pháp

Một lượt duy nhất qua toàn bộ tệp, mỗi bài đưa qua `kiem_tra_bai_tho()`, chạy **tuần
tự** qua bảy tầng. Trượt tầng nào thì **dừng ngay**; các tầng sau mang `da_chay=False`.

Dừng sớm không phải để nhanh mà để **đúng**: tính khuôn thanh trên một dòng 6 tiếng là
gán cho tác giả một lựa chọn phong cách mà họ chưa hề thực hiện.

### 1.1. Bảy tầng và tiêu chí chặn

| Tầng | Điều luật | Tiêu chí chặn | Nguồn quyết định |
|---|---|---|---|
| 1. Hình thức và số dòng | H3, **H4** | Từ 4 dòng trở lên **và** số dòng là bội của 4 | Tài liệu §2 |
| 2. Độ dài dòng | H1, H2 | **Mọi** dòng đúng 7 tiếng | Tài liệu §2, §10 |
| 3. Đối chiếu Đường luật | F1–F5 | **không chặn** — chỉ ghi nhận `nghi_duong_luat` | Tài liệu §3, F5 |
| 4. Thanh luật | S1–S3 | **Mọi** dòng khớp khuôn `B T B` hoặc `T B T` | QĐ-1, QĐ-2 |
| 5. Vần | S6, S9–S12 | ≥1 cụm **4 dòng liên tiếp** có vần chân | QĐ-3, QĐ-5, QĐ-7, QĐ-7b |
| 6. Nhịp | S13–S15 | Mọi dòng thuộc bảy kiểu, và có nhịp chủ đạo phủ cả bài | QĐ-4, QĐ-4b, QĐ-6b |
| 7. Khổ và bố cục | S16–S21 | Không có khổ rỗng | Tài liệu §7 |

### 1.2. Ba chỗ dự án chặt hơn tài liệu — nêu minh bạch

| Tài liệu nói | Dự án quyết |
|---|---|
| S2: P2/P4/P6 ***nên*** luân phiên — chữ *nên*, nói ở mức dòng | **QĐ-1**: bắt buộc, áp lên **mọi** dòng |
| ~~S4~~: ***có thể*** phá khuôn — **đã xoá khỏi bảng luật 18/09** | **QĐ-2**: không cho phá khuôn |
| S13: nhịp ***không cố định*** cho toàn bài | **QĐ-4b**: phải có một nhịp chủ đạo phủ mọi dòng |

> **Bốn mã đã xoá khỏi bảng luật ngày 18/09/2026:** `S4` (quyền phá khuôn), `S5` (cách phá
> khuôn), `S7` (gộp vào `S1`), `S8` (quyền không gieo vần — chọi với QĐ-7b). Bảng luật đi
> từ 30 điều xuống **26 điều**; số hiệu để trống vĩnh viễn, không đánh lại. Chi tiết:
> `docs/Report_stage_of_rule.md` §3.1.

Đây là **chính sách của dự án**, không phải cách đọc tài liệu. Văn bản
`Luat_Tho_That_Ngon_Tu_Do.md` giữ nguyên, không sửa một chữ. Vì vậy báo cáo luôn nêu
song song hai con số ở §0.1.

### 1.3. Bảng vần có nguồn

Tầng 5 dùng bảng vần thông của **Trần Trọng Kim, *Việt thi*, mục I-6**, bản số hoá
Wikisource; đối chiếu với **Bùi Kỷ, *Quốc văn cụ thể*, Tân Việt 1950**. Hồ sơ nguồn đầy
đủ: `docs/Nguon_Bang_Van_Thong.md`.

Bảng gồm **73 cạnh từ nguồn + 4 cạnh suy diễn = 77 cạnh, 62 vần**, và là **đồ thị,
không phải phân hoạch**: quan hệ hiệp vần **không bắc cầu**. Chính tác giả viết
*"ang thông với ương (không thông được với uông…)"* rồi vài dòng sau *"uông thông với
ương"*. Ép bảng này thành các lớp tương đương sẽ bịa thêm **18** cặp hiệp vần mà nguồn
không cho. *(Con số 16 là đo trên 73 cạnh nguồn; trên đủ 77 cạnh là 18.)*

### 1.4. Hai mức số liệu

| Loại | Dùng để | Ví dụ trong báo cáo này |
|---|---|---|
| **Mức bài** | Ra quyết định: nhận, loại, sửa, đổi nhãn | 24.366 đạt · 37.668 trượt |
| Mức dòng | Chỉ chẩn đoán nguyên nhân | 160.828 lần vi phạm S2 |

Một bài có thể phạm cùng một điều ở nhiều dòng, nên **số lần vi phạm luôn lớn hơn số
bài** và hai loại số này không so sánh trực tiếp được.

**Một chỉ số đã bị loại khỏi báo cáo:** lần đo đầu có mục *"dòng hỏng có chữ Latin —
99,19%"*. Đó là rác đo đạc, vì tiếng Việt viết bằng chữ Latin nên `[a-zA-Z]` khớp mọi
dòng. Bản này dùng dấu hiệu `f, j, w, z` để nhận diện tên riêng ngoại ngữ thật.

---

## 2. Cấu trúc bản ghi kết quả

Mỗi bài xuất ra một dòng JSON mang **dấu vết đầy đủ bảy tầng**, để câu trả lời *"vì sao
pass"* và *"vì sao trượt"* đều kiểm lại được từng vế.

> **Bổ sung 18/09 — bản ghi nay TỰ ĐỨNG ĐƯỢC.** Trước đây tệp chỉ có bằng chứng **mức
> tầng** (*"8/8 dòng khớp khuôn"*). Muốn kiểm lại một câu ấy thì phải mở tệp nguồn 60 MB,
> tìm đúng id, rồi tự đếm tiếng và tự phân thanh — tức là **bằng chứng không tự kiểm
> được**. Nay mỗi bản ghi mang thêm hai trường:
>
> - **`tho`** — nguyên văn bài thơ
> - **`dong`** — dấu vết từng dòng: `so_tieng`, `tieng[]`, `thanh[]`, `P2_P4_P6`,
>   `khuon`, `van_cuoi`, `thanh_cuoi`
>
> `P2_P4_P6` trả `null` cho dòng không đủ 7 tiếng, để phân biệt *"không có P2/P4/P6 của
> thể"* với *"có nhưng lệch khuôn"*. Cả `bai_dat.jsonl` lẫn `bai_truot.jsonl` đều có.

### 2.1. Bài đạt — `datalake/analysis/bai_dat.jsonl`

Trường `ly_do_dat` ghép bằng chứng của **cả bảy cổng**:

```
T1 Hình thức và số dòng: 8 dòng — có phân dòng, và 8 = 4 × 2
T2 Độ dài dòng: 8/8 dòng đúng 7 tiếng; nhỏ nhất = lớn nhất = 7
T3 Đối chiếu Đường luật: 8 dòng — không đủ ba vế số dòng + độc vận + niêm
T4 Thanh luật: 8/8 dòng khớp khuôn; 0 dòng phá khuôn; 2 cụm 4 dòng theo tổ hợp
   #10 #10
T5 Vần: dòng 1–4 có vần chân, sơ đồ aaxa (vần ba dòng, kế thừa Đường luật):
   mài / nhai / kín / dài; tổng 5 cụm có vần
T6 Nhịp: nhịp chủ đạo 4/3 phủ cả 8/8 dòng — KHÔNG có khai báo nhịp nên chỉ
   kiểm được số học
T7 Khổ và bố cục: 1 khổ, kích thước [8], không khổ rỗng
```

### 2.2. Bài trượt — `datalake/analysis/bai_truot.jsonl`

Mang thêm `tang_dung_lai` và `ly_do_truot` có **địa chỉ dòng**:

```
tang_dung_lai: 4
ly_do_truot: [{ma_luat: "S2", dong: 1,
               ky_vong: "P2/P4/P6 luân phiên theo khuôn bằng (B T B)",
               thuc_te: "P2/P4/P6 = T B B",
               goi_y: "Đổi thanh ở P2, P4 hoặc P6"}]
```

Các tầng sau tầng dừng đều mang `da_chay: false` — **chưa kiểm**, khác hẳn *đã kiểm và
đạt*.

### 2.3. Một bản ghi hoàn chỉnh gồm những gì

```
id · tieu_de · trang_thai · thuoc_the
tho                  nguyên văn bài thơ
dong[]               dấu vết từng dòng (7 trường mỗi dòng)
tang[]               bảy tầng: ma_luat, da_chay, dat, trich_luat, bang_chung, chi_tiet
ly_do_dat            bằng chứng bảy cổng ghép thành một câu
bang_chung           tóm tắt mức bài
dac_diem_mem         so_kho, kich_thuoc_tung_kho, so_do_van_theo_kho,
                     ma_phoi_khuon_theo_cum, van_lung, cap_van_lech_thanh,
                     ty_le_dong_theo_khuon, nghi_duong_luat
ghi_chu[]            ghi chú mức bài
```

Bài trượt có thêm `tang_dung_lai` và `ly_do_truot`.

---

## 3. BÀI ĐẠT — chân dung 24.366 bài qua đủ bảy tầng

### 3.1. Độ dài

| Số dòng | Số bài | Tỷ lệ | Dáng |
|---:|---:|---:|---|
| 8 | 13.130 | 53,89% | **Bát cú** — một khối tám dòng liền, dáng cổ điển nhất |
| 4 | 3.903 | 16,02% | **Tứ tuyệt** — một khổ trọn vẹn |
| 16 | 2.816 | 11,56% | 4 khổ × 4 dòng |
| 12 | 936 | 3,84% | 3 khổ × 4 dòng |
| 28 | 936 | 3,84% | 7 khổ × 4 dòng |
| 20 | 841 | 3,45% | 5 khổ × 4 dòng |
| 24 | 581 | 2,38% | 6 khổ × 4 dòng |
| 56 | 286 | 1,17% | Trường thiên |

Hơn **một nửa** bài đạt là bát cú 8 dòng. Phần còn lại gần như đều là bội số của 4 —
dấu hiệu corpus nghiêng mạnh về cấu trúc khổ tứ tuyệt.

### 3.2. Cấu trúc khổ

| Số khổ | Số bài | Tỷ lệ |
|---:|---:|---:|
| 1 | 15.690 | 64,39% |
| 2 | 2.138 | 8,77% |
| 4 | 2.045 | 8,39% |
| 3 | 988 | 4,05% |
| 7 | 943 | 3,87% |
| 5 | 873 | 3,58% |

### 3.3. Sơ đồ vần — cụm bốn dòng có vần chân

Đếm theo **cụm**, không theo bài: một bài dài có nhiều cụm bốn dòng liên tiếp.
Tổng **189.422 cụm có vần chân** trên 24.366 bài, trung bình **7,77 cụm mỗi bài**.

Từ QĐ-7b (18/09/2026) tiêu chí là *"cụm phải có ít nhất một cặp hiệp vần chân"*,
không phải *"phải khớp một trong bốn sơ đồ §5.2"*. Bảng dưới vì vậy gồm **mọi** sơ
đồ có vần, không riêng bốn sơ đồ có tên.

| Sơ đồ | Số cụm | Tỷ lệ | Ghi chú |
|---|---:|---:|---|
| `axax` | 37.314 | 19,70% | D1–D3 hiệp, D2–D4 buông |
| `aaxa` | 32.147 | 16,97% | **Vần ba dòng, kế thừa Đường luật** (§5.2) |
| `xaxa` | 26.806 | 14,15% | D2–D4 hiệp |
| `aaaa` | 19.923 | 10,52% | **Độc vận cả cụm** — trước QĐ-7b bị loại |
| `xaax` | 17.081 | 9,02% | |
| `xxaa` | 17.004 | 8,98% | |
| `aaax` | 7.396 | 3,90% | |
| `xaaa` | 7.391 | 3,90% | |
| `axaa` | 6.185 | 3,27% | |
| `aaxx` | 5.710 | 3,01% | |
| `abab` | 4.039 | 2,13% | **Vần cách** (§5.2) |
| `axxa` | 4.198 | 2,22% | |
| `aabb` | 2.441 | 1,29% | **Vần liền** (§5.2) |
| `abba` | 1.176 | 0,62% | **Vần ôm** (§5.2) |
| `????` và biến thể | 611 | 0,32% | Quan hệ vần **không bắc cầu** — cụm không quy về sơ đồ chữ cái, nhưng **vẫn có vần chân** |

**Bốn sơ đồ §5.2 chỉ chiếm khoảng một phần năm số cụm.** Con số này là lý do QĐ-7b đúng: nếu
giữ danh sách đóng thì gần bốn phần năm quan hệ vần thật trong corpus bị coi như
không tồn tại.

### 3.4. Đặc điểm mềm — ghi nhận, không dùng để loại

| Đặc điểm | Số bài | Tỷ lệ | Ghi chú |
|---|---:|---:|---|
| Có vần lưng ở P4/P5 | 13.533 | 55,54% | S1 (gộp S7) là **quyền** — làm dòng thơ dính chặt hơn |
| Có cặp vần lệch lớp thanh | 9.168 | 37,63% | S9 **cho phép** — ví dụ `xanh` (B) hiệp `mảnh` (T) |

### 3.5. Nhịp — số liệu này KHÔNG dùng được

| Nhịp chủ đạo | Số bài | Tỷ lệ |
|---|---:|---:|
| `4/3` | 24.366 | **100,00%** |

**Đừng đọc bảng này là "toàn bộ thơ đạt đều nhịp 4/3".** Nó là hiện vật đo đạc: không
có bộ tách từ thì mọi dòng 7 tiếng đều cắt được theo cả bảy kiểu, giao luôn khác rỗng,
và `4/3` là phần tử đầu bảng. Con số 100,00% chính là **bằng chứng tầng 6 đang rỗng
nghĩa**, không phải một phát hiện về thơ.

---

## 4. BÀI TRƯỢT — 37.668 bài, dừng ở cổng nào

### 4.1. Phân bố theo cổng dừng

| Cổng dừng | Số bài | Tỷ lệ | Ví dụ |
|---|---:|---:|---|
| **1. Hình thức và số dòng** | **4.668** | **12,39%** | id=7391 *"UỐNG TRÀ"* — 6 dòng |
| 2. Độ dài dòng | 2.069 | 5,49% | id=4557 *"Xuân bất tận"* — D1 sáu tiếng |
| 3. Đối chiếu Đường luật | **0** | — | tầng ghi nhận, không chặn |
| **4. Thanh luật** | **30.571** | **81,16%** | id=27 *"SAY"* — 4/8 dòng phá khuôn |
| 5. Vần | 360 | **0,96%** | id=4051 *"Xin ủ mùa thu"* — sơ đồ `xxxx` |
| 6. Nhịp | 0 | 0,00% | — |
| 7. Khổ và bố cục | 0 | 0,00% | — |

### 4.2. Số lần vi phạm theo điều luật

| Mã | Số lần | Điều luật |
|---|---:|---|
| S2 | 160.828 | P2/P4/P6 nên luân phiên bằng – trắc |
| H1 | 7.645 | Mỗi dòng phải có đúng 7 tiếng |
| **H4** | **4.668** | Số dòng trong bài phải là bội của 4 |
| H3 | 655 | Văn bản phải được phân dòng, từ 4 dòng trở lên |
| S11 | **360** | Sơ đồ vần — cụm bốn dòng phải có vần chân |

**S11 từ 6.576 xuống 360** sau QĐ-7b. Đây là thay đổi lớn nhất của lượt đo này.

**H2 không bao giờ xuất hiện trong bảng**, và đó là đúng thiết kế: H2 nói *"H1 áp dụng
cho toàn bộ các dòng"* — một điều luật về **lượng từ**, được thi hành bằng cấu trúc vòng
lặp không có nhánh miễn trừ, chứ không bằng một phép kiểm sinh `ViPham`.

**F3 đã biến mất khỏi bảng này.** Bản trước ghi 4.288 lần vi phạm F3 — nhưng F3 nói
*"Không yêu cầu độc vận cho toàn bài"*, tức là một câu **nới**. Không ai "vi phạm" được
một điều chỉ nói rằng thứ gì đó không bắt buộc. Xem `Report_stage_of_rule.md` §7.3.

Nhắc lại: đây là **số lần vi phạm**, không phải số bài. 160.828 lần phạm S2 rải trên
30.571 bài — trung bình 5,26 dòng phá khuôn mỗi bài.

**Nhưng trung bình che mất hình dạng thật.** Phân bố lệch phải rất mạnh:

| Số dòng phá khuôn | Số bài | Tỷ lệ |
|---:|---:|---:|
| **1** | **6.162** | **20,16%** |
| 2 | 4.295 | 14,05% |
| 3 | 3.626 | 11,86% |
| 4 | 3.005 | 9,83% |
| 5 | 2.382 | 7,79% |
| 6 trở lên | 11.101 | 36,31% |

**Một phần năm số bài ở cổng 4 chỉ lệch đúng MỘT dòng.** Nếu QĐ-1 được nới thành *"cho
phép tối đa 1 dòng phá khuôn"*, 6.162 bài sẽ qua được cổng này. Báo cáo nêu con số,
**không** đề xuất nới.

### 4.3. Cổng 1 — số dòng không phải bội của 4

**4.668 bài** — cổng chặn nhiều thứ hai, sau cổng 4.

| Dư khi chia 4 | Số bài | Tỷ lệ |
|---:|---:|---:|
| 2 | 2.043 | 43,77% |
| 3 | 1.388 | 29,73% |
| 1 | 1.237 | 26,50% |

| Số dòng | Số bài | Tỷ lệ |
|---:|---:|---:|
| **6** | **943** | **20,20%** |
| 3 | 548 | 11,74% |
| 7 | 502 | 10,75% |
| 5 | 473 | 10,13% |
| 10 | 309 | 6,62% |
| 14 | 243 | 5,21% |

Ví dụ thật — id=7391 *"UỐNG TRÀ"*, thơ chỉnh nhưng 6 dòng:

```
Ghế đá thảnh thơi thưởng thức trà,
Uống chè thanh nhiệt ẩm lòng ta.
Nhâm nhi từng ngụm hồn phiêu lãng,
Nhìn ngắm mây trời đón xuân sang.
Cảnh sắc tạo nên những mơ màng,
Hồn thơ lai láng hát tình tang.

  → 6 dòng — không phải bội của 4 (dư 2)
  H4: cần "số dòng là bội của 4" | đang "6 dòng, dư 2 khi chia 4"
      Luật cứng, không có ngoại lệ — bài không thuộc thể.
      KHÔNG thêm hay bớt dòng để ép qua: nội dung thơ phải giữ nguyên.
```

**Dạng bị loại nhiều nhất là bài 6 dòng** — 943 bài, một phần năm. Đáng lưu ý vì `S17`
trong tài liệu có nhắc *"khổ phổ biến là 4 dòng; cũng dùng được khổ 2, 3, 5, 6 dòng"*.
Nếu chủ dự án muốn nhận khổ 6 dòng thì đây là chỗ xem lại trước tiên.

Chỉ **655** bài trong số này vi phạm thêm H3 (dưới 4 dòng); phần còn lại đủ dài nhưng sai
bội 4.

> **Biên bản của cổng này KHÔNG gợi ý sửa bài.** H4 là luật cứng: sai là sai, và thêm hay
> bớt dòng để ép qua là **sửa nội dung thơ** — điều chủ dự án đã cấm thẳng. Bộ kiểm phán,
> không viết thơ hộ.

### 4.4. Cổng 2 — dòng sai số tiếng

**2.069 bài, 7.645 dòng hỏng.** Ví dụ có bằng chứng:

```
id=13   "QUA TÌM BẬU BẬU NƠI ĐÂU": 1/20 dòng sai
    D17: Đường về ngơ ngác hỏi bậu vì đâu?     cần 7 tiếng | đang 8

id=39   "THƯƠNG MẸ LẮM MẸ ƠI": 1/28 dòng sai
    D3:  Mắt mẹ loà rồi, mẹ nghỉ đi thôi,      cần 7 tiếng | đang 8

id=2729 "(không tiêu đề)": 1/16 dòng sai
    D7:  Bao giờ nước sông ngừng chảy,         cần 7 tiếng | đang 6
```

Cả ba đều là dạng **19–27 dòng hoàn hảo, một dòng lệch** — H2 không có ngoại lệ.

> **Ví dụ cũ đã phải thay.** Bản trước dùng `id=17 "THÀNH CỔ"` làm ví dụ cổng 2 (dòng ký
> tên `— Lê Bá Dương` chỉ 3 tiếng). Sau khi có **H4**, bài ấy 5 dòng nên **trượt ngay ở
> cổng 1** và không bao giờ tới cổng 2 nữa. Ví dụ đã đổi sang ba ca thật hiện tại. Ca
> `id=17` nay xem ở `Report_stage_of_rule.md` §8.3.3 (dạng dòng ký tên).

### 4.5. Cổng 3 — ghi nhận, không chặn

**4.288 bài** được đánh dấu `nghi_duong_luat` nhưng **đi tiếp bình thường**.

```
id=1 "BÂNG KHUÂNG": 8 dòng, độc vận và có niêm — giống khuôn Đường luật,
                    nhưng §3 cho phép nên KHÔNG loại
```

Trong 4.288 bài này: toàn bộ qua cổng 4 (Đường luật vốn chặt về niêm luật), và từ
QĐ-7b **cả 4.288 bài đều vào tập đạt** — 0 bài trượt cổng 5. Trước QĐ-7b có 2.096
bài trượt vì độc vận `aaaa` không nằm trong bốn sơ đồ §5.2.

### 4.6. Cổng 4 — phá khuôn thanh luật (nút cổ chai)

**30.571 bài — 81,16% toàn bộ bài trượt.**

```
id=2 "ANH GỬI CHO EM": 13/32 dòng phá khuôn: D1, D3, D4, D5, D8, D17, D20, D21…
    D1: Anh gửi cho em gửi bông vàng,
    cần P2/P4/P6 luân phiên theo khuôn bằng (B T B) | đang P2/P4/P6 = T B B
```

**Đây là chỗ cần đọc kỹ nhất của cả báo cáo.** Tài liệu luật dùng chữ ***nên*** ở S2 và
cho phép phá khuôn ở S4. Nếu đọc theo đúng câu chữ tài liệu, phần lớn trong 30.571 bài
này **không sai gì cả**. Chúng trượt vì **QĐ-1 và QĐ-2** — hai quyết định của dự án,
chặt hơn tài liệu.

Con số này là cái giá đo được của yêu cầu *"tuân thủ toàn bộ Rule"*. Báo cáo nêu thẳng
để chủ dự án cân nhắc, **không** đề xuất nới luật.

### 4.7. Cổng 5 — không cụm bốn dòng nào có vần chân

**360 bài** — 1,46% số bài vào cổng, **0,96%** toàn bộ bài trượt.

Từ QĐ-7b (18/09/2026) tiêu chí là *"trong phạm vi bốn câu, nếu không có vần chân nào
thì trượt"*. Cụm duy nhất bị loại là `xxxx`.

**Cả 360 bài đều là `xxxx`** — không cặp tiếng cuối nào trong bất kỳ cụm bốn dòng nào
hiệp vần. Đây là số liệu, không phải ước lượng: mọi bằng chứng ở cổng này đều ghi
`xxxx`.

Ví dụ thật, id=4051:

```
Cho tôi ủ chút sương trăng trước,
Với lá vàng rơi cuối ngõ khuya.
Nhỡ khi tiếc nuối người quay lại,
Đã sẵn hương thu ướp tóc thề.

  → không cụm bốn dòng liên tiếp nào có vần chân — dòng 1–4: xxxx
```

**Thay đổi so với bản trước.** Cổng 5 từng chặn 6.576 bài vì đòi khớp đúng một trong
bốn sơ đồ §5.2. Ba nhóm lớn nhất bị loại khi đó — `aaaa` độc vận (2.277), `xaxa`
(1.531), `aaxx` (972) — **đều có vần chân thật sự**, chỉ là sơ đồ không có tên trong
§5.2. Nay cả ba đều đạt.

> **S8 đã bị xoá khỏi bảng luật** cùng ngày. S8 nói *"Bài có thể không gieo vần"*,
> trong khi cổng này loại đúng bài không gieo vần. Giữ cả hai là tự mâu thuẫn, và vi
> phạm N2 ngay trong chính tầng 5.

## 5. Vấn đề chất lượng dữ liệu ngoài luật thơ

> **Phạm vi mục này:** các con số dưới đây nói về **chất lượng bản ghi**, không phải về
> phán quyết luật thơ. Chúng không đổi khi bộ luật đổi — nhưng ở lượt 18/09 vẫn được
> **chạy lại và đối chiếu**, không mang sang từ bản cũ. Hai chỗ đã sửa: số khoá lạ
> (31 → **29**, đếm lại bằng máy) và chất lượng phần cứu được ở §5.1.1.


| Vấn đề | Số lượng | Tỷ lệ | Hậu quả thực tế |
|---|---:|---:|---|
| `markdown_poem` rỗng nhưng vẫn có `score` | 5.116 | 7,6% | Đường ống đã **chấm điểm cho nội dung không tồn tại** |
| Bài trùng nội dung hoàn toàn | 15.916 bản dư (15.029 nhóm) | — | Huấn luyện trên tập này sẽ **đè trọng số** lên vài nghìn bài lặp |
| `original_title` rỗng | 42.883 | 63,9% | Không truy ngược được nguồn, không khử trùng theo tên được |
| `source_file` thiếu | 65.978 | 98,3% | Không biết bài đến từ đợt thu thập nào |
| Khoá lạ trong `result` | **29 khoá khác nhau** | — | Nội dung thật **nằm rải rác ở khoá sai** — xem §5.1.1 |

### 5.1. Trôi lược đồ — 29 khoá lạ

`content_fix` · `content_note` · `content_analysis` · `content_fixed` · `title_fixed` ·
`markdown_poem_content` · `content` · `title_inferred` · `markdown_poem_fixed` ·
`content_correction` · `content_fix_notes` · `content_processed` · `title_correction` ·
`content_notes` · `content_correction_notes` · `title_fix` · `markdown_content` ·
`title_suggestion` · `title` · `poem_type_detail` · `markdown_poem_final` ·
`markdown_poem_full` · `evaluation_details` · `error_fixes` · `correction_notes` ·
`content_details` · `poem_content` · `markdown_type` · `content_fix_note`

`result` có **33 khoá** tất cả; bốn khoá chuẩn là `markdown_poem`, `score`,
`score_reason`, `poem_type`. Còn lại **29 khoá lạ** liệt kê trên.

Đây là dấu vết một đường ống chắp vá: mỗi lần vá lỗi lại sinh một tên khoá mới.

*(Bản trước ghi 31; đếm lại bằng máy ra 29 — danh sách liệt kê vốn đã đúng 29 mục, chỉ
con số trong tiêu đề là sai.)*

### 5.1.1. KẾT QUẢ TRUY 5.116 BÀI RỖNG — đã thực hiện

Quét toàn bộ 5.116 bản ghi có `markdown_poem` rỗng, tìm trong 14 khoá có khả năng chứa thơ, lấy giá trị chuỗi đầu tiên có xuống dòng:

| Kết quả | Số bài |
|---|---:|
| **CỨU ĐƯỢC — nội dung nằm ở khoá khác** | **1.934** (37,8%) |
| Không có nội dung ở bất kỳ khoá nào | 3.182 (62,2%) |

**Nội dung nằm ở đâu:**

| Khoá | Số bài |
|---|---:|
| `markdown_poem_content` | 703 |
| `content_fix` | 490 |
| `content_fixed` | 366 |
| `content` | 269 |
| `markdown_poem_fixed` | 93 |
| `content_processed` | 4 |
| `content_correction` | 3 |
| `markdown_content` | 2 |
| `poem_content` · `markdown_poem_final` · `markdown_poem_full` · `content_details` | 4 |

**Chất lượng phần cứu được:** **673 / 1.934 bài (34,8%) đạt luật ngay** khi đưa qua `rule.py` — đo lại 18/09 bằng bộ luật bảy tầng. *(Bản trước ghi 1.244/64,3%, nhưng đó là đo bằng bộ luật cũ khi chưa có H4 và chưa có ba tầng chặn S2/S11/S14.)*

Ví dụ `id=2875`, nội dung nằm ở `content_fix`, đạt luật:

```
Xuân còn nấn ná ở xung quanh,
Chợt rét nàng Bân đuổi nắng hanh.
Bất chấp mai đào đang gạ nở,
Heo may õng ẹo lả lơi cành.
```

Toàn bộ đã xuất ra `datalake/analysis/bai_rong_cuu_duoc.jsonl`.

> **Kết luận:** **673** bài thơ đạt đủ bảy tầng đang bị bỏ phí chỉ vì đường ống ghi vào sai tên khoá. Đây là số bài thu hồi được **không tốn một đồng gọi mô hình nào**.

3.182 bài còn lại rỗng thật — nhưng vẫn có `score` và `score_reason`, nghĩa là **đường ống đã chấm điểm cho nội dung không tồn tại**. Đó là một lỗi cần truy ngược lên phía sinh dữ liệu.

### 5.2. `score` và việc đạt luật — ĐO LẠI, kết luận cũ đã đổi

> ⚠️ **Mục này đã đo lại từ đầu sau QĐ-7b và kết luận cũ KHÔNG còn đúng.** Bản trước
> kết luận *"score không dự báo được việc đạt luật"*, nhưng nó đo bằng cột **thuộc thể**
> — một chỉ số gần bão hoà (82–96%), nên mọi khác biệt bị nén lại. Đo bằng cột **đạt cả
> bảy tầng** cho ra bức tranh khác hẳn.

| score | Số bài | % thuộc thể | **% ĐẠT cả bảy tầng** |
|---:|---:|---:|---:|
| 2 | 100 | 60,00% | 24,00% |
| 3 | 457 | 61,49% | 26,70% |
| 4 | 3.168 | 69,76% | 24,43% |
| 5 | 9.167 | 82,49% | 24,36% |
| 6 | 2.907 | 92,02% | 34,81% |
| 6,5 | 24.394 | 90,74% | 37,79% |
| 7 | 2.182 | 96,52% | 47,39% |
| 7,5 | 17.407 | 94,13% | 51,29% |
| **8** | 929 | 91,71% | **57,70%** |
| **8,5** | 1.191 | 78,76% | **37,62%** |

**Hai điều đọc được:**

1. **Từ score 2 đến score 8, tỷ lệ đạt tăng gần đơn điệu: 24% → 58%.** Đây là tương quan
   thật, và nó bác bỏ kết luận cũ. Bộ chấm *có* bắt được tín hiệu liên quan tới việc tuân
   thủ luật thơ — chỉ là tín hiệu ấy bị cột *thuộc thể* che mất.
2. **Score 8,5 gãy khỏi xu hướng** — rơi từ 57,70% xuống 37,62%, thấp hơn cả score 6,5.
   Nó cũng có tỷ lệ *thuộc thể* thấp bất thường (78,76%, thấp hơn mọi mức từ 5 trở lên).
   Giả thuyết cũ vẫn đứng vững cho riêng nhóm này: bộ chấm khen những bài **thơ 8 chữ**
   hay, vốn không thuộc thể bảy chữ.

**Phân bố điểm vẫn dồn cục bất thường:** 6,5 và 7,5 chiếm 41.801 / 62.034 bài = **67,4%**
corpus. Đó là dấu hiệu chấm bằng máy với thang thô.

> **Khuyến nghị đã đổi.** Không còn nói *"không dùng score làm tiêu chí lọc"*. Nói chính
> xác hơn: **score dùng được để XẾP ƯU TIÊN, không dùng được để LỌC NHỊ PHÂN** — ngay ở
> mức cao nhất (8) cũng chỉ 57,70% đạt luật, nên không có ngưỡng nào cho ra tập sạch.
> Và **phải loại riêng nhóm 8,5** trước khi dùng.

## 6. Điểm mù của H1 — đã đo, và khuyến nghị

> **Phạm vi mục này:** đo trên toàn corpus ở mức DÒNG, độc lập với bảy tầng. **Đã đo lại
> ngày 18/09** bằng `datalake/scripts/do_diem_mu.py` — kết quả đổi đáng kể, xem §6.2.


### 6.1. Điểm mù là gì

```
"(1957)"  →  "một nghìn chín trăm năm mươi bảy"  →  7 tiếng  →  ĐẠT
```

Dòng chỉ ghi năm có thể **tình cờ đủ 7 tiếng** và lọt qua H1. `rule.py` làm đúng theo §2.1 của tài liệu luật; vấn đề nằm ở chỗ H1 đo *độ dài*, không đo *đây có phải câu thơ không*.

### 6.2. Đo mức độ thực tế

| Phép đo | Kết quả |
|---|---:|
| Dòng chỉ gồm chữ số trong toàn corpus | 17 |
| Trong đó đọc ra đúng 7 tiếng | 2 |
| **Nằm trong một bài ĐẠT (thật sự lọt lưới)** | **0** |

Hai dòng 7 tiếng đó đều nằm trong bài vốn đã trượt vì lý do khác. **Điểm mù có thật về nguyên tắc nhưng tần suất bằng không trong corpus này.**

Mở rộng phép đo sang mọi dấu hiệu cấu trúc phi thơ, đếm trên **24.366 bài ĐẠT** — tức
những bài đã lọt hết bảy cổng và sẽ thật sự đi vào tập huấn luyện:

| Dấu hiệu | Số bài đạt dính | Độ tin cậy của dấu hiệu |
|---|---:|---|
| Dòng bọc kín trong ngoặc hoặc dấu sao | 6 | **Cao** — không thấy ca báo nhầm nào |
| Khổ đầu chỉ có một dòng | 7 | **Thấp** — nhiều ca là câu thơ thật, xem cảnh báo ở §6.4 |
| Dòng ký tên tác giả | 0 | Không xuất hiện trong bài đạt |
| Dòng đánh số La Mã | 0 | Không xuất hiện trong bài đạt |
| **Tổng bài đạt có ít nhất một dấu hiệu** | **12 — 0,049%** | Tương đương **5 bài trên mỗi 10.000** |

> **Đo lại 18/09 sau QĐ-7b.** Bản trước ghi 42 bài trên tập đạt 16.391. Nay tập đạt là
> 24.366 — **lớn hơn 49%** — mà số bài dính dấu hiệu lại **giảm còn 12**. Không mâu
> thuẫn: các cổng mới (H4 ở cổng 1) loại đúng những bài có dòng siêu dữ liệu, vì dòng ấy
> làm số dòng lệch khỏi bội của 4. Điểm mù của H1 nay còn nhỏ hơn trước.

Ví dụ thật sự là nhiễu:

```
id=4354   D6 (7 tiếng): (Bát nước chè xanh vị đượm đà.)
id=179072 D5 (7 tiếng): (Đến khổ! Khi người yêu ở xa.)
id=207664 D10 (7 tiếng): (Phải đâu chỉ bố hiểu thầm thôi!)
```

Danh sách đầy đủ: `datalake/analysis/dong_nghi_ngo_trong_bai_dat.jsonl`.

### 6.3. Một bộ lọc SAI đã bị loại bỏ

Lần đo đầu tôi dùng mẫu từ vựng — dòng bắt đầu bằng *gửi · tặng · nhớ · tiễn* thì coi là lời đề tặng. Kết quả: **2.828 dòng bị gắn cờ, và phần lớn là dòng thơ thật**:

```
id=2  D2: Gửi hương hoa cải, bướm lang thang.   ← thơ, không phải đề tặng
id=6  D10: Tiễn một người yêu một buổi chiều.   ← thơ
id=65 D2: Nhớ về chuyện cũ dạ buồn hơn.        ← thơ
```

Lý do thất bại rất căn bản: *gửi, tặng, nhớ, tiễn* **chính là từ vựng của thơ trữ tình**. Một bộ lọc dựa vào chúng sẽ cắt mất đúng phần dữ liệu tốt nhất.

> **Bài học:** với dữ liệu thơ, tín hiệu **từ vựng** không phân biệt được thơ với siêu dữ liệu. Chỉ tín hiệu **cấu trúc** làm được.

### 6.4. Khuyến nghị

**Không thêm luật nào vào `rule.py`.** Tài liệu luật không quy định "dòng phải là câu thơ", nên thêm vào đó là bịa luật. Việc lọc nhiễu thuộc **tầng chuẩn bị dữ liệu**, không thuộc tầng luật thơ.

Đề xuất một bước tiền xử lý riêng, đặt trước khi kiểm luật, với đúng bốn quy tắc có độ chính xác cao:

| # | Quy tắc | Căn cứ |
|---|---|---|
| L1 | Bóc dòng **bọc kín** trong `( )`, `[ ]` hoặc `*...*` | **6** ca trong bài đạt, không có ca báo nhầm nào |
| L2 | Bóc dòng **chỉ gồm chữ số** hoặc số La Mã | 17 ca toàn corpus, 0 ca trong bài đạt |
| L3 | Bóc dòng **đầu/cuối bài** mà không đủ 7 tiếng | bắt trọn nhóm F (242 bài) |
| L4 | Bóc dòng có **trên 15 tiếng** | bắt trọn nhóm B (22 bài) |

Bốn quy tắc này đều dựa vào **hình thức và vị trí**, không đụng tới từ vựng, nên không cắt nhầm thơ.

**Ba quy tắc KHÔNG nên dùng**, vì đã đo và thấy báo nhầm:

- ❌ Dòng bắt đầu bằng *gửi · tặng · nhớ · tiễn* → 2.828 ca, phần lớn là thơ thật
- ❌ Dòng kết thúc bằng dấu hai chấm → 427 ca, nhiều dòng thơ dẫn lời nói
- ❌ Khổ đầu chỉ một dòng → `"Bâng khuâng trời rộng nhớ sông dài."` là câu thơ Huy Cận

**Về ngưỡng chấp nhận:** với tần suất **0,049%**, điểm mù này **không đáng chặn cả đường
ống**. Khuyến nghị đưa **12** bài vào danh sách rà tay một lần, rồi chuyển L1–L4 thành
bước tiền xử lý thường trực cho các đợt nạp dữ liệu sau.

Riêng **L1 nay chỉ còn 6 ca** nên gần như không còn việc; hai quy tắc đáng giữ là **L3**
(bóc dòng đầu/cuối không đủ 7 tiếng — bắt trọn nhóm F, 242 bài) và **L4** (dòng trên 15
tiếng — bắt trọn nhóm B, 22 bài), vì chúng nhắm vào **bài trượt**, nơi còn 37.668 bản
ghi chứ không phải 12.

---

## 7. Dữ liệu dùng được và đề xuất hành động

Bảng này trả lời câu hỏi thực dụng: **lấy được bao nhiêu bài để huấn luyện.**

| Tập | Số bài | Trạng thái |
|---|---:|---|
| **Đạt cả bảy tầng** | **24.366** | dùng được, nhưng còn trùng lặp — xem §5 |
| Thuộc thể nhưng chưa đạt chuẩn dự án | 30.931 | rà theo cổng dừng, **gần như toàn bộ ở cổng 4** |
| Cứu bằng bóc dòng siêu dữ liệu (nhóm B, C, F) | 298 | tự động hoá được |
| Cứu bằng sửa tay (nhóm D, E) | 1.398 | cần người |
| Bản ghi rỗng nhưng thu hồi được nội dung | 1.934 | chạy `datalake/scripts/ba_viec.py` |
| Tách sang bộ 8 chữ | 135 | đổi nhãn, không phải sửa |

### 7.1. Ba việc đáng làm, xếp theo tỉ lệ đổi lại

1. **Cổng 4 là chỗ duy nhất còn đáng bàn** — 30.571 bài, **81,16% toàn bộ bài trượt**.
   Cổng 5 nay chỉ còn 360 bài. Nếu muốn thêm dữ liệu thì phải nhìn lại QĐ-1/QĐ-2, không
   còn chỗ nào khác để lấy.

   *(Hai mẫu số dễ lẫn: **81,16%** là phần của cổng 4 trong **37.668 bài trượt**; còn
   **98,84%** là phần của nó trong **30.931 bài thuộc thể mà chưa đạt** — mẫu số này bỏ
   ra 6.737 bài vốn không thuộc thể vì trượt cổng 1 hoặc 2.)*
2. **Thu hồi 1.934 bản ghi rỗng** — nội dung nằm ở khoá sai, thu hồi bằng script, không
   cần người. **673** trong số đó đạt đủ bảy tầng ngay.
3. **Bóc 298 dòng siêu dữ liệu** khỏi trường thơ — dòng ký tên, dòng ghi chú, dòng ghi
   nơi chốn và ngày tháng. Ví dụ thật ở `Report_stage_of_rule.md` §8.2.3 và §8.3.3.
4. **Xem lại bảng vần** nếu muốn lấy thêm ở cổng 5. Trong 360 bài bị loại, một phần là
   thơ **có** vần thông mà bảng Trần Trọng Kim không công nhận — `hơn ≁ cồn`,
   `vàng ≁ trắng`. Chỗ cần sửa là **bảng vần**, không phải tiêu chí tầng 5. Xem
   `Report_stage_of_rule.md` §8.5.2 và §8.5.3.

**Không** đề xuất nới QĐ-1/QĐ-2 để lấy lại 30.571 bài ở cổng 4. Đó là quyết định của
chủ dự án, và báo cáo này chỉ có nhiệm vụ nêu đúng cái giá — mà cái giá nay đã đo được
đến từng lớp: **6.162 bài chỉ lệch một dòng**, 4.295 bài lệch hai dòng.

---

## 8. Ghi chú về độ tin cậy của bộ kiểm

> **Phạm vi mục này:** nói về bản thân `rule.py`, không phải về corpus. §8.1 ghi lại hai
> sửa chữa ngày 17/09; các thay đổi lớn hơn sau đó (QĐ-5 bảng vần có nguồn, QĐ-7 tầng 5
> chặn thật) được ghi ở `docs/Plan_Rule_Phan_Tang.md` và `docs/Nguon_Bang_Van_Thong.md`.


Trong quá trình phân tích, mọi dòng bị `rule.py` báo 8 tiếng đều được đối chiếu bằng mắt trên mẫu và **đều đúng là 8 tiếng**. Không tìm thấy trường hợp buộc tội oan.

### 8.1. Hai sửa chữa trong ngày và tác động ĐO ĐƯỢC của chúng

Bộ kiểm được rà lại toàn bộ đối chiếu với `docs/Luat_Tho_That_Ngon_Tu_Do.md` cùng ngày, sửa hai chỗ:

- **Dấu câu**: bản trước liệt kê tay và thiếu gạch ngang dài `—`, gạch ngang ngắn `–`. Nay nhận diện theo phân loại Unicode.
- **Chữ số**: thêm cách đọc số thập phân (`4.0` → *bốn phẩy không*) và số có số 0 đứng đầu.

Tác động lên corpus, đo bằng cách chạy **cả hai bản** trên toàn bộ 62.034 bài:

| | Số bài đạt theo tiêu chí 17/09 (H1 + H3) |
|---|---:|
| Bộ đếm **bản đầu** | 59.429 |
| Bộ đếm **hiện tại** | 59.437 |
| **Chênh lệch** | **+8** (0,013%) |

> **Đọc cho đúng mẫu số.** Hai hàng trên dùng **cùng một tiêu chí** — tiêu chí ngày 17/09
> (H3 ≥ 2 dòng và H1 mọi dòng 7 tiếng) — và **chỉ khác nhau ở phép đếm tiếng**. Đó là
> cách duy nhất đo được tác động của riêng hai sửa chữa ấy. Con số 59.437 **không phải**
> `thuoc_the` hay `dat` của bộ luật hôm nay (55.297 và 24.366); nó là một đường cơ sở
> lịch sử, cố ý giữ nguyên tiêu chí cũ.

| Chiều dịch chuyển | Số bài |
|---|---:|
| ĐẠT → TRƯỢT (luật siết lại) | **0** |
| TRƯỢT → ĐẠT (luật nới ra) | **8** |

Tám bài đó:

```
id=4636   "Quãng vắng đêm trường — tâm sự ai,"   bỏ gạch ngang        → 7 tiếng
id=7284   "Ôi thời hiện đại 4.0,"                 "bốn phẩy không"     → 7 tiếng
id=179095 "– “Cô hẳn biết tên tôi đấy nhỉ?"       bỏ gạch ngang + nháy → 7 tiếng
```

Cả tám đều là **sửa cho ĐÚNG §2.1** của tài liệu luật — "dấu câu không tính là tiếng" và "chữ số phải quy về cách đọc". Không luật cứng nào được thêm, bớt hay nới ngoại lệ ở lượt sửa đó: khi ấy `rule.py` mới
có ba luật cứng H1, H2, H3 — H4 được bổ sung sau, ngày 18/09.

> **Nói thẳng chiều tác động:** hai sửa chữa này khiến corpus có **thêm 8 bài đạt**, không phải bớt đi. Trên nguyên tắc chúng có thể siết (một dòng 6 tiếng kèm gạch ngang trước đây bị đếm nhầm thành 7), nhưng trong corpus này **không có ca nào như vậy**, nên chiều siết bằng 0.

### 8.2. Một lỗi đo lường đã mắc và đã sửa

Lần đo tác động đầu tiên cho ra con số sai (10 bài siết / 13 bài nới), vì bản mô phỏng "bộ đếm cũ" của tôi **bỏ sót phần đọc số nguyên vốn đã có** trong bản đầu. Bảng ở §8.1 là bản đo lại trung thực, giữ nguyên phần đọc số ở đường cơ sở và chỉ thay đổi đúng hai thứ đã sửa.

**Cách tự kiểm chứng:** `python datalake/scripts/so_sanh_ban_luat.py`. Script dựng lại bộ
đếm cũ (danh sách dấu câu liệt kê tay, chỉ đọc số nguyên), rồi chạy **cùng một tiêu chí
17/09** với hai bộ đếm và đếm số bài đổi phán quyết theo từng chiều.

Các số liệu trong báo cáo này được tính **sau** hai sửa chữa đó.

#### 8.3. Chính script so sánh đã hỏng âm thầm — phát hiện 18/09

Khi chạy lại toàn bộ ngày 18/09, `so_sanh_ban_luat.py` cho ra **35.065 bài đổi phán
quyết** thay vì 8, và tệp báo cáo phình từ 2 KB lên **1,2 MB**.

Nguyên nhân: script so đường cơ sở 17/09 (tiêu chí H1 + H3) với `kiem_tra_bai_tho().dat`.
Khi viết ngày 17/09, hai vế ấy chỉ khác nhau ở **phép đếm tiếng** nên phép so đúng. Sang
18/09, `.dat` đã thành phán quyết của **cả bảy tầng** — phép so lặng lẽ biến thành *"bộ
luật cũ vs bộ luật mới"*, **đo hai biến cùng lúc**.

Đó đúng là sai lầm mà docstring của chính script cảnh báo:

> *"Đường cơ sở phải giống bản đầu ở MỌI thứ trừ đúng hai chỗ đã sửa, nếu không phép so
> sánh đo nhầm sang thứ khác."*

**Đã sửa:** tách một hàm tiêu chí dùng chung, tham số hoá đúng hàm đếm. Kết quả về lại
**0 siết / 8 nới**, khớp bảng ở §8.1.

**Bài học có giá trị ngoài ca này:** một phép so sánh chỉ đúng khi **mọi biến trừ một**
được giữ cố định. Khi hệ thống đổi, những phép so viết từ trước **không tự báo hỏng** —
chúng vẫn chạy, vẫn ra số, chỉ là số ấy trả lời một câu hỏi khác.

---

## 9. Cách tái lập

```python
import json
from application.rule import kiem_tra_bai_tho

for line in open("datalake/dataraw/final_data_7_chu.jsonl", encoding="utf-8"):
    rec = json.loads(line)
    tho = (rec.get("result") or {}).get("markdown_poem")
    if isinstance(tho, str) and tho.strip():
        v = kiem_tra_bai_tho(tho)
        # v.dat, v.vi_pham, v.so_do_van_theo_kho, v.phoi_khuon_theo_kho, ...
```

Toàn bộ số liệu trong báo cáo đến từ hàm này. Phép kiểm là thuần và tất định: cùng đầu vào luôn cho cùng kết quả.

`v.dat` là **một giá trị bool cho cả bài**, không phải điểm số. Muốn đếm đúng thì đếm
số bài có `v.dat == True`; đừng đếm tỷ lệ dòng đạt rồi lấy trung bình — hai cách cho ra
hai bức tranh khác hẳn nhau.

Hai cờ, đọc cho đúng:

```python
v.thuoc_the   # chỉ H1-H4   -> 55.297 bài
v.dat         # cả bảy tầng -> 24.366 bài
v.tang_dung_lai   # bài trượt dừng ở cổng nào
v.tang            # dấu vết đủ bảy tầng, mỗi tầng có bang_chung
```

Cách chạy lại toàn bộ và sinh lại mọi tệp kết quả:

```
python datalake/scripts/kiem_tra_toan_bo.py
```

Toàn bộ số liệu phán quyết trong bản này được **đo lại từ đầu ngày 18/09/2026** bằng
`rule.py` hiện tại. Chạy hai lần liên tiếp cho kết quả trùng khít — phép kiểm là thuần
và tất định.

---

## 10. Tệp kết quả đã xuất

Thư mục `datalake/analysis/`:

| Tệp | Số bản ghi | Nội dung |
|---|---:|---|
| `TONG_HOP.md` | — | Bản tóm tắt người đọc được, **do máy sinh** — đừng sửa tay |
| `tong_hop.json` | — | Chính số liệu đó, dạng máy đọc |
| `bai_dat.jsonl` | 24.366 | Bài đạt: **nguyên văn thơ** + dấu vết **từng dòng** + bằng chứng **cả bảy cổng** |
| `bai_truot.jsonl` | 37.668 | Bài trượt: **nguyên văn thơ** + dấu vết từng dòng + `tang_dung_lai` + `ly_do_truot` có địa chỉ dòng |
| `vi_du_truot_theo_tang.json` | — | 10 ví dụ thật mỗi cổng, kèm bằng chứng và nội dung dòng hỏng |
| `bai_khong_co_noi_dung.jsonl` | 5.116 | Bản ghi rỗng |
| `bai_truot_chi_tiet.jsonl` | 37.668 | **Mọi** bài trượt: từng dòng hỏng kèm số tiếng và nhóm nguyên nhân |
| `bai_rong_cuu_duoc.jsonl` | 1.934 | Bài thu hồi từ khoá sai: `khoa_nguon`, `dat_luat`, toàn văn |
| `dong_nghi_ngo_trong_bai_dat.jsonl` | 12 | Bài đạt nhưng còn dòng siêu dữ liệu lẫn vào |

Các tệp này dùng trực tiếp làm đầu vào cho hàng đợi sửa tay hoặc bước tiền xử lý.

`tong_hop.json` từ lượt đo này có thêm ba khoá: `pha_khuon_cua_bai_truot_tang4` (phân bố
dòng phá khuôn), `to_hop_khuon_cum_bon_dong` (bảng 16 tổ hợp §6c), `phan_bo_score`. Cả ba
đều được `doi_soat_tai_lieu.py` dùng làm nguồn đối chiếu cho tài liệu.

### 10.1. Toàn bộ thư mục đã sinh lại ngày 18/09

Trước lượt này, ba tệp `.jsonl` và chín báo cáo `reports/*.txt` vẫn mang mốc **17/09** —
tức số liệu của bộ luật cũ. Đã chạy lại **mười script**; mọi tệp nay cùng một bộ luật.

| Tệp | Trước (17/09) | Sau (18/09) |
|---|---:|---:|
| `bai_truot_chi_tiet.jsonl` | 2.597 *(chỉ cổng 2)* | **37.668** *(mọi bài trượt)* |
| `dong_nghi_ngo_trong_bai_dat.jsonl` | 42 | **12** |
| `bai_rong_cuu_duoc.jsonl` — số bài **đạt luật** | 1.244 | **673** |
| `reports/so_sanh_ban_luat.txt` | 2 KB | 2 KB *(sau khi sửa lỗi §8.3)* |

Chín báo cáo văn bản trong `reports/`: `bao_cao.txt` · `bao_cao2.txt` … `bao_cao7.txt` ·
`bao_cao_moi.txt` · `so_sanh_ban_luat.txt` — tất cả đã sinh lại.

Kiểm chứng đầy đủ sau lượt đo:

```
python datalake/scripts/doi_soat_ket_qua.py 500   # phân hoạch id, chạy lại mẫu
python datalake/scripts/doi_soat_tai_lieu.py      # mọi con số trong .md truy được về nguồn
```
