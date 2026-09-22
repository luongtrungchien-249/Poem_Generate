# PLAN — Thiết kế lại `rule.py` thành các tầng

**Ngày lập:** 17/09/2026
**Tài liệu luật:** `docs/Luat_Tho_That_Ngon_Tu_Do.md`
**Tệp mục tiêu:** `src/application/rule.py`
**Trạng thái:** ✅ đã chốt toàn bộ QĐ-1 → QĐ-7 (18/09/2026). Đang thi công T1.

---

## 1. Vì sao có plan này

Yêu cầu của chủ dự án:

1. Một bài thơ phải **vượt qua toàn bộ các tầng** (toàn bộ các rule) mới được coi là Pass.
2. Từng bài phải **thể hiện rõ đã vượt qua từng tầng thế nào**, có bằng chứng cho mỗi tầng.
3. Mọi số liệu phải **chạy lại từ đầu cho từng bài**, không tái sử dụng thống kê của bản trước.

Vấn đề hiện tại: `ly_do_dat` chỉ ghi `"H1+H2: cả N/N dòng đúng 7 tiếng. H3: có phân dòng."`
Bảng `LUAT` có 30 điều nhưng bằng chứng chỉ nhắc 3. Người đọc không biết 27 điều còn lại
có được chạy hay không.

### 1.1. Một sai lầm của bản plan trước, ghi lại để không lặp

Bản plan đầu tiên tự đặt ra hai tiêu chí **không có trong tài liệu**:

- *"tỷ lệ dòng theo khuôn ≥ 0,5"* — S2 chỉ nói *"nên luân phiên"*, không có con số.
- *"mỗi khổ ≤ 2 lớp vần"* — S11 chỉ nói *"nên nhất quán"*, không có con số.

Nghiêm trọng hơn, ngưỡng 0,5 được chọn **vì nó giữ lại 84,82% số bài** — tức là nắn luật
cho vừa dữ liệu. Đó là điều cấm.

> **Luật của plan này:** tiêu chí đạt của mỗi tầng phải **trích nguyên văn được** từ tài
> liệu luật. Chỗ nào tài liệu không đưa ra tiêu chí đo được, tầng đó **không được bịa ra
> tiêu chí** — phải đưa lên thành quyết định của chủ dự án, và **không được chọn phương án
> dựa trên số bài sống sót**.

---

## 2. Bốn nguyên tắc bất di bất dịch

| #  | Nguyên tắc                                                                                                                                                                                          |
| -- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| N1 | Tiêu chí mỗi tầng phải trích được từ câu chữ tài liệu. Không có chữ thì không có tiêu chí.                                                                                      |
| N2 | Điều luật loại**quyền** (*"có thể"*, *"chấp nhận"*, *"tự do"*) **không bao giờ** được dùng để đánh trượt. Trượt vì dùng quyền là mâu thuẫn tự thân. |
| N3 | Điều luật đòi**ý đồ tác giả** hoặc **ngữ nghĩa** thì ghi công khai là *không kiểm được*, không lặng lẽ cho qua.                                                 |
| N4 | Mọi số liệu đến từ**một lượt chạy mới trên toàn bộ tệp**. Không con số nào được chép lại từ báo cáo cũ.                                                              |

---

## 3. Kiểm kê TỪNG ĐIỀU trong 30 điều luật

Bảng dưới sinh ra từ chính `LUAT`, `LOAI_DIEU_MEM` và `TANG` trong `rule.py`, nên không
thể lệch khỏi mã đang chạy.

### 3.0. Bảng tổng — cả 30 điều

| Mã | Nguyên văn | Tầng | Loại | Phân loại mềm | Vai trò trong bộ kiểm |
|---|---|:---:|---|---|---|
| **H1** | Mỗi dòng phải có đúng 7 tiếng | 2 | cứng | — | ⛔ **TIÊU CHÍ CHẶN** |
| **H2** | H1 áp dụng cho toàn bộ các dòng, không ngoại lệ | 2 | cứng | — | ⛔ **TIÊU CHÍ CHẶN** |
| **H3** | Văn bản phải được phân dòng, từ 4 dòng trở lên | 1 | cứng | — | ⛔ **TIÊU CHÍ CHẶN** |
| **H4** | Số dòng trong bài phải là bội của 4 | 1 | cứng | — | ⛔ **TIÊU CHÍ CHẶN** |
| **F1** | Không áp dụng luật niêm giữa các dòng | 3 | đã gỡ bỏ | — | 📋 chỉ ghi nhận |
| **F2** | Không yêu cầu cặp đối bắt buộc | 3 | đã gỡ bỏ | — | 🚫 không kiểm được |
| **F3** | Không yêu cầu độc vận cho toàn bài | 3 | đã gỡ bỏ | — | 📋 chỉ ghi nhận |
| **F4** | Không yêu cầu Khai – Thừa – Chuyển – Hợp | 3 | đã gỡ bỏ | — | 🚫 không kiểm được |
| **F5** | Số dòng không giới hạn về lượng, nhưng phải là bội của 4 | 3 | đã gỡ bỏ | — | 📋 chỉ ghi nhận |
| **S1** | P1, P3, P5 có thể tự do về thanh; có thể dùng thêm vần lưng ở P4 hoặc P5 | 4 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S2** | P2, P4, P6 nên luân phiên bằng – trắc | 4 | mềm | bắt buộc | ⛔ **TIÊU CHÍ CHẶN** |
| **S3** | P7 gắn với vần, cần chọn có chủ đích | 4 | mềm | bắt buộc | 🚫 không kiểm được |
| **S6** | Vần chủ đạo là vần chân, đặt ở P7 | 5 | mềm | mô tả | 📋 chỉ ghi nhận |
| **S8** | Bài có thể không gieo vần | 5 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S9** | Có thể dùng vần bằng, vần trắc hoặc phối hợp | 5 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S10** | Chấp nhận vần thông, không yêu cầu vần chính tuyệt đối | 5 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S11** | Sơ đồ vần nên nhất quán trong phạm vi một khổ | 5 | mềm | bắt buộc | ⛔ **TIÊU CHÍ CHẶN** |
| **S12** | Có thể đổi vần khi sang khổ mới | 5 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S13** | Nhịp do nghĩa của dòng quyết định | 6 | mềm | mô tả | 📋 chỉ ghi nhận 🔻 |
| **S14** | Nên có một nhịp chủ đạo | 6 | mềm | bắt buộc | ⛔ **TIÊU CHÍ CHẶN** |
| **S15** | Đổi nhịp nên trùng chỗ chuyển ý | 6 | mềm | bắt buộc | 🚫 không kiểm được 🔻 |
| **S16** | Số dòng trong bài không hạn định về lượng, nhưng phải là bội của 4 | 7 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S17** | Khổ phổ biến là 4 dòng; dùng được 2, 3, 5, 6 dòng | 7 | mềm | mô tả | 📋 chỉ ghi nhận |
| **S18** | Có thể viết liên hoàn, không chia khổ | 7 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S19** | Triển khai theo mạch cảm xúc hoặc mạch tự sự | 7 | mềm | mô tả | 🚫 không kiểm được |
| **S20** | Có thể dùng điệp dòng, điệp khổ, điệp cấu trúc | 7 | mềm | **quyền** | 📋 chỉ ghi nhận |
| **S21** | Có thể kết mở | 7 | mềm | **quyền** | 📋 chỉ ghi nhận |

**Ký hiệu:** ⛔ đánh trượt được · 🚫 máy không kiểm được (N3) · 📋 đo và ghi, không phán
quyết · 🔻 bị một quyết định dự án ghi đè · **quyền** = N2 cấm dùng để đánh trượt.

**Tổng kết một câu: chỉ 7 trong 30 điều thực sự đánh trượt bài.** 23 điều còn lại vẫn
được đo và ghi vào biên bản từng bài, nhưng không loại ai.

---

### 3.1. Bốn điều CỨNG — H1, H2, H3, H4

| Mã | Nguyên văn | Tầng | Phân tích |
|---|---|:---:|---|
| `H3` | Văn bản phải được phân dòng, từ 4 dòng trở lên | 1 | ⛔ Đo trực tiếp: đếm số dòng, đòi ≥ 4. Đứng đầu vì mọi tầng sau đều nói về quan hệ **giữa** các dòng |
| `H4` | Số dòng trong bài phải là bội của 4 | 1 | ⛔ **Bổ sung 18/09/2026**, nguyên văn chủ dự án: *"đây là Rule cứng không có ngoại lệ"*. Phép kiểm: `n % 4 == 0`. Lưu ý **0 chia hết cho 4** nên H4 một mình không bắt được bài rỗng — H3 mới bắt |
| `H1` | Mỗi dòng phải có đúng 7 tiếng | 2 | ⛔ Đo được, nhưng **phép đếm tiếng mới là chỗ khó**: §2.1 nói dấu câu không tính, chữ số phải quy về cách đọc |
| `H2` | H1 áp dụng cho toàn bộ các dòng, không ngoại lệ | 2 | ⛔ Không phải một phép kiểm riêng mà là **lượng từ** của H1. Nó biến H1 thành "mọi dòng", và là căn cứ cho phán quyết ở mức BÀI |

Tài liệu §2 gọi bốn điều này là *"điều kiện cần và đủ"* để nhận diện thể. Vì vậy cờ
`thuoc_the` chỉ hỏi bốn điều này — **55.297 bài**.

> **H4 làm `thuoc_the` giảm 59.437 → 55.297.** Vì H4 là ràng buộc **cứng**, nó vào cả cờ
> `thuoc_the` chứ không chỉ `dat`. Một bài 6 dòng nay **không còn thuộc thể** thất ngôn tự
> do, chứ không phải chỉ "không đạt chuẩn dự án".

---

### 3.2. Năm điều F — ĐÃ GỠ BỎ, không phải điều kiện loại trừ

> ⚠️ **Đây là chỗ bản plan trước sai, và nó làm loại oan 4.288 bài.**

§3 tài liệu mang tiêu đề *"Điều bị loại bỏ khỏi thể"*. F1–F5 là các **ràng buộc đã được
gỡ**, và câu chốt của §3 nói thẳng:

> *"Việc một bài thất ngôn tự do vẫn có niêm, có đối, có độc vận là **được phép**. Nhưng
> đó là **lựa chọn của tác giả, không phải tiêu chí nhận diện thể**."*

| Mã | Nguyên văn | Phân tích |
|---|---|---|
| `F1` | Không áp dụng luật niêm giữa các dòng | 📋 Niêm **được đo** để báo cáo, nhưng có niêm không làm bài trượt |
| `F2` | Không yêu cầu cặp đối bắt buộc | 🚫 Phép đối là quan hệ **từ loại + ngữ nghĩa** giữa hai dòng — máy không kiểm được |
| `F3` | Không yêu cầu độc vận cho toàn bài | 📋 Độc vận **được đo**, không làm bài trượt. Bản trước dựng `ViPham(ma="F3")` — sai, vì không ai "vi phạm" được một câu nới |
| `F4` | Không yêu cầu Khai – Thừa – Chuyển – Hợp | 🚫 Bố cục đòi **hiểu nội dung** |
| `F5` | Số dòng không giới hạn về lượng, nhưng phải là bội của 4 | 📋 **Hợp nhất với S16 và H4 ngày 18/09.** Hai vế nói hai chuyện: *không giới hạn* là về **lượng**, *bội của 4* là về **hình dạng**. Tập hợp lệ `{4, 8, 12, …}` vừa vô hạn vừa chia hết cho 4 |

**§3 và §9 Bước 2 của tài liệu mâu thuẫn nhau:**

| | |
|---|---|
| §3 | có niêm/đối/độc vận là được phép, **không phải tiêu chí nhận diện** |
| §9 Bước 2 | nếu 4 hoặc 8 dòng + độc vận + niêm + đối thì thuộc Đường luật |

**Chọn theo §3** vì: (1) §3 nói thẳng về *tiêu chí nhận diện thể*; (2) F5 phủ định trực
tiếp con số 4/8 mà §9 Bước 2 dựa vào; (3) chủ dự án — tác giả tài liệu — đã xác nhận.

Ngay cả nếu theo §9 Bước 2 thì tầng 3 cũng **không được chặn**, vì tài liệu đòi **bốn** vế
mà máy chỉ kiểm được **ba** (F2 đối không kiểm được). Chặn dựa trên ba phần tư điều kiện
là loại oan.

⇒ **Tầng 3 là tầng GHI NHẬN**, `tieu_chi_tu = ()`, không dựng `ViPham` nào.

---

### 3.3. Ba điều thanh luật — S1, S2, S3

| Mã | Nguyên văn | Phân loại | Phân tích |
|---|---|---|---|
| `S1` | P1, P3, P5 có thể tự do về thanh; có thể dùng thêm vần lưng ở P4 hoặc P5 | **quyền** | 📋 Một câu **nới**. Nó nói rõ chỉ P2/P4/P6 mới có ràng buộc — tức là giới hạn phạm vi của S2 |
| `S2` | P2, P4, P6 nên luân phiên bằng – trắc | bắt buộc | ⛔ **Đo được ở mức dòng**, nhưng tài liệu không cho ngưỡng ở mức bài → **QĐ-1** |
| `S3` | P7 gắn với vần, cần chọn có chủ đích | bắt buộc | 🚫 *"có chủ đích"* đòi **ý đồ tác giả** — N3 |

**Cái giá đo được:** tầng 4 chặn **30.571 bài — 55,29%** số bài đi vào nó, và **69,66%**
toàn bộ bài trượt. Nếu đọc đúng câu chữ tài liệu (chữ *"nên"* ở S2), phần lớn
số bài này **không sai gì cả**. Chúng trượt vì QĐ-1 và QĐ-2.

---

### 3.4. Bảy điều vần — S6 đến S12

| Mã | Nguyên văn | Phân loại | Phân tích |
|---|---|---|---|
| `S6` | Vần chủ đạo là vần chân, đặt ở P7 | mô tả | 📋 Phát biểu về thông lệ. Nó **định nghĩa chỗ nhìn**: so vần là so tiếng thứ 7 |
| `S8` | Bài có thể không gieo vần | **quyền** | 📋 **Điều quan trọng nhất của tầng 5.** Nó cấm mọi tiêu chí dạng *"bài phải có vần"* |
| `S9` | Có thể dùng vần bằng, vần trắc hoặc phối hợp | **quyền** | 📋 Cặp vần **lệch lớp thanh vẫn là hiệp vần**. Được đo (`so_cap_van_lech_thanh`): 33,27% bài đạt có |
| `S10` | Chấp nhận vần thông, không yêu cầu vần chính tuyệt đối | **quyền** | 📋 Sinh ra nhu cầu **bảng vần thông** → QĐ-5, và bảng phải **có nguồn** |
| `S11` | Sơ đồ vần nên nhất quán trong phạm vi một khổ | bắt buộc | ⛔ *"nhất quán"* không đo được nếu không có danh sách sơ đồ → **QĐ-7** dùng §5.2 |
| `S12` | Có thể đổi vần khi sang khổ mới | **quyền** | 📋 Vì vậy sơ đồ vần tính **trong từng khổ**, và chữ cái đánh liên tục qua các khổ |

**Chỗ tinh tế:** S8 (quyền không gieo vần) và S11 (nên nhất quán) kéo ngược nhau. Giải
bằng QĐ-7: tiêu chí là *"tồn tại ít nhất một cụm 4 dòng liên tiếp khớp một sơ đồ §5.2"* —
đây là điều kiện **tồn tại**, không phải điều kiện **phổ quát**, nên không mâu thuẫn S8.

---

### 3.5. Ba điều nhịp — S13 đến S15

| Mã | Nguyên văn | Phân loại | Phân tích |
|---|---|---|---|
| `S13` | Nhịp do nghĩa của dòng quyết định | mô tả 🔻 | 📋 *"do nghĩa quyết định"* nghĩa là **máy không suy được từ hình thức**. **QĐ-4 ghi đè**: xét theo hình thức, khớp bảy kiểu §6 |
| `S14` | Nên có một nhịp chủ đạo | bắt buộc | ⛔ *"nên"* → **QĐ-4b**: phải tồn tại một kiểu nhịp phủ **mọi** dòng. Dùng phép **giao**, không dùng ngưỡng phần trăm |
| `S15` | Đổi nhịp nên trùng chỗ chuyển ý | bắt buộc 🔻 | 🚫 *"chỗ chuyển ý"* đòi **ngữ nghĩa** — N3. **QĐ-4b** cũng ghi đè phần cho phép đổi nhịp |

> ⚠️ **Cả ba điều này hiện không chặn được bài nào.** Ngắt nhịp là ngắt theo **ranh giới
> từ**; chưa có bộ tách từ tiếng Việt thì mọi dòng 7 tiếng đều "cắt được" theo cả bảy kiểu.
> Bằng chứng: **100,00% bài đạt được gán nhịp chủ đạo `4/3`**. Đó là hiện vật đo đạc, không
> phải phát hiện về thơ. Xem §6B.2.

---

### 3.6. Sáu điều khổ và bố cục — S16 đến S21

| Mã | Nguyên văn | Phân loại | Phân tích |
|---|---|---|---|
| `S16` | Số dòng trong bài không hạn định về lượng, nhưng phải là bội của 4 | **quyền** | 📋 Cùng nội dung với F5 sau khi hợp nhất 18/09. Ràng buộc bội-4 do **H4** thi hành ở tầng 1, không phải ở đây |
| `S17` | Khổ phổ biến là 4 dòng; dùng được 2, 3, 5, 6 dòng | mô tả | 📋 Chữ *"phổ biến"* là thống kê, không phải yêu cầu. Không được biến thành tiêu chí |
| `S18` | Có thể viết liên hoàn, không chia khổ | **quyền** | 📋 Bài một khối liền vẫn hợp lệ — **58,02%** bài đạt là một khổ |
| `S19` | Triển khai theo mạch cảm xúc hoặc mạch tự sự | mô tả | 🚫 Đòi **hiểu nội dung** — N3 |
| `S20` | Có thể dùng điệp dòng, điệp khổ, điệp cấu trúc | **quyền** | 📋 Lặp lại **không phải lỗi**. Quan trọng: cấm mọi phép kiểm dạng "trùng lặp thì loại" |
| `S21` | Có thể kết mở | **quyền** | 📋 Không đòi dòng kết quy tụ |

**Năm trong sáu điều là quyền hoặc mô tả.** Vì vậy tầng 7 chỉ còn chặn được **một** thứ:
khổ rỗng — thứ duy nhất ở đây thực sự sai chứ không phải lựa chọn phong cách.

Tầng 7 chặn 0 bài, và **đó là đúng**, không phải tầng thừa.

---

### 3.7. Tổng kết kiểm kê

| Nhóm | Số điều | Đánh trượt được |
|---|---:|---:|
| Cứng (H) | 4 | **4** |
| Đã gỡ bỏ (F) | 5 | 0 |
| Mềm — bắt buộc | 6 | **3** (S2, S11, S14) |
| Mềm — quyền | 11 | 0 *(N2 cấm)* |
| Mềm — mô tả | 4 | 0 |
| **Tổng** | **30** | **7** |

| Vai trò | Số điều | Mã |
|---|---:|---|
| ⛔ Tiêu chí chặn | 7 | H1, H2, H3, **H4**, S2, S11, S14 |
| 🚫 Không kiểm được (N3) | 5 | F2, F4, S3, S15, S19 |
| 🔻 Bị quyết định ghi đè | 2 | S13, S15 *(S4 đã xoá 18/09)* |
| 📋 Chỉ ghi nhận | 18 | phần còn lại |

**Tổng số điều luật: 30** (trước 18/09 là 29; H4 được chủ dự án bổ sung).

---

## 4. Tám tầng

```
Tầng 0  CHUẨN HOÁ           tách khổ → dòng → tiếng               tiền đề, không phán
   │
Tầng 1  H3·H4   HÌNH THỨC +  ≥4 dòng VÀ số dòng là bội của 4      ⛔ CHẶN — trích §2
   │            SỐ DÒNG      (H4 bổ sung 18/09, luật cứng)
   │            ↓ chưa có dòng thì không đếm tiếng được
Tầng 2  H1+H2   ĐỘ DÀI       mọi dòng đúng 7 tiếng                 ⛔ CHẶN — trích §2
   │            ↓ dòng không đủ 7 tiếng thì P2/P4/P6 vô nghĩa
Tầng 3  F1-F5    ĐỐI CHIẾU ĐL ghi nhận nghi_duong_luat, KHÔNG chặn  ℹ️ GHI NHẬN — §3
   │
Tầng 4  S1·S2·S3  THANH LUẬT  MỌI dòng khớp khuôn bằng hoặc trắc    ⛔ CHẶN — QĐ-1, QĐ-2
Tầng 5  S6,S8–S12 VẦN         ≥1 cụm 4 dòng LIÊN TIẾP khớp một      ⛔ CHẶN — QĐ-3, QĐ-5,
                              trong 4 sơ đồ §5.2                       QĐ-7
Tầng 6  S13–S15   NHỊP        6a mọi dòng thuộc bảy kiểu; 6b có      ⛔ CHẶN — QĐ-4, QĐ-4b,
                              nhịp chủ đạo phủ mọi dòng                QĐ-6b (rỗng nghĩa nếu
                                                                       chưa có tách từ)
Tầng 7  S16–S21   KHỔ & BỐ CỤC khổ hợp lệ, không khổ rỗng           ⛔ CHẶN
```

**Dừng sớm ở tầng chặn là vấn đề đúng đắn, không phải tốc độ.** Tính khuôn trên một dòng
6 tiếng là gán cho tác giả một lựa chọn phong cách mà họ chưa hề thực hiện.

Tầng 7 gần như luôn đạt, vì S16–S21 hầu hết là quyền. Nó vẫn chạy và vẫn nộp bằng chứng.

---

## 5. Bằng chứng từng tầng

Mỗi bài mang dấu vết đủ 8 tầng, **kể cả tầng bị bỏ qua**.

```json
"tang": [
  {"so": 1, "ma": ["H3","H4"], "muc": "chan", "da_chay": true, "dat": true,
   "trich_luat": "Văn bản phải được phân dòng, từ 4 dòng trở lên. [H4: số dòng phải là bội của 4]",
   "bang_chung": "20 dòng — có phân dòng, và 20 = 4 × 5",
   "chi_tiet": {"so_dong": 20, "du_khi_chia_4": 0, "la_boi_cua_4": true,
                "co_phan_dong": true}},

  {"so": 2, "ma": ["H1","H2"], "muc": "chan", "da_chay": true, "dat": true,
   "trich_luat": "Mỗi dòng phải có đúng 7 tiếng; áp dụng toàn bộ dòng, không ngoại lệ",
   "bang_chung": "20/20 dòng đúng 7 tiếng; nhỏ nhất = lớn nhất = 7",
   "chi_tiet": {"so_tieng_tung_dong": [7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7,7],
                "so_dau_cau_da_loai": 14,
                "quy_tac_dem": "chỉ tính tiếng; dấu câu loại theo phân loại Unicode"}},

  {"so": 3, "ma": ["F1","F2","F3","F4","F5"], "muc": "ghi_nhan",
   "da_chay": true, "dat": true,
   "trich_luat": "Có niêm/đối/độc vận là được phép, không phải tiêu chí nhận diện thể (§3)",
   "bang_chung": "20 dòng — không đủ ba vế số dòng + độc vận + niêm",
   "chi_tiet": {"nghi_duong_luat": false,
                "F2_khong_kiem_duoc": "phép đối đòi so từ loại và ngữ nghĩa",
                "F4_khong_kiem_duoc": "bố cục Khai–Thừa–Chuyển–Hợp đòi hiểu nội dung"}},

  {"so": 4, "ma": ["S1","S2","S3"], "muc": "chan", "da_chay": true, "dat": true,
   "trich_luat": "P2, P4, P6 nên luân phiên bằng – trắc",
   "bang_chung": "20/20 dòng khớp khuôn; 0 dòng phá khuôn (QĐ-1, QĐ-2)",
   "chi_tiet": {"khuon_tung_dong": ["bang","trac","trac","bang","..."],
                "so_dong_pha_khuon": 0,
                "S3_khong_kiem_duoc": "P7 chọn có chủ đích — đòi ý đồ tác giả"}},

  {"so": 5, "ma": ["S6","S8","S9","S10","S11","S12"], "muc": "chan",
   "da_chay": true, "dat": true,
   "trich_luat": "Sơ đồ vần nên nhất quán trong phạm vi một khổ",
   "bang_chung": "sơ đồ aaxa|bbxb, nhất quán trong từng khổ; so vần theo âm đệm–âm chính–âm cuối",
   "chi_tiet": {"phan_tich_van_cuoi": [{"tieng":"xanh","am_dem":null,"am_chinh":"a","am_cuoi":"nh","thanh":"B"}],
                "so_do_tung_kho": ["aaxa","bbxb"], "lech_thanh": 2, "van_lung": [[3,5]]}},

  {"so": 6, "ma": ["S13","S14","S15"], "muc": "chan", "da_chay": true, "dat": true,
   "trich_luat": "Bảy kiểu nhịp của §6; nên có một nhịp chủ đạo (S14)",
   "bang_chung": "nhịp chủ đạo 4/3 phủ cả 20/20 dòng",
   "chi_tiet": {"nhip_chu_dao": "4/3",
                "nhip_kha_di_tung_dong": [["2/2/3","4/3"], ["4/3"], ["4/3","3/4"]],
                "nguon_nhip": "khai_bao",
                "S15_khong_kiem_duoc": "đổi nhịp trùng chỗ chuyển ý — đòi ngữ nghĩa"}},

  {"so": 7, "ma": ["S16","S17","S18","S19","S20","S21"], "muc": "chan",
   "da_chay": true, "dat": true,
   "trich_luat": "Số dòng không hạn định; có thể liên hoàn",
   "bang_chung": "5 khổ đều 4 dòng, không khổ rỗng"}
]
```

Bài trượt ở tầng 2 sẽ có tầng 3–7 mang `"da_chay": false` và
`"bang_chung": "bỏ qua vì tầng 2 đã chặn"` — **không giả vờ đã kiểm**.

Lưu ý tầng 3 mang `"muc": "ghi_nhan"`: nó **luôn** `dat = true` và không góp vào phán
quyết chung. Quan sát của nó nằm ở `chi_tiet["nghi_duong_luat"]`.

---

## 6. Bốn quyết định — ĐÃ CHỐT

Chủ dự án chốt ngày 17/09/2026. Nguyên tắc bao trùm:

> **Toàn bộ Rule đưa ra cần tuân thủ. Không được điều chỉnh để giữ lại số lượng bài đẹp.**

### QĐ-1 — S2 áp dụng lên TOÀN BỘ dòng ✅

**Nguyên văn quyết định:** *"phải áp dụng lên toàn bộ dòng của một bài thơ"*

Tiêu chí tầng 4: **mọi dòng** phải khớp khuôn bằng (P2 B, P4 T, P6 B) hoặc khuôn trắc
(P2 T, P4 B, P6 T). Không có ngưỡng phần trăm. Một dòng lệch là cả bài trượt tầng 4.

### QĐ-2 — Không cho phá khuôn ✅

**Nguyên văn quyết định:** *"sao lại phá khuôn; không được phá khuôn, phải tuân thủ toàn bộ
Rule đã có"*

Không có ngoại lệ "phá khuôn có chủ đích". Dòng ở trạng thái `pha` là trượt. S4 và S5 do đó đã bị xoá khỏi bảng luật 18/09; phần dưới không
còn việc để làm: không có phá khuôn thì không cần xét phá tập trung hay rải rác.

### QĐ-3 — Sơ đồ vần phải dựa trên ngữ âm tiếng Việt ✅

**Nguyên văn quyết định:** *"sơ đồ vần thì phải tìm lấy thông tin bằng ngôn ngữ tiếng Việt"*

**Chủ dự án đã duyệt cách phân tích sau** (ví dụ được chấp nhận ngày 17/09):

> `hoa` hiện cho vần `oa`, `ha` cho vần `a` — nhưng `oa` thực ra là **âm đệm** /w/ cộng
> **âm chính** /a/, nên quan hệ vần giữa hai tiếng phải xét lại cho đúng.

Nghĩa là phép so vần không được cắt phụ âm đầu rồi so phần còn lại như hiện nay. Phải phân
tích âm tiết theo đúng cấu trúc tiếng Việt rồi mới so.

Bảng `VAN_THONG` hiện tại gồm 10 lớp **do tôi tự liệt kê**, không có căn cứ ngữ âm — bị loại
bỏ. Thay bằng bảng dựng từ cấu trúc âm tiết. Nguồn bảng vần thông: xem QĐ-5.

### QĐ-4 — Nhịp phải theo đúng bảy kiểu của tài liệu ✅

**Nguyên văn quyết định:** *"phải tuân thủ các phần nhịp trong rule đề ra, không được phép
thay đổi nhịp"* · *"toàn bộ câu phải tuân thủ đúng nhịp — các nhịp trong Rule mới được chấp
nhận"*

**Tiêu chí tầng 6:** **mỗi dòng** phải ngắt được theo ít nhất một trong **bảy kiểu nhịp** ở
§6 của tài liệu, và **mọi chỗ ngắt phải rơi vào ranh giới từ**. Không kiểu nào khớp thì dòng
trượt, và cả bài trượt tầng 6.

Bảy kiểu được chấp nhận, không thêm kiểu nào khác:

| Nhịp | Hiệu quả theo tài liệu §6                   |
| ----- | ------------------------------------------------ |
| 4/3   | Cân bằng, kế thừa âm hưởng Đường luật |
| 3/4   | Hiện đại, mở về phía sau                   |
| 2/2/3 | Chia nhỏ, nhấn từng vế                       |
| 2/5   | Nhấn mạnh phần mở đầu dòng                |
| 5/2   | Dồn nén rồi buông ngắn                      |
| 1/6   | Nhấn cực mạnh một tiếng đầu               |
| 3/2/2 | Trúc trắc, tạo đột biến                    |

**Ví dụ do chủ dự án đưa ra, dùng làm ca kiểm thử chuẩn:**

```
Chiều rơi | chậm xuống | mái rêu xanh      2/2/3  ✅ mọi chỗ cắt trùng ranh giới từ
Chiều | rơi chậm xuống mái rêu xanh        1/6    ❌ xẻ đôi từ ghép "chiều rơi"
```

Việc này đòi tách từ tiếng Việt — xem QĐ-6. **Không có tách từ thì không cài được tầng 6.**

### QĐ-4b — S14 "nên có một nhịp chủ đạo" ✅

**Nguyên văn quyết định:** *"nên ưu tiên nhịp của bài thơ"*

**Tiêu chí mức bài:** phải **tồn tại ít nhất một kiểu nhịp tương thích với mọi dòng** của
bài. Kiểu đó là *nhịp chủ đạo*. Không tồn tại kiểu nào như vậy thì bài trượt tầng 6.

Cách đọc này được chọn vì nó **không cần ngưỡng phần trăm** — tránh được điều N1 cấm. Nói
"đa số dòng" thì phải định nghĩa đa số là bao nhiêu, mà tài liệu không nói. Nói "tồn tại một
kiểu phủ hết mọi dòng" thì là phép kiểm nhị phân, không có chỗ cho con số tuỳ tiện.

"Ưu tiên nhịp của bài thơ" còn quyết định cách chọn nhịp cho từng dòng: khi một dòng ngắt
được theo nhiều kiểu, **lấy kiểu trùng với nhịp chủ đạo của bài**, không lấy kiểu tiện tay.

```
Bài 4 dòng, nhịp khả dĩ từng dòng:
  D1: {2/2/3, 4/3}
  D2: {4/3}
  D3: {4/3, 3/4}
  D4: {4/3, 5/2}
  → giao của bốn tập = {4/3}  → nhịp chủ đạo là 4/3, bài ĐẠT tầng 6

  Nếu D2 chỉ ngắt được {3/4} thì giao rỗng → bài TRƯỢT tầng 6
```

---

### QĐ-6b — Phạm vi tầng 6: "chỉ cần tuân thủ bảy nhịp trong Rule" ✅

**Nguyên văn quyết định (17/09/2026):** *"về phần 6 thì thơ chỉ cần tuân thủ cái nhịp mà
tôi đưa ra này là được rồi"* — kèm nguyên văn §6 của tài liệu luật.

**Đã kiểm lại §6 tài liệu.** §6 gồm đúng hai thứ, không hơn: bảng **bảy** kiểu nhịp
(`4/3, 3/4, 2/2/3, 2/5, 5/2, 1/6, 3/2/2`) và ba điều S13, S14, S15. Không có kiểu nhịp thứ
tám ở bất kỳ chỗ nào khác trong tài liệu. Vậy **tập nhịp hợp lệ là tập ĐÓNG gồm bảy kiểu
trên** — đúng như QĐ-4 và QĐ-6 đã chốt. Quyết định này xác nhận lại, không mở thêm.

**Tầng 6 vì vậy chia làm hai phép kiểm, thi hành theo thứ tự:**

|    | Phép kiểm                                                                                | Nguồn                                                                       | Hiệu lực |
| -- | ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------- | ---------- |
| 6a | Mỗi dòng ngắt được theo**ít nhất một** trong bảy kiểu                     | QĐ-6b — chính là câu*"chỉ cần tuân thủ cái nhịp tôi đưa ra"* | ⛔ chặn   |
| 6b | Tồn tại**một** kiểu tương thích với **mọi** dòng — nhịp chủ đạo | QĐ-4b, đã chốt trước đó                                              | ⛔ chặn   |

6a là điều kiện cần của 6b: giao của các tập rỗng thì từng tập cũng phải khác rỗng trước đã.
Giữ tách rời để biên bản nói được bài hỏng ở đâu — *dòng 3 không ngắt được kiểu nào* khác
hẳn *mọi dòng đều hợp lệ nhưng không có kiểu chung*.

**QĐ-6b KHÔNG huỷ QĐ-4b.** Bạn đã chốt QĐ-4b bằng câu *"nên ưu tiên nhịp của bài thơ"* và
lần này không nói bỏ nó. Nếu ý bạn là **bỏ 6b, chỉ giữ 6a**, đó là sửa một dòng trong
`_tang6_nhip` — nói một câu là tôi gỡ. Tôi không tự gỡ, vì gỡ đi là nới luật, mà N1 cấm tôi
nới luật khi bạn chưa nói.

#### Cảnh báo bắt buộc đọc — 6a hiện là phép kiểm RỖNG NGHĨA

Ngắt nhịp là ngắt theo **ranh giới từ**, không phải theo vị trí tiếng. Chưa có bộ tách từ
tiếng Việt thì mọi dòng 7 tiếng đều "cắt được" thành 4/3, thành 3/4, thành 2/5… vì phép cắt
chỉ là đếm số. Tức là:

```
Không có tách từ  ->  nhip_kha_di_cua_dong() trả về CẢ BẢY kiểu cho MỌI dòng 7 tiếng
                  ->  6a luôn đạt, 6b luôn đạt (giao = cả bảy kiểu)
                  ->  tầng 6 KHÔNG loại được bài nào
```

Đây không phải lựa chọn của tôi mà là giới hạn đo lường, và nó đã được ghi ở §6B.2 và §6B.3.
Hệ quả thực tế, nói thẳng:

| Loại thơ                                                                             | Tầng 6 làm được gì                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thơ trong corpus** (`final_data_7_chu.jsonl`) — không có khai báo nhịp | Chỉ chặn được dòng**không đủ 7 tiếng**, mà tầng 1 đã chặn rồi. Thực chất **đi qua trắng**. Biên bản phải ghi `khong_kiem_duoc="thiếu bộ tách từ"`, **không được ghi là ĐẠT**. |
| **Thơ do mô hình sinh ra** — mô hình khai báo nhịp từng dòng           | Chặn thật: nhịp khai báo phải thuộc bảy kiểu (6a) và phải có kiểu chung (6b)                                                                                                                                            |

Vì vậy con số "bài đạt toàn bộ 8 tầng" trên corpus sẽ là con số **chưa qua tầng 6 thật sự**,
và báo cáo phải nói rõ câu đó ở ngay cạnh con số — không được để người đọc hiểu nhầm rằng
corpus đã qua kiểm nhịp.

---

### QĐ-7 — Tiêu chí CHẶN của tầng 5 ✅

**Nguyên văn quyết định (18/09/2026):** *"tiêu chí để có thể qua tầng 5 là trong bài phải có
ít nhất là 4 dòng liên tiếp có cấu trúc như thế ở cuối"* — kèm nguyên văn §5.2 tài liệu luật.

**Tiêu chí:** trượt một cửa sổ bốn dòng liên tiếp suốt cả bài; **chỉ cần MỘT cửa sổ** khớp
một trong bốn sơ đồ §5.2 là tầng 5 đạt.

| Sơ đồ | Tên tài liệu gọi |
|---|---|
| `aabb` | vần liền |
| `abab` | vần cách |
| `abba` | vần ôm |
| `aaxa` | vần ba dòng, kế thừa Đường luật |

Tập này **đóng**. Hai mục còn lại của §5.2 không phải sơ đồ thứ năm:

- *"Vần chân khổ liên kết"* (`K1 a a x a, K2 b b x b, K3 c c x c`) là `aaxa` lặp qua nhiều
  khổ, chữ cái đổi theo khổ. Cửa sổ bốn dòng bất kỳ của nó vẫn là `aaxa`.
- *"Vần hỗn hợp: phối nhiều sơ đồ trên trong cùng một bài"* chính là **lý do** tiêu chí chỉ
  đòi một cửa sổ. Đòi cả bài theo một sơ đồ duy nhất là cấm vần hỗn hợp — chặt hơn tài liệu
  ở đúng chỗ tài liệu cho phép.

**Khớp NGHIÊM NGẶT hai chiều.** Hai dòng cùng chữ cái thì bắt buộc hiệp vần, và hai dòng
khác chữ cái thì bắt buộc **không** hiệp; dòng mang `x` phải không hiệp với dòng nào trong
cửa sổ. Nếu chỉ đòi chiều thuận thì bốn dòng cùng một vần sẽ bị nhận nhầm là `aabb`.

**Cửa sổ vắt qua khổ được.** Quyết định nói *"trong bài"*, không nói *"trong một khổ"*.

**Không có ngưỡng phần trăm nào** ⇒ không phạm N1.

#### Hai hệ quả phải nói rõ

1. ~~**Bài dưới bốn dòng trượt tầng 5.**~~ **Hệ quả này đã hết hiệu lực từ 18/09.** Khi
   viết QĐ-7, H3 mới chỉ đòi từ hai dòng nên bài 2–3 dòng đi tới được tầng 5. Nay H3 đòi
   **≥ 4 dòng** và H4 đòi **bội của 4**, nên bài ngắn bị chặn ngay ở **tầng 1** — nhánh
   "dưới 4 dòng" trong tầng 5 không còn với tới được qua đường chạy bình thường.
2. **Khổ có quan hệ vần không bắc cầu không khớp sơ đồ nào.** Ví dụ ba dòng kết bằng
   `vang / vương / vuông`: vang~vương và vương~vuông, nhưng vang ≁ vuông (Trần Trọng Kim ghi
   rõ). Khổ ấy nhận nhãn `?` và không tính là khớp.

---

### 6.5. Ba chỗ quyết định CHẶT HƠN văn bản tài liệu — ghi nhận minh bạch

Ghi ở đây để mã nguồn và tài liệu không nói hai điều khác nhau. Đây là **chính sách của dự
án**; văn bản `Luat_Tho_That_Ngon_Tu_Do.md` giữ nguyên, không sửa một chữ.

| Tài liệu nói                                                                                                      | Quyết định dự án                                                          |
| -------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| *(S4 đã xoá 18/09/2026)* — không còn điều nào cho phép phá khuôn                   | QĐ-2: không cho phá khuôn — nay **không ghi đè điều nào**                   |
| S2:*"P2, P4, P6 **nên** luân phiên"* — chữ *nên*, nói ở mức dòng                                 | QĐ-1: bắt buộc, áp lên mọi dòng                                         |
| S13:*"Nhịp do **nghĩa** của dòng quyết định"*                                                         | QĐ-4: nhịp phải khớp một trong bảy kiểu, xét theo hình thức          |
| S13:*"**không cố định** cho toàn bài"* · S15: *"**đổi nhịp** nên trùng chỗ chuyển ý"* | QĐ-4b: phải tồn tại một nhịp chủ đạo phủ**mọi** dòng         |
| §6: bảng bảy nhịp không nói dòng*phải* thuộc kiểu nào                                                   | QĐ-6b/6a: mọi dòng phải ngắt được theo ít nhất một trong bảy kiểu |

Vì vậy thiết kế giữ **hai cờ phán quyết** (§8.1): `thuoc_the` trả lời theo tài liệu
(**H1–H4**, sau khi H4 được bổ sung 18/09), `dat` trả lời theo chuẩn dự án (toàn bộ các
tầng chặn). Cả hai con số cùng được báo cáo.

### 6.6. Hệ quả đo được — nêu thẳng, không dùng để phản đối

Bảng này nay là **số đo thật** trên toàn bộ 67.150 bản ghi, không còn là ước lượng.
Sinh lại: `python datalake/scripts/kiem_tra_toan_bo.py`.

| Cổng | Tiêu chí sau khi chốt | Vào | Qua | Chặn | % chặn |
|---|---|---:|---:|---:|---:|
| 1 | H3 ≥4 dòng **và** H4 bội của 4 | 62.034 | 57.366 | 4.668 | 7,52% |
| 2 | H1+H2: mọi dòng đúng 7 tiếng | 57.366 | 55.297 | 2.069 | 3,61% |
| 3 | F1–F5: **ghi nhận**, không chặn | 55.297 | 55.297 | 0 | 0,00% |
| **4** | QĐ-1 + QĐ-2: **mọi dòng** khớp khuôn | 55.297 | 24.726 | **30.571** | **55,29%** |
| 5 | QĐ-7: ≥1 cụm 4 dòng khớp §5.2 | 24.726 | **24.366** | 6.576 | 26,60% |
| 6 | QĐ-4b: có nhịp chủ đạo | 24.366 | 24.366 | 0 | 0,00% |
| 7 | Không khổ rỗng | 24.366 | 24.366 | 0 | 0,00% |

**Kết quả cuối: 24.366 bài đạt — 39,28%** trên 62.034 bài có nội dung.
`thuoc_the` (chỉ H1–H4): **55.297**.

Đây là hệ quả trực tiếp của yêu cầu *"tuân thủ toàn bộ Rule"*; plan này không tìm cách làm
nhẹ nó. Cổng 4 một mình chiếm **69,66%** toàn bộ bài trượt, và phần lớn số bài ấy **không
sai gì theo câu chữ tài liệu** — chúng trượt vì QĐ-1 và QĐ-2.

⚠️ **Cổng 6 chặn 0 bài không phải vì thơ đạt nhịp** mà vì tầng 6 đang rỗng nghĩa khi thiếu
bộ tách từ — xem cảnh báo ở QĐ-6b. Con số 24.366 là **chưa qua kiểm nhịp thật sự**.

---

## 6B. Hai hạng mục kỹ thuật mới do QĐ-3 và QĐ-4 kéo theo

Hai quyết định này không phải chỉnh tham số. Chúng đòi **dữ liệu ngôn ngữ tiếng Việt** mà dự
án hiện chưa có.

### 6B.1. Bảng vần tiếng Việt — phục vụ QĐ-3

Hiện trạng: `VAN_THONG` có 10 lớp tôi tự liệt kê, không có căn cứ ngữ âm. **Bị loại bỏ.**

#### Cấu trúc âm tiết tiếng Việt — cơ sở của phép so vần

Đây là mô tả chuẩn của ngữ âm học tiếng Việt, không phải thứ tôi tự đặt:

```
ÂM TIẾT = Thanh điệu + [Âm đầu] + VẦN
VẦN      = [Âm đệm] + Âm chính + [Âm cuối]
```

| Thành phần | Nội dung                                                                            |
| ------------ | ------------------------------------------------------------------------------------ |
| Âm đầu    | phụ âm mở đầu, có thể vắng (`anh`, `oa`)                                 |
| Âm đệm    | bán nguyên âm /w/, viết là`o` hoặc `u` — `hoa`, `quê`, `tuy`       |
| Âm chính   | nguyên âm đơn hoặc nguyên âm đôi (`iê/yê/ia`, `uô/ua`, `ươ/ưa`) |
| Âm cuối    | phụ âm cuối`m n ng nh p t c ch` hoặc bán nguyên âm `i/y`, `o/u`         |
| Thanh điệu | ngang · huyền · sắc · hỏi · ngã · nặng                                     |

#### Ba thứ cần dựng

1. **Bộ phân tích âm tiết** — trả về đủ năm thành phần trên. Đây là thứ thay cho `van_cua()`
   hiện tại vốn chỉ cắt âm đầu rồi lấy phần còn lại.
2. **Phép so vần chính** — hai tiếng hiệp vần chính khi trùng **âm chính** và **âm cuối**.
3. **Bảng vần thông** — các cặp âm chính hoặc âm cuối được thi pháp truyền thống cho phép
   hiệp. **Đây là phần cần nguồn** (điều kiện nghiệm thu H), vì các sách thi pháp không hoàn
   toàn thống nhất. Xem QĐ-5.

Cấu trúc âm tiết ở trên là dữ kiện ngôn ngữ học phổ thông nên tôi cài được ngay; riêng bảng
vần thông thì không được tự liệt kê.

### 6B.2. Nhịp — phục vụ QĐ-4 và QĐ-4b

Theo QĐ-6, phần này **không kéo thêm công cụ ngôn ngữ nào**. Chỉ dùng bảy kiểu nhịp trong
tài liệu.

```python
def nhip_chu_dao(nhip_kha_di_tung_dong: tuple[frozenset[str], ...]) -> str | None:
    """Nhịp chủ đạo = kiểu nhịp tương thích với MỌI dòng của bài (QĐ-4b).

    Trả None nghĩa là không tồn tại nhịp nào phủ hết bài -> trượt tầng 6.
    Khi có nhiều kiểu cùng phủ hết, ưu tiên theo thứ tự liệt kê ở §6 tài liệu.
    """
    if not nhip_kha_di_tung_dong:
        return None
    giao = set(nhip_kha_di_tung_dong[0])
    for tap in nhip_kha_di_tung_dong[1:]:
        giao &= tap
    for ten in NHIP_TAI_LIEU:            # giữ đúng thứ tự tài liệu
        if ten in giao:
            return ten
    return None
```

Tập nhịp khả dĩ của một dòng đến từ đâu:

| Nguồn              | Cách lấy                                                                                                             |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| Mô hình sinh thơ | Mô hình khai báo nhịp cùng bản nháp; hệ thống kiểm khai báo thuộc bảy kiểu                               |
| Corpus có sẵn     | Không có khai báo — mọi dòng 7 tiếng nhận cả bảy kiểu, và bằng chứng ghi rõ chỉ kiểm được số học |

### QĐ-5 — Nguồn bảng vần ✅

**Nguyên văn quyết định:** *"tìm kiếm về cái phần bảng vần của Việt Nam hiện nay, bạn có thể
tìm kiếm thêm thông tin nhé"*

Chủ dự án **cho phép tra cứu tài liệu ngữ âm và thi pháp tiếng Việt** để dựng bảng vần.

Quy trình bắt buộc, theo điều kiện nghiệm thu H:

1. Tra cứu, thu thập bảng vần và bảng vần thông đang dùng trong tiếng Việt hiện nay.
2. **Trình nguồn cho chủ dự án duyệt trước khi đưa vào mã** — ghi rõ tài liệu, tác giả,
   phần nào lấy từ đâu.
3. Chỗ nào các nguồn không thống nhất thì nêu ra để chủ dự án chọn, không tự quyết.
4. Bảng vào mã dưới dạng hằng số có chú thích nguồn ngay tại chỗ.

**Vẫn cấm:** tôi tự liệt kê bảng vần theo cảm tính như bản `VAN_THONG` hiện tại.

Phần **cấu trúc âm tiết** (âm đầu · âm đệm · âm chính · âm cuối · thanh điệu) là dữ kiện ngôn
ngữ học phổ thông, cài được ngay mà không cần chờ duyệt nguồn.

### QĐ-6 — Nguồn thông tin về nhịp ✅

**Nguyên văn quyết định:** *"về nhịp thì hãy lấy thông tin trong Rule đã được tôi thiết lập
sẵn, tránh lan man"*

**Chốt:** tầng 6 chỉ dùng **bảy kiểu nhịp trong §6 của tài liệu luật**. Không thêm thư viện
tách từ, không thêm từ điển tiếng Việt bên ngoài.

#### Hệ quả phải nói thẳng

Tài liệu cho **bảy kiểu nhịp** nhưng không cho **ranh giới từ**. Thiếu ranh giới từ thì phép
kiểm "chỗ ngắt có trùng ranh giới từ không" không thực hiện được, và mọi dòng 7 tiếng đều
chia được về mặt số học theo cả bảy kiểu (4+3 = 7, 3+4 = 7, 2+2+3 = 7…).

Vì vậy tầng 6 có hai chế độ, tuỳ nguồn gốc bài thơ:

| Nguồn bài                         | Nhịp có được khai báo không                            | Tầng 6 làm gì                                                                                                                                               |
| ----------------------------------- | ------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Thơ do mô hình sinh ra** | Có — mô hình khai báo nhịp từng dòng cùng bản nháp | **Chặn thật**: kiểm nhịp khai báo thuộc bảy kiểu, và tồn tại nhịp chủ đạo phủ mọi dòng (QĐ-4b)                                        |
| **Corpus có sẵn**           | Không — tệp không có trường nhịp                      | **Ghi nhận**: mọi dòng 7 tiếng đều thoả về mặt số học; bằng chứng ghi rõ *"không có khai báo nhịp nên chỉ kiểm được số học"* |

Đây là giới hạn của dữ liệu, không phải chỗ nới luật. Bằng chứng của tầng 6 phải **nói rõ đã
kiểm được gì và chưa kiểm được gì**, đúng nguyên tắc N3.

> **Lợi ích của quyết định này:** giữ `rule.py` thuần, không kéo `underthesea` hay `pyvi` vào
> tầng `application` — vốn bị `.importlinter` cấm và sẽ buộc phải dựng thêm port và adapter.

---

## 7. Chạy lại từ đầu — quy tắc số liệu

Theo N4:

1. **Không con số nào được chép từ báo cáo cũ.** Mọi bảng trong báo cáo mới phải sinh từ
   một lượt chạy trên toàn bộ 67.150 bản ghi bằng bản `rule.py` mới.
2. **So sánh bản cũ với bản mới bằng cách chạy song song trong cùng một lượt**, không so
   với hằng số nhớ được. Cách làm đã có sẵn ở `datalake/scripts/so_sanh_ban_luat.py`.
3. **Đối soát bắt buộc** mỗi lượt chạy, như `kiem_tra_toan_bo.py` đang làm:
   `số dòng đọc == số bản ghi == đạt + trượt + rỗng`, và `số lần gọi luật == đạt + trượt`.
   Sai một đẳng thức thì script dừng, không in số liệu.
4. **Kiểm chứng độc lập** bằng `doi_soat_ket_qua.py`: phân hoạch id, lấy mẫu chạy lại,
   nhất quán nội tại.

---

## 8. Kiểu dữ liệu và tương thích ngược

### 8.1. Hai cờ phán quyết, không gộp làm một

```python
thuoc_the: bool   # chỉ H1–H4 — câu trả lời của TÀI LIỆU LUẬT (§2)
dat: bool         # qua mọi tầng CHẶN — câu trả lời của DỰ ÁN
```

Lý do giữ cả hai: §9 Bước 4 nói thẳng các lựa chọn mềm *"không dùng để loại bài"*. Nếu chỉ
còn một cờ gộp, bộ kiểm sẽ trả lời sai câu hỏi *"bài này có thuộc thể thất ngôn tự do
không"*. Báo cáo corpus từ nay nêu **cả hai con số**.

### 8.2. Không đổi chữ ký hàm nào

13 hàm public hiện có (`dem_tieng`, `thanh_cua`, `van_cua`, `hiep_van`, `khuon_cua_dong`,
`suy_so_do_van`, `tach_tieng`, `tach_kho`, `doc_so`, `van_lung_cua_dong`,
`phoi_khuon_cua_kho`, `nhip_hop_le`, `mo_ta_luat`) giữ nguyên, trở thành ruột của các tầng.

`kiem_tra_bai_tho(van_ban)` giữ nguyên chữ ký, thêm tham số tuỳ chọn `ho_so`.
`PoemVerdict` giữ nguyên mọi trường cũ, thêm `tang`, `thuoc_the`, `tang_dung_lai`, `ho_so`.

Ba nơi đang dùng `rule.py` — `poem_verifier.py`, `adapters/tools/poem_check.py`,
`tests/unit/application/test_rule.py` — không phải sửa chữ ký để chạy được. Riêng phần
**ngữ liệu** của test thì có phải sửa: bài mẫu 2 dòng nay trượt H4, xem §11.

---

## 9. Lộ trình

| Pha   | Việc                                                                                                                                                                                                            | Tiêu chí hoàn thành                                                                                                                                    |
| ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T0    | ✅ Chốt QĐ-1 → QĐ-4                                                                                                                                                                                          | Đã ghi ở §6                                                                                                                                            |
| T0b   | ✅ Chốt QĐ-4b, QĐ-5, QĐ-6                                                                                                                                                                                    | Đã ghi ở §6 và §6B                                                                                                                                   |
| T1b-1 | ✅ **XONG 18/09** — nguồn: Trần Trọng Kim, *Việt thi* I-6 (Wikisource); đối chiếu: Bùi Kỷ, *Quốc văn cụ thể* 1950. Hồ sơ: `docs/Nguon_Bang_Van_Thong.md`. Chủ dự án đã duyệt. | 73 cạnh từ nguồn + 4 cạnh 🔶 SD-2 = 77 cạnh / 62 vần; mỗi cạnh truy được về câu chữ trong sách |
| T1b-1b | ✅ **XONG 18/09** — `VAN_THONG` (lớp rời nhau) → `CAP_VAN_THONG` (đồ thị 77 cạnh); `hiep_van` tra cạnh; `suy_so_do_van` bỏ gom cụm bắc cầu | Test `test_hiep_van_KHONG_bac_cau_dung_nhu_nguon` khoá đúng câu `ang ≁ uông` của tác giả |
| T1b-2 | Dựng bộ phân tích âm tiết 5 thành phần                                                                                                                                                                   | Test:`hoa` tách được âm đệm `o` + âm chính `a`; `quê` tách được âm đệm `u` + âm chính `ê`                                  |
| T1b-3 | Nạp bảng vần đã duyệt, bỏ`VAN_THONG` cũ                                                                                                                                                                | Mỗi lớp vần có chú thích nguồn ngay tại chỗ                                                                                                       |
| T1c   | Cài tầng 6 hai bước 6a/6b theo QĐ-6b, chỉ dùng bảy kiểu trong tài liệu (QĐ-6)                                                                                                                        | Test: bốn dòng có nhịp khả dĩ giao nhau ở`4/3` thì nhịp chủ đạo là `4/3`; giao rỗng thì trượt tầng 6                                 |
| T1    | Kiểu`KetQuaTang`, bảng 8 tầng, bảng phân loại 30 điều luật                                                                                                                                            | Test: mọi mã trong`LUAT` thuộc **đúng một** tầng; mọi điều loại *quyền* **không** nằm trong tiêu chí đạt của tầng nào |
| T2    | Chuyển phép kiểm hiện có vào tầng, chưa đổi hành vi                                                                                                                                                   | 45 test cũ xanh nguyên                                                                                                                                   |
| T3    | Chạy tuần tự, dừng sớm, sinh bằng chứng từng tầng                                                                                                                                                       | Test: bài hỏng tầng 2 thì tầng 3–7 có`da_chay = False`                                                                                            |
| T4    | Cài tiêu chí tầng 4–7 theo QĐ đã chốt                                                                                                                                                                   | Test: một dòng lệch khuôn thì trượt tầng 4 (QĐ-1, QĐ-2); một dòng không ngắt được theo bảy kiểu nhịp thì trượt tầng 6 (QĐ-4)      |
| T5    | `poem_verifier` + biên bản sửa nêu rõ **trượt ở tầng nào**, trích luật                                                                                                                       | Biên bản ghi tầng, mã luật, nguyên văn tiêu chí                                                                                                   |
| T6    | `kiem_tra_toan_bo.py` xuất dấu vết 8 tầng cho từng bài                                                                                                                                                   | `bai_dat.jsonl` có đủ 8 tầng mỗi bài                                                                                                               |
| T7    | **Chạy lại từ đầu toàn bộ corpus** bằng bản mới                                                                                                                                                  | Đối soát khớp; báo cáo cập nhật bằng số mới sinh                                                                                                |

---

## 10. Nghiệm thu

| # | Điều kiện                                                                                                                                                                               |
| - | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| A | Mọi tiêu chí chặn trong mã đều**trích được** một câu trong tài liệu luật, ghi ở trường `trich_luat`                                                             |
| B | Không điều luật loại*quyền* nào xuất hiện trong tiêu chí đạt của bất kỳ tầng nào — có test cưỡng chế                                                              |
| C | S3 và S15 được ghi công khai là*không kiểm được*, không lặng lẽ cho qua                                                                                                    |
| D | Mọi con số trong báo cáo mới đến từ lượt chạy mới; so sánh cũ–mới bằng chạy song song                                                                                    |
| E | Đối soát`số bản ghi == đạt + trượt + rỗng` khớp; kiểm chứng độc lập 0 lệch                                                                                              |
| F | 45 test cũ của`rule.py` xanh nguyên; toàn dự án xanh                                                                                                                               |
| G | Không tiêu chí nào được nới ra sau khi nhìn số bài trượt. Mọi thay đổi tiêu chí phải có lý do ngữ âm hoặc trích dẫn tài liệu, ghi vào nhật ký quyết định |
| H | Bảng vần và từ điển tách từ có nguồn ghi rõ, không phải do tôi tự liệt kê                                                                                                 |

---

## 11. Phụ lục — trạng thái hiện tại

Cột *"khi lập plan"* là 17/09, cột *"hiện tại"* đo ngày 18/09 sau khi thi công.

| Hạng mục | Khi lập plan | Hiện tại |
|---|---|---|
| `rule.py` | 816 dòng | **2.238 dòng**, 46 hàm |
| Số điều luật | 29 | **30** (H4 bổ sung 18/09) |
| Tiêu chí chặn | 5 | **7** |
| Test riêng của `rule.py` | 45 | **126** (`test_rule.py` 37 + `test_rule_tang.py` 52, có tham số hoá) |
| Test toàn dự án | 357 | **438** |
| Bài đạt trên corpus | — | **24.366** / 62.034 (39,28%) |

**Nơi dùng `rule.py`:** `poem_verifier.py` · `adapters/tools/poem_check.py` ·
`tests/unit/application/test_rule*.py`

**Script liên quan:**

| Script | Việc |
|---|---|
| `datalake/scripts/kiem_tra_toan_bo.py` | Chạy lại corpus, sinh mọi tệp kết quả và `TONG_HOP.md` |
| `datalake/scripts/doi_soat_ket_qua.py` | Kiểm chứng độc lập: phân hoạch id, lấy mẫu chạy lại |
| `datalake/scripts/so_sanh_ban_luat.py` | So hai bản luật bằng cách chạy song song |
| `datalake/scripts/doi_soat_tai_lieu.py` | **Chặn số liệu bịa trong tài liệu** — đối chiếu mọi con số trong ba tài liệu với nguồn sinh ra nó. Đã cắm vào CI |

---

## 12. SỬA `rule.py` — 21/09/2026, phép lùi âm đầu (T8)

**Duyệt:** chủ dự án, 21/09/2026. **Băm đổi từ** `9f808d59…` **sang** bản mới ở
`tests/architecture/test_rule_dong_bang.py`.

### 12.1. Lỗi

Cắt âm đầu theo khớp **dài nhất** là đúng cho hầu hết ca (`ngh` phải thử trước `ng`),
nhưng sai ở một chỗ có thật:

```
van_cua("gìn")  = "n"     ← sai, phải là "in"     ("gi" + "n", đúng ra "g" + "ìn")
van_cua("nhìn") = "in"
hiep_van("gìn", "nhìn")  ->  False        ❌
```

Một bài gieo `gìn` với `nhìn` bị chấm là **không hiệp vần** — sai ở tầng 5, chạy hằng
ngày. Chú thích §5 của `rule.py` đã lường trước ca này (*"'gì' không phải là 'gi' +
rỗng, mà là 'g' + 'ì'"*) nhưng phép lùi cũ chỉ chạy khi phần dư **rỗng**, không chạy khi
phần dư **không có nguyên âm**. `gian`, `giết`, `giữ` đúng chỉ vì phần dư (`an`, `êt`,
`ư`) tình cờ hợp lệ.

### 12.2. Sửa

Thêm `_am_dau_kha_di`: ưu tiên khớp dài nhất **mà phần dư còn nguyên âm**; không có thì
lùi về quy tắc cũ. Dùng chung cho `van_cua` và `phan_tich_am_tiet`.

Tiêu chí là *"có nguyên âm"* chứ **không** phải *"tra được trong bảng âm chính"* — hẹp
hơn thì an toàn hơn, và nới tay ở đây là đổi kết quả của **mọi** phép so vần có `gi`
cùng một lúc. Test `tests/unit/application/test_van_gin.py` ghim cả hai chiều: ca hỏng
phải sửa được, và `gian`/`giết`/`giữ`/`giờ`/`giàu`/`nghiêng`/`quà`/`chuyện`/`thuở` phải
giữ nguyên kết quả cũ.

**Phạm vi cố ý hẹp.** Không kèm bảng âm chính, không kèm phép kiểm âm tiết hợp lệ, không
kèm H5 — QĐ-TTS-1 (`docs/Plan_TTS_Tieu_De_Reviewer.md` §3) đã đóng phần đó. Một lượt sửa
file đóng băng mang đúng một lý do, để sau còn tra được thay đổi nào gây hệ quả nào.

### 12.3. Đo lại toàn corpus — N4

Chạy `datalake/scripts/kiem_tra_toan_bo.py` trên toàn bộ **67.150** bản ghi:

| Thống kê | Trước | Sau | Chênh |
| -------- | ----- | --- | ----- |
| `bai_dat` | 24.366 | **24.366** | **0** |
| `cum_co_van_chan` | 189.415 | 189.422 | **+7** |
| `bai_dat_co_van_lung` | 13.532 | 13.533 | +1 |
| sơ đồ `axax` | 37.312 | 37.314 | +2 |
| sơ đồ `aaxa` | 32.145 | 32.147 | +2 |
| sơ đồ `xaxa` | 26.805 | 26.806 | +1 |
| sơ đồ `aaaa` | 19.921 | 19.923 | +2 |
| sơ đồ `xaax` | 17.079 | 17.081 | +2 |
| sơ đồ `xxaa` | 17.002 | 17.004 | +2 |
| sơ đồ `xaaa` | 7.393 | 7.391 | −2 |
| sơ đồ `axxa` | 4.200 | 4.198 | −2 |

Đọc bảng này cho đúng: **không bài nào đổi phán quyết**. Các cụm chỉ **chuyển từ sơ đồ ít
vần sang sơ đồ nhiều vần hơn** — đó là lý do `xaaa` và `axxa` giảm trong khi tổng
`cum_co_van_chan` tăng. Hướng thay đổi đúng như đã lường trước khi chạy: phép sửa chỉ
khiến những cặp trước đây *không* được nhận ra là hiệp vần nay được nhận ra; không cặp
nào đang hiệp bị mất.

`doi_soat` của lượt đo: `khop = true`, không lỗi.

### 12.4. Tài liệu đã cập nhật theo số mới

`doi_soat_tai_lieu.py` đỏ 20 chỗ sau khi đo — **đúng như cơ chế phải làm**, vì ba tài
liệu còn trích số cũ. Đã cập nhật: `Report_stage_of_rule.md`,
`Report_analyst_17-09_pass-notpass.md`, và mục 11 của chính tài liệu này (`rule.py`:
2.200 → **2.238 dòng**, 45 → **46 hàm**). Chạy lại: ✅ *"Mọi con số trong tài liệu đều
truy được về nguồn."*
