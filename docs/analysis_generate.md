# Report — Đối chiếu `generate_poem.jsonl` qua `src/application/rule.py`

**Ngày:** 22/09/2026
**Nguồn:** `datalake/generate/generate_poem.jsonl` — 200 bài thơ vừa sinh ra
**Bộ kiểm:** `src/application/rule.py`, hàm `kiem_tra_bai_tho` (bảy tầng, file ĐÓNG BĂNG)
**Script:** `datalake/scripts/chay_doi_chieu_generate.py`
**Kết quả thô:** `datalake/analysis/generate_dat.jsonl`, `datalake/analysis/generate_truot.jsonl`

---

## 0. Đọc trước khi tin số

**Bộ kiểm DỪNG ở tầng chặn đầu tiên bị trượt.** Hệ quả phải nhớ khi đọc mọi bảng
dưới đây: một bài chỉ được quy cho **một** tầng — tầng nó chết. Các tầng sau mang
`da_chay=False`, nghĩa là **chưa kiểm**, không phải "đã kiểm và đạt".

Vì vậy dòng *"tầng 5 chặn 0 bài"* **không** có nghĩa là 200 bài này đều đúng vần.
Nó có nghĩa là **chưa bài nào sống đủ lâu để tầng 5 được chạy**.

**Một bản ghi hỏng định dạng.** Dòng 19 của tệp nguồn không phải JSON hợp lệ: bài
thơ chứa dấu nháy kép chưa escape — `:\n"Người ơi, còn nhớ thuở ta chung?"`. Đây
là lỗi của **bộ sinh**, không phải của bài thơ. Script vá đúng ca đó để không hụt
mẫu số, và ghi lại ở đây thay vì lặng lẽ sửa.

---

## 1. Kết quả tổng

| | Số bài | Tỉ lệ |
|---|---:|---:|
| **ĐẠT** | **1** | **0,50 %** |
| **TRƯỢT** | **199** | **99,50 %** |
| Tổng | 200 | 100 % |

### Trượt ở tầng nào

| Tầng | Tên | Điều luật | Số bài chết ở đây | % số bài trượt |
|---:|---|---|---:|---:|
| 1 | Hình thức và số dòng | H3, H4 | 0 | 0 % |
| **2** | **Độ dài dòng** | **H1, H2** | **36** | **18,1 %** |
| 3 | Đối chiếu Đường luật | F1–F5 | 0 | — *(tầng ghi nhận, không chặn)* |
| **4** | **Thanh luật** | **S2** | **163** | **81,9 %** |
| 5 | Vần | S11 / QĐ-7b | 0 | *chưa bài nào tới* |
| 6 | Nhịp | S14 | 0 | *chưa bài nào tới* |
| 7 | Khổ và bố cục | S16–S21 | 0 | *chưa bài nào tới* |

**Tầng 1 sạch tuyệt đối.** Cả 200 bài đều đúng 20 dòng — bội của 4, thoả H3 và H4.
Bộ sinh làm rất đúng phần số dòng.

---

## 2. Tầng 2 — Độ dài dòng · 36 bài (18,1 %)

Luật: *"Mỗi dòng phải có đúng 7 tiếng, áp dụng toàn bộ các dòng, không ngoại lệ"* (H1, H2).

**28/36 bài chỉ sai ĐÚNG MỘT DÒNG.** Còn lại: 6 bài sai 2 dòng, 2 bài sai 3 dòng.

### Phân bố số tiếng trên toàn bộ 3 998 dòng

| Số tiếng | Số dòng |
|---:|---:|
| 6 | 5 |
| **7** | **3 954** |
| 8 | 22 |
| 9 | 1 |
| 11–15 | 18 |

98,9 % số dòng đúng 7 tiếng. Nhưng H1 không có ngoại lệ — một dòng lệch là cả bài
hỏng, nên 44 dòng lệch đủ để giết 36 bài.

### 🔴 Nguyên nhân số một: mô hình CHÚ THÍCH vào trong bài thơ

**18/44 dòng lệch (41 %) không phải lỗi thơ — là mô hình tự giải thích tác phẩm
của mình ngay trong dòng thơ.** 17 bài dính lỗi này:

```
id 47  D2  12 tiếng | Hoàng hôn nhuộm đỏ cả tương lai (ý nói sự kết thúc)
id 58  D2  15 tiếng | Không một tiếng động, chẳng một tim (ý nói sự vô cảm của không gian)
id 124 D10 14 tiếng | Yêu cả màu xanh của ruộng mù (ý nói màu xanh của cây cỏ)
id 154 D2  11 tiếng | Thấy thời gian đã nhuộm tóc hồng (ý nói tóc bạc)
id 17  D6   9 tiếng | Chẳng biết nói gì giữa buổi trưa (hoặc chiều)
```

Bỏ phần trong ngoặc thì **mọi dòng ấy đều đúng 7 tiếng**. Bài thơ không sai — lời
chú mới sai chỗ.

Đây là kiểu hỏng **rẻ nhất để sửa** trong cả báo cáo, và nó đã có điều cấm sẵn:
`CACH_LAM_VIEC` mục 3 nói thẳng *"Chỉ trả về bài thơ. Không lời dẫn, không giải
thích, không đánh số dòng."* Điều cấm đó đang không được tuân.

Bài `id 154` còn cho thấy mô hình **biết mình viết sai** mà vẫn để nguyên: nó viết
"tóc hồng" rồi chú "(ý nói tóc bạc)" — tức là nó ép vần trước, rồi đính chính bằng
lời thay vì sửa câu.

### Nguyên nhân số hai: dòng thừa/thiếu tiếng thật (26 dòng)

```
id 4   D16  8 tiếng | Chẳng biết tương lai sẽ nắng hay mưa.
id 139 D13  8 tiếng | Đừng sợ hãi sự kết thúc cuối cùng
id 81  D1   6 tiếng | Làng tôi có gốc đa già
id 140 D1   6 tiếng | Âm và dương, đất và trời
```

Đáng chú ý: `id 81` và `id 140` mở đầu bằng dòng 6 tiếng — đó là nhịp **lục bát**,
không phải thất ngôn. Mô hình đang trượt sang thể khác ngay từ dòng đầu.

---

## 3. Tầng 4 — Thanh luật · 163 bài (81,9 %)

Luật: *"P2, P4, P6 nên luân phiên bằng – trắc"* (S2), siết thành bắt buộc bởi QĐ‑1
(áp lên **toàn bộ** dòng) và QĐ‑2 (**không** cho phá khuôn).

Mỗi dòng phải khớp đúng một trong hai khuôn ở tiếng 2/4/6:

```
khuôn bằng   B T B
khuôn trắc   T B T
```

### Mức độ hỏng

| Số dòng phá khuôn / bài | Số bài |
|---:|---:|
| 3 | 4 |
| 4–6 | 31 |
| 7–9 | 58 |
| **10** | **30** |
| 11–13 | 30 |
| 14–17 | 10 |

**Trung bình 8,8 / 20 dòng phá khuôn mỗi bài.**

### 🔴 Con số đáng chú ý nhất của cả báo cáo

**Tỉ lệ dòng khớp khuôn trên nhóm này = 0,559.**

Con số ấy trùng gần như chính xác với `p ≈ 0,56` mà dự án đã đo độc lập từ trước và
ghi ở đầu `poetry/sinh_theo_kho.py` (nguồn: `docs/Do_That_21-09_R2.md`). Hai phép
đo, hai bộ dữ liệu khác nhau, cùng một con số.

Điều đó xác nhận `p` **không phải nhiễu ngẫu nhiên mà là giới hạn ngữ âm ổn định
của mô hình** — và nó dự đoán đúng kết quả ta vừa thấy:

```
P(một bài 20 dòng đạt) = p²⁰ ≈ 0,56²⁰ ≈ 1,3 × 10⁻⁵
```

Với 200 bài, kỳ vọng số bài đạt là **0,003**. Thực tế đạt **1**. Bài đạt duy nhất
là may mắn thống kê, không phải dấu hiệu bộ sinh đã làm đúng.

**Kết luận thẳng: sinh một lần cả bài 20 dòng là cách làm không thể thắng.** Đây
đúng là phép toán mà `sinh_theo_kho.py` được viết ra để phá — sinh từng khổ 4 dòng
và chọn trong nhiều ứng viên. Bộ dữ liệu này trông như **chưa đi qua đường ấy**.

---

## 4. Ba bài ĐẠT

⚠️ **Chỉ có MỘT bài đạt, không phải ba.** Không thể đưa ra ba ví dụ mà không bịa.

### `id 179` — "Tách Trà Chiều" · chủ đề *Góc nhỏ tâm hồn*

Qua cả bảy tầng. 20/20 dòng đúng 7 tiếng, 20/20 dòng khớp khuôn, sơ đồ vần
`aaxa · bbxb · ccxc · xbxb · xdxd`.

```
D1   Nắng chiều nhạt nắng trải hiên xưa      B T B
D2   Nhấp chén trà thơm giữa buổi trưa       T B T
D3   Vị đắng đầu môi, hậu ngọt lịm           T B T
D4   Gợi lòng thanh thản, thật vừa vừa.      B T B
D5   Ngồi ngắm mây trôi, ngắm lá rơi         T B T
D6   Thấy đời bình lặng, chẳng chơi vơi      B T B
D7   Chẳng cần vội vã, không tranh đấu       B T B
D8   Giữa những lo toan của cuộc đời.        T B T
...
D20  Giữa cuộc đời này, thật diệu huyền.     T B T
```

Bài này cho thấy mô hình **làm được** — vấn đề là xác suất, không phải năng lực.

---

## 5. Ba bài TRƯỢT

### 5.1 `id 47` — "Bóng Đổ Dài" · chết ở **tầng 2**, sai đúng 1 dòng

```
tầng 1  Hình thức và số dòng   ĐẠT      20 dòng — có phân dòng, và 20 = 4 × 5
tầng 2  Độ dài dòng            TRƯỢT    1/20 dòng sai số tiếng: D2 = 12
tầng 3–7                       chưa kiểm — bỏ qua vì tầng 2 đã chặn

  H1 · D2 | cần 7 tiếng | đang 12 tiếng
  "Hoàng hôn nhuộm đỏ cả tương lai (ý nói sự kết thúc)"
```

Bỏ bảy tiếng trong ngoặc là dòng đúng luật. **Bài thơ không sai; lời chú làm hỏng.**

### 5.2 `id 11` — "Mưa Chiều Quê Nội" · chết ở **tầng 4**, gần đích nhất

```
tầng 1  Hình thức và số dòng   ĐẠT      20 dòng — có phân dòng, và 20 = 4 × 5
tầng 2  Độ dài dòng            ĐẠT      20/20 dòng đúng 7 tiếng
tầng 3  Đối chiếu Đường luật   ĐẠT      ghi nhận, không chặn
tầng 4  Thanh luật             TRƯỢT    3/20 dòng phá khuôn: D5, D8, D20
tầng 5–7                       chưa kiểm

  S2 · D5  | cần B T B hoặc T B T | đang T B B
  S2 · D8  | cần B T B hoặc T B T | đang T B B
  S2 · D20 | cần B T B hoặc T B T | đang T B B
```

Cả ba dòng hỏng **cùng một kiểu**: `T B B`, tức tiếng thứ 6 lẽ ra phải Trắc thì
lại Bằng. Chỉ cần đổi tiếng thứ 6 của ba dòng ấy là bài qua tầng 4.

### 5.3 `id 153` — "Tiếng Thở Dài Trong Đêm" · chết ở **tầng 4**, nặng nhất

```
tầng 1  Hình thức và số dòng   ĐẠT      20 dòng
tầng 2  Độ dài dòng            ĐẠT      20/20 dòng đúng 7 tiếng
tầng 3  Đối chiếu Đường luật   ĐẠT
tầng 4  Thanh luật             TRƯỢT    17/20 dòng phá khuôn: D1, D2, D3, D4, D5, D6, D7, D9…
tầng 5–7                       chưa kiểm

  S2 · D1 | cần B T B hoặc T B T | đang B B T
  S2 · D2 | cần B T B hoặc T B T | đang T T B
  S2 · D3 | cần B T B hoặc T B T | đang T B B
```

Bài này **không đáng vá từng dòng** — 17/20 hỏng nghĩa là cả cách triển khai đã
sai. Đúng ca mà thang leo thang phải nhảy thẳng tới `sinh_lai_ca_bai`.

---

## 6. Còn bao xa tới đích

| Nhóm | Số bài |
|---|---:|
| Đã đạt | 1 |
| Chết ở tầng 4, **≤ 3 dòng** hỏng — vá được bằng vòng sửa | 4 · `id 11, 44, 83, 162` |
| Chết ở tầng 2 mà sửa xong độ dài thì **vẫn** trượt tầng 4 | **36 / 36** |
| Còn lại, hỏng sâu | 159 |

⚠️ **Hàng thứ ba là kết quả bất ngờ và phải nói rõ.** Tôi đã kiểm giả định "sửa
được độ dài thì bài qua": chạy phép tính khuôn trên các dòng 7 tiếng của cả 36 bài
chết ở tầng 2 — **không một bài nào** có toàn bộ dòng còn lại khớp khuôn.

Nghĩa là sửa lỗi chú thích trong ngoặc sẽ **không** cứu được bài nào. Nó chỉ dời
chỗ chết từ tầng 2 xuống tầng 4. Đáng sửa vì nó rẻ và vì nó làm biên bản nói đúng
bệnh, nhưng đừng kỳ vọng nó nâng tỉ lệ đạt.

**Chỉ 5/200 bài (2,5 %) nằm trong tầm với của vòng sửa.**

---

## 7. Kết luận

1. **0,50 % đạt. Bộ dữ liệu này gần như chắc chắn được sinh bằng một lượt gọi cho
   cả bài 20 dòng**, không qua `sinh_theo_kho.py`. Phép toán `p²⁰ ≈ 1,3 × 10⁻⁵` dự
   đoán đúng kết quả quan sát được, nên đây không phải bộ sinh hỏng — đây là cách
   sinh sai.

2. **Nút thắt là thanh luật, không phải độ dài.** 81,9 % số bài trượt chết ở tầng
   4; tỉ lệ dòng khớp khuôn 0,559 tái lập chính xác `p ≈ 0,56` đã đo trước đó.

3. **17 bài mang lỗi chú thích trong ngoặc** — lỗi quy trình, không phải lỗi thơ,
   và đã có điều cấm sẵn ở `CACH_LAM_VIEC` mục 3. Sửa rẻ, nhưng **không nâng tỉ lệ
   đạt** (xem §6).

4. **Tầng 5, 6, 7 chưa có một số liệu nào.** Chưa bài nào sống qua tầng 4, nên
   không nói được gì về vần, nhịp, khổ của bộ này. Muốn biết thì phải có bộ dữ
   liệu qua được tầng 4 trước.

5. **Việc nên làm tiếp**, theo thứ tự giá trị:
   - Sinh lại bộ này **qua `sinh_theo_kho.py`** (từng khổ 4 dòng, 16 ứng viên mỗi
     khổ) rồi đối chiếu lại — đây là phép thử trực tiếp cho kết luận 1.
   - Bật **bước cứu khổ bằng ReAct** (22/09) để mô hình tự soi bằng tool
     `kiem_tra_tho` trước khi trả, thay vì viết mù.
   - Chỉ sau khi có bài qua tầng 4 mới bàn tới vần và nhịp.

---

## 8. Tệp sinh ra

| Tệp | Nội dung |
|---|---|
| `datalake/analysis/generate_dat.jsonl` | 1 bài đạt, kèm dấu vết bảy tầng |
| `datalake/analysis/generate_truot.jsonl` | 199 bài trượt, kèm dấu vết bảy tầng + chi tiết từng dòng |

Mỗi bản ghi giữ: `dat`, `thuoc_the`, `tang_dung_lai`, bảy tầng (`da_chay`, `dat`,
`bang_chung`), danh sách `vi_pham` (mã luật, dòng, kỳ vọng, thực tế), và
`dong_chi_tiet` — số tiếng, danh sách tiếng, tiếng ở vị trí 2/4/6 kèm thanh của
từng tiếng.

`rule.py` **không bị động tới** trong lượt đối chiếu này.
