# BÁO CÁO PHÂN TÍCH CORPUS — BÀI ĐẠT / BÀI KHÔNG ĐẠT LUẬT

**Tệp phân tích:** `datalake/dataraw/final_data_7_chu.jsonl`
**Ngày:** 17/09/2026
**Bộ luật áp dụng:** `src/application/rule.py` (bản thi hành được của `docs/Luat_Tho_That_Ngon_Tu_Do.md`)

---

> ## ⚠️ SỐ LIỆU TRONG BÁO CÁO NÀY ĐÃ CŨ — đo lại ngày 18/09/2026
>
> Hai thay đổi sau lần đo 17/09 làm đổi kết quả, và báo cáo này **chưa được viết lại**:
>
> 1. **QĐ-5** — bảng vần thông thay bằng bảng có nguồn (Trần Trọng Kim, *Việt thi* I-6).
>    Bảng cũ là do tôi tự liệt kê.
> 2. **QĐ-7** — tầng 5 bắt đầu **chặn thật**: bài phải có ít nhất một cụm 4 dòng liên tiếp
>    khớp một trong bốn sơ đồ §5.2. Trước đó tầng 5 cho qua tất cả.
>
> **Phễu mới, đo lại từ đầu trên toàn bộ 67.150 bản ghi (18/09/2026):**
>
> | Cổng | Vào | Qua | Chặn tại đây |
> |---|---:|---:|---:|
> | 1. Hình thức (H3) | 62.034 | 62.032 | 2 |
> | 2. Độ dài dòng (H1, H2) | 62.032 | 59.437 | 2.595 |
> | 3. Loại trừ Đường luật (F1–F5) | 59.437 | 55.149 | 4.288 |
> | 4. Thanh luật (S1–S5) | 55.149 | 21.374 | 33.775 |
> | **5. Vần (S6–S12)** | 21.374 | **16.391** | **4.983** ← QĐ-7 |
> | 6. Nhịp (S13–S15) | 16.391 | 16.391 | 0 |
> | 7. Khổ và bố cục (S16–S21) | 16.391 | 16.391 | 0 |
>
> - Thuộc thể theo **tài liệu** (chỉ H1–H3): **59.437**
> - Đạt theo **chuẩn dự án** (cả 7 tầng): **16.391** — 26,42% trên 62.034 bài có nội dung
> - Không có nội dung: 5.116 · Đối soát: `67.150 dòng = 67.150 bản ghi = 67.150 id duy nhất` ✅
>
> **Cổng 6 chặn 0 bài, và đó KHÔNG phải vì thơ đạt nhịp.** Chưa có bộ tách từ tiếng Việt nên
> mọi dòng 7 tiếng đều "cắt được" theo cả bảy kiểu nhịp — phép kiểm rỗng nghĩa, đã ghi ở
> QĐ-6b của `Plan_Rule_Phan_Tang.md`. Con số 16.391 là **chưa qua kiểm nhịp thật sự**.
>
> Số liệu chi tiết từng bài: `datalake/analysis/` · Sinh lại: `datalake/scripts/kiem_tra_toan_bo.py`

---

## 0. Tóm tắt cho người bận

> ### ĐƠN VỊ PHÁN QUYẾT LÀ **BÀI**, KHÔNG PHẢI DÒNG
>
> Chỉ cần **một** dòng lệch khỏi 7 tiếng là **cả bài** rời khỏi thể thất ngôn tự do — tài liệu luật §10 nói rõ điều này, và `rule.py` cài đúng như vậy.
>
> Hệ quả khi đọc báo cáo: mọi số liệu **mức dòng** trong tài liệu này chỉ dùng để **chẩn đoán nguyên nhân**, tuyệt đối không dùng làm thước đo chất lượng corpus. Một bài 32 dòng có 31 dòng hoàn hảo và 1 dòng 6 tiếng thì vẫn là **bài hỏng**, không phải "bài đạt 97%".

### Bảng A — Tình trạng dữ liệu, đo bằng `rule.py`

Đây là **sự thật về corpus**. Không con số nào ở đây phụ thuộc vào quyết định xử lý của ai.

**Phán quyết — mức BÀI (con số chính thức):**

| Chỉ số | Giá trị | Nghĩa là gì |
|---|---:|---|
| Bản ghi | 67.150 | Số dòng JSON trong tệp, không phải số bài thơ |
| Dung lượng | 60,5 MB | Đọc hết mất khoảng 40 giây |
| Bài có nội dung thơ | 62.034 | 5.116 bản ghi còn lại có trường thơ rỗng |
| **BÀI ĐẠT luật H1–H3** | **59.437 — 95,81%** | Mọi dòng đúng 7 tiếng, không sót dòng nào |
| **BÀI TRƯỢT** | **2.597 — 4,19%** | Có ít nhất một dòng lệch → cả bài bị loại |

**Chẩn đoán — mức DÒNG (không phải thước đo chất lượng):**

| Chỉ số | Giá trị | Vì sao KHÔNG được dùng làm thước đo |
|---|---:|---|
| Dòng đúng 7 tiếng | 806.220 / 815.235 — 98,89% | Con số này **luôn đẹp hơn sự thật**: 9.015 dòng hỏng chỉ chiếm 1,11% số dòng nhưng đủ giết 2.597 bài |
| **Dòng tốt bị mất theo bài hỏng** | **42.956 — 5,27% corpus** | Đây mới là thiệt hại thật: những dòng **đúng 7 tiếng** nhưng nằm trong bài hỏng nên bị loại cùng |

> **Đọc hai bảng cạnh nhau:** ở mức dòng chỉ 1,11% hỏng, nhưng vì bài là đơn vị nguyên khối nên **5,27% số dòng của corpus bị loại** — gấp gần năm lần. Đó là cái giá của tính nguyên khối, và là lý do 1.679 bài chỉ hỏng đúng một dòng vẫn đáng công sửa tay.

### Bảng B — Dữ liệu dùng được sau xử lý

> **Bảng B KHÔNG phải tỷ lệ vượt luật.** Tỷ lệ vượt luật là **59.437 — 95,81%** ở bảng A và chỉ có một con số đó. Bảng B đếm thứ khác: sau khi khử trùng lặp và thu hồi nội dung bị ghi sai chỗ thì còn lại bao nhiêu bài dùng được. Hai bảng có mẫu số khác nhau, **không cộng chung được**.

| Chỉ số | Giá trị | Nguồn gốc |
|---|---:|---|
| Đạt luật + không trùng lặp | 43.911 | Từ 59.437 bài đạt, khử 15.526 bản sao nội dung |
| Thu hồi từ khoá ghi sai | +1.244 | **Chưa từng nằm trong mẫu số nào** — vốn thuộc nhóm 5.116 bài có `markdown_poem` rỗng; lấy nội dung ở khoá khác ra rồi đưa qua **đúng bộ luật đó** (§5.1.1) |
| **Tổng dùng được ngay** | **45.155** | Không cần sửa tay, không cần gọi mô hình |

1.244 bài ở hàng giữa **không phải bài mới được cho qua luật**. Việc có chấp nhận nội dung lấy từ khoá phi chuẩn (`content_fix`, `markdown_poem_content`…) làm dữ liệu hợp lệ hay không là **quyết định quản trị dữ liệu**, thuộc quyền chủ dự án — vì vậy nó đứng thành một dòng riêng có nhãn rõ, không gộp vào con số chính.

**Kết luận một câu:** corpus sạch hơn mong đợi về mặt luật thơ; phần trượt **không phải do văn bản bẩn mà do lẫn thể loại khác** — 93,4% dòng hỏng là dòng thơ thật, chữ Việt thuần, chỉ không phải 7 tiếng.

---

## 1. Phương pháp

Một lượt duy nhất qua toàn bộ tệp, mỗi bài đưa qua `kiem_tra_bai_tho()`. Phán quyết `dat` chỉ phụ thuộc ba ràng buộc cứng:

| Mã | Nội dung |
|---|---|
| H1 | Mỗi dòng đúng 7 tiếng |
| H2 | H1 áp dụng cho toàn bộ dòng, không ngoại lệ |
| H3 | Văn bản phải được phân dòng |

Mọi quy tắc mềm (S1–S21) chỉ được ghi nhận để mô tả, **không dùng để loại bài** — đúng §9 Bước 4 của tài liệu luật.

**Đơn vị phán quyết là bài.** `kiem_tra_bai_tho()` trả `dat = True` chỉ khi **mọi** dòng đạt; một dòng lệch là `dat = False` cho cả bài, không có điểm thành phần, không có ngưỡng phần trăm. Đây là cài đặt trực tiếp của §10 tài liệu luật: *"chỉ cần một dòng lệch khỏi 7 tiếng, bài rời khỏi thất ngôn tự do"*.

Vì vậy báo cáo phân biệt hai loại số liệu:

| Loại | Dùng để | Ví dụ |
|---|---|---|
| **Mức bài** | Ra quyết định: nhận, loại, sửa, đổi nhãn | 59.437 bài đạt · 2.597 bài trượt |
| Mức dòng | Chỉ chẩn đoán nguyên nhân | 9.015 dòng hỏng, phân theo độ dài và vị trí |

**Một chỉ số đã bị loại bỏ khỏi báo cáo:** lần đo đầu tiên có mục "dòng hỏng có chữ Latin — 99,19%". Đây là rác đo đạc, vì tiếng Việt viết bằng chữ Latin nên `[a-zA-Z]` khớp mọi dòng. Số liệu trong báo cáo này là bản đo lại, dùng dấu hiệu `f, j, w, z` (các chữ ngoài bảng chữ tiếng Việt) để nhận diện tên riêng ngoại ngữ thật sự.

---

## 2. Cấu trúc bản ghi

```json
{
  "status": "success",
  "id": 1,
  "original_title": "BÂNG KHUÂNG",
  "result": {
    "markdown_poem": "...",
    "score": 8,
    "score_reason": "...",
    "poem_type": "thơ 7 chữ"
  },
  "source_file": "libosa_results.jsonl"
}
```

- `status`: 100% là `"success"`
- `poem_type`: 100% là `"thơ 7 chữ"` — **nhãn này không đáng tin, xem §5**
- JSON hỏng: 0

---

## 3. BÀI VƯỢT QUA ĐƯỢC LUẬT — chân dung

**59.437 bài (95,81%)**

### 3.1. Hình thức

| Số dòng | Số bài | Tỷ lệ | Hình dung |
|---:|---:|---:|---|
| 8 | 20.625 | 34,70% | Dáng **bát cú** — khuôn khổ cổ điển nhất, một khối tám dòng liền |
| 4 | 10.141 | 17,06% | Dáng **tứ tuyệt** — một khổ trọn vẹn, ngắn gọn |
| 16 | 9.243 | 15,55% | **4 khổ × 4 dòng** |
| 12 | 4.705 | 7,92% | **3 khổ × 4 dòng** |
| 20 | 3.926 | 6,61% | **5 khổ × 4 dòng** |
| 24 | 2.166 | 3,64% | **6 khổ × 4 dòng** |

**Đọc bảng này thế nào:** mọi mốc phổ biến đều là **bội số của 4**, trừ mốc 8 dòng. Nghĩa là corpus có hai dáng chủ đạo — khối bát cú liền mạch, và bài xếp thành nhiều khổ tứ tuyệt. Không có mốc lẻ nào chen vào top.

**65,4% số bài chia khổ 4 dòng hoàn toàn**; 26,8% là khối 8 dòng liền không chia khổ. Hai dáng này gộp lại đã chiếm hơn 92% corpus.

### 3.2. Vần — họ sơ đồ của khổ 4 dòng

| Sơ đồ | Tỷ lệ | Tên gọi theo §5.2 | Nghe ra sao |
|---|---:|---|---|
| `aaxa` | 31,45% | **vần ba dòng, kế thừa Đường luật** | Dòng 1, 2, 4 cùng vần; dòng 3 buông ra rồi quay về — tạo cảm giác lửng rồi khép |
| `xxxx` | 16,71% | khổ không gieo vần (S8) | Không có tiếng vọng nào giữa các dòng; nhạc tính dồn hết vào nhịp |
| `xaxa` | 16,60% | vần cách, hai dòng lẻ buông | Chỉ dòng chẵn bắt vần — nhịp đôi rõ, dòng lẻ tự do |
| `aaxx` | 9,61% | hai dòng đầu hiệp | Mở bằng một cặp vần rồi thả trôi nửa sau |
| `axxa` | 6,66% | vần ôm hở | Dòng đầu và dòng cuối ôm nhau, giữa để trống |
| `aaaa` | 5,61% | độc vận cả khổ | Bốn dòng cùng một vần — nặng, trang trọng, dễ đơn điệu |
| `abab` | 2,51% | vần cách đầy đủ | Hai lớp vần đan nhau, đặc trưng thơ mới |
| `aabb` | 0,94% | vần liền | Từng cặp một, gần với đồng dao |

**Nhận định:** corpus nghiêng mạnh về truyền thống Đường luật. Sơ đồ `aaxa` — đúng mẫu tài liệu gọi là "vần ba dòng, kế thừa Đường luật" — chiếm gần một phần ba, trong khi `abab` và `aabb` của thơ mới cộng lại chưa tới 3,5%.

### 3.3. Thanh luật (S2, §4.2)

| Khuôn | Số dòng | Tỷ lệ | Nghĩa là gì |
|---|---:|---:|---|
| bằng (P2 B, P4 T, P6 B) | 306.153 | 40,11% | Dòng mở bằng thanh ngang/huyền ở tiếng thứ 2 — êm, trôi |
| trắc (P2 T, P4 B, P6 T) | 279.706 | 36,65% | Mở bằng thanh trắc — gắt, dứt khoát |
| phá khuôn | 177.405 | 23,24% | Đủ 7 tiếng nhưng P2/P4/P6 không luân phiên — **được phép** theo S4 |

**Đọc bảng này thế nào:** hai khuôn chia nhau gần đều (40% và 37%), cho thấy người viết dùng cả hai chứ không nghiêng hẳn về một phía. Gần một phần tư số dòng phá khuôn — đây là **lựa chọn phong cách, không phải lỗi**, nên không dòng nào trong số 177.405 dòng đó làm bài trượt.

**76,8% số dòng tuân thủ khuôn luân phiên.** Phá khuôn được S4 cho phép nên không ảnh hưởng tới phán quyết.

### 3.4. Các quan sát khác trên bài đạt

| Chỉ số | Giá trị | Nghĩa là gì |
|---|---:|---|
| Nghi là Đường luật (đủ 4/8 dòng + độc vận + niêm) | 3.599 — 6,06% | Bài chặt tới mức gần như Đường luật thật — nằm sát ranh giới bị loại khỏi thể |
| Có ít nhất một cặp vần lệch lớp thanh | 18.561 — 31,23% | Hai tiếng cùng vần nhưng khác bằng/trắc, ví dụ `xanh` (B) hiệp `mảnh` (T) — S9 cho phép |
| Có vần lưng ở P4/P5 (S7) | 23.432 — 39,42% | Có tiếng giữa dòng bắt vần với tiếng cuối dòng — làm dòng thơ dính chặt hơn |

3.599 bài đứng ngay **ranh giới §9 Bước 2**. Theo quyết định cài đặt Đ1, chúng chỉ bị cảnh báo chứ không bị loại — vì phép "đối" chưa kiểm được tự động, và báo nhầm ở đây nghĩa là loại oan một bài hợp lệ.

---

## 4. BÀI KHÔNG VƯỢT QUA — nguyên nhân

**2.597 bài (4,19%), gồm 9.015 dòng hỏng**

### 4.0. Một dòng hỏng là đủ

Trước khi đọc bất kỳ bảng nào bên dưới, cần nắm con số này:

| Bài trượt vì… | Số bài | Tỷ lệ số bài trượt |
|---|---:|---:|
| **đúng 1 dòng hỏng** | **1.679** | **64,65%** |
| 2 dòng hỏng | 243 | 9,36% |
| 3 dòng hỏng | 95 | 3,66% |
| 4 dòng hỏng | 218 | 8,39% |
| 5 dòng hỏng trở lên | 360 | 13,86% |
| 0 dòng hỏng (vi phạm H3 — không phân dòng) | 2 | 0,08% |

**Gần hai phần ba số bài trượt chỉ vì một dòng duy nhất.** Một bài 32 dòng có 31 dòng hoàn hảo vẫn bị loại nguyên bài — đó là điều mà mọi thống kê mức dòng che mất.

Đây cũng là lý do thứ tự ưu tiên xử lý ở §7 đặt nhóm "sửa một dòng" lên đầu: chi phí sửa thấp nhất, số bài thu hồi lớn nhất.

### 4.1. Phát hiện chính

> **93,39% dòng hỏng KHÔNG mang bất kỳ dấu hiệu nhiễu nào.**
> Chúng là dòng thơ thật, chữ Việt thuần, chỉ đơn giản không phải 7 tiếng.

Bảng dưới đếm theo **cả hai đơn vị**. Cột "Số bài" là con số dùng để ra quyết định, vì bài mới là thứ bị loại; cột "Số dòng" chỉ cho thấy mức độ tập trung của từng loại nhiễu.

| Nguyên nhân | **Số bài** | **% bài trượt** | Số dòng | % dòng hỏng | Đây là loại dòng nào | Ví dụ thật từ corpus |
|---|---:|---:|---:|---:|---|---|
| **Dòng thơ thật, chỉ sai số tiếng** | **2.237** | **86,14%** | **8.419** | **93,39%** | Câu thơ hoàn chỉnh, chữ Việt thuần, chỉ không phải 7 tiếng | `Đường về ngơ ngác hỏi bậu vì đâu?` — 8 tiếng |
| Dòng phụ chú mở bằng ngoặc/dấu sao | 168 | 6,47% | 235 | 2,61% | Ghi chú của người biên tập, bị gộp vào trường thơ | `*(Gửi chị Trúc)*` — 3 tiếng |
| Đề tặng, lời đề từ | 160 | 6,16% | 165 | 1,83% | Dòng "tặng ai", thường nằm ngay dưới tiêu đề | `Gửi theo Thanh Nam,` — 4 tiếng |
| Tên riêng ngoài bảng chữ tiếng Việt | 131 | 5,04% | 163 | 1,81% | Địa danh, tên người nước ngoài viết nguyên dạng | `Buổi chiều hiu hắt góc Whitlam.` — 6 tiếng |
| Có chữ số (năm tháng, địa danh) | 47 | 1,81% | 65 | 0,72% | Dòng ghi nơi chốn và thời điểm sáng tác | `Bát Tràng, 1973` — 9 tiếng |
| Dòng phân cách `*` | 35 | 1,35% | 58 | 0,64% | Ký hiệu ngắt phần của bản in gốc | `*` — 0 tiếng |
| Tên phiên âm có gạch nối | 27 | 1,04% | 36 | 0,40% | Tên nước ngoài phiên âm, mỗi gạch nối là một âm tiết | `Nắng êm đềm trắng đêm Lê-nin-grát,` — 8 tiếng |
| Văn xuôi lẫn vào (tiểu dẫn, chú thích) | 22 | 0,85% | 22 | 0,24% | Cả đoạn văn xuôi nằm trong trường thơ | `Xóm Ngự Viên ở cạnh đường Gia Hội (Huế)…` — 16 tiếng |
| Ký tên tác giả | 10 | 0,39% | 10 | 0,11% | Chữ ký cuối bài | `— Lê Bá Dương` — 3 tiếng |

*Một bài có thể dính nhiều loại nên tổng cột "Số bài" vượt 2.597.*

### Cách đọc bảng này

**Hàng đầu tiên là toàn bộ câu chuyện, ở cả hai đơn vị đếm.** 86,14% số bài trượt (và 93,39% số dòng hỏng) không mang dấu hiệu bất thường nào — chúng là câu thơ thật sự, đọc lên vẫn ra thơ, chỉ là không đúng 7 tiếng.

**Chênh lệch giữa hai cột nói lên điều gì.** Nhiễu siêu dữ liệu chiếm 6,61% số dòng hỏng nhưng tới 13,86% số bài trượt — vì mỗi bài thường chỉ dính **một** dòng nhiễu, và một dòng là đủ giết cả bài. Ngược lại, lỗi "dòng thơ thật" tập trung dày trong ít bài hơn (một bài thơ 8 chữ hỏng cả 66 dòng).

> Bóc nhiễu siêu dữ liệu chỉ chạm tới **596 / 9.015 dòng**, nhưng lại **cứu được tới 360 bài** — hiệu suất trên đơn vị bài cao hơn nhiều so với vẻ ngoài của cột "số dòng".

**Tám hàng dưới có một điểm chung:** chúng đều là **siêu dữ liệu bị gộp nhầm vào trường nội dung** — lời đề tặng, năm sáng tác, chữ ký, ký hiệu ngắt phần. Không có dòng nào trong đó là lỗi của người làm thơ; tất cả là lỗi của khâu thu thập. Vì vậy chúng **bóc ra được bằng máy** (xem bộ lọc L1–L4 ở §6.4), khác hẳn hàng đầu vốn phải sửa bằng tay hoặc đổi nhãn thể loại.

**Hai hàng dễ hiểu nhầm:**

- *Tên phiên âm có gạch nối* — `Lê-nin-grát` đếm 3 tiếng là **đúng theo §2.1** của tài liệu luật ("ra-đi-ô" = 3 tiếng). Dòng vẫn hỏng thật, không phải bộ đếm sai.
- *Đề tặng, lời đề từ* — hàng này chỉ đáng tin **vì nó được đo trên các dòng đã sai số tiếng**. Áp đúng mẫu đó lên dòng đủ 7 tiếng thì báo nhầm hàng loạt, xem §6.3.

**Hệ quả cho kế hoạch xử lý:** đây không phải bài toán *làm sạch văn bản* mà là bài toán *phân loại thể loại*. Viết bộ lọc dấu câu, bộ bóc chú thích… chỉ chạm tới chưa đầy 7% khối lượng vấn đề.

### 4.2. Hỏng theo độ dài dòng *(chẩn đoán mức dòng)*

| Độ dài | Số dòng | Tỷ lệ | Thường là chuyện gì |
|---:|---:|---:|---|
| 6 tiếng (thiếu 1) | 1.935 | 21,46% | **Rơi mất một chữ** khi sao chép — đọc lên nghe hụt hẳn một nhịp |
| **8 tiếng (thừa 1)** | **6.372** | **70,68%** | Phần lớn là **thơ 8 chữ bị gán nhãn nhầm**, không phải thơ 7 chữ viết lỗi |
| 0–5 tiếng | 557 | 6,18% | Dòng siêu dữ liệu: chữ ký, đề tặng, ký hiệu ngắt phần |
| ≥ 9 tiếng | 151 | 1,68% | Văn xuôi lẫn vào — có dòng dài tới **75 tiếng** |

**Đọc bảng này thế nào:** hai hàng đầu chiếm 92% và chúng nói hai câu chuyện ngược nhau. Thiếu một tiếng thường là **lỗi dữ liệu** nên sửa được. Thừa một tiếng thường là **thể loại khác** nên không sửa được, chỉ đổi nhãn.

### 4.3. Hỏng theo vị trí *(chẩn đoán mức dòng)*

| Vị trí | Số dòng | Tỷ lệ | Ý nghĩa chẩn đoán |
|---|---:|---:|---|
| Giữa bài | 7.501 | 83,21% | Lỗi nằm trong thân bài → là chuyện của **bản thân bài thơ** (sai thể, rơi chữ) |
| Dòng đầu bài | 1.095 | 12,15% | Gần như luôn là **siêu dữ liệu**: đề tặng, tiểu dẫn, năm sáng tác |
| Dòng cuối bài | 419 | 4,65% | Thường là **chữ ký tác giả** hoặc nơi chốn – ngày tháng |

**Đọc bảng này thế nào:** vị trí của dòng hỏng gần như quyết định cách xử lý. Hỏng ở **đầu hoặc cuối** (16,8%) thì chỉ cần cắt bỏ dòng đó là xong — đó chính là căn cứ cho quy tắc L3 ở §6.4. Hỏng ở **giữa bài** thì phải đọc mới biết là rơi chữ hay sai thể loại.

### 4.4. Hai quần thể thất bại hoàn toàn khác nhau

#### Quần thể 1 — lệch đúng MỘT dòng: 1.679 bài (64,7% số bài trượt)

Độ dài của dòng lệch đó:

| Độ dài | Số bài | Tỷ lệ |
|---:|---:|---:|
| **6 tiếng** | **1.060** | **63,1%** |
| 8 tiếng | 338 | 20,1% |
| khác | 281 | 16,8% |

Ví dụ:

```
id=2729  D7 (6 tiếng): Bao giờ nước sông ngừng chảy,
id=2947 D28 (6 tiếng): Rồi núi sông mộng cũng tan.
id=3039 D28 (6 tiếng): Bạn con chưa hẳn bạn con.
```

Đọc lên nghe hụt hẳn một nhịp. Nguyên nhân gần như chắc chắn là **rơi chữ khi sao chép hoặc OCR**, không phải chủ ý tác giả. **Quần thể này cứu được** — chỉ cần bổ sung một tiếng, và `rule.py` đã chỉ sẵn dòng nào, thiếu bao nhiêu.

#### Quần thể 2 — lệch trên 3 dòng: 578 bài, đóng góp 5.819 dòng 8 tiếng

```
Bài thơ viết nửa đời còn dang dở,      (8 tiếng)
Bởi anh quên tóc em chẻ bên nào.       (8 tiếng)
Tìm nhau theo dấu mòn ngày tháng cũ,   (8 tiếng)
Trăng quên tròn biết tóc chẻ về đâu.   (8 tiếng)
```

Đây là **thơ 8 chữ chuẩn mực, bị gán nhãn `poem_type: "thơ 7 chữ"`**.

| Tỷ lệ dòng 8 tiếng trong bài | Số bài |
|---:|---:|
| 100% | 111 |
| 90% | 13 |
| 80% | 33 |

**Quần thể này không cứu được và cũng không nên xoá** — nên tách sang bộ dữ liệu thơ 8 chữ.

#### Giải thích một nghịch lý số liệu

67% *số bài* trượt không có dòng 8 tiếng nào, nhưng 70% *số dòng* hỏng lại là 8 tiếng. Lý do: quần thể 2 ít bài nhưng mỗi bài hỏng hàng chục dòng; quần thể 1 nhiều bài nhưng mỗi bài chỉ hỏng một dòng.

> Hai quần thể trên là cách nhìn theo *số dòng hỏng*. Mục 4.5 dưới đây phân nhóm theo *nguyên nhân*, dùng bảng mã riêng A–H — hai cách phân loại độc lập với nhau.

### 4.5. Phân nhóm chi tiết kèm tên bài

Toàn bộ 2.597 bài trượt đã được xuất ra `datalake/analysis/bai_truot_chi_tiet.jsonl`, mỗi bản ghi gồm `id`, `tieu_de`, `nguyen_nhan`, và danh sách dòng hỏng kèm số tiếng. 1.452 bài có tiêu đề; số còn lại để trống.

| Nhóm | Số bài | Tỷ lệ | Xử lý đề xuất |
|---|---:|---:|---|
| **D. Đúng một dòng thiếu một tiếng** | **1.060** | **40,8%** | Sửa tay — nghi rơi chữ |
| H. Lệch nhiều dòng, thể không thuần nhất | 525 | 20,2% | Rà từng bài |
| E. Đúng một dòng thừa một tiếng | 338 | 13,0% | Sửa tay |
| F. Đúng một dòng lệch nhiều tiếng | 242 | 9,3% | Thường là dòng đề tặng — bóc ra |
| G. Hai dòng lệch | 241 | 9,3% | Sửa tay |
| A. Thơ 8 chữ bị gán nhãn 7 chữ | 135 | 5,2% | Chuyển sang bộ 8 chữ |
| C. Có dòng phân cách không chứa tiếng | 34 | 1,3% | Bóc dòng `*` |
| B. Lẫn văn xuôi trong trường thơ | 22 | 0,8% | Bóc tiểu dẫn khỏi trường thơ |

#### Nhóm A — thơ 8 chữ bị gán nhãn sai

| id | Tên bài | Số dòng | Dòng hỏng |
|---:|---|---:|---:|
| 3449 | Người như sự sống mãi sinh sôi | 66 | 66 |
| 4277 | 67, Khúc thêm cho Huyền Châu | 26 | 26 |
| 3330 | Gửi Tây Thi | 16 | 13 |
| 4382 | Nhớ lắm rừng ơi | 14 | 12 |
| 4256 | Trăng mật | 12 | 12 |
| 4441 | Trà một mình | 4 | 4 |

```
id=4441 "Trà một mình"
  D1 (8 tiếng): Bạn ở xa, nơi đài vừa báo bão,
  D2 (8 tiếng): Ly rót rồi, chưa thể đặt lên môi.
  D3 (8 tiếng): Ly lật sẵn, chờ tay ai gõ cửa,
```

Nhịp 3/5 đặc trưng của thơ 8 chữ, không phải thơ 7 chữ bị lỗi.

#### Nhóm B — văn xuôi lẫn vào, luôn ở dòng đầu

| id | Tên bài | Tổng dòng | Dòng hỏng | Độ dài dòng hỏng |
|---:|---|---:|---:|---:|
| 3811 | Hai con chó | 51 | 1 | **75 tiếng** |
| 4513 | Các vị La Hán chùa Tây Phương | 61 | 1 | 63 tiếng |
| 4631 | Đôi lời tâm sự | 41 | 1 | 23 tiếng |
| 3513 | Thơ tặng Béc-tôn Bờ-re-sơ | 17 | 1 | 21 tiếng |
| 3530 | Thăm thầy giáo | 21 | 1 | 17 tiếng |
| 3308 | Xóm Ngự Viên | 61 | 1 | 16 tiếng |

Cả sáu bài đều chỉ hỏng **đúng dòng 1** — đó là lời tiểu dẫn bị gộp vào trường thơ. Bóc dòng đầu ra là bài hợp lệ ngay.

#### Nhóm C — dòng phân cách `*` giữa các phần

| id | Tên bài | Tổng dòng | Số dòng `*` |
|---:|---|---:|---:|
| 3310 | Xuân tha hương | 108 | 8 |
| 3317 | Oan nghiệt | 76 | 4 |
| 4259 | Hai sắc hoa tigôn | 46 | 2 |
| 3329 | Mưa xuân (I) | 45 | 1 |
| 4213 | Lá thư thành phố | 49 | 1 (`***`) |
| 3328 | Những bóng người trên sân ga | 37 | 1 |

Đây là quy ước trình bày của bản in gốc, không phải dòng thơ. Xoá là bài hợp lệ.

#### Nhóm D — thiếu đúng một tiếng, nghi rơi chữ

| id | Tên bài | Dòng | Nội dung |
|---:|---|---:|---|
| 3382 | Hành quân thần tốc | D10 | Nấu chưa chín, lệnh hành quân. |
| 3446 | Đem cả tình yêu làm vũ khí | D23 | Nay giặc đến nhà ta đó |
| 3494 | Nằm bệnh viện gửi Diệu | D21 | Yêu bạn, Montaigne tự giải lời: |
| 2729 | *(không tiêu đề)* | D7 | Bao giờ nước sông ngừng chảy, |
| 2947 | *(không tiêu đề)* | D28 | Rồi núi sông mộng cũng tan. |
| 3039 | *(không tiêu đề)* | D28 | Bạn con chưa hẳn bạn con. |

#### Nhóm E — thừa đúng một tiếng

| id | Tên bài | Dòng | Nội dung |
|---:|---|---:|---|
| 13 | QUA TÌM BẬU BẬU NƠI ĐÂU | D17 | Đường về ngơ ngác hỏi bậu vì đâu? |
| 39 | THƯƠNG MẸ LẮM MẸ ƠI | D3 | Mắt mẹ loà rồi, mẹ nghỉ đi thôi, |
| 3298 | Khăn hồng | D1 | Gửi chị, chị cho em chiếc khăn thêu, |
| 3518 | Những cái chết | D33 | Người chẳng ra người, ma chẳng ra ma! |
| 3699 | Sinh nhật | D1 | Hôm nay là ngày sinh nhật của anh, |

#### Nhóm F — dòng lệch là lời đề tặng, không phải thơ

| id | Tên bài | Dòng | Nội dung |
|---:|---|---:|---|
| 17 | THÀNH CỔ | D5 | — Lê Bá Dương |
| 3273 | Tiễn một người | D1 | Gửi theo Thanh Nam, |
| 3323 | Xây lại cuộc đời | D1 | Gửi chị Trúc, |
| 3345 | Nuôi bướm | D1 | *Tặng Vương Ý Nhi* |
| 3398 | Lòng chiến sĩ | D1 | *(Kính dâng Phạm Ngũ Lão)* |

Nhóm này **không phải lỗi thơ** — chỉ là siêu dữ liệu bị gộp vào trường nội dung.

#### Nhóm G — hai dòng lệch, có ca đặc biệt

```
id=4208 "Bên hàng rào Ái Tử"  10 dòng
  D1 (1 tiếng): I
  D6 (1 tiếng): II
```

Đây là **số thứ tự phần**, không phải dòng thơ. Bài thực chất gồm hai phần 4 dòng hợp lệ.

#### Một quan sát về trùng lặp trong nhóm trượt

Các bài `id=2728`, `id=3111`, `id=3213` có nội dung khác nhau nhưng cùng một dạng lỗi, và `id=3741 "Thơ ghé bến người"` có D1 và D17 **giống hệt nhau** — dấu hiệu lặp khổ khi thu thập. Tiêu đề lặp nhiều nhất trong nhóm trượt: `HỒ CHÍ MINH SÁNG MÃI TÊN NGƯỜI` (5 lần), `Sinh nhật`, `XUÂN`, `TÔI ĐI TÌM TÔI` (4 lần mỗi tiêu đề).

---

## 5. Vấn đề chất lượng dữ liệu ngoài luật thơ

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

Mở rộng phép đo sang mọi dấu hiệu cấu trúc phi thơ trên 59.437 bài đạt:

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

| Tập | Số bài | Trạng thái |
|---|---:|---|
| **Đạt luật + không trùng lặp** | **43.911** | dùng được ngay |
| **Thu hồi từ khoá sai, đạt luật ngay** | **1.244** | dùng được ngay |
| Đạt luật nhưng trùng nội dung | 15.526 | khử trùng |
| Cứu bằng bóc dòng siêu dữ liệu (nhóm B, C, F) | 298 | tự động hoá được |
| Cứu bằng sửa tay (nhóm D, E, G) | 1.639 | cần người |
| Thu hồi được nhưng chưa đạt luật | 690 | rà tiếp |
| Tách sang bộ 8 chữ | 135 | đổi nhãn |
| Rỗng thật, không cứu được | 3.182 | truy ngược đường ống |

**Tổng dùng được ngay: 45.155 bài.**

### Năm việc theo thứ tự ưu tiên

1. **Dựng `datalake/datasilver/`** gộp 43.911 bài đạt + 1.244 bài thu hồi = **45.155 bài**. Đây là tập dùng được ngay làm ví dụ few-shot cho bộ sinh và ngữ liệu vàng cho eval.
2. **Chạy bộ lọc L1–L4** (§6.4) trên nhóm B, C, F — thu thêm khoảng 298 bài mà không cần người can thiệp.
3. **Tách 135 bài 8 chữ** sang bộ riêng thay vì xoá. Chúng là dữ liệu tốt, chỉ sai nhãn.
4. **Đưa 1.639 bài lệch 1–2 dòng vào hàng đợi sửa tay.** `rule.py` đã chỉ đúng dòng và số tiếng thiếu nên chi phí sửa rất thấp.
5. **Truy ngược 3.182 bài rỗng thật** — chúng vẫn có `score`, nghĩa là đường ống đã chấm điểm cho nội dung không tồn tại.

---

## 8. Ghi chú về độ tin cậy của bộ kiểm

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

`v.dat` là **một giá trị bool cho cả bài**, không phải điểm số. Muốn đếm đúng thì đếm số bài có `v.dat == True`, đừng đếm tỷ lệ dòng đạt rồi lấy trung bình — hai cách cho ra hai bức tranh khác hẳn nhau (98,89% so với 95,81%).

Toàn bộ số liệu trong bản này được đo lại từ đầu bằng `rule.py` hiện tại vào ngày 17/09/2026, và tái lập chính xác các con số của lần chạy trước.

---

## 10. Tệp kết quả đã xuất

Thư mục `datalake/analysis/`:

| Tệp | Số bản ghi | Nội dung |
|---|---:|---|
| `bai_truot_chi_tiet.jsonl` | 2.597 | Mọi bài trượt: `id`, `tieu_de`, `nguyen_nhan`, từng dòng hỏng kèm số tiếng |
| `bai_rong_cuu_duoc.jsonl` | 1.934 | Bài thu hồi từ khoá sai: `khoa_nguon`, `dat_luat`, toàn văn thơ |
| `dong_nghi_ngo_trong_bai_dat.jsonl` | 42 | Bài đạt luật nhưng còn dòng siêu dữ liệu lẫn vào |

Cả ba tệp dùng trực tiếp làm đầu vào cho hàng đợi sửa tay hoặc bước tiền xử lý.
