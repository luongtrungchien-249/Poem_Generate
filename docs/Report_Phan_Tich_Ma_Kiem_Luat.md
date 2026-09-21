# Báo cáo đọc mã: `compare_rule.py` và `src/application/rule.py`

Ngày: 2026-09-21 · Nhánh: `UI-for-Project`
Phạm vi: đọc từng dòng hai file, đối chiếu mã với chú thích và tài liệu luật.
Cách kiểm chứng: các khẳng định có đánh dấu ✅ đã được chạy thật bằng Python trên repo, không suy luận suông.

---

## PHẦN 0 — Hai file này là hai thế hệ khác nhau

| | `compare_rule.py` | `src/application/rule.py` |
|---|---|---|
| Vị trí | gốc repo, ngoài `src/` | trong tầng `application` |
| Thể thơ | lục bát, 7 chữ tứ tuyệt, 7 chữ hiện đại, thất ngôn bát cú, 8 chữ | chỉ thất ngôn tự do |
| Kết quả trả về | `(bool, list[str], list[str])` — lỗi là **chuỗi** | `PoemVerdict` — dataclass có `ViPham`, `BaoCaoDong`, `KetQuaTang` |
| Mức độ lỗi | nhúng chuỗi `[CRITICAL!]` vào câu văn | trường dữ liệu + phân tầng `chan`/`ghi_nhan` |
| Triết lý | lỗi kèm **lời khuyên sửa câu chữ** | *"Bộ kiểm **phán**, mô hình **sửa**"* — cấm gợi ý sửa nội dung |
| Nguồn luật | luật ngầm trong code | bảng `LUAT` là **dữ liệu**, có test đối chiếu |
| Trạng thái | **không import được** (xem 1.1) | đang chạy, có test |

Hai file **không** chồng lấn về thể thơ, nên không thay thế được nhau. Nhưng chúng chồng lấn hoàn toàn về *hạ tầng*: tách tiếng, phân thanh B/T, tách vần, so vần. Đó là chỗ nên hợp nhất, không phải chỗ nên chọn một bỏ một.

---

# PHẦN 1 — `compare_rule.py`

## 1.1 Lỗi chặn đường: file không import được ✅

```python
import __main__                                  # dòng 7
from .constants import CRITICAL_ERROR_KEYWORDS   # dòng 11
from .rhyme import (...)                         # dòng 12
```

- `import __main__` không được dùng ở bất kỳ đâu trong file. Đây là import thừa, và còn có thể gây hiệu ứng phụ khi module bị nạp lại.
- Hai import **tương đối** (`.constants`, `.rhyme`) đòi file phải nằm trong một package. Nó đang nằm ở gốc repo, và `grep` toàn bộ `*.py` không thấy module `rhyme.py`, `constants.py`, cũng không thấy ai gọi `luc_bat_rule_check` hay `is_rhyme_match`. Nghĩa là: **file này hiện không chạy được và không ai gọi nó**.
- Docstring dòng 4 vẫn ghi `checker.py` — tên file cũ.

Hệ quả thực tế: mọi lỗi phân tích dưới đây là lỗi *tiềm ẩn*, chưa gây hại vì code chưa sống. Đây cũng là cơ hội: sửa trước khi nối vào hệ thống thì rẻ hơn nhiều.

## 1.2 `evaluate_errors` (18–22)

```python
critical = sum(1 for e in errors if any(kw in e for kw in kw_list))
```

**Mạnh:** tách mức độ khỏi thân hàm kiểm, đổi bảng từ khoá là đổi được phân loại.

**Yếu:** đây là **cơ chế phân loại mức độ thứ ba** của cùng một file, song song với:
- `return len(errors) == 0` (6/7 hàm),
- `[e for e in errors if "[CRITICAL!]" in e]` (dòng 574, riêng `tam_chu`).

Ba cơ chế cho cùng một khái niệm, và chúng **không nhất quán với nhau**: một lỗi có nhãn `[CRITICAL!]` chưa chắc khớp `kw_list`, và ngược lại. Phân loại mức độ bằng cách **tìm chuỗi con trong câu tiếng Việt** là thiết kế dễ vỡ — sửa một chữ trong thông điệp lỗi có thể âm thầm hạ một lỗi nặng xuống lỗi nhẹ, không test nào bắt được.

> `rule.py` đã giải đúng bài này: mức độ nằm ở `DinhNghiaTang.muc` và `LoaiLuat`, là dữ liệu chứ không phải văn bản.

## 1.3 `annotate_poem_words` (25–32)

Hàm ngắn, đúng việc, không trạng thái. Không có gì để chê ngoài việc thiếu docstring.

## 1.4 `luc_bat_rule_check` (35–257)

### 1.4.1 🔴 Lệch pha lục/bát sau một khổ lẻ dòng (dòng 95, 107)

```python
expected = 6 if (i % 2 == 0) else 8      # 95
is_luc   = (idx % 2 == 0)                # 107
```

`i`/`idx` là chỉ số trên danh sách **phẳng** `all_lines`. Khổ 1 có 3 dòng thì dòng đầu khổ 2 mang chỉ số 3 (lẻ) và bị chấm như dòng **bát**: kỳ vọng 8 tiếng, kiểm luật `2B-4T-6B-8B`. Toàn bộ phần còn lại của bài bị chấm ngược luật.

Lỗi khổ lẻ dòng đã được báo ở dòng 82–87, nhưng bài vẫn chạy tiếp và sinh hàng chục lỗi giả. Với vòng lặp sửa thơ bằng LLM, phản hồi giả còn tệ hơn không có phản hồi: mô hình sẽ "sửa" những chỗ vốn đúng.

**Cách sửa:** đánh số dòng theo vị trí *trong khổ*, hoặc dừng ngay sau khi phát hiện khổ lẻ dòng.

### 1.4.2 🔴 `elif` nuốt lỗi ở dòng bát (dòng 148–161)

```python
if t2 != "Bằng" or t8 != "Bằng":   ...          # 148
elif not (t4 == "Trắc" and t6 == "Bằng"): ...   # 155
```

Dòng sai cả từ 2 lẫn từ 4 chỉ được báo lỗi từ 2. Mô hình sửa xong từ 2, chạy lại, mới thấy lỗi từ 4 — tốn thêm một vòng gọi LLM cho mỗi lỗi bị che.

Trớ trêu là ngay bên trong mỗi nhánh, tác giả **đã** dùng đúng kỹ thuật gom lỗi (`wrong_words = []`). Chỉ cần gom cả bốn vị trí vào một danh sách duy nhất.

Nhánh lục (110–131) có cùng vấn đề ở mức nhẹ hơn: nhánh Tiểu Đối (115) báo một thông điệp gộp, không tách được từ 3 sai hay từ 6 sai.

### 1.4.3 🟡 Docstring nói ngược với code (dòng 43 vs 191)

Docstring: *"Lục T6 ↔ Bát T6/T4 rhyme check applies within each pair (**same rule**)"* — tức luôn áp dụng.
Code dòng 191: `if j >= n or j in new_stanza_starts: continue` — bỏ qua khi ranh giới khổ rơi vào giữa cặp.

Một trong hai phải sửa. Chú thích sai nguy hiểm hơn không có chú thích, vì người đọc sau sẽ tin nó.

### 1.4.4 🟡 Báo trùng cùng một khiếm khuyết (dòng 226–231)

```python
elif not rhyme_6_4 and rhyme_6_6:
    if get_tone(w_b4) != "Trắc" or get_tone(w_b6) != "Bằng":
        errors.append("[Luật Bằng/Trắc ...][CRITICAL!] Mô hình chuẩn: từ 4 phải Trắc, từ 6 phải Bằng.")
```

Mục 1 (dòng 155–161) **đã** kiểm đúng điều này rồi. Một dòng sai sinh hai thông điệp lỗi, và thông điệp ở đây còn tệ hơn: nó không nói từ nào sai, sai thành thanh gì.

Tương tự, `n % 2 != 0` (74) và vòng kiểm khổ lẻ dòng (82) cùng báo về một nguyên nhân gốc.

### 1.4.5 🟡 Bỏ kiểm tra trong im lặng (dòng 171, 200, 242)

Mọi khối niêm/vần đều canh `if len(...) >= 4/6/8`. Dòng thiếu tiếng chỉ nhận **lỗi độ dài**, còn niêm và vần **không được chấm và không ai được báo**. Bài hỏng năm chỗ chỉ hiện một lỗi.

Nên ghi thẳng vào `errors` rằng các phép kiểm phụ thuộc đã bị bỏ qua — chính là nguyên tắc N3 mà `rule.py` áp dụng (`chi_tiet["S3_khong_kiem_duoc"]`).

### 1.4.6 🟢 Điểm mạnh của hàm này

- Xử lý khổ bằng `new_stanza_starts` là ý đúng: vần chân vắt qua khổ thì không nên ép.
- Luật Tiểu Đối (115–121) là chi tiết chuyên môn thật, không phải luật bịa.
- Kiểm "điệp thanh" ngang/huyền ở từ 6 và từ 8 (138–147) là nét tinh — nhiều bộ kiểm lục bát bỏ qua.
- `successes` được ghi đầy đủ chứ không chỉ ghi lỗi. Với vòng sửa LLM, cho mô hình biết chỗ nào **đã đúng** để giữ lại cũng quan trọng ngang việc chỉ chỗ sai.

## 1.5 `bay_chu_rule_check` (259–389)

**Mạnh:** bảng `expected_patterns` (322–335) là cách phát biểu luật Bằng/Trắc gọn và đúng; đảo Luật Bằng ↔ Luật Trắc chỉ bằng một cờ.

**Yếu:**

| Dòng | Vấn đề |
|---|---|
| 283–287 | Lỗi số dòng **không có** nhãn `[CRITICAL!]`, trong khi cùng loại lỗi ở các hàm khác thì có → cùng khiếm khuyết, khác mức độ tuỳ hàm |
| 310–311 | `if len(chunk) < 4: break` — phần dư cuối bài bị bỏ **im lặng** |
| 316 | Canh `len(line) >= 6` nhưng dòng 356 lại canh `>= 7`; hai ngưỡng khác nhau cho hai khối trong cùng một vòng lặp |
| 356 | `line3` không bao giờ được kiểm vần — đúng luật (câu 3 buông vần), nhưng không có dòng chú thích nào nói vậy |
| 373–379 | Bắt buộc câu 1 gieo vần. Thất ngôn tứ tuyệt cho phép **thủ cú bất nhập vận** (câu 1 không vần) → loại oan một thể hợp lệ |
| 374 vs 375 | `sugg_1` lấy gợi ý theo `w2_7` nhưng câu văn lại nói về dòng `i+1` — người đọc và LLM đều dễ hiểu nhầm |

## 1.6 `bay_chu_modern_rule_check` (392–420)

Hàm sạch nhất file: ngắn, một việc, có tham số `expected_lines` tường minh.

Một điểm cần ghi rõ: hàm này **chỉ kiểm số dòng và số tiếng**, không kiểm vần, không kiểm thanh. Tên `rule_check` gợi ý nhiều hơn thế. Docstring có nói *"without imposing Đường-law tones"* nhưng không nói là cũng bỏ luôn vần.

Còn một lỗi logic nhỏ ở 403–408: `if expected_lines is not None and len != expected` / `else`. Khi `expected_lines is None`, nhánh `else` vẫn chạy và ghi `successes` — tức là "đạt cấu trúc" dù chưa hề kiểm gì. Thông điệp thành công không có cơ sở.

## 1.7 `bay_chu_bat_cu_rule_check` (423–478)

**Mạnh:** đây là hàm viết theo phong cách hiện đại nhất file — list comprehension, `zip`, dựng `expected` từ `base`/`opposite` thay vì gõ tay 8 dòng. Mẫu niêm bát cú `[base, opp, opp, base, base, opp, opp, base]` đúng.

**Yếu:**

- Dòng 466–472: `anchor = rhyme_words[1]`, rồi vòng lặp so `anchor` với **chính nó** — một phép so luôn đúng, thừa.
- Cùng lỗi với 1.5: bắt buộc dòng 1 hiệp vần, loại oan thể thủ cú bất nhập vận.
- Dòng 469 và 471 có thể cùng kích hoạt cho một tiếng → hai thông điệp lỗi cho một khiếm khuyết.

## 1.8 `tam_chu_rule_check` (480–575)

### 1.8.1 🔴 Khổ sai số tiếng thì không được chấm vần (545, 564)

```python
if   len(chunk) == 4 and all(len(line) == 8 for line in chunk): ...   # 545
elif len(chunk) >  1 and all(len(line) == 8 for line in chunk): ...   # 564
```

Nhánh `elif` nhằm xử lý "mẩu cuối không đủ 4 câu", nhưng điều kiện `all(len(line) == 8)` **giống hệt** nhánh trên. Kết quả: khổ đủ 4 câu mà có một câu sai số tiếng thì **rơi qua cả hai nhánh** và không được chấm vần lần nào.

### 1.8.2 🔴 Chú thích nói ngược với code (519, 485, 531–538)

- Dòng 519: `# --- 2. Kiểm tra Bằng/Trắc (Khuyến nghị, không bắt lỗi Critical) ---`
- Dòng 485: `- Provides soft warnings for Tone (Bằng/Trắc) musicality rules.`
- Dòng 531–538: cả **bốn** thông điệp đều gắn `[CRITICAL!]`, và dòng 574 lọc đúng chuỗi đó để quyết định đạt/trượt.

Nói cách khác: cái được mô tả là "cảnh báo mềm" đang là **điều kiện cứng đánh trượt bài**. Đây là loại sai lệch tệ nhất — người bảo trì đọc chú thích rồi ra quyết định dựa trên một hành vi không tồn tại.

### 1.8.3 🟢 Điểm mạnh

Nhận diện ba sơ đồ vần AABB/ABAB/ABBA (549–558) là cách xử lý đúng cho thơ tám chữ: không ép một sơ đồ duy nhất, chấp nhận cả ba rồi gọi đúng tên. Đây chính là tinh thần mà `rule.py` phát biểu chặt chẽ hơn ở QĐ-7b.

## 1.9 Khối `__main__` (577–618)

Bài thơ 36 dòng của Tản Đà nằm trong file mã nguồn. Đây là **ngữ liệu kiểm thử quý** — nên chuyển thành test cố định dưới `tests/unit/`, để có kiểm thử hồi quy thật thay vì một lệnh `print` phải chạy tay mới biết kết quả.

---

# PHẦN 2 — `src/application/rule.py`

## 2.0 Nhận định tổng quát

File 2.200 dòng này **hơn hẳn một bậc** so với `compare_rule.py` về mặt kỹ thuật lẫn kỷ luật. Ba điều đáng học:

1. **Luật là dữ liệu, không phải chú thích.** Bảng `LUAT` (68–140) cho phép test kiến trúc đối chiếu `MA_CUNG` với `HAM_KIEM_CUNG` — thêm luật cứng mà quên viết hàm kiểm thì test đỏ. Tài liệu không cưỡng chế được thì sớm muộn sẽ lệch khỏi mã; ở đây nó cưỡng chế được.
2. **Phân biệt ba loại thẩm quyền** (`LOAI_DIEU_MEM`, 166–186): `bat_buoc` / `quyen` / `mo_ta`. Nguyên tắc N2 — *đánh trượt một bài vì tác giả dùng đúng cái quyền tài liệu cho phép là mâu thuẫn tự thân* — được cưỡng chế bằng test. Đây là suy nghĩ ở mức thiết kế, không phải mức code.
3. **Ghi công khai điều không kiểm được** (`chi_tiet["S3_khong_kiem_duoc"]`, …). Lặng lẽ cho qua và để người đọc tưởng đã kiểm là dối trá về mặt kỹ thuật; file này từ chối làm vậy.

Ngoài ra: `_bo_qua()` phân biệt `da_chay=False` với `dat=False` — "chưa kiểm" khác hẳn "đã kiểm và đạt". Hai cờ `dat` / `thuoc_the` cố ý không gộp. Chú thích ghi cả **lỗi đã trả giá** (§3, `_tang2`, `_tang3`) để người sau không khôi phục nhầm. Đây là mức tài liệu hoá hiếm gặp.

## 2.1 🔴 §5b viết xong nhưng **chưa được nối vào** — QĐ-3 chưa có hiệu lực ✅

Toàn bộ §5b (dòng 790–910) — `AmTiet`, `phan_tich_am_tiet`, `van_hiep` — được viết để sửa đúng một lỗi, ghi rõ ở dòng 797:

```
#     van_cua("hoa") = "oa"   ≠   van_cua("ha") = "a"    -> KHÔNG hiệp vần
#
# Sai. ... hai tiếng này HIỆP VẦN — đúng như thơ ca tiếng Việt vẫn gieo
```

Nhưng `hiep_van` ở dòng 931 vẫn gọi hàm **cũ**:

```python
van_a, van_b = van_cua(tieng_a), van_cua(tieng_b)
```

Kiểm chứng đã chạy:

```
hiep_van('hoa','ta').hiep  -> False
hiep_van('hoa','nhà').hiep -> False
```

Đúng cái ca mà chú thích nói là phải sửa, vẫn sai. Grep toàn repo: `phan_tich_am_tiet` **chỉ** được gọi trong `tests/unit/application/test_rule_tang.py`. Trong đường chạy thật, không dòng nào dùng nó.

Hệ quả nghiêm trọng vì đây là tầng 5 — tầng vần:
- Mọi bài gieo vần qua âm đệm (`hoa`–`nhà`, `quen`–`đen`, `tuyết`–`biếc`) bị **loại oan**.
- Có test xanh cho `phan_tich_am_tiet`, nên bảng điều khiển hiện "đã có QĐ-3" trong khi sản phẩm chưa có. Test đang bảo vệ code chết.
- Docstring `van_cua` (779–781) còn ghi *"GIỮ LẠI để tương thích ngược. Phép so vần **chính thức nay dùng** `phan_tich_am_tiet()`"* — phát biểu này hiện **sai sự thật**.

**Sửa:** đổi dòng 931 sang `phan_tich_am_tiet(tieng_a).van_hiep` và tương tự cho `b`, rồi chạy lại ngữ liệu vàng. Lưu ý `CAP_VAN_THONG` được xây trên khoá của `van_cua` (dạng "ang", "ương"), nên phải đối chiếu xem khoá bảng có khớp với `van_hiep` (âm chính + âm cuối) không — ví dụ `van_hiep("vang") = "ang"` khớp, nhưng `van_hiep("hoa") = "a"` trong khi bảng có cặp `("a","ơ")`. Đây là bước phải đo, không được đoán.

## 2.2 🔴 `nghi_duong_luat` **vĩnh viễn** bằng False ✅

Dòng 2119:

```python
nghi = ket_qua_tang[2].da_chay and not ket_qua_tang[2].dat
```

Nhưng `_tang3_loai_tru_duong_luat` trả về `dat=True` **luôn luôn** — chính chú thích dòng 1698 khẳng định thế: *"`dat=True` LUÔN LUÔN. Tầng ghi nhận không có khái niệm trượt"*.

Vậy `not dat` luôn False → `nghi` luôn False. Kiểm chứng đã chạy trên một bài thất ngôn độc vận có niêm: `tang3.dat = True`, `nghi_duong_luat = False`.

Hậu quả:
- Trường `PoemVerdict.nghi_duong_luat` **không bao giờ** đúng.
- Ghi chú *"Bài có số dòng, độc vận và niêm giống Đường luật…"* (2120–2124) là **mã chết**, không bao giờ chạy.
- Hàm `nghi_la_duong_luat()` (§8, dòng 1290–1308) — cả một mục có chú thích công phu về Đ1 và §9 Bước 2 — kết quả bị vứt bỏ ở tầng ngoài.

Đây là lỗi **hồi quy do sửa đúng một chỗ khác**: khi tầng 3 được sửa từ `muc="chan"` về `"ghi_nhan"` (ghi trong docstring là bản sửa 18/09/2026, gỡ oan 4.288 bài), dòng 2119 đọc `dat` đã mất nghĩa mà không ai đổi theo.

**Sửa:** `nghi = bool(ket_qua_tang[2].chi_tiet.get("nghi_duong_luat"))`. Giá trị vẫn được tầng 3 ghi đúng vào `chi_tiet`; chỉ đường dẫn ra ngoài bị đứt.

## 2.3 🟡 `thuoc_the` nay gồm cả H4, nhưng ba chỗ docstring vẫn ghi "chỉ H1–H3"

`thuoc_the` (2110–2112) tính từ tầng 1 và tầng 2. Từ 18/09/2026, tầng 1 kiểm **H3 và H4**. Nên `thuoc_the` thực chất là H1–H4.

`_tang1_hinh_thuc` nói rõ điều này (*"H4 là ràng buộc CỨNG nên nó vào cả cờ `thuoc_the`"*), nhưng ba chỗ khác vẫn ghi cũ:
- `PoemVerdict` docstring: `` `thuoc_the`  chỉ H1–H3 ``
- `kiem_tra_bai_tho` docstring: cùng câu
- Chú thích dòng 2109: `# thuoc_the chỉ hỏi tài liệu luật: tầng 1 và tầng 2, tức H1–H3.`

Không sai về hành vi, nhưng với một file mà giá trị lớn nhất nằm ở độ tin cậy của chú thích, đây là chỗ phải vá.

## 2.4 🟡 Nhãn `?` được tính là hiệp vần khi thống kê lệch thanh (2094–2100)

```python
if so_do[i] != "x" and so_do[i] == so_do[j]:
```

Nhãn `?` nghĩa là *quan hệ vần trong khổ không bắc cầu, khổ này không có sơ đồ xác định* (chú thích `suy_so_do_van`). Hai dòng cùng mang `?` **chưa chắc hiệp vần với nhau** — ví dụ chính chú thích đưa ra: `vang / vương / vuông`, trong đó `vang ≁ vuông` nhưng cả ba đều nhãn `?`.

Điều kiện trên xếp `vang` và `vuông` thành một cặp hiệp vần, rồi đo thanh của chúng. Số liệu `van_lech_thanh` vì thế phóng đại. Đây là số liệu mô tả, không đánh trượt bài, nên mức độ là 🟡 — nhưng nó mâu thuẫn trực tiếp với nguyên tắc mà file tự đặt ra: *không dùng gom cụm bắc cầu*.

**Sửa:** thêm `so_do[i] != "?"`, hoặc gọi thẳng `hiep_van(...).hiep` thay vì tin vào nhãn.

## 2.5 🟡 `doc_so` vỡ ở 10¹² ✅

```python
_HANG = ("", "nghìn", "triệu", "tỷ")   # dòng 434
...
ra.append(_HANG[bac])                  # dòng 491
```

`_HANG` có 4 phần tử nên `bac` tối đa là 3. Số từ 10¹² trở lên (nghìn tỷ) làm `bac = 4`:

```
doc_so(10**12) -> IndexError: tuple index out of range
```

Một dòng thơ chứa số lớn sẽ làm **cả bộ kiểm văng exception**, không phải trả về "bài trượt". Với đường chạy xử lý corpus hàng chục nghìn bài, một bài hỏng làm sập cả mẻ.

**Sửa:** kẹp `bac` lại, hoặc nếu `bac >= len(_HANG)` thì đọc rời từng chữ số (`_doc_chu_so_roi`) — đó cũng là cách người Việt thật sự đọc những số quá dài.

## 2.6 🟡 Hai bảng phụ âm đầu trùng nhau

`_PHU_AM_DAU` (§5) và `_AM_DAU` (§5b) có **nội dung giống hệt**, chỉ khác tên và chú thích. Hai nguồn sự thật cho cùng một dữ liệu: sửa một bên quên bên kia thì `van_cua` và `phan_tich_am_tiet` sẽ bất đồng về cùng một tiếng, và bất đồng ấy sẽ không có test nào bắt.

## 2.7 🟡 `HAM_KIEM_CUNG` chỉ sai địa chỉ H1

```python
"H1": "kiem_tra_bai_tho -> ViPham(ma='H1') cho từng dòng lệch 7 tiếng",
```

Thực tế `ViPham(ma="H1")` được dựng trong `_tang2_do_dai`. Bảng này tồn tại chính là để chống lệch giữa luật và mã, nên chính nó lệch thì mỉa mai — dù test chỉ đối chiếu **khoá**, không đối chiếu nội dung mô tả.

## 2.8 🟢 Tầng 6 rỗng nghĩa — nhưng đã được khai báo đúng

`_tang6_nhip` chặn **0/16.391** bài, và file **tự nói ra điều đó** bằng chữ in hoa, kèm lý do (chưa có bộ tách từ nên mọi dòng 7 tiếng đều "cắt được" thành 4/3, 3/4, 2/5…), kèm `chi_tiet["nguon_nhip"] = "khong_khai_bao"` để biên bản nói thật.

Đây **không phải lỗi** — đây là mẫu mực về cách xử lý một phép kiểm chưa làm được. So sánh với 1.4.5 của `compare_rule.py`, nơi phép kiểm bị bỏ qua trong im lặng: cùng một tình huống, hai cách hành xử ở hai đầu quang phổ.

## 2.9 🟢 Những chỗ khác đáng ghi nhận

| Vị trí | Điểm mạnh |
|---|---|
| `_la_dau_cau` (§3) | Nhận diện dấu câu theo **phân loại Unicode** thay vì liệt kê tay, sau khi đã trả giá vì thiếu "—" và "–". Chú thích ghi lại nguyên nhân gốc: *"danh sách liệt kê thì luôn thiếu"* |
| `CAP_VAN_THONG` (§5) | Chú thích chứng minh bảng vần thông **không bắc cầu** bằng chính lời Trần Trọng Kim, đo được 55 vần / 73 cạnh / 16 bộ ba vi phạm, rồi kết luận không được gom cụm. Đây là nghiên cứu, không phải code |
| `suy_so_do_van` (§7) | Chỉ gán chữ cái khi thành phần liên thông là **clique**; ngược lại gán `?`. Đúng về toán và đúng về nguồn |
| `suy_so_do_van_toan_bai` (§7) | Nhập lớp vần chỉ khi **mọi** tiếng hiệp với **mọi** tiếng đã có, không so với một đại diện — vì quan hệ không bắc cầu |
| `PHOI_KHUON_16` (§6c) | Giữ nguyên bảng của chủ dự án làm **dữ liệu**, và test ghim tính chất "B-T-B = 0, T-B-T = 1, mã = nhị phân + 1" nên không ai gõ nhầm thứ tự mà bảng vẫn lặng lẽ đúng |
| `_tang1_hinh_thuc` | Từ chối gợi ý "thêm/bớt dòng cho đủ bội 4", với lý do: đó là bảo người ta xoá một câu thơ hoặc viết thêm câu không có trong bài |

## 2.10 🟡 Kích thước file

2.200 dòng, trong đó ước chừng **quá nửa là chú thích**. Chú thích ở đây có giá trị thật (nó ghi quyết định, nguồn, và lỗi đã trả giá — những thứ git log không giữ được ở dạng đọc được). Nhưng file đang gánh 10 mục §1–§10 với các trách nhiệm khá rời nhau: bảng luật, đếm âm tiết, ngữ âm học, bảng vần, khuôn thanh, nhịp, sơ đồ vần, bảy tầng.

Đề xuất tách theo đúng ranh giới § đã có — `luat_bang.py`, `am_tiet.py`, `van.py`, `tang.py` — vì các mục đã tự phân chia sẵn. Đây là việc **không gấp** và có rủi ro (mọi import hiện tại phải đổi); chỉ nên làm khi đã có mục 2.1 và 2.2 được sửa và test xanh.

---

# PHẦN 3 — Nhìn hai file cạnh nhau

## 3.1 Bốn bài học `compare_rule.py` nên mượn từ `rule.py`

1. **Lỗi là dữ liệu, không phải chuỗi.** Thay `list[str]` bằng `list[ViPham]` có trường `ma`, `dong`, `ky_vong`, `thuc_te`. Xoá được cả ba cơ chế phân loại mức độ đang mâu thuẫn ở 1.2.
2. **Ghi công khai điều không kiểm được.** Sửa 1.4.5 và 1.8.1 — bỏ kiểm tra thì phải nói ra.
3. **Chú thích phải khớp code, hoặc đừng viết.** Ba chỗ nói ngược nhau (1.4.3, 1.6, 1.8.2) đều nằm ở `compare_rule.py`.
4. **Bộ kiểm phán, mô hình sửa.** Các thông điệp kiểu *"Hãy thay thế bằng các từ có thanh điệu đúng"* (128, 160) đi ngược nguyên tắc `rule.py` đặt ra. Gợi ý câu chữ là bộ kiểm đang viết thơ hộ.

## 3.2 Một bài học ngược chiều

`compare_rule.py` **có** `successes` — danh sách những chỗ đã đúng. `rule.py` có `bang_chung` nhưng ở mức tầng, không ở mức từng dòng/từng vị trí. Với vòng sửa LLM, "dòng 3 đã đạt chuẩn Bằng/Trắc, giữ nguyên" là thông tin đắt ngang "dòng 5 sai từ 4": nó khoanh vùng cái mô hình **không được** đụng vào.

## 3.3 Hạ tầng trùng lặp cần hợp nhất

Bốn phép toán được cài **hai lần** với hai thuật toán khác nhau:

| Việc | `compare_rule.py` | `rule.py` |
|---|---|---|
| Tách tiếng | `clean_and_tokenize` (ở `rhyme.py`, hiện không tìm thấy) | `tach_tieng` — xử lý dấu câu Unicode, gạch nối, chữ số |
| Phân thanh | `get_tone` → `"Bằng"/"Trắc"` | `thanh_cua` → `"B"/"T"` |
| Tách vần | ẩn trong `is_rhyme_match` | `van_cua` + `phan_tich_am_tiet` |
| Vần thông | ẩn, có `poem_type` | `CAP_VAN_THONG`, có nguồn sách được duyệt |

`rule.py` mạnh hơn rõ rệt ở cả bốn (đặc biệt: đếm tiếng có trừ dấu câu và quy chữ số về cách đọc). Nếu `compare_rule.py` được nối lại vào hệ thống, nó nên **gọi** hạ tầng của `rule.py` thay vì mang bản sao thứ hai — hai bộ đếm tiếng khác nhau nghĩa là hai bộ kiểm có thể phán khác nhau về cùng một dòng thơ, mà không ai truy được lệch từ đâu.

---

# PHẦN 4 — Bảng ưu tiên

| # | File | Vấn đề | Mức | Mục |
|---|---|---|---|---|
| 1 | `rule.py` | §5b chưa nối — `hiep_van` vẫn dùng `van_cua`, QĐ-3 chưa có hiệu lực, loại oan bài gieo vần qua âm đệm | 🔴 Cao | 2.1 |
| 2 | `rule.py` | `nghi_duong_luat` vĩnh viễn False; §8 và ghi chú tương ứng là mã chết | 🔴 Cao | 2.2 |
| 3 | `rule.py` | `doc_so` ném `IndexError` từ 10¹² — sập cả mẻ xử lý | 🟡 TB | 2.5 |
| 4 | `compare_rule.py` | Lệch pha lục/bát sau khổ lẻ dòng → hàng loạt lỗi giả | 🔴 Cao\* | 1.4.1 |
| 5 | `compare_rule.py` | Khổ tám chữ sai số tiếng không được chấm vần (hai nhánh cùng điều kiện) | 🔴 Cao\* | 1.8.1 |
| 6 | `compare_rule.py` | `elif` che lỗi Bằng/Trắc dòng bát | 🟡 TB\* | 1.4.2 |
| 7 | `compare_rule.py` | Ba chỗ chú thích nói ngược code | 🟡 TB\* | 1.4.3, 1.6, 1.8.2 |
| 8 | `rule.py` | `thuoc_the` gồm H4 nhưng ba docstring vẫn ghi H1–H3 | 🟡 TB | 2.3 |
| 9 | `rule.py` | Nhãn `?` bị tính là hiệp vần khi đo lệch thanh | 🟡 TB | 2.4 |
| 10 | `compare_rule.py` | Bắt buộc câu 1 gieo vần → loại oan thủ cú bất nhập vận | 🟡 TB\* | 1.5, 1.7 |
| 11 | `rule.py` | `_PHU_AM_DAU` và `_AM_DAU` trùng nội dung | 🟢 Thấp | 2.6 |
| 12 | `rule.py` | `HAM_KIEM_CUNG["H1"]` sai địa chỉ hàm | 🟢 Thấp | 2.7 |
| 13 | `compare_rule.py` | `import __main__`, import tương đối không dùng được, khối `__main__` chứa ngữ liệu | 🟢 Thấp\* | 1.1, 1.9 |

\* `compare_rule.py` hiện **không import được và không ai gọi**, nên mọi mục của nó là rủi ro *tiềm ẩn*. Nếu quyết định không nối lại vào hệ thống thì nên xoá file hoặc chuyển vào thư mục lưu trữ, thay vì để một bản sao logic luật thơ nằm ở gốc repo — người sau sẽ đọc nó và tưởng đó là luật đang chạy.
