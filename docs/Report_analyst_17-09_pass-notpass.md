# BÁO CÁO PHÂN TÍCH CORPUS — BÀI ĐẠT / BÀI KHÔNG ĐẠT LUẬT

**Tệp phân tích:** `datalake/dataraw/final_data_7_chu.jsonl` — 67.150 bản ghi
**Ngày đo:** 18/09/2026 · **Bộ luật:** `src/application/rule.py`, bảy tầng
**Sinh lại:** `python datalake/scripts/kiem_tra_toan_bo.py`

> Bản 17/09 của báo cáo này đo bằng một bộ luật chỉ chặn ở H1–H3. Toàn bộ số liệu
> phán quyết dưới đây đã **đo lại từ đầu**, từng bài một, qua đủ bảy tầng. Không con
> số nào được mang sang từ bản cũ.

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
| **Thuộc thể** — theo tài liệu luật (chỉ H1–H3) | **59.437** | *"Bài này có phải thất ngôn tự do không?"* — câu trả lời của `Luat_Tho_That_Ngon_Tu_Do.md` §2 |
| **Đạt** — theo chuẩn dự án (cả bảy tầng) | **16.391** | *"Bài này có tuân thủ toàn bộ Rule không?"* — câu trả lời của dự án, sau QĐ-1 → QĐ-7 |

Khoảng cách 43.046 bài giữa hai con số **không phải lỗi**. Nó là hệ quả đo được của
các quyết định đã chốt, chủ yếu là QĐ-1 và QĐ-2 (không cho phá khuôn thanh luật).

Tỉ lệ đạt: **16.391 / 62.034 bài có nội dung = 26,42%**.

### 0.2. Phễu bảy cổng

Bài phải qua cổng N mới sang cổng N+1. Cột *chưa chạy* là số bài **chưa được kiểm** ở
cổng đó vì đã bị chặn trước — chưa kiểm, không phải đạt.

| Cổng | Điều luật | Vào | Qua | Chặn tại đây | Chưa chạy |
|---|---|---:|---:|---:|---:|
| 1. Hình thức | H3 | 62.034 | 62.032 | 2 | 0 |
| 2. Độ dài dòng | H1, H2 | 62.032 | 59.437 | 2.595 | 2 |
| 3. Loại trừ Đường luật | F1–F5 | 59.437 | 55.149 | 4.288 | 2.597 |
| **4. Thanh luật** | S1–S5 | 55.149 | 21.374 | **33.775** | 6.885 |
| 5. Vần | S6–S12 | 21.374 | **16.391** | 4.983 | 40.660 |
| 6. Nhịp | S13–S15 | 16.391 | 16.391 | 0 | 45.643 |
| 7. Khổ và bố cục | S16–S21 | 16.391 | 16.391 | 0 | 45.643 |

**Cổng 4 là nút cổ chai thật sự** — một mình nó loại 33.775 bài, gấp 6,8 lần cổng đứng
thứ hai.

### 0.3. Đối soát

```
67.150 dòng đọc = 67.150 bản ghi parse được = 67.150 id duy nhất       ✅
67.150 bản ghi  = 16.391 đạt + 45.643 trượt + 5.116 không có nội dung  ✅
62.034 lần gọi rule.py = 16.391 đạt + 45.643 trượt                     ✅
```

Không bản ghi nào bị bỏ sót, trùng, hay đếm hai lần.

### 0.4. ⚠️ Ba điều phải biết trước khi dùng con số 16.391

**1. Cổng 6 chặn 0 bài, và đó KHÔNG phải vì thơ đạt nhịp.**
Ngắt nhịp là ngắt theo *ranh giới từ*. Chưa có bộ tách từ tiếng Việt nên mọi dòng 7
tiếng đều "cắt được" theo cả bảy kiểu — phép kiểm rỗng nghĩa. Bằng chứng trực tiếp:
**100,00% bài đạt được gán nhịp chủ đạo `4/3`** — không phải vì thơ Việt toàn nhịp
4/3, mà vì giao của bảy kiểu luôn khác rỗng và `4/3` đứng đầu bảng. **16.391 là con số
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
| 1. Hình thức | H3 | Từ 2 dòng trở lên | Tài liệu §2 |
| 2. Độ dài dòng | H1, H2 | **Mọi** dòng đúng 7 tiếng | Tài liệu §2, §10 |
| 3. Loại trừ Đường luật | F1–F5 | Không khớp khuôn Đường luật | Tài liệu §9 Bước 2 |
| 4. Thanh luật | S1–S5 | **Mọi** dòng khớp khuôn `B T B` hoặc `T B T` | QĐ-1, QĐ-2 |
| 5. Vần | S6–S12 | ≥1 cụm **4 dòng liên tiếp** khớp một sơ đồ §5.2 | QĐ-3, QĐ-5, QĐ-7 |
| 6. Nhịp | S13–S15 | Mọi dòng thuộc bảy kiểu, và có nhịp chủ đạo phủ cả bài | QĐ-4, QĐ-4b, QĐ-6b |
| 7. Khổ và bố cục | S16–S21 | Không có khổ rỗng | Tài liệu §7 |

### 1.2. Ba chỗ dự án chặt hơn tài liệu — nêu minh bạch

| Tài liệu nói | Dự án quyết |
|---|---|
| S2: P2/P4/P6 ***nên*** luân phiên — chữ *nên*, nói ở mức dòng | **QĐ-1**: bắt buộc, áp lên **mọi** dòng |
| S4: ***có thể*** phá khuôn ở bất kỳ dòng nào khi dụng ý đòi hỏi | **QĐ-2**: không cho phá khuôn |
| S13: nhịp ***không cố định*** cho toàn bài | **QĐ-4b**: phải có một nhịp chủ đạo phủ mọi dòng |

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
ương"*. Ép bảng này thành các lớp tương đương sẽ bịa thêm 16 cặp hiệp vần mà nguồn
không cho.

### 1.4. Hai mức số liệu

| Loại | Dùng để | Ví dụ trong báo cáo này |
|---|---|---|
| **Mức bài** | Ra quyết định: nhận, loại, sửa, đổi nhãn | 16.391 đạt · 45.643 trượt |
| Mức dòng | Chỉ chẩn đoán nguyên nhân | 177.405 lần vi phạm S2 |

Một bài có thể phạm cùng một điều ở nhiều dòng, nên **số lần vi phạm luôn lớn hơn số
bài** và hai loại số này không so sánh trực tiếp được.

**Một chỉ số đã bị loại khỏi báo cáo:** lần đo đầu có mục *"dòng hỏng có chữ Latin —
99,19%"*. Đó là rác đo đạc, vì tiếng Việt viết bằng chữ Latin nên `[a-zA-Z]` khớp mọi
dòng. Bản này dùng dấu hiệu `f, j, w, z` để nhận diện tên riêng ngoại ngữ thật.

---

## 2. Cấu trúc bản ghi kết quả

Mỗi bài xuất ra một dòng JSON mang **dấu vết đầy đủ bảy tầng**, để câu trả lời *"vì sao
pass"* và *"vì sao trượt"* đều kiểm lại được từng vế.

### 2.1. Bài đạt — `datalake/analysis/bai_dat.jsonl`

Trường `ly_do_dat` ghép bằng chứng của **cả bảy cổng**:

```
T1 Hình thức: 8 dòng — văn bản có phân dòng
T2 Độ dài dòng: 8/8 dòng đúng 7 tiếng; nhỏ nhất = lớn nhất = 7
T3 Loại trừ Đường luật: 8 dòng, không đủ ba vế số dòng + độc vận + niêm
T4 Thanh luật: 8/8 dòng khớp khuôn; 0 dòng phá khuôn
T5 Vần: dòng 1–4 khớp sơ đồ aaxa (vần ba dòng): mài / nhai / kín / dài
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

---

## 3. BÀI ĐẠT — chân dung 16.391 bài qua đủ bảy tầng

### 3.1. Độ dài

| Số dòng | Số bài | Tỷ lệ | Dáng |
|---:|---:|---:|---|
| 8 | 8.818 | 53,80% | **Bát cú** — một khối tám dòng liền, dáng cổ điển nhất |
| 16 | 2.443 | 14,90% | 4 khổ × 4 dòng |
| 28 | 915 | 5,58% | 7 khổ × 4 dòng |
| 20 | 785 | 4,79% | 5 khổ × 4 dòng |
| 12 | 776 | 4,73% | 3 khổ × 4 dòng |
| 24 | 544 | 3,32% | 6 khổ × 4 dòng |
| 4 | 480 | 2,93% | **Tứ tuyệt** — một khổ trọn vẹn |
| 56 | 286 | 1,74% | Trường thiên |

Hơn **một nửa** bài đạt là bát cú 8 dòng. Phần còn lại gần như đều là bội số của 4 —
dấu hiệu corpus nghiêng mạnh về cấu trúc khổ tứ tuyệt.

### 3.2. Cấu trúc khổ

| Số khổ | Số bài | Tỷ lệ |
|---:|---:|---:|
| 1 | 8.677 | 52,94% |
| 4 | 1.812 | 11,05% |
| 2 | 1.617 | 9,87% |
| 7 | 936 | 5,71% |
| 3 | 840 | 5,12% |
| 5 | 827 | 5,05% |

### 3.3. Sơ đồ vần — cụm bốn dòng nào đã khớp

Đếm theo **cụm**, không theo bài: một bài dài có nhiều cụm bốn dòng liên tiếp cùng
khớp. Tổng **38.514 cụm khớp** trên 16.391 bài, trung bình 2,35 cụm mỗi bài.

| Sơ đồ | Số cụm | Tỷ lệ | Tên tài liệu gọi |
|---|---:|---:|---|
| `aaxa` | 30.625 | **79,52%** | **Vần ba dòng, kế thừa Đường luật** — D1, D2, D4 cùng vần, D3 buông ra rồi quay về |
| `abab` | 4.171 | 10,83% | **Vần cách** — hai lớp vần đan nhau, đặc trưng thơ mới |
| `aabb` | 2.512 | 6,52% | **Vần liền** — từng cặp một, gần với đồng dao |
| `abba` | 1.206 | 3,13% | **Vần ôm** — dòng đầu và dòng cuối ôm lấy cặp giữa |

Bốn phần năm số cụm là `aaxa`. Corpus này, ở phần đạt luật, mang **quán tính Đường
luật rất mạnh** — dù cổng 3 đã loại 4.288 bài Đường luật thật sự ra rồi.

### 3.4. Đặc điểm mềm — ghi nhận, không dùng để loại

| Đặc điểm | Số bài | Tỷ lệ | Ghi chú |
|---|---:|---:|---|
| Có vần lưng ở P4/P5 | 10.230 | 62,41% | S7 là **quyền** — làm dòng thơ dính chặt hơn |
| Có cặp vần lệch lớp thanh | 5.560 | 33,92% | S9 **cho phép** — ví dụ `xanh` (B) hiệp `mảnh` (T) |

### 3.5. Nhịp — số liệu này KHÔNG dùng được

| Nhịp chủ đạo | Số bài | Tỷ lệ |
|---|---:|---:|
| `4/3` | 16.391 | **100,00%** |

**Đừng đọc bảng này là "toàn bộ thơ đạt đều nhịp 4/3".** Nó là hiện vật đo đạc: không
có bộ tách từ thì mọi dòng 7 tiếng đều cắt được theo cả bảy kiểu, giao luôn khác rỗng,
và `4/3` là phần tử đầu bảng. Con số 100,00% chính là **bằng chứng tầng 6 đang rỗng
nghĩa**, không phải một phát hiện về thơ.

---

## 4. BÀI TRƯỢT — 45.643 bài, dừng ở cổng nào

### 4.1. Phân bố theo cổng dừng

| Cổng dừng | Số bài | Tỷ lệ | Ví dụ |
|---|---:|---:|---|
| 1. Hình thức | 2 | 0,00% | id=351237 — chỉ 1 dòng, không có phân dòng |
| 2. Độ dài dòng | 2.595 | 5,69% | id=13 *"QUA TÌM BẬU BẬU NƠI ĐÂU"* |
| 3. Loại trừ Đường luật | 4.288 | 9,39% | id=1 *"BÂNG KHUÂNG"* |
| **4. Thanh luật** | **33.775** | **74,00%** | id=2 *"ANH GỬI CHO EM"* |
| 5. Vần | 4.983 | 10,92% | id=28 *"TĨNH VẬT"* |
| 6. Nhịp | 0 | 0,00% | — |
| 7. Khổ và bố cục | 0 | 0,00% | — |

### 4.2. Số lần vi phạm theo điều luật

| Mã | Số lần | Điều luật |
|---|---:|---|
| S2 | 177.405 | P2/P4/P6 nên luân phiên bằng – trắc |
| H1 | 9.015 | Mỗi dòng phải có đúng 7 tiếng |
| S11 | 4.983 | Sơ đồ vần nên nhất quán trong phạm vi một khổ |
| F3 | 4.288 | Không yêu cầu độc vận cho toàn bài |
| H3 | 2 | Văn bản phải được phân dòng |

Nhắc lại: đây là **số lần vi phạm**, không phải số bài. 177.405 lần phạm S2 rải trên
33.775 bài — trung bình 5,25 dòng phá khuôn mỗi bài.

### 4.3. Cổng 2 — dòng sai số tiếng

**2.595 bài, 9.015 dòng hỏng.** Ví dụ có bằng chứng:

```
id=13 "QUA TÌM BẬU BẬU NƠI ĐÂU": 1/20 dòng sai
    D17: Đường về ngơ ngác hỏi bậu vì đâu?     cần 7 tiếng | đang 8

id=17 "THÀNH CỔ": 1/5 dòng sai
    D5: — Lê Bá Dương                          cần 7 tiếng | đang 3
```

Ca `id=17` là **siêu dữ liệu lẫn vào thơ**: dòng ký tên tác giả bị gộp vào trường nội
dung. Đây là lỗi dữ liệu, không phải lỗi bài thơ — xem §5 và §7.

### 4.4. Cổng 3 — nghi là Đường luật

**4.288 bài.** Bài đủ 4 hoặc 8 dòng, độc vận, có niêm.

```
id=1 "BÂNG KHUÂNG": 8 dòng, độc vận và có niêm — khớp khuôn Đường luật
```

Nhắc lại giới hạn ở §0.4: tài liệu đòi **bốn** vế, máy chỉ kiểm được **ba**. Vế thứ tư
là phép đối, đòi so từ loại và ngữ nghĩa. Vì vậy 4.288 là con số **nghi ngờ**, và cách
xử lý an toàn là rà tay trước khi loại hẳn.

### 4.5. Cổng 4 — phá khuôn thanh luật (nút cổ chai)

**33.775 bài — 74% toàn bộ bài trượt.**

```
id=2 "ANH GỬI CHO EM": 13/32 dòng phá khuôn: D1, D3, D4, D5, D8, D17, D20, D21…
    D1: Anh gửi cho em gửi bông vàng,
    cần P2/P4/P6 luân phiên theo khuôn bằng (B T B) | đang P2/P4/P6 = T B B
```

**Đây là chỗ cần đọc kỹ nhất của cả báo cáo.** Tài liệu luật dùng chữ ***nên*** ở S2 và
cho phép phá khuôn ở S4. Nếu đọc theo đúng câu chữ tài liệu, phần lớn trong 33.775 bài
này **không sai gì cả**. Chúng trượt vì **QĐ-1 và QĐ-2** — hai quyết định của dự án,
chặt hơn tài liệu.

Con số này là cái giá đo được của yêu cầu *"tuân thủ toàn bộ Rule"*. Báo cáo nêu thẳng
để chủ dự án cân nhắc, **không** đề xuất nới luật.

### 4.6. Cổng 5 — không cụm bốn dòng nào khớp §5.2

**4.983 bài.** Sơ đồ **thực tế** của cụm bốn dòng đầu:

| Sơ đồ thật | Số bài | Tỷ lệ | Vì sao không khớp |
|---|---:|---:|---|
| `xaxa` | 1.579 | 31,69% | Chỉ D2 và D4 hiệp; D1, D3 buông. Gần `abab` nhưng thiếu lớp vần thứ hai |
| `aaxx` | 1.002 | 20,11% | Mở bằng một cặp vần rồi thả trôi nửa sau |
| `axxa` | 711 | 14,27% | Vần ôm **hở** — D1 và D4 ôm nhau nhưng giữa để trống |
| `xxxx` | 657 | 13,18% | Không dòng nào hiệp dòng nào |
| `aaaa` | 403 | 8,09% | **Độc vận cả khổ** — bốn dòng cùng một vần |
| `axax` | 236 | 4,74% | Chỉ D1 và D3 hiệp |
| *(bài dưới 4 dòng)* | 122 | 2,45% | Không đủ một cụm bốn dòng để xét |

Hai nhóm đáng chú ý:

- **`xaxa` (31,69%)** là dạng hỏng phổ biến nhất, và nó **rất gần** `abab`. Chỉ cần sửa
  tiếng cuối của một trong hai dòng lẻ là bài khớp vần cách.
- **`aaaa` (8,09%)** là độc vận — một lựa chọn cổ điển hợp lệ trong nhiều thể thơ,
  nhưng **không nằm trong bốn sơ đồ §5.2**. Nếu chủ dự án muốn nhận độc vận, đó là một
  quyết định bổ sung cho §5.2, không phải sửa mã.
- **122 bài dưới 4 dòng** trượt vì QĐ-7 đòi một cụm bốn dòng, trong khi H3 chỉ đòi từ
  hai dòng. Những bài này `thuoc_the = True` nhưng `dat = False`.

---

## 5. Vấn đề chất lượng dữ liệu ngoài luật thơ

> **Phạm vi mục này:** các con số dưới đây nói về **chất lượng bản ghi**, không phải về
> phán quyết luật thơ. Chúng không đổi khi bộ luật đổi, nên được giữ nguyên từ lượt đo
> 17/09. Các số ở dạng "x/67.150" vẫn đúng vì mẫu số là toàn corpus.


| Vấn đề | Số lượng | Tỷ lệ | Hậu quả thực tế |
|---|---:|---:|---|
| `markdown_poem` rỗng nhưng vẫn có `score` | 5.116 | 7,6% | Đường ống đã **chấm điểm cho nội dung không tồn tại** |
| Bài trùng nội dung hoàn toàn | 15.916 bản dư (15.029 nhóm) | — | Huấn luyện trên tập này sẽ **đè trọng số** lên vài nghìn bài lặp |
| `original_title` rỗng | 42.883 | 63,9% | Không truy ngược được nguồn, không khử trùng theo tên được |
| `source_file` thiếu | 65.978 | 98,3% | Không biết bài đến từ đợt thu thập nào |
| Khoá lạ trong `result` | **31 khoá khác nhau** | — | Nội dung thật **nằm rải rác ở khoá sai** — xem §5.1.1 |

### 5.1. Trôi lược đồ — 31 khoá lạ

`content_fix` · `content_note` · `content_analysis` · `content_fixed` · `title_fixed` ·
`markdown_poem_content` · `content` · `title_inferred` · `markdown_poem_fixed` ·
`content_correction` · `content_fix_notes` · `content_processed` · `title_correction` ·
`content_notes` · `content_correction_notes` · `title_fix` · `markdown_content` ·
`title_suggestion` · `title` · `poem_type_detail` · `markdown_poem_final` ·
`markdown_poem_full` · `evaluation_details` · `error_fixes` · `correction_notes` ·
`content_details` · `poem_content` · `markdown_type` · `content_fix_note`

Đây là dấu vết một đường ống chắp vá: mỗi lần vá lỗi lại sinh một tên khoá mới.

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
| `content_processed` · `content_correction` · `markdown_content` · `poem_content` · `markdown_poem_final` · `markdown_poem_full` | 13 |

**Chất lượng phần cứu được:** 1.244 / 1.934 bài (64,3%) **đạt luật ngay** khi đưa qua `rule.py`.

Ví dụ `id=2875`, nội dung nằm ở `content_fix`, đạt luật:

```
Xuân còn nấn ná ở xung quanh,
Chợt rét nàng Bân đuổi nắng hanh.
Bất chấp mai đào đang gạ nở,
Heo may õng ẹo lả lơi cành.
```

Toàn bộ đã xuất ra `datalake/analysis/bai_rong_cuu_duoc.jsonl`.

> **Kết luận:** 1.244 bài thơ hợp lệ đang bị bỏ phí chỉ vì đường ống ghi vào sai tên khoá. Đây là số bài thu hồi được **không tốn một đồng gọi mô hình nào**.

3.182 bài còn lại rỗng thật — nhưng vẫn có `score` và `score_reason`, nghĩa là **đường ống đã chấm điểm cho nội dung không tồn tại**. Đó là một lỗi cần truy ngược lên phía sinh dữ liệu.

### 5.2. `score` không dự báo được việc đạt luật

| score | Số bài | Tỷ lệ đạt | Quan sát |
|---:|---:|---:|---|
| 4 | 3.168 | 92,61% | |
| 5 | 9.167 | 95,12% | |
| 6,5 | 24.394 | 96,30% | **Cụm dồn lớn nhất** — 39% toàn corpus rơi vào đúng một giá trị |
| **7** | 2.182 | **98,53%** | Đỉnh tuân thủ, nhưng cỡ mẫu nhỏ |
| 7,5 | 17.407 | 96,69% | Cụm dồn lớn thứ hai |
| 8 | 929 | 94,19% | Bắt đầu tụt |
| **8,5** | 1.191 | **83,88%** | **Điểm cao nhất lại tuân thủ kém nhất** — thấp hơn cả điểm 4 |

**Đọc bảng này thế nào:** nếu `score` đo được chất lượng thơ 7 chữ, cột bên phải phải tăng dần từ trên xuống. Nó không tăng. Điểm 8,5 đạt luật kém hơn điểm 4 tới 9 điểm phần trăm — nhiều khả năng vì bộ chấm khen những bài **thơ 8 chữ** hay, vốn không thuộc thể này.

Điểm cao **không** đồng nghĩa đúng luật — score 8,5 còn đạt thấp hơn score 5. Phân bố điểm dồn cục bất thường ở 6,5 và 7,5 (chiếm 67% corpus), dấu hiệu chấm bằng máy.

> **Không dùng `score` làm tiêu chí lọc dữ liệu đúng luật.**

---

## 6. Điểm mù của H1 — đã đo, và khuyến nghị

> **Phạm vi mục này:** đo trên toàn corpus ở mức DÒNG, độc lập với bảy tầng. Giữ nguyên
> từ lượt đo 17/09.


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

Mở rộng phép đo sang mọi dấu hiệu cấu trúc phi thơ trên 59.437 bài **thuộc thể** (qua H1–H3):

| Dấu hiệu | Số bài đạt dính | Độ tin cậy của dấu hiệu |
|---|---:|---|
| Dòng bọc kín trong ngoặc hoặc dấu sao | 30 | **Cao** — không thấy ca báo nhầm nào |
| Khổ đầu chỉ có một dòng | 27 | **Thấp** — nhiều ca là câu thơ thật, xem cảnh báo ở §6.4 |
| Dòng ký tên tác giả | 0 | Không xuất hiện trong bài đạt |
| Dòng đánh số La Mã | 0 | Không xuất hiện trong bài đạt |
| **Tổng bài đạt có ít nhất một dấu hiệu** | **42 — 0,07%** | Tương đương **7 bài trên mỗi 10.000** |

Ví dụ thật sự là nhiễu:

```
id=3370 D1 (7 tiếng): (Trích thơ dài "Sử một trung đoàn")
id=3509 D1 (7 tiếng): *Tưởng niệm đồng chí Hoàng Văn Thụ*
id=17861 D1 (7 tiếng): *Tác giả: Hàn Phong - Nguyễn Hưng Thịnh*
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
| L1 | Bóc dòng **bọc kín** trong `( )`, `[ ]` hoặc `*...*` | 30 ca, không có ca báo nhầm nào |
| L2 | Bóc dòng **chỉ gồm chữ số** hoặc số La Mã | 17 ca |
| L3 | Bóc dòng **đầu/cuối bài** mà không đủ 7 tiếng | bắt trọn nhóm F (242 bài) |
| L4 | Bóc dòng có **trên 15 tiếng** | bắt trọn nhóm B (22 bài) |

Bốn quy tắc này đều dựa vào **hình thức và vị trí**, không đụng tới từ vựng, nên không cắt nhầm thơ.

**Ba quy tắc KHÔNG nên dùng**, vì đã đo và thấy báo nhầm:

- ❌ Dòng bắt đầu bằng *gửi · tặng · nhớ · tiễn* → 2.828 ca, phần lớn là thơ thật
- ❌ Dòng kết thúc bằng dấu hai chấm → 427 ca, nhiều dòng thơ dẫn lời nói
- ❌ Khổ đầu chỉ một dòng → `"Bâng khuâng trời rộng nhớ sông dài."` là câu thơ Huy Cận

**Về ngưỡng chấp nhận:** với tần suất 0,07%, điểm mù này **không đáng chặn cả đường ống**. Khuyến nghị đưa 42 bài vào danh sách rà tay một lần, rồi chuyển L1–L4 thành bước tiền xử lý thường trực cho các đợt nạp dữ liệu sau.

---

## 7. Dữ liệu dùng được và đề xuất hành động

Bảng này trả lời câu hỏi thực dụng: **lấy được bao nhiêu bài để huấn luyện.**

| Tập | Số bài | Trạng thái |
|---|---:|---|
| **Đạt cả bảy tầng** | **16.391** | dùng được, nhưng còn trùng lặp — xem §5 |
| Thuộc thể nhưng chưa đạt chuẩn dự án | 43.046 | rà theo cổng dừng, phần lớn ở cổng 4 |
| Cứu bằng bóc dòng siêu dữ liệu (nhóm B, C, F) | 298 | tự động hoá được |
| Cứu bằng sửa tay (nhóm D, E) | 1.398 | cần người |
| Bản ghi rỗng nhưng thu hồi được nội dung | 1.934 | chạy `datalake/scripts/ba_viec.py` |
| Tách sang bộ 8 chữ | 135 | đổi nhãn, không phải sửa |

### 7.1. Ba việc đáng làm, xếp theo tỉ lệ đổi lại

1. **`xaxa` → `abab` ở cổng 5** — 1.579 bài, mỗi bài chỉ cần sửa **một tiếng cuối**.
   Đây là tỉ lệ đổi lại tốt nhất trong cả corpus.
2. **Thu hồi 1.934 bản ghi rỗng** — nội dung nằm ở khoá sai, thu hồi bằng script, không
   cần người.
3. **Bóc 298 dòng siêu dữ liệu** khỏi trường thơ — dòng ký tên, dòng ghi chú.

**Không** đề xuất nới QĐ-1/QĐ-2 để lấy lại 33.775 bài ở cổng 4. Đó là quyết định của
chủ dự án, và báo cáo này chỉ có nhiệm vụ nêu đúng cái giá.

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

| | Số bài đạt |
|---|---:|
| `rule.py` bản đầu | 59.429 |
| `rule.py` hiện tại | 59.437 |
| **Chênh lệch** | **+8** (0,013%) |

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

Cả tám đều là **sửa cho ĐÚNG §2.1** của tài liệu luật — "dấu câu không tính là tiếng" và "chữ số phải quy về cách đọc". Không luật cứng nào được thêm, bớt hay nới ngoại lệ: `rule.py` vẫn đúng ba luật H1–H3.

> **Nói thẳng chiều tác động:** hai sửa chữa này khiến corpus có **thêm 8 bài đạt**, không phải bớt đi. Trên nguyên tắc chúng có thể siết (một dòng 6 tiếng kèm gạch ngang trước đây bị đếm nhầm thành 7), nhưng trong corpus này **không có ca nào như vậy**, nên chiều siết bằng 0.

### 8.2. Một lỗi đo lường đã mắc và đã sửa

Lần đo tác động đầu tiên cho ra con số sai (10 bài siết / 13 bài nới), vì bản mô phỏng "bộ đếm cũ" của tôi **bỏ sót phần đọc số nguyên vốn đã có** trong bản đầu. Bảng ở §8.1 là bản đo lại trung thực, giữ nguyên phần đọc số ở đường cơ sở và chỉ thay đổi đúng hai thứ đã sửa.

**Cách tự kiểm chứng:** dựng lại bộ đếm cũ bằng danh sách dấu câu liệt kê tay cộng `doc_so()` cho token toàn chữ số, chạy song song với `kiem_tra_bai_tho()` hiện tại trên cùng tệp, rồi đếm số bài đổi phán quyết theo từng chiều.

Các số liệu trong báo cáo này được tính **sau** hai sửa chữa đó.

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
v.thuoc_the   # chỉ H1-H3   -> 59.437 bài
v.dat         # cả bảy tầng -> 16.391 bài
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
| `bai_dat.jsonl` | 16.391 | Bài đạt, `ly_do_dat` ghép bằng chứng **cả bảy cổng** |
| `bai_truot.jsonl` | 45.643 | Bài trượt, kèm `tang_dung_lai` và `ly_do_truot` có địa chỉ dòng |
| `bai_khong_co_noi_dung.jsonl` | 5.116 | Bản ghi rỗng |
| `bai_truot_chi_tiet.jsonl` | 2.597 | Bài trượt ở cổng 2: từng dòng hỏng kèm số tiếng |
| `bai_rong_cuu_duoc.jsonl` | 1.934 | Bài thu hồi từ khoá sai: `khoa_nguon`, `dat_luat`, toàn văn |
| `vi_du_truot_theo_tang.json` | — | Ví dụ thật kèm bằng chứng cho từng cổng |
| `dong_nghi_ngo_trong_bai_dat.jsonl` | 42 | Bài đạt nhưng còn dòng siêu dữ liệu lẫn vào |

Cả ba tệp dùng trực tiếp làm đầu vào cho hàng đợi sửa tay hoặc bước tiền xử lý.
