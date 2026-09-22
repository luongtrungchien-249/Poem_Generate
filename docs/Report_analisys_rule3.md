# Report — Đối chiếu `bai_dat.jsonl` qua `compare_rule.py` BẢN NỚI (rule3)

**Ngày:** 22/09/2026
**Corpus:** `datalake/analysis/bai_dat.jsonl` — 24.366 bài thất ngôn đã ĐẠT bảy tầng của `src/application/rule.py`
**Bộ luật đối chiếu:** `compare_rule.py`, hàm `bay_chu_rule_check`, **sau bản sửa "nới luật Bằng/Trắc thất ngôn"** (§1.1 đầu file ấy)
**Script:** `datalake/scripts/chay_doi_chieu_rule3.py`
**Kết quả thô:** `bai_dat_rule3.jsonl`, `bai_truot_rule3.jsonl`, `tong_hop_rule3.json`

---

## 0. Đọc trước khi tin số

Lượt chạy này dùng **cùng corpus, cùng hàm kiểm** như `Report_analisys_rule2.md`. Khác biệt
duy nhất là `compare_rule.py` đã nới luật Bằng/Trắc: **chỉ câu đầu mỗi khổ 4 câu** phải giữ
nhịp "nhị tứ lục phân minh" (tiếng 2/4/6 luân phiên B-T-B hoặc T-B-T); ba câu còn lại của
mỗi khổ không còn bị chấm thanh điệu.

Vì chỉ một biến đổi, mọi chênh lệch rule2 → rule3 quy được về đúng một nguyên nhân.

Bằng chứng trong report này **không** lấy từ các trường `thanh`, `van_cuoi` có sẵn trong
corpus — chúng do `rule.py` tính. Toàn bộ số liệu dưới đây dựng lại bằng chính tầng ngữ âm
của `compare_rule.py` (`clean_and_tokenize`, `get_tone`, `van_cua`, `is_rhyme_match`), vì
câu hỏi là *bộ luật ấy* phán thế nào.

---

## 1. Kết quả tổng

| | Số bài | Tỉ lệ |
|---|---:|---:|
| **ĐẠT** | **3.813** | **15,65 %** |
| **TRƯỢT** | **20.553** | **84,35 %** |
| Tổng | 24.366 | 100 % |

### So với rule2 (trước khi nới)

| | rule2 | rule3 | Chênh |
|---|---:|---:|---:|
| ĐẠT | 3.146 (12,91 %) | 3.813 (15,65 %) | **+667 bài, +2,74 điểm %** |
| TRƯỢT | 21.220 (87,09 %) | 20.553 (84,35 %) | −667 bài |

Nới luật cứu được **667 bài** — những bài mà lỗi duy nhất là thanh điệu ở câu 2/3/4 của khổ.
Phần còn lại, **84,35 % vẫn trượt**, và không một bài nào trong số đó trượt vì Bằng/Trắc.

---

## 2. Vì sao con số chỉ nhích 2,74 điểm

### 2.1. Phép kiểm Bằng/Trắc mới đã trở nên VÔ HIỆU trên corpus này

Đếm trực tiếp trên toàn bộ 24.366 bài:

```
Số DÒNG bất kỳ lệch luân phiên 2-4-6     : 0
Số bài có ít nhất 1 dòng lệch            : 0
Số CÂU ĐẦU KHỔ lệch luân phiên           : 0
```

**Không một dòng nào** trong corpus vi phạm luân phiên 2/4/6 — `rule.py` đã bắt điều kiện ấy
ở tầng của nó trước khi bài lọt vào `bai_dat.jsonl`. Mà phép kiểm mới chỉ xét đúng điều kiện
đó trên câu đầu khổ, nên nó **không thể sinh lỗi** trên tập này.

Hệ quả kiểm chứng được: nhóm lỗi *"Vi phạm Bằng/Trắc"* biến mất hoàn toàn.

| Nhóm lỗi (đếm theo lượt) | rule2 | rule3 |
|---|---:|---:|
| Sai Vần | 30.170 | 30.170 |
| Lỗi Gieo Vần (thanh cuối không Bằng) | 24.049 | 24.049 |
| **Vi phạm Bằng/Trắc** | **6.959** | **0** |

Hai nhóm vần **không đổi một lượt nào** — đúng như thiết kế, hai khối gieo vần không bị đụng tới.

### 2.2. 6.959 lượt lỗi cũ đo cái gì

Vì mọi dòng đều đã luân phiên đúng, 6.959 lượt lỗi B/T của rule2 **không** đo việc dòng thơ
sai nhịp. Chúng đo việc dòng 2/3/4 không khớp **bảng niêm Đường luật suy ra từ dòng 1** —
tức luật *niêm giữa các câu*, không phải luật *trong câu*. Đó chính là ràng buộc vừa được bỏ.

### 2.3. Trần của tỉ lệ đạt

Chỉ 667/6.959 lượt lỗi ấy nằm trên những bài mà đó là lỗi **duy nhất**. 6.292 lượt còn lại
nằm trên các bài đằng nào cũng trượt vì vần. Nới luật Bằng/Trắc nữa cũng không nhích được
thêm — trần đã chạm.

---

## 3. Phần trượt còn lại nằm ở đâu

### 3.1. Theo nhóm lý do

| Nhóm | Số bài dính | % số bài trượt |
|---|---:|---:|
| Lỗi Gieo Vần (thanh cuối câu 1/2/4 không Bằng) | 17.388 | 84,60 % |
| Sai Vần (câu 1/2/4 không hiệp vần) | 17.300 | 84,17 % |

Tổng vượt 100 % vì một bài thường dính cả hai.

### 3.2. Theo số dòng — chỗ lệch lớn nhất

| Số dòng | Đạt | Trượt | Tỉ lệ đạt |
|---:|---:|---:|---:|
| 4 | 2.429 | 1.474 | **62,23 %** |
| **8** | **313** | **12.817** | **2,38 %** |
| 12 | 237 | 699 | 25,32 % |
| 16 | 359 | 2.457 | 12,75 % |
| 20 | 148 | 693 | 17,60 % |
| 24 | 113 | 468 | 19,45 % |
| 28 | 145 | 791 | 15,49 % |

Bài 4 dòng đạt 62 %. Bài 8 dòng đạt **2,38 %** — thấp hơn 26 lần. Bài 8 dòng lại chiếm
13.130/24.366 = 53,9 % corpus, nên chính nó kéo tỉ lệ chung xuống.

### 3.3. Nguyên nhân của hố 8 dòng: bát cú bị chấm như hai bài tứ tuyệt

Thất ngôn bát cú có **một độc vận** cho các câu 1, 2, 4, 6, 8; câu 5 **kết thanh Trắc** là
đúng phép. Nhưng `bay_chu_rule_check` cắt bài 8 dòng thành hai khổ tứ tuyệt độc lập rồi đòi
mỗi khổ tự có bộ vần riêng ở câu 1, 2, 4 của khổ — với khổ 2, "câu 1 của khổ" chính là dòng 5.

Đo trên 12.817 bài 8 dòng bị trượt:

```
... có dòng 5 kết thanh TRẮC          : 12.335  (96,24 %)
... trượt CHỈ VÌ đúng lỗi dòng 5 ấy   :  2.753  (21,48 %)
```

96 % bài 8 dòng trượt có dòng 5 kết Trắc — tức **làm đúng phép bát cú**. Và 2.753 bài trượt
mà không có lỗi nào khác ngoài lỗi này. Đây là lỗi của bộ kiểm, không phải của bài thơ.

### 3.4. Bảng vần thông thiếu các cặp thông dụng

12 cặp vần bị chấm "không hiệp" nhiều nhất:

| Cặp vần | Số lượt | Ghi chú |
|---|---:|---|
| `-ay` / `-ây` | 2.743 | cặp vần thông cổ điển, **thiếu** trong `_CAP_VAN` |
| `-au` / `-âu` | 1.945 | cặp vần thông cổ điển, **thiếu** |
| `-an` / `-ang` | 1.486 | khác âm cuối (n/ng) — chấm trượt là hợp lý |
| `-uôn` / `-ương` | 645 | |
| `-em` / `-êm` | 590 | bảng chỉ có `("êm","im")`, thiếu `("em","êm")` |
| `-uô` / `-ươ` | 571 | |
| `-ai` / `-ây` | 416 | |
| `-ao` / `-âu` | 348 | |
| `-ơ` / `-ươ` | 298 | |
| `-ang` / `-ăng` | 280 | |
| `-an` / `-ân` | 273 | bảng có `("ăn","ân")`, thiếu `("an","ân")` |
| `-uôn` / `-uông` | 269 | |

Riêng `ay/ây` và `au/âu` là **4.688 lượt**. Bảng `_CAP_VAN` đã có cặp ă/â (`("ăm","âm")`,
`("ăn","ân")`) nhưng bỏ sót đúng hai cặp a/â phổ biến nhất trong thơ. Đây là **khe hở của
bảng vần**, không phải lỗi của bài thơ.

### 3.5. Phân bố số lỗi mỗi bài

| Số lỗi | 0 | 1 | 2 | 3 | 4 | 5–9 | 10–19 | ≥20 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Số bài | 3.813 | 4.552 | 9.969 | 2.339 | 1.507 | 1.812 | 327 | 47 |

4.552 bài chỉ sai **đúng một chỗ**. Cộng với 9.969 bài sai hai chỗ, 71 % số bài trượt nằm
trong tầm sửa một đến hai dòng.

---

## 4. Ba ví dụ ĐẠT

### 4.1. `id = 72` — "TRẢ HƯƠNG", 8 dòng, 0 lỗi

```
1. Nhác bóng xuân hồng ngơ ngác đông,
2. Gió xa se cuộn rối tơ lòng.
3. Người đi biết có còn ươm mộng,
4. Xuân ấy tròn nguyên một chữ nồng.
5. Rồi mai én lượn mỏi từng không,
6. Vương níu mà chi cải đã ngồng.
7. Đem chưng thương nhớ đêm đồng vọng,
8. Hương trả về nơi lúa ủ đòng.
```

**Vì sao đạt:**

| Dòng | 2/4/6 | Tiếng cuối | Vần | Thanh cuối |
|---:|---|---|---|---|
| 1 | T-B-T | đông | `-ông` | B |
| 2 | B-T-B | lòng | `-ong` | B |
| 4 | T-B-T | nồng | `-ông` | B |
| 5 | B-T-B | không | `-ông` | B |
| 6 | T-B-T | ngồng | `-ông` | B |
| 8 | T-B-T | đòng | `-ong` | B |

- Số tiếng: cả 8 dòng đều 7 tiếng ✓
- Bằng/Trắc câu đầu khổ: dòng 1 `T-B-T` ✓, dòng 5 `B-T-B` ✓
- Vần khổ 1: `đông`(-ông) ↔ `lòng`(-ong) HIỆP (cặp `("ong","ông")` trong nhóm vần thông);
  `lòng`(-ong) ↔ `nồng`(-ông) HIỆP
- Vần khổ 2: `không` ↔ `ngồng` HIỆP; `ngồng`(-ông) ↔ `đòng`(-ong) HIỆP
- Thanh cuối các câu 1/2/4 của **cả hai khổ** đều Bằng ✓

Bài này qua được hố 8 dòng ở §3.3 chỉ vì dòng 5 tình cờ kết thanh **Bằng** (`không`) — tức
nó **không** làm theo phép bát cú chuẩn. Đó là điều kiện để lọt, và là lý do chỉ 2,38 % bài
8 dòng đạt.

### 4.2. `id = 2698` — 4 dòng, 0 lỗi

```
1. Anh lấy nỗi đau làm mật ong,
2. Chao ôi từng giọt chảy như lòng.
3. Em biết đời ong đi vạn dặm,
4. Chắt cả mùa xuân giọt mật trong.
```

**Vì sao đạt:** dòng 1 `T-B-T` ✓. Ba tiếng vần `ong` – `lòng` – `trong` cùng vần `-ong`,
cùng thanh Bằng ✓. Dòng 3 kết `dặm` (Trắc) — **không bị kiểm**, vì luật chỉ soi câu 1, 2, 4.

### 4.3. `id = 4117` — "Tôi mang Hồ Gươm đi", 16 dòng, 0 lỗi

Bốn khổ, mỗi khổ một bộ vần riêng, và cả bốn đều khép kín trong khổ:

| Khổ | Dòng | Vần câu 1 / 2 / 4 | Kết quả |
|---:|---|---|---|
| 1 | 1–4 | `xa` / `nhòa` / `hoa` — đều `-a` | HIỆP |
| 2 | 5–8 | `tranh` / `thành` / `xanh` — đều `-anh` | HIỆP |
| 3 | 9–12 | `đông` / `Hồng` / `trông` — đều `-ông` | HIỆP |
| 4 | 13–16 | `đây` / `đầy` / `cây` — đều `-ây` | HIỆP |

Câu đầu mỗi khổ: dòng 1 `B-T-B`, dòng 5 `T-B-T`, dòng 9 `T-B-T`, dòng 13 `B-T-B` — đều luân
phiên hợp lệ ✓. Câu 3 của mỗi khổ (`cá`, `đọng`, `rét`, `sóng`) đều kết Trắc, đều không bị kiểm.

Bài dài mà vẫn đạt vì nó **được viết theo đúng lối khổ tứ tuyệt liên hoàn** — chính là lối
mà bộ kiểm giả định.

---

## 5. Ba ví dụ TRƯỢT

### 5.1. `id = 1` — "BÂNG KHUÂNG", 8 dòng, 2 lỗi — *trượt vì khe hở bảng vần*

```
1. Đã biết không nên nhớ một người,     -ươi  B
2. Mà còn khắc khoải đến không nguôi.   -uôi  B
4. Cuối buổi hình xa ở mạn đồi.         -ôi   B
5. Mấy bận đi qua lòng định gọi,        -oi   T
6. Đôi lần đứng lại dạ dừng thôi.       -ôi   B
8. Để cứ bâng khuâng hận nửa đời.       -ơi   B
```

**Lỗi bộ kiểm báo:**

```
[Sai Vần] [CRITICAL!] Khổ 1: Từ cuối Dòng 1 ('người') chưa vần với Dòng 2 ('nguôi').
          Gợi ý: -uôi | Từ cuối Dòng 4 ('đồi') chưa vần với Dòng 2 ('nguôi'). Gợi ý: -uôi
[Lỗi Gieo Vần Khổ 2] Dòng 5 ('gọi' - Trắc) sai thanh điệu.
```

**Truy nguyên:**

- `người` → vần `-ươi`; `nguôi` → vần `-uôi`. Nhóm vần thông `("ai","oi","ôi","ơi","ươi","ui")`
  **có** `ươi` nhưng **không có** `uôi`. Nên `ươi` ↔ `uôi` bị chấm không hiệp — dù trong thơ
  Việt đây là cặp vần thông bình thường. **Khe hở bảng vần.**
- `đồi`(-ôi) ↔ `nguôi`(-uôi): cùng lý do.
- Dòng 5 `gọi` kết Trắc: đây là **câu 5 của bát cú**, kết Trắc là đúng phép — nhưng bộ kiểm
  coi nó là "câu 1 của khổ 2" nên đòi thanh Bằng. Chính là lỗi §3.3.

Bài này **không sai luật thơ**. Nó trượt vì hai khiếm khuyết của bộ kiểm cùng lúc.

### 5.2. `id = 36` — "NGÔI NHÀ HẠNH PHÚC", 8 dòng, **1 lỗi duy nhất** — *bát cú hoàn hảo bị đánh trượt*

```
1. Lá trải bên thềm nhuộm nếp tranh,    -anh  B
2. Lời yêu ước nguyện mãi song hành.    -anh  B
3. Len dòng gió ấm xua chiều quạnh,     -anh  T
4. Lựa dải tơ mềm buộc nắng hanh.       -anh  B
5. Luống cỏ xanh tươi chồng trỉa nhánh, -anh  T
6. Lề hoa rực thắm vợ vun cành.         -anh  B
7. Lam chiều quyện ngõ viền tiên cảnh,  -anh  T
8. Lạc nẻo chân tình đẹp ngỡ tranh.     -anh  B
```

**Đây là một bài thất ngôn bát cú chỉnh:** độc vận `-anh` suốt 8 câu; các câu 1, 2, 4, 6, 8
kết thanh Bằng; các câu 3, 5, 7 kết thanh Trắc — **đúng phép**.

**Bộ kiểm chấm được gần hết:**

```
✓ Cấu trúc: 8 dòng (chia thành 2 khổ 4 câu).
✓ Số tiếng: Tất cả các dòng đều đạt chuẩn 7 tiếng.
✓ [Dòng 1] Luật Bằng/Trắc chuẩn xác (2 Trắc - 4 Bằng - 6 Trắc).
✓ [Dòng 5] Luật Bằng/Trắc chuẩn xác (2 Trắc - 4 Bằng - 6 Trắc).
✓ [Gieo Vần] Khổ 1: 'tranh' - 'hành' - 'hanh' hiệp vần chuẩn xác.
✓ [Gieo Vần] Khổ 2: 'nhánh' - 'cành' - 'tranh' hiệp vần chuẩn xác.
```

**Rồi trượt vì đúng một dòng:**

```
[Lỗi Gieo Vần Khổ 2] Dòng 5 ('nhánh' - Trắc) sai thanh điệu.
                     Từ cuối các câu 1, 2 và 4 bắt buộc phải là vần Bằng.
```

Câu 5 bát cú **phải** kết Trắc. Bộ kiểm đòi Bằng vì nó tưởng dòng 5 mở một bài tứ tuyệt mới.
Đây là ví dụ sạch nhất của lỗi §3.3, và là bài đại diện cho **2.753 bài** trượt chỉ vì lỗi này.

### 5.3. `id = 2986` — 8 dòng, 2 lỗi — *thiếu cặp `ay`/`ây`*

**Các tiếng vần:** khổ 1 `bay`(-ay) / `đầy`(-ây) / `say`(-ay); khổ 2 `tay`(-ay) / `ngây`(-ây) / `mây`(-ây)

```
[Sai Vần] [CRITICAL!] Khổ 1: 'bay' chưa vần với 'đầy'. Gợi ý: -ây
                             'say' chưa vần với 'đầy'. Gợi ý: -ây
[Sai Vần] [CRITICAL!] Khổ 2: 'tay' chưa vần với 'ngây'. Gợi ý: -ây
```

**Truy nguyên:** `_CAP_VAN` có `("ai","ay")`, `("ăm","âm")`, `("ăn","ân")` — nhưng **không có
`("ay","ây")`**. Với người đọc thơ, `bay` – `đầy` – `say` – `mây` là một bộ vần hoàn toàn
bình thường. Với bảng này thì không.

Đáng chú ý: cặp `ngây` ↔ `mây` (khổ 2, dòng 6↔8) được chấm HIỆP, vì cả hai cùng `-ây`. Nên
bài trượt không phải vì thiếu vần, mà vì bảng chia đôi một bộ vần vốn liền.

Đây là bài đại diện cho **2.743 lượt** lỗi `ay`/`ây` — nhóm đông nhất trong toàn bộ số lỗi vần.

---

## 6. Kết luận

1. **Nới luật Bằng/Trắc đạt đúng mục tiêu đề ra, nhưng biên độ nhỏ:** +667 bài, 12,91 % →
   15,65 %. Ràng buộc bị gỡ là *niêm giữa các câu*, không phải nhịp trong câu.

2. **Phép kiểm Bằng/Trắc mới vô hiệu trên corpus này** — 0/24.366 dòng lệch luân phiên 2/4/6,
   vì `rule.py` đã bắt sẵn ở tầng trên. Nó vẫn có ích với đầu vào chưa qua `rule.py`, nhưng
   trên tập này thì không phân biệt được gì.

3. **84,35 % còn trượt, và phần lớn không phải lỗi của bài thơ.** Ba nguyên nhân hệ thống,
   theo thứ tự tác động:

   | # | Nguyên nhân | Quy mô đo được |
   |---|---|---|
   | 1 | Bát cú bị cắt thành hai tứ tuyệt → đòi câu 5 kết Bằng | 12.335 bài 8 dòng; 2.753 bài trượt **chỉ** vì nó |
   | 2 | Bảng vần thông thiếu `ay/ây`, `au/âu`, `ươi/uôi`, `em/êm`, `an/ân` | 4.688 lượt riêng hai cặp đầu |
   | 3 | Bắt buộc câu 1 mỗi khổ phải gieo vần | (chưa tách riêng; nằm trong 17.300 bài Sai Vần) |

4. **Nếu muốn nâng tỉ lệ đạt, sửa Bằng/Trắc nữa là vô ích** — trần đã chạm. Đòn bẩy nằm ở
   nguyên nhân #1: nhận diện bài 8 dòng là bát cú và chấm bằng `bay_chu_bat_cu_rule_check`
   (hàm ấy đã có sẵn và xử lý độc vận 1/2/4/6/8 đúng) thay vì cắt đôi.

5. **Cảnh báo giữ nguyên:** `compare_rule.py` là **hồ sơ đối chiếu, không chạy trong hệ thống
   sống**. Không nhập luật từ đây vào `rule.py` hay vào prompt. Các khiếm khuyết nêu ở §3 được
   **cố ý giữ** để hồ sơ phản ánh đúng bộ luật thế hệ trước.

---

## 7. Tệp sinh ra

| Tệp | Số dòng | Nội dung |
|---|---:|---|
| `datalake/analysis/bai_dat_rule3.jsonl` | 3.813 | Bài ĐẠT, kèm `rule3_dat_chuan` (danh sách chỗ đúng) |
| `datalake/analysis/bai_truot_rule3.jsonl` | 20.553 | Bài TRƯỢT, kèm `rule3_loi` đầy đủ |
| `datalake/analysis/tong_hop_rule3.json` | — | Thống kê + 6 ví dụ kèm bằng chứng từng dòng |
| `datalake/scripts/chay_doi_chieu_rule3.py` | — | Script tái lập toàn bộ số liệu trên |

Chạy lại: `python datalake/scripts/chay_doi_chieu_rule3.py`
