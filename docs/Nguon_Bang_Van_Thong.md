# Hồ sơ nguồn bảng vần thông — trình duyệt theo QĐ-5

**Ngày:** 18/09/2026 · **Trạng thái:** ✅ **ĐÃ DUYỆT** — chủ dự án chốt *"lấy bản số hoá
của Trần Trọng Kim"*. Bảng đã nạp vào `src/application/rule.py` (`CAP_VAN_THONG`).

> **Ba chỗ suy diễn 🔶 ở §4 chưa được gật riêng.** Tôi đã thi hành cả ba theo hướng **không
> nới luật** (SD-1 có câu của tác giả chống lưng, SD-2 là ví dụ của chính tác giả, SD-3 là
> hướng chặt), và ghi rõ nhãn `🔶 SD-n` ngay tại chỗ trong mã. Bạn bác chỗ nào thì sửa chỗ
> đó, không ảnh hưởng phần lấy từ nguồn.

Tài liệu này phục vụ điều kiện nghiệm thu **H** của `Plan_Rule_Phan_Tang.md`:

> *"Bảng vần và từ điển tách từ có nguồn ghi rõ, không phải do tôi tự liệt kê."*

Mọi bảng dưới đây đều chép từ nguồn in được, có liên kết kiểm chứng. Chỗ nào là **suy diễn
của tôi** đều gắn nhãn 🔶 và cần bạn gật riêng.

---

## 1. Nguồn đã tra — nhận và loại

| # | Nguồn | Xuất xứ | Kết luận |
|---|---|---|---|
| **1** | **Trần Trọng Kim — *Việt thi*, mục I-5 "Vần chính", I-6 "Vần thông"** | Sách in, bản số hoá trên Wikisource tiếng Việt, đã hiệu đính (`Trang:Việt thi.pdf`) | ✅ **NHẬN — nguồn chính.** Có bảng đầy đủ, mỗi cặp vần kèm câu thơ dẫn chứng từ *Kiều*, *Cung oán*, *Chinh phụ ngâm*, *Quốc sử ca*. |
| **2** | **Bùi Kỷ (Ưu Thiên) — *Quốc văn cụ thể*, in lần 2, NXB Tân Việt, Sài Gòn 1950** | Bản quét trên Internet Archive (`quocvancuthe_2nd`) | ✅ **NHẬN — nguồn đối chiếu.** Nêu cùng nguyên tắc nhưng chỉ cho 4 ví dụ, **không có bảng**. Dùng để kiểm chéo, không dùng để lập bảng. |
| 3 | Dương Quảng Hàm — *Việt Nam văn học sử yếu* | Bản quét Internet Archive (`vietnamvanhocsuyeu`) | ❌ **KHÔNG DÙNG.** Đã tải toàn văn OCR (979 KB) và tra: **không có mục vần thông**. Sách là văn học sử, không phải sách luật thơ. Tôi đã đề cử nhầm ở lượt trước. |
| 4 | Mai Ngọc Chừ — *Vần thơ Việt Nam dưới ánh sáng ngôn ngữ học*, NXB Văn hoá Thông tin (tái bản 2006) | Xác nhận sách có thật; tác giả là GS.TS, ĐHKHXH&NV Hà Nội | ⚠️ **KHÔNG TIẾP CẬN ĐƯỢC.** Không có bản số hoá. Đây vẫn là nguồn tốt nhất về học thuật — nếu bạn có sách giấy, nó thay được nguồn 1. |
| 5 | "BẢNG THÔNG VẬN THƠ ĐƯỜNG LUẬT" trên violet.vn | Ghi *"Dũng Nguyên sưu tầm"* | ❌ **LOẠI.** Không có xuất xứ. Và bảng này **rộng hơn** Trần Trọng Kim (thêm `ây~ay`, `uâng`, `oai`, `oang`…) mà không nói lấy từ đâu. Nhận nó là nới luật bằng nguồn vô danh. |

### Về quyết định "lấy giao hai nguồn" của bạn

Bạn chốt: *"chỉ nhận cặp cả hai nguồn đều cho"*. **Tôi không thi hành được đúng như vậy**, và
phải nói thẳng lý do: **không tồn tại nguồn thứ hai có bảng** trong số tra được. Bùi Kỷ chỉ
cho 4 ví dụ. Lấy giao theo đúng chữ sẽ còn lại 3 cặp — bảng vô dụng.

Điều làm được và đã làm: **đối chiếu từng điểm Bùi Kỷ có nói với Trần Trọng Kim.**

| Bùi Kỷ, *Quốc văn cụ thể* (nguyên văn) | Quy về cặp vần | Trần Trọng Kim | Khớp? |
|---|---|---|---|
| *"Lành mành (vần chính) thông với lĩnh mình (vần thông)"* | `anh ~ inh` | "anh, ênh, inh thông với nhau" | ✅ |
| *"Lục cục thông với lộc cộc"* | `uc ~ ôc` | "o, ô, u thông được với nhau" | ✅ |
| *"Lã cả thông với lĩ cỡ"* | `a ~ ơ` | "a thông với ơ" | ✅ |
| *"Có tô … thông với có tô"* | — | — | ⬜ OCR hỏng, bỏ |

**3 điểm kiểm được, 3 khớp, 0 mâu thuẫn.** Hai tác giả cũng phát biểu cùng một nguyên tắc:
Trần Trọng Kim — *"cùng một giọng phát âm"*; Bùi Kỷ — *"đọc theo một giọng tương-tự"*.

Vì không có mâu thuẫn nào để hoà giải, tôi đề nghị đọc lại quyết định của bạn thành: **lấy
bảng Trần Trọng Kim, Bùi Kỷ giữ vai trò kiểm chéo; cặp nào hai nguồn mâu thuẫn thì loại.**
Hiện chưa có cặp nào bị loại theo tiêu chí đó. Cần bạn gật.

---

## 2. Phát hiện quyết định: bảng gốc KHÔNG bắc cầu — và tác giả nói thẳng điều đó

Đây là điểm quan trọng nhất của cả hồ sơ.

Trần Trọng Kim viết nguyên văn:

> **ang** thông với **ương** *(không thông được với **uông** vì **a** không thông được với **ô**)*

nhưng cũng viết, chỉ vài dòng dưới:

> **uông** thông với **ương**

Tức là `ang ~ ương` và `uông ~ ương`, **nhưng `ang ≁ uông`** — và chính tác giả mở ngoặc giải
thích tại sao. Đây không phải lỗi sách, mà là bản chất của hiện tượng.

Tôi đã dựng đồ thị từ toàn bộ bảng và đếm bằng máy:

```
Số vần trong bảng : 55
Số cặp hiệp vần   : 73
Vi phạm bắc cầu   : 16 bộ ba  (a~b, b~c, nhưng a≁c)
```

Vài bộ ba tiêu biểu:

| | | |
|---|---|---|
| `a ~ ơ ~ ư` | nhưng | `a ≁ ư` |
| `ang ~ ương ~ uông` | nhưng | `ang ≁ uông` ← tác giả ghi rõ |
| `ay ~ ai ~ oi` | nhưng | `ay ≁ oi` |
| `un ~ on ~ uôn` | nhưng | `un ≁ uôn` |
| `uân ~ ăn ~ ân` | nhưng | `uân ≁ ân` |
| `au ~ ao ~ iêu` | nhưng | `au ≁ iêu` |

**Hệ quả trực tiếp:** nếu ép bảng này thành các **lớp tương đương rời nhau** — đúng cấu trúc
`VAN_THONG` tôi đang dùng trong `rule.py` — thì 55 vần gộp thành 16 lớp, lớp lớn nhất gồm 8
vần (`ao, au, eo, iu, iêu, yêu, êu, ưu`), và:

> ### ⛔ Ép phân hoạch sẽ **bịa thêm 16 cặp hiệp vần** mà Trần Trọng Kim **không cho**.

Bịa thêm 16 cặp là **nới luật** — đúng thứ N1 cấm, và đúng thứ bạn đã cấm tôi hai lần. Vậy
**mô hình đồ thị bạn chọn là bắt buộc về mặt kỹ thuật, không phải một lựa chọn phong cách.**
Test `test_cac_lop_van_thong_phai_ROI_NHAU` tôi viết hôm qua phải bị gỡ, vì nó ép đúng cái
cấu trúc sai này.

---

## 3. Bảng vần thông — nguyên văn Trần Trọng Kim

Chép đúng thứ tự và cách liệt kê của tác giả. Cột cuối là câu thơ tác giả dẫn làm chứng.

### 3.1. Nguyên tắc gốc (trên âm chính)

> *"Khi một âm phát ra là do sự vận-động của môi và lưỡi. Hai âm theo một sự vận-động ấy gần
> như nhau, tất là hơi tương-tự nhau, như **a** với **ơ** đều cùng một sự vận-động của môi và
> lưỡi, thì **a** có thể thông với **ơ**."*

| Nhóm âm chính | Nguyên văn |
|---|---|
| `a, ơ` | "thông được với nhau" |
| `ơ, ư` | "thông được với nhau" |
| `e, ê, i` | "thông được với nhau" |
| `o, ô, u` | "thông được với nhau" |

Lưu ý `a ~ ơ` và `ơ ~ ư` là **hai phát biểu rời**, không phải một nhóm ba. Suy ra `a ≁ ư`.

### 3.2. Vần bằng — âm cuối là nguyên âm / bán nguyên âm

| Cặp / nhóm | Dẫn chứng của tác giả |
|---|---|
| `a ~ ơ` | *"Thâm khuê vắng ngắt như **tờ** / Cửa châu gió lọt, rèm **ngà** sương gieo"* (Cung oán) |
| `ơ ~ ư` | *"Diện tiền trình với tiểu-**thư** / Thoạt trông dường có ngẩn-**ngơ** chút tình"* (Kiều) |
| `e, ê, i` | *"Thấy lời đoan chính dễ **nghe** / Chàng càng thêm nể thêm **vì** mười phân"* |
| `o, ô, u` | *"Lầm-dầm khấn vái nhỏ **to** / Sụp ngồi đặt cỏ trước **mồ** bước ra"* |
| `ai ~ ay` | *"Vĩ lô sàn-sạt hơi **may** / Một trời thu để riêng **ai** một mình"* |
| `ai, oi, ôi, ơi, ươi, ui` | 10 cặp, mỗi cặp một dẫn chứng riêng: ai-oi, ai-ôi, ai-ơi, ai-ươi, ai-ui, oi-ôi, oi-ơi, ôi-ui, ơi-ui, ươi-ui |
| `ao ~ au` | *"Người lên ngựa, kẻ chia **bào** / Rừng phong thu đã nhuộm…"* |
| `ao, eo, êu, iêu, yêu, iu, ưu` | ao-iêu, ao-iu, ao-ưu, eo-iêu, êu-yêu, iu-iêu, ưu-iêu |

⚠️ **`ay` KHÔNG thuộc nhóm `ai, oi, ôi…`** — chỉ thông với `ai`. Tác giả tách riêng.

### 3.3. Vần bằng — âm cuối là phụ âm

| Cặp / nhóm | Ghi chú của tác giả |
|---|---|
| `am ~ ơm` | |
| `ăm ~ âm` | |
| `êm ~ im` | |
| `an ~ ơn` | |
| `ăn ~ ân`, `ăn ~ uân` | hai phát biểu rời ⇒ `ân ≁ uân` |
| `en, in, iên, uyên` | |
| `on, ôn, uôn` | |
| `on ~ un` | phát biểu rời ⇒ `un ≁ ôn`, `un ≁ uôn` |
| `ang ~ ương` | ***"(không thông được với uông vì a không thông được với ô)"*** |
| `ăng, âng, ưng` | |
| `ong, ông, ung` | |
| `uông ~ ương` | |
| `anh, ênh, inh` | |

### 3.4. Vần trắc

Tác giả nói rõ đây chỉ là **mẫu**, không phải bảng đủ:

> *"Những vần thông của vần trắc **cũng theo một nguyên-tắc như** những vần thông của vần
> bằng. Sau này trích mấy câu ở trong Cung-oán ra để **làm mẫu**."*

| Dẫn chứng | Quy về vần |
|---|---|
| `é ~ ị` | `e ~ i` |
| `ổ ~ ũ` | `ô ~ u` |
| `ọ ~ ủa` | `o ~ ua` |
| `ĩa ~ uệ` | `ia ~ uê` |
| `áo ~ iễu` | `ao ~ iêu` |
| `ói ~ ủi` | `oi ~ ui` |
| `ác ~ ước` | `ac ~ ươc` |
| `ấc ~ ực` | `âc ~ ưc` |
| `ạm ~ ợm` | `am ~ ơm` |
| `ặn ~ ẩn` | `ăn ~ ân` |
| `óng ~ úng` | `ong ~ ung` |
| `ật ~ ắt` | `ât ~ ăt` |
| `ật ~ ứt` | `ât ~ ưt` |
| `út ~ uốt` | `ut ~ uôt` |

---

## 4. 🔶 Ba chỗ tôi phải suy diễn — cần bạn gật từng chỗ

### 🔶 SD-1. Quan hệ hiệp vần độc lập với thanh điệu

Bảng chia bằng/trắc, nhưng mọi cặp vần trắc khi bỏ thanh đều **trùng** một quy tắc đã có ở
phần vần bằng (xem cột phải §3.4). Và tác giả nói thẳng *"cũng theo một nguyên-tắc như"*.

Thêm một lý do thuộc ngữ âm: tiếng Việt **không có** âm tiết thanh bằng kết thúc bằng
`-c/-ch/-p/-t`. Nên phần bằng không thể chứa `ac, ưc, ât…` — hai danh sách **bù nhau**, không
mâu thuẫn nhau.

**Đề nghị:** `hiep_van(a, b)` so trên **vần** (âm đệm + âm chính + âm cuối), **không xét thanh**.
Thanh vẫn được ghi vào bằng chứng (`dong_thanh`) để tầng khác dùng.

### 🔶 SD-2. Danh sách vần trắc là mẫu, nên lấy quy tắc chứ không lấy liệt kê

Nếu SD-1 được duyệt thì §3.4 không thêm gì mới ngoài bốn cặp: `o~ua`, `ia~uê`, `ac~ươc`,
`ât~ưt`. Tôi đề nghị **nhận cả bốn** — chúng là mẫu tác giả đưa, không phải tôi suy ra.

### 🔶 SD-3. Vần có âm đệm (`oa, oe, uê, uy, uân…`)

Bảng gần như không nhắc, trừ `uân`, `uyên`, `uông`, `uôn`, `uê`. Trang violet.vn có thêm
`oa, oai, oang, uy…` nhưng **vô danh nên đã loại**.

**Đề nghị:** vần có âm đệm mà bảng không nhắc thì **chỉ hiệp vần chính** (trùng vần y hệt),
không suy rộng. Đây là hướng **chặt**, không nới.

---

## 5. Bảng tôi tự bịa sai ở đâu — đối chiếu

| Cặp | Bảng tôi bịa | Trần Trọng Kim | |
|---|---|---|---|
| `ao ~ au` | thiếu | **có** | tôi thiếu, đã đoán đúng |
| `âm ~ ăm` | thiếu | **có** | tôi thiếu, đã đoán đúng |
| `ươi ~ ơi` | thiếu | **có** | tôi thiếu, đã đoán đúng |
| `ây ~ ay` | thiếu | **KHÔNG CÓ** | ❌ tôi đã đoán sai ở lượt trước |
| `e ~ a` | **có** | **KHÔNG CÓ** | ❌ tôi bịa ra, phải bỏ |

Chỗ `ây ~ ay`: lượt trước tôi nói bảng của tôi "thiếu `ây~ay`". Sai. Cặp đó chỉ có trong bảng
vô danh trên violet.vn; Trần Trọng Kim không cho.

---

## 6. Việc sẽ làm sau khi bạn duyệt

1. Gỡ `test_cac_lop_van_thong_phai_ROI_NHAU` — nó ép cấu trúc sai (§2)
2. Thay `VAN_THONG` (lớp rời nhau) bằng `CAP_VAN_THONG` — 73 cạnh, mỗi cạnh ghi nguồn
3. Viết lại `hiep_van()` thành tra cạnh; bỏ `lop_van()` / `_MA_LOP_VAN`
4. Viết lại `suy_so_do_van()` thành **đối chiếu với sơ đồ ứng viên** ở §5.2 tài liệu luật
5. Test: 16 bộ ba vi phạm bắc cầu phải cho ra đúng kết quả không bắc cầu
6. Đo lại phân bố sơ đồ vần trên corpus, cập nhật báo cáo

**Trạng thái thi công (18/09/2026): đã làm xong mục 1–5.** Mục 6 chờ QĐ-7.
Số đo sau khi nạp: **73 cạnh từ nguồn + 4 cạnh 🔶 SD-2 = 77 cạnh, 62 vần.**

---

## 7. Liên kết kiểm chứng

- Trần Trọng Kim, *Việt thi*, I-5 Vần chính — https://vi.wikisource.org/wiki/Vi%E1%BB%87t_thi/I-5
- Trần Trọng Kim, *Việt thi*, I-6 Vần thông — https://vi.wikisource.org/wiki/Vi%E1%BB%87t_thi/I-6
- Bùi Kỷ, *Quốc văn cụ thể*, Tân Việt 1950 — https://archive.org/details/quocvancuthe_2nd
- Dương Quảng Hàm, *Việt Nam văn học sử yếu* (đã tra, không có mục vần thông) — https://archive.org/details/vietnamvanhocsuyeu
