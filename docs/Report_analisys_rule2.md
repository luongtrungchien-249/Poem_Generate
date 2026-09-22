# Report — Đối chiếu `bai_dat.jsonl` qua `compare_rule.py`

**Ngày:** 22/09/2026
**Đầu vào:** `datalake/analysis/bai_dat.jsonl` — 24.366 bài đã ĐẠT cả bảy tầng của `rule.py`
**Bộ luật đối chiếu:** `compare_rule.py` — **logic gốc, chỉ bù phần lõi còn thiếu**
**Script:** `datalake/scripts/chay_doi_chieu_rule2.py`
**Đầu ra:** `bai_dat_rule2.jsonl` (3.146 dòng) · `bai_truot_rule2.jsonl` (21.220 dòng) · `tong_hop_rule2.json`

> **`rule.py` không bị động tới.** Băm kiểm trước và sau:
> `0a0b2488f2ab10562b8a42a78f7550189664d69c05031f83c4aa4702f1321975` — khớp `BAM_DA_CHOT`.
> `pytest tests/architecture` xanh 375/375.

---

## 1. Lượt sửa `compare_rule.py` đã làm gì — và cố ý KHÔNG làm gì

`compare_rule.py` trước đây **không import nổi**: `import __main__` thừa, và hai import
tương đối `from .constants` / `from .rhyme` trỏ tới một gói **chưa bao giờ tồn tại** trong
repo. Không chạy được thì không đối chiếu được.

**Đã bù — đúng sáu cái mà thân bài cần và chưa bao giờ có** (§0 của file):

| Tên | Vốn ở | Nay |
| --- | --- | --- |
| `CRITICAL_ERROR_KEYWORDS` | `.constants` | bảng từ khoá tra chuỗi `"CRITICAL!"` |
| `clean_and_tokenize` | `.rhyme` | tách tiếng: loại dấu câu theo phân loại Unicode, gạch nối tách tiếp, chữ số quy về cách đọc |
| `get_tone` | `.rhyme` | Bằng = ngang/huyền; Trắc = sắc/hỏi/ngã/nặng |
| `get_bang_type` | `.rhyme` | phân biệt ngang ↔ huyền cho luật điệp thanh câu Bát |
| `is_rhyme_match` | `.rhyme` | vần chính + vần thông (bảng Trần Trọng Kim, "Việt thi" I-6) |
| `get_suggested_endings` | `.rhyme` | gợi ý phần vần, lấy từ chính bảng trên |

**CỐ Ý KHÔNG ĐỔI — logic luật nguyên văn.** Toàn bộ phần từ `evaluate_errors` trở xuống
được chép y nguyên từ `git show HEAD:compare_rule.py`. Đã đối chiếu bằng SHA-256:

```
sha256(thân bài trong file mới) == sha256(thân bài từ git)   →   TRÙNG KHÍT
```

Nghĩa là **mọi khiếm khuyết thiết kế đã ghi ở `docs/Report_Phan_Tich_Ma_Kiem_Luat.md` vẫn
còn nguyên**: cắt bài 8 dòng thành hai khổ tứ tuyệt, bắt buộc câu 1 gieo vần, `elif` nuốt
lỗi ở dòng bát, hai nhánh cùng điều kiện ở thơ tám chữ. Đó là chủ ý — hồ sơ đối chiếu phải
phản ánh đúng bộ luật thế hệ trước, không phải bản đã được sửa hộ.

> ⚠️ **HẾT HIỆU LỰC TỪ 22/09/2026 — bản sửa "nới luật Bằng/Trắc thất ngôn".**
> Theo yêu cầu chủ dự án, `bay_chu_rule_check` và `bay_chu_bat_cu_rule_check` nay **chỉ
> chấm Bằng/Trắc ở câu đầu**; bảng 4 dòng và bảng 8 dòng base/opposite đã bỏ. Chi tiết ở
> §1.1 đầu `compare_rule.py`.
>
> Hệ quả với report này:
> - Khẳng định SHA-256 trùng khít ở trên **không còn đúng** cho hai khối đó. Phần còn lại
>   của thân bài vẫn nguyên văn.
> - Trong danh sách khiếm khuyết ngay trên, mục *"cắt bài 8 dòng thành hai khổ tứ tuyệt"*
>   đã mất phần lớn tác hại: hai khổ không còn bị suy lại luật Bằng/Trắc độc lập (khối
>   gieo vần thì vẫn chia theo khổ 4 câu như cũ). Ba mục còn lại vẫn nguyên.
> - **Mọi số liệu về thơ 7 chữ trong report này thuộc về bộ luật TRƯỚC khi nới.** Muốn có
>   con số khớp hành vi hiện tại thì phải chạy lại `datalake/scripts/chay_doi_chieu_rule2.py`.

Tầng ngữ âm ở §0 là cài đặt **độc lập**, không import từ `rule.py`: một ý kiến thứ hai mà
dùng lại ngữ âm của bộ kiểm đang sống thì không còn là ý kiến thứ hai.

---

## 2. Hai tầng ngữ âm có nói cùng một thứ tiếng không?

Vì §0 độc lập, chênh lệch có thể đến từ **hai** nguồn: khác *luật*, hay khác cách đọc *âm
tiết*. Không tách hai nguồn ấy thì mọi con số ở §3 đều không diễn giải được. Đã đo trên
mẫu ngẫu nhiên (seed cố định, tái lập được):

| Phép | Khớp | Tỷ lệ |
| --- | ---: | ---: |
| Tách tiếng (đếm âm tiết) | 4.000 / 4.000 | **100,00 %** |
| Phân thanh Bằng/Trắc | 28.000 / 28.000 | **100,00 %** |
| So vần | 3.939 / 4.000 | **98,47 %** |

Hai cài đặt **độc lập** mà thống nhất tuyệt đối ở đếm tiếng và phân thanh. Vậy toàn bộ
chênh lệch phán quyết ở §3 là **do luật**, không do ngữ âm.

**1,53 % lệch ở phép so vần đáng chú ý riêng.** `compare_rule.py` §0 so vần bằng **âm
chính + âm cuối** (bỏ âm đệm), nên `hoa` ~ `ta`, `hoa` ~ `nhà`. `rule.py` vẫn so bằng
`van_cua` (cắt phụ âm đầu), nên hai tiếng ấy **không** hiệp. Đây chính là QĐ-3 đã viết
trong `rule.py` §5b nhưng **chưa được nối vào** — xem `docs/Plan_Cai_Thien_Rule.md` §7.
Báo cáo này là bằng chứng thực nghiệm rằng phép so theo ngữ âm chạy được trên toàn corpus
và cho kết quả khác ở khoảng 1,5 % số cặp.

---

## 3. Kết quả

| Phép chấm | Đạt | Trượt | % đạt | % trượt |
| --- | ---: | ---: | ---: | ---: |
| **`bay_chu_rule_check`** (thất ngôn Đường luật, cắt theo khổ 4 câu) | **3.146** | **21.220** | **12,91 %** | **87,09 %** |
| `bay_chu_modern_rule_check` (7 chữ hiện đại) | 24.366 | 0 | 100,00 % | 0,00 % |

Hai con số nói hai chuyện khác nhau, và **không con nào là "rule.py sai"**:

- **100 %** ở hàng dưới là điều phải xảy ra. `bay_chu_modern_rule_check` chỉ kiểm số dòng
  và "mỗi dòng đúng 7 tiếng" — đúng bằng tầng 1 và tầng 2 của `rule.py`. Đây là **phép
  kiểm tính nhất quán**, và nó xanh.
- **12,91 %** ở hàng trên đo một thứ khác: *bao nhiêu bài thất ngôn tự do cũng thoả luật
  Đường theo cách đọc tứ tuyệt*.

### 3.1. Phân bố số lỗi mỗi bài

| Số lỗi | 0 | 1 | 2 | 3 | 4 | 5 | 6–10 | ≥11 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Số bài | 3.146 | 4.352 | 9.694 | 2.565 | 1.722 | 770 | 1.720 | 397 |

**45,7 % số bài trượt mang đúng 2 lỗi** — con số bất thường ấy là manh mối dẫn tới §5.

### 3.2. Lý do trượt (đếm theo lượt lỗi)

| Lượt | Nhóm |
| ---: | --- |
| 30.170 | `[Sai Vần]` — vần chân câu 1/2/4 trong khổ |
| 24.049 | `[Lỗi Gieo Vần]` — tiếng cuối không mang thanh Bằng |
| 6.959 | `Vi phạm Bằng/Trắc` — P2/P4/P6 sai khuôn |

**Không một lỗi số tiếng, không một lỗi số dòng.** Hai bộ luật thống nhất tuyệt đối ở hai
ràng buộc cứng — đúng như §2 đã dự đoán.

### 3.3. Theo số dòng — chỗ bất thường lộ ra

| Số dòng | Đạt | Trượt | % đạt |
| ---: | ---: | ---: | ---: |
| 4 | 1.983 | 1.920 | **50,8 %** |
| **8** | **238** | **12.892** | **1,8 %** |
| 12 | 192 | 744 | 20,5 % |
| 16 | 288 | 2.528 | 10,2 % |
| 20 | 129 | 712 | 15,3 % |
| 24 | 108 | 473 | 18,6 % |
| 28 | 142 | 794 | 15,2 % |
| 32 | 34 | 248 | 12,1 % |

Bài **4 dòng đạt 50,8 %**, bài **8 dòng chỉ đạt 1,8 %** — chênh **28 lần** giữa hai độ dài
của cùng một thể. Một bộ luật lành mạnh không thể chênh như vậy. §5 giải thích.

---

## 4. Ba bài ĐẠT — bằng chứng chi tiết

### 4.1. ID 2881 — 8 dòng, 0 lỗi

```
D1: Ai nắn thân em khéo trĩnh tròn,      P2P4P6=T-B-T [trắc]  P7=tròn(B)  vần=on
D2: Làn da trắng mịn, ruột như son.      P2P4P6=B-T-B [bằng]  P7=son (B)  vần=on
D3: Ngọt thơm thỏa dạ người quân tử,     P2P4P6=B-T-B [bằng]  P7=tử  (T)  vần=ư
D4: Duyên nợ mặn nồng với nước non.      P2P4P6=T-B-T [trắc]  P7=non (B)  vần=on
D5: Thân em vừa trắng lại vừa tròn,      P2P4P6=B-T-B [bằng]  P7=tròn(B)  vần=on
D6: Bảy nổi ba chìm với nước non.        P2P4P6=T-B-T [trắc]  P7=non (B)  vần=on
D7: Rắn nát mặc dầu tay kẻ nặn,          P2P4P6=T-B-T [trắc]  P7=nặn (T)  vần=ăn
D8: Mà em vẫn giữ một lòng son.          P2P4P6=B-T-B [bằng]  P7=son (B)  vần=on
```

Bằng chứng bộ kiểm tự nộp:

```
+ Cấu trúc: 8 dòng (chia thành 2 khổ 4 câu).
+ Số tiếng: Tất cả các dòng đều đạt chuẩn 7 tiếng.
+ [Khổ 1] Xác định được Luật Trắc (do từ 2 câu 1 là thanh Trắc).
+ [Dòng 1] Niêm luật chuẩn xác (2 Trắc - 4 Bằng - 6 Trắc).
```

**Vì sao đạt — và vì sao nó hiếm.** Bộ luật cắt bài thành hai khổ rời, đòi **mỗi khổ tự đủ
vần 1-2-4**. Bài này thoả được vì nó độc vận `-on` xuyên suốt: khổ 1 có `tròn–son–non`,
khổ 2 có `tròn–non–son`. Dòng 3 (`tử`) và dòng 7 (`nặn`) buông vần, mang thanh Trắc — đúng
vị trí câu 3 của mỗi khổ. Khuôn Luật Trắc khớp cả tám dòng.

Chỉ **238/13.130** bài 8 dòng làm được điều này. Xem §5.

### 4.2. ID 3209 — 4 dòng, 0 lỗi

```
D1: Bấy lâu sát ngõ chẳng ngăn tường,    P2P4P6=B-T-B [bằng]  P7=tường(B)  vần=ương
D2: Không dám sờ tay sợ lấm hương.       P2P4P6=T-B-T [trắc]  P7=hương(B)  vần=ương
D3: Xiêm áo đêm nay tề chỉnh quá,        P2P4P6=T-B-T [trắc]  P7=quá  (T)  vần=a
D4: Muốn ôm hồn cúc ở trong sương.       P2P4P6=B-T-B [bằng]  P7=sương(B)  vần=ương
```

**Vì sao đạt:** P2 câu 1 là `lâu` (Bằng) → **Luật Bằng**, khuôn đòi câu 1 và 4 là `B-T-B`,
câu 2 và 3 là `T-B-T` — khớp cả bốn. Vần chính `-ương` ở dòng 1, 2, 4, cả ba thanh Bằng.
Dòng 3 kết `quá` (Trắc), buông vần.

### 4.3. ID 3274 — "Viết sau khi hoàn thành *Từ điển Truyện Kiều*", 4 dòng, 0 lỗi

```
D1: Ông hỏi đời sau ai khóc mình,        P2P4P6=T-B-T [trắc]  P7=mình(B)  vần=inh
D2: Mà nay bốn biển lại lừng danh.       P2P4P6=B-T-B [bằng]  P7=danh(B)  vần=anh
D3: Cho hay mọi cái đều mây nổi,         P2P4P6=B-T-B [bằng]  P7=nổi (T)  vần=ôi
D4: Còn với non sông một chữ tình.       P2P4P6=T-B-T [trắc]  P7=tình(B)  vần=inh
```

**Vì sao đạt:** P2 câu 1 là `hỏi` (Trắc) → **Luật Trắc**, khuôn đảo so với 4.2, khớp cả
bốn. Vần `mình` (inh) – `danh` (anh) – `tình` (inh) là **vần thông**, không phải vần
chính: nhóm `(anh, ênh, inh)` của Trần Trọng Kim. Bảng vần ở §0 là thứ cho phép nhận ra nó
— nếu chỉ so vần chính thì bài này đã trượt oan.

---

## 5. Ba bài TRƯỢT — và nguyên nhân thật của 87,09 %

Cả ba ví dụ dưới đây đều mang **đúng 2 lỗi**, và ở cả ba, **cả hai lỗi đều phát sinh từ
dòng 5**.

### 5.1. ID 1 — "BÂNG KHUÂNG", 8 dòng, 2 lỗi

```
D1: Đã biết không nên nhớ một người,     P7=người(B) vần=ươi   ← vần
D2: Mà còn khắc khoải đến không nguôi.   P7=nguôi(B) vần=uôi   ← vần
D3: Đầu mai bóng mải bên sườn núi,       P7=núi  (T) vần=ui
D4: Cuối buổi hình xa ở mạn đồi.         P7=đồi  (B) vần=ôi    ← vần
D5: Mấy bận đi qua lòng định gọi,        P7=gọi  (T) vần=oi    ← bị đòi vần Bằng
D6: Đôi lần đứng lại dạ dừng thôi.       P7=thôi (B) vần=ôi    ← vần
D7: Nhìn theo một quãng rồi hai lối,     P7=lối  (T) vần=ôi
D8: Để cứ bâng khuâng hận nửa đời.       P7=đời  (B) vần=ơi    ← vần
```

```
[Sai Vần] [CRITICAL!] Khổ 1: Từ cuối Dòng 1 ('người') chưa vần với Dòng 2 ('nguôi').
          Gợi ý: -uôi | Từ cuối Dòng 4 ('đồi') chưa vần với Dòng 2 ('nguôi'). Gợi ý: -uôi
[Lỗi Gieo Vần Khổ 2] Dòng 5 ('gọi' - Trắc) sai thanh điệu.
          Từ cuối các câu 1, 2 và 4 bắt buộc phải là vần Bằng.
```

**Đọc cho đúng.** Bài này gieo vần ở **dòng 1, 2, 4, 6, 8** — `người / nguôi / đồi / thôi
/ đời`. Đó là sơ đồ vần của **thất ngôn bát cú**, và nó đúng luật: dòng 3, 5, 7 buông vần,
kết thanh Trắc. Khuôn thanh khớp trọn tám dòng.

Hai lỗi trên đều là **hệ quả của một khiếm khuyết duy nhất**: `bay_chu_rule_check` xử lý
bài theo **từng cụm 4 dòng rời** (`for i in range(0, n, 4)`), nên nó coi dòng 5 là "câu 1
của khổ 2" và đòi dòng ấy mang vần Bằng. Bát cú không hề đòi thế.

Lỗi thứ nhất có nguyên nhân khác, và nó **thật**: `nguôi` (uôi) không nằm trong nhóm
`(ai, oi, ôi, ơi, ươi, ui)` của bảng — **bảng vần thông không có mục `uôi`**. Bốn tiếng
còn lại hiệp nhau bình thường. Tôi **không thêm `uôi` vào bảng** vì làm vậy là nắn luật cho
vừa dữ liệu — nguyên tắc N1 của dự án cấm điều đó. Ghi lại để bạn quyết.

### 5.2. ID 3 — "QUÊ HƯƠNG", 8 dòng, 2 lỗi

```
D1: Đã bấy lâu nay cứ miệt mài,          P7=mài (B)  vần=ai   ← vần
D2: Trong vòng luẩn quẩn kiếm sinh nhai. P7=nhai(B)  vần=ai   ← vần
D3: Về bên giếng nước rêu phong kín,     P7=kín (T)  vần=in
D4: Nép dưới hàng cau nắng đổ dài.       P7=dài (B)  vần=ai   ← vần
D5: Nhớ mãi đầu cha phơ mái tóc,         P7=tóc (T)  vần=oc   ← bị đòi vần Bằng
D6: Thương hoài áo mẹ bạc màu vai.       P7=vai (B)  vần=ai   ← vần
D7: Nhìn theo lối cũ vàng hoa cải,       P7=cải (T)  vần=ai
D8: Thấy chậm bàn chân nặng gót hài.     P7=hài (B)  vần=ai   ← vần
```

Độc vận `-ai` trọn năm vị trí 1-2-4-6-8, khuôn thanh khớp cả tám dòng — **bát cú hoàn
chỉnh, không một chỗ hỏng**. Trượt chỉ vì dòng 5 (`tóc`, Trắc) không chịu làm "câu 1 của
khổ 2".

### 5.3. ID 4 — "VUA VỌNG CỔ", 8 dòng, 2 lỗi

```
D1: Kính cẩn nghiêng mình biệt viễn châu, P7=châu(B)  vần=âu  ← vần
D2: Ông vua Vọng cổ đã về chầu.           P7=chầu(B)  vần=âu  ← vần
D3: Thiên đường viết tiếp làn tân cổ,     P7=cổ  (T)  vần=ô
D4: Thượng giới đàn hoài điệu sáu câu.    P7=câu (B)  vần=âu  ← vần
D5: Thập lục huyền cầm ngân nức nở,       P7=nở  (T)  vần=ơ   ← bị đòi vần Bằng
D6: Tình anh bán chiếu trỗi thương sầu.   P7=sầu (B)  vần=âu  ← vần
D7: Màn nhung hé mở người không thấy,     P7=thấy(T)  vần=ây
D8: Bảy bá ôm cầm khảy tận đâu.           P7=đâu (B)  vần=âu  ← vần
```

Độc vận `-âu`, năm vị trí, cùng một nguyên nhân trượt.

### 5.4. Đo giả thuyết trên toàn tập

Nếu ba ca trên là bát cú bị chấm nhầm bằng luật tứ tuyệt, hiện tượng ấy phải để lại dấu
vết ở quy mô lớn. Bảng §3.3 chính là dấu vết đó:

- bài **4 dòng** — cách cắt theo cụm 4 **không gây hại**, vì bài vốn là một khổ → **50,8 %** đạt;
- bài **8 dòng** — cách cắt phá đúng sơ đồ bát cú → **1,8 %** đạt;
- **13.130 bài 8 dòng**, chỉ **238** đạt.

Bài 8 dòng chiếm hơn nửa corpus đầu vào, nên riêng khiếm khuyết này kéo tỷ lệ chung xuống
gần **một nửa** con số lẽ ra phải có.

---

## 6. Kết luận

**1. Con số phải báo cáo: 12,91 % đạt / 87,09 % trượt** (3.146 / 21.220 trên 24.366 bài) —
kết quả chạy thật của `bay_chu_rule_check` với **logic gốc nguyên vẹn**.

**2. 87,09 % ấy phần lớn không đo cái nó trông như đang đo.** Nguyên nhân chính là khiếm
khuyết đã biết của bộ luật cũ: chỉ chia bài theo cụm 4 dòng, nên bài bát cú vần 1-2-4-6-8
bị đòi hai bộ vần độc lập. Bằng chứng định lượng: 4 dòng đạt 50,8 % còn 8 dòng đạt 1,8 %.

**3. Phép đối chiếu không phát hiện lỗi nào của `rule.py`.**
- Không một bài nào lệch về số tiếng hay số dòng — hai bộ luật, hai cài đặt ngữ âm **độc
  lập**, vẫn khớp **100 %** ở đếm tiếng và phân thanh.
- `bay_chu_modern_rule_check` đạt 100 %, xác nhận tầng 1 và tầng 2 của `rule.py` chặt đúng
  như công bố.
- Chênh lệch còn lại nằm ở chỗ `compare_rule.py` áp **niêm và độc vận Đường luật** — đúng
  hai thứ mà F1 và F3 đã **gỡ bỏ khỏi thể** thất ngôn tự do.

**4. Phát hiện đáng hành động duy nhất nằm ở §2:** hai phép so vần lệch 1,53 %, vì §0 so
theo âm chính + âm cuối còn `rule.py` vẫn dùng `van_cua`. Đây là QĐ-3 chưa được nối vào —
`docs/Plan_Cai_Thien_Rule.md` §7.

**5. Câu hỏi để lại:** bảng vần thông không có mục `uôi`, nên `nguôi` không hiệp với `thôi`
/ `đồi` (§5.1). Không tự thêm vì N1 cấm nắn luật cho vừa dữ liệu; muốn bổ sung thì phải có
căn cứ nguồn, theo thủ tục QĐ-5.

**6. Nếu muốn biết bộ luật cũ *lẽ ra* chấm được bao nhiêu** khi các khiếm khuyết thiết kế
được sửa, con số đo được ở một lượt thử riêng là **65,60 %** (so với 12,91 % hiện tại).
Lượt thử ấy **không** được giữ lại trong `compare_rule.py`, theo đúng yêu cầu giữ nguyên
logic gốc.

---

## 7. Tệp đã sinh

| Tệp | Dòng | Nội dung |
| --- | ---: | --- |
| `datalake/analysis/bai_dat_rule2.jsonl` | 3.146 | bài đạt cả `rule.py` lẫn `bay_chu_rule_check` |
| `datalake/analysis/bai_truot_rule2.jsonl` | 21.220 | bài đạt `rule.py` nhưng trượt luật Đường, kèm lỗi |
| `datalake/analysis/tong_hop_rule2.json` | — | thống kê, đồng thuận ngữ âm, 8 ví dụ mỗi phía |
| `compare_rule.py` | — | logic gốc + §0 phần lõi bù thêm |
| `datalake/scripts/chay_doi_chieu_rule2.py` | — | script tái lập |

Mỗi bản ghi mang: `id`, `tieu_de`, `tho`, `so_dong`, `rule1_dat`, `rule2_dat`,
`rule2_cach_doc`, `rule2_modern_dat`, `rule2_so_loi`, `rule2_loi_nang`, `rule2_loi_nhe`,
`rule2_loi`, `rule2_dat_chuan`, `rule2_modern_loi`.
