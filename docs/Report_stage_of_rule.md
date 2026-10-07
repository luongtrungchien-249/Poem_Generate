# KIẾN TRÚC TẦNG CỦA `rule.py`

**Cập nhật:** 18/09/2026 · **Đối tượng:** `src/application/rule.py` — 2.238 dòng. 46 hàm
**Tài liệu luật gốc:** `docs/Luat_Tho_That_Ngon_Tu_Do.md`
**Corpus đo:** `datalake/dataraw/final_data_7_chu.jsonl` — 67.150 bản ghi
**Sinh lại số liệu:** `python datalake/scripts/kiem_tra_toan_bo.py`
**Đối soát tài liệu:** `python datalake/scripts/doi_soat_tai_lieu.py`

> Mọi con số trong tài liệu này đều truy được về `datalake/analysis/tong_hop.json`
> hoặc về chính `rule.py`, và có script cưỡng chế điều đó.

---

## 0. Kết quả một trang

|                                                   |                  Số bài |
| ------------------------------------------------- | ------------------------: |
| Tổng bản ghi                                    |                    67.150 |
| Không có nội dung                              |                     5.116 |
| Có nội dung, đã qua`rule.py`                |                    62.034 |
| **Thuộc thể** — theo tài liệu (H1–H4) |          **55.297** |
| **ĐẠT** — qua cả bảy tầng             | **24.366** (39,28%) |
| **TRƯỢT**                                 |          **37.668** |

### Phễu bảy cổng

| Cổng                                  | Mức           | Điều luật |   Vào |              Qua |            % qua |            Chặn |          % chặn |        Còn lại | Đánh dấu |
| -------------------------------------- | -------------- | ------------ | -----: | ---------------: | ---------------: | ---------------: | ---------------: | ---------------: | ----------: |
| **1. Hình thức và số dòng** | ⛔ chặn       | H3, H4       | 62.034 |           57.366 |           92,48% |  **4.668** |            7,52% |           92,48% |          — |
| 2. Độ dài dòng                     | ⛔ chặn       | H1, H2       | 57.366 |           55.297 |           96,39% |            2.069 |            3,61% |           89,14% |          — |
| 3. Đối chiếu Đường luật         | ℹ️ ghi nhận | F1–F5       | 55.297 |           55.297 |          100,00% |                0 |            0,00% |           89,14% |       4.288 |
| **4. Thanh luật**               | ⛔ chặn       | S1–S3       | 55.297 |           24.726 | **44,71%** | **30.571** | **55,29%** |           39,86% |          — |
| 5. Vần                                | ⛔ chặn       | S6, S9–S12  | 24.726 | **24.366** |           98,54% |              360 |            1,46% | **39,28%** |          — |
| 6. Nhịp                               | ⛔ chặn       | S13–S15     | 24.366 |           24.366 |          100,00% |                0 |            0,00% |           39,28% |          — |
| 7. Khổ và bố cục                   | ⛔ chặn       | S16–S21     | 24.366 |           24.366 |          100,00% |                0 |            0,00% |           39,28% |          — |

**Ba mẫu số khác nhau, đừng lẫn:**

- **% qua** và **% chặn** — mẫu số là số bài **đi vào cổng đó**. Đây là độ khắt khe của
  **riêng** cổng ấy.
- **Còn lại** — mẫu số là **toàn bộ 62.034 bài có nội dung**. Đường sống sót tích luỹ.
- **Đánh dấu** — số bài cổng ghi nhận có phát hiện nhưng **vẫn cho đi tiếp**.

Đọc theo cột *% chặn*, thứ tự khắt khe là: **cổng 4 (55,29%)** ≫ cổng 1 (7,52%) ≫
cổng 2 (3,61%) ≫ cổng 5 (1,46%). Ba cổng còn lại không chặn bài nào.

**Cổng 4 một mình chiếm 99,86% toàn bộ bài trượt** (30.571 / 30.931 bài thuộc thể mà
chưa đạt). Sau các thay đổi ngày 18/09, đây là chỗ duy nhất còn đáng bàn nếu muốn thêm
dữ liệu.

**Đối soát:** `67.150 dòng đọc = 67.150 bản ghi = 67.150 id duy nhất` ✅ ·
`67.150 = 24.366 đạt + 37.668 trượt + 5.116 rỗng` ✅

---

## 1. Vấn đề mà kiến trúc tầng giải quyết

Bản đầu của `rule.py` trả về một giá trị `dat` duy nhất. Khi một bài trượt, không ai trả
lời được ba câu hỏi:

1. Nó hỏng ở đâu?
2. Những phần còn lại đã được kiểm chưa, hay chưa bao giờ chạy tới?
3. Điều luật nào sinh ra phán quyết đó?

Yêu cầu gốc của chủ dự án:

> *"Một bài thơ cần vượt qua toàn bộ các tầng (toàn bộ các Rule) mới được coi là bài thơ
> này pass. Từng bài thơ cần thể hiện rõ xem vượt qua từng tầng thế nào — kiểu có bằng
> chứng nó vượt tầng đó thế nào."*

---

## 2. Toàn cảnh — dòng chảy một bài thơ

```
                         kiem_tra_bai_tho(van_ban)
                                    │
        ┌───────────────────────────┴───────────────────────────┐
        │  CHUẨN BỊ CHUNG  (§9)  — chạy MỘT lần, bảy tầng dùng chung
        │   tach_kho()          văn bản  ->  các khổ             │
        │   _phan_tich_dong()   mỗi dòng ->  BaoCaoDong          │
        │                       (tiếng, thanh, khuôn, vần cuối)  │
        │   suy_so_do_van_toan_bai()                             │
        └───────────────────────────┬───────────────────────────┘
                                    │
   ┌────────────────────────────────▼────────────────────────────────┐
   │ T1 Hình thức+số   H3·H4  ≥4 dòng VÀ bội của 4             ⛔ CHẶN │
   │ T2 Độ dài dòng   H1·H2   MỌI dòng đúng 7 tiếng           ⛔ CHẶN │
   │ T3 Đối chiếu ĐL  F1–F5   ghi nhận nghi_duong_luat      ℹ️ GHI NHẬN│
   │ T4 Thanh luật    S1–S3   MỌI dòng khớp khuôn B·T         ⛔ CHẶN │
   │ T5 Vần        S6,S9–S12  ≥1 cụm 4 dòng CÓ vần chân       ⛔ CHẶN │
   │ T6 Nhịp          S13–S15 có nhịp chủ đạo phủ cả bài      ⛔ CHẶN │
   │ T7 Khổ & bố cục  S16–S21 không có khổ rỗng               ⛔ CHẶN │
   └────────────────────────────────┬────────────────────────────────┘
                                    │
                             PoemVerdict
                    ┌───────────────┴───────────────┐
              thuoc_the                            dat
          (chỉ T1+T2 = H1–H4)              (các tầng CHẶN)
        câu trả lời của TÀI LIỆU        câu trả lời của DỰ ÁN
             55.297 bài                      24.366 bài
```

### 2.1. Vì sao dừng sớm

Dừng sớm **không phải để chạy nhanh**. Tính khuôn thanh trên một dòng 6 tiếng là gán cho
tác giả một lựa chọn phong cách mà họ chưa hề thực hiện — con số sinh ra sẽ **sai mà
trông như đúng**. Tầng sau chỉ có nghĩa khi tầng trước đã đạt.

Hệ quả bắt buộc: tầng chưa chạy mang `da_chay = False`, **không** phải `dat = False`.
Trộn hai chuyện này là cách nhanh nhất để báo cáo nói dối.

### 2.2. Vì sao phân tích một lần rồi dùng chung

Nếu mỗi tầng tự tách tiếng, bảy tầng có thể hiểu khác nhau về cùng một dòng thơ, và khi
số liệu lệch sẽ không ai truy được lệch từ đâu. `_phan_tich_dong()` chạy đúng một lần cho
mỗi dòng, ra một `BaoCaoDong` bất biến, rồi bảy tầng cùng đọc vật đó.

### 2.3. Hai mức tầng: CHẶN và GHI NHẬN

```python
if kq.muc == "chan" and not kq.dat:
    tang_dung_lai = kq.so
    return False          # dừng cả dây chuyền

# và khi tổng hợp:
dat = all(kq.dat for kq in ket_qua_tang if kq.muc == "chan")
```

Tầng `ghi_nhan` quan sát rồi cho đi tiếp. Phát hiện của nó nằm trong `chi_tiet`, **không**
góp vào phán quyết. Nếu không có cơ chế này thì mọi quan sát đều biến thành bản án, và
đó chính là lỗi đã xảy ra với tầng 3 — xem §7.3.

---

## 3. BẢNG ĐẦY ĐỦ 26 ĐIỀU LUẬT

Bảng này sinh ra từ chính `LUAT`, `LOAI_DIEU_MEM` và `TANG` trong `rule.py`, nên không
thể lệch khỏi mã.

| Mã           | Nguyên văn                                                                         | Tầng | Loại        | Phân loại mềm | Vai trò trong bộ kiểm     |
| ------------- | ------------------------------------------------------------------------------------ | :---: | ------------ | ---------------- | ---------------------------- |
| **H1**  | Mỗi dòng phải có đúng 7 tiếng                                                 |   2   | cứng        | —               | ⛔**TIÊU CHÍ CHẶN** |
| **H2**  | H1 áp dụng cho toàn bộ các dòng, không ngoại lệ                             |   2   | cứng        | —               | ⛔**TIÊU CHÍ CHẶN** |
| **H3**  | Văn bản phải được phân dòng, từ 4 dòng trở lên                           |   1   | cứng        | —               | ⛔**TIÊU CHÍ CHẶN** |
| **H4**  | Số dòng trong bài phải là bội của 4                                           |   1   | cứng        | —               | ⛔**TIÊU CHÍ CHẶN** |
| **F1**  | Không áp dụng luật niêm giữa các dòng                                        |   3   | đã gỡ bỏ | —               | 📋 chỉ ghi nhận            |
| **F2**  | Không yêu cầu cặp đối bắt buộc                                               |   3   | đã gỡ bỏ | —               | 🚫 không kiểm được      |
| **F3**  | Không yêu cầu độc vận cho toàn bài                                           |   3   | đã gỡ bỏ | —               | 📋 chỉ ghi nhận            |
| **F4**  | Không yêu cầu Khai – Thừa – Chuyển – Hợp                                    |   3   | đã gỡ bỏ | —               | 🚫 không kiểm được      |
| **F5**  | Số dòng không giới hạn về lượng, nhưng phải là bội của 4                |   3   | đã gỡ bỏ | —               | 📋 chỉ ghi nhận            |
| **S1**  | P1, P3, P5 có thể tự do về thanh; có thể dùng thêm vần lưng ở P4 hoặc P5 |   4   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S2**  | P2, P4, P6 nên luân phiên bằng – trắc                                          |   4   | mềm         | bắt buộc       | ⛔**TIÊU CHÍ CHẶN** |
| **S3**  | P7 gắn với vần, cần chọn có chủ đích                                        |   4   | mềm         | bắt buộc       | 🚫 không kiểm được      |
| **S6**  | Vần chủ đạo là vần chân, đặt ở P7                                          |   5   | mềm         | mô tả          | 📋 chỉ ghi nhận            |
| **S9**  | Có thể dùng vần bằng, vần trắc hoặc phối hợp                               |   5   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S10** | Chấp nhận vần thông, không yêu cầu vần chính tuyệt đối                   |   5   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S11** | Sơ đồ vần nên nhất quán trong phạm vi một khổ                              |   5   | mềm         | bắt buộc       | ⛔**TIÊU CHÍ CHẶN** |
| **S12** | Có thể đổi vần khi sang khổ mới                                               |   5   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S13** | Nhịp do nghĩa của dòng quyết định                                             |   6   | mềm         | mô tả          | 📋 chỉ ghi nhận 🔻         |
| **S14** | Nên có một nhịp chủ đạo                                                       |   6   | mềm         | bắt buộc       | ⛔**TIÊU CHÍ CHẶN** |
| **S15** | Đổi nhịp nên trùng chỗ chuyển ý                                              |   6   | mềm         | bắt buộc       | 🚫 không kiểm được 🔻   |
| **S16** | Số dòng trong bài không hạn định về lượng, nhưng phải là bội của 4    |   7   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S17** | Khổ phổ biến là 4 dòng; dùng được 2, 3, 5, 6 dòng                          |   7   | mềm         | mô tả          | 📋 chỉ ghi nhận            |
| **S18** | Có thể viết liên hoàn, không chia khổ                                         |   7   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S19** | Triển khai theo mạch cảm xúc hoặc mạch tự sự                                 |   7   | mềm         | mô tả          | 🚫 không kiểm được      |
| **S20** | Có thể dùng điệp dòng, điệp khổ, điệp cấu trúc                          |   7   | mềm         | **quyền** | 📋 chỉ ghi nhận            |
| **S21** | Có thể kết mở                                                                    |   7   | mềm         | **quyền** | 📋 chỉ ghi nhận            |

**Đọc bảng:**

| Ký hiệu                    | Nghĩa                                                                                                           |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| ⛔**TIÊU CHÍ CHẶN** | Điều luật này thực sự đánh trượt bài                                                                  |
| 🚫 không kiểm được      | Đòi ý đồ tác giả hoặc ngữ nghĩa — ghi công khai vào`chi_tiet` (N3)                                |
| 📋 chỉ ghi nhận            | Thuộc phạm vi tầng, được đo và báo cáo, nhưng không sinh phán quyết                                |
| 🔻                           | Bị một quyết định của dự án**ghi đè** (chặt hơn tài liệu)                                    |
| **quyền**             | Tài liệu dùng chữ*"có thể"*,*"chấp nhận"*, *"tự do"* — **N2 cấm dùng để đánh trượt** |

### 3.1. Bốn mã đã XOÁ khỏi bảng luật (18/09/2026)

Số hiệu **để trống vĩnh viễn**. Không đánh số lại — dồn `S6` lên thành `S4` sẽ khiến mọi
tham chiếu cũ trong báo cáo, test và dữ liệu đã xuất trỏ sai điều luật mà không ai biết.
Hỏng im lặng là kiểu hỏng tệ nhất.

| Mã               | Nguyên văn cũ                                               | Vì sao xoá                                                                                                                                                                                                             |
| ----------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| ~~**S4**~~ | *"Có thể phá khuôn khi dụng ý biểu đạt đòi hỏi"* | QĐ-2 đã cấm phá khuôn. Chủ dự án:*"Xóa mã S4, S5 luôn đi vì chưa có cho bài hiện tại"*                                                                                                              |
| ~~**S5**~~ | *"Phá khuôn nên tập trung ở dòng cần nhấn"*          | Không còn đối tượng — cấm phá khuôn thì không còn gì để "tập trung"                                                                                                                                     |
| ~~**S7**~~ | *"Có thể dùng thêm vần lưng ở P4 hoặc P5"*           | **Gộp vào S1**. Vần lưng là quyền về vị trí *trong một dòng*, cùng loại với tự do thanh ở P1/P3/P5 — không nói gì về quan hệ vần *giữa các dòng*, vốn là việc của tầng 5        |
| ~~**S8**~~ | *"Bài có thể không gieo vần"*                           | QĐ-7b đòi mỗi cụm bốn dòng phải có vần chân — tức là loại đúng bài không gieo vần. Giữ S8 thì bảng luật vừa cho phép vừa cấm cùng một chuyện, và**vi phạm N2 ngay trong tầng 5** |

Hai hệ quả kiến trúc:

- **Xoá S4 làm `GHI_DE_BOI_QUYET_DINH` từ 3 mục xuống 2.** S4 là điều duy nhất QĐ-2 ghi
  đè; không còn S4 thì QĐ-2 thôi là quyết định đi ngược tài liệu, thành tiêu chí thẳng.
  Đây là **bớt mâu thuẫn, không phải bớt chặt chẽ** — tiêu chí tầng 4 không đổi một chữ.
- **Xoá S8 làm tầng 5 không ghi đè điều nào.** Cùng lý do.

### 3.2. Chỉ 7 trong 26 điều thực sự đánh trượt bài

| Mã     | Tầng | Vì sao điều này chặn được                                                          |
| ------- | :---: | ------------------------------------------------------------------------------------------ |
| `H3`  |   1   | Ràng buộc**cứng** — tài liệu §2 gọi là điều kiện nhận diện thể        |
| `H4`  |   1   | Ràng buộc**cứng** — *"số dòng phải là bội của 4, không có ngoại lệ"* |
| `H1`  |   2   | Ràng buộc**cứng**                                                                 |
| `H2`  |   2   | Ràng buộc**cứng** — nói rõ H1 không có ngoại lệ                            |
| `S2`  |   4   | Mềm, chữ*"nên"* →**QĐ-1** nâng thành bắt buộc                               |
| `S11` |   5   | Mềm, chữ*"nên"* →**QĐ-7 + QĐ-7b** cho nó một tiêu chí đo được          |
| `S14` |   6   | Mềm, chữ*"nên"* →**QĐ-4b**; nhưng tầng 6 hiện rỗng nghĩa, xem §7.6        |

Ba trong bảy điều này (`S2`, `S11`, `S14`) **không tự nó chặn được** — tài liệu chỉ nói
*"nên"*, không cho tiêu chí đo được. Chúng chặn được là nhờ một quyết định của dự án. Đó
là lý do báo cáo luôn nêu song song `thuoc_the` (55.297) và `dat` (24.366).

**Bốn điều cứng H1–H4 chặn được ngay từ câu chữ tài liệu.** 19 điều còn lại không đánh
trượt bài nào. Chúng vẫn được đo và ghi vào biên bản.

### 3.3. Năm điều máy không kiểm được — và không giấu

| Mã     | Nguyên văn                                                  | Vì sao không kiểm được                                                |
| ------- | ------------------------------------------------------------- | --------------------------------------------------------------------------- |
| `F2`  | Không yêu cầu cặp đối bắt buộc                        | Phép đối là quan hệ**từ loại và ngữ nghĩa** giữa hai dòng |
| `F4`  | Không yêu cầu Khai – Thừa – Chuyển – Hợp             | Bố cục đòi**hiểu nội dung**                                     |
| `S3`  | P7 gắn với vần, cần chọn**có chủ đích**        | Đòi**ý đồ tác giả**                                            |
| `S15` | Đổi nhịp nên trùng**chỗ chuyển ý**              | Đòi**ngữ nghĩa**                                                  |
| `S19` | Triển khai theo**mạch cảm xúc** hoặc mạch tự sự | Đòi**hiểu nội dung**                                              |

Cả năm được ghi thẳng vào `chi_tiet` của tầng tương ứng dưới khoá `<mã>_khong_kiem_duoc`.
Đây là nguyên tắc **N3**: không lặng lẽ cho qua.

`F2` và `F4` là lý do hàm mang tên `nghi_la_duong_luat()` — tài liệu đòi bốn vế, máy chỉ
kiểm được ba.

### 3.4. Hai điều bị quyết định của dự án ghi đè 🔻

| Mã     | Tài liệu nói                                                                | Dự án quyết                                                        |
| ------- | ------------------------------------------------------------------------------ | --------------------------------------------------------------------- |
| `S13` | *"Nhịp do nghĩa của dòng quyết định"* — không cố định toàn bài | **QĐ-4 + QĐ-4b**: đòi một nhịp chủ đạo phủ mọi dòng |
| `S15` | *"Đổi nhịp nên trùng chỗ chuyển ý"*                                  | **QĐ-4b**: đòi một nhịp chủ đạo                         |

Cả hai đều về **nhịp**. Ghi trong `GHI_DE_BOI_QUYET_DINH`, và test
`test_moi_ghi_de_deu_tro_ve_mot_dieu_luat_co_that` bắt buộc mỗi mục trỏ về một điều luật
có thật. Đây là **chính sách của dự án**, không phải cách đọc tài liệu.

> Trước 18/09 bảng này có ba mục; `S4` rời khỏi bảng khi chính S4 bị xoá. Bảng ghi đè
> phải rỗng đúng chỗ không còn mâu thuẫn — ghi bừa một mục không còn đối tượng là **báo
> một mâu thuẫn không tồn tại**.

### 3.5. Tám điều loại QUYỀN — không bao giờ được đánh trượt

`S1` · `S9` · `S10` · `S12` · `S16` · `S18` · `S20` · `S21`

Nguyên tắc **N2**: trượt vì tác giả dùng đúng một quyền tài liệu cho phép là mâu thuẫn tự
thân.

Ví dụ rõ nhất là **S1**, và nó cho thấy hai cách thi hành một quyền:

```
"P1, P3, P5 có thể tự do"  ->  bằng SỰ VẮNG MẶT của mã. Không dòng nào trong
                               rule.py đọc P1/P3/P5 để phán quyết.
"có thể dùng vần lưng"     ->  ĐO rồi ghi vào chi_tiet, không phán quyết.
```

Nếu S1 *có* mã kiểm thì mới là đã vi phạm S1.

Test `test_khong_dieu_QUYEN_nao_lam_tieu_chi_chan` cưỡng chế điều này.

### 3.6. Năm điều F — đã gỡ bỏ, KHÔNG phải điều kiện loại trừ

`F1` · `F2` · `F3` · `F4` · `F5` nằm ở §3 tài liệu, tiêu đề *"Điều bị loại bỏ khỏi thể"*.
Chúng nói thể này **không đòi** niêm, **không đòi** đối, **không đòi** độc vận, **không
giới hạn** số dòng ở 4 hoặc 8.

Đọc ngược năm điều này thành *"có các thứ đó thì bị loại"* đã làm tầng 3 loại oan 4.288
bài. Chi tiết ở §7.3.

---

## 4. Luật là DỮ LIỆU, không phải mã

Đây là quyết định kiến trúc quan trọng nhất của file.

| Bảng             | Vị trí        | Nội dung                                                      |
| ----------------- | --------------- | -------------------------------------------------------------- |
| `LUAT`          | §1, dòng 51   | 26 điều luật: H1–H4, F1–F5, S1–S3, S6, S9–S21           |
| `LOAI_DIEU_MEM` | §1b, dòng 154 | Xếp 17 điều mềm thành`bat_buoc` / `quyen` / `mo_ta` |
| `TANG`          | §1c, dòng 190 | Bảy tầng, mỗi tầng một`DinhNghiaTang`                   |

```python
@dataclass(frozen=True, slots=True)
class DinhNghiaTang:
    so: int
    ten: str
    ma_luat: tuple[str, ...]          # MỌI điều luật thuộc tầng
    tieu_chi_tu: tuple[str, ...]      # điều luật THỰC SỰ sinh phán quyết
    khong_kiem_duoc: tuple[str, ...]  # điều đòi ý đồ hoặc ngữ nghĩa
    muc: MucChan                      # "chan" | "ghi_nhan"
    trich_luat: str                   # NGUYÊN VĂN câu luật làm căn cứ
```

### 4.1. Ba trường tách rời nhau, và vì sao

`ma_luat` ⊇ `tieu_chi_tu` ⊎ `khong_kiem_duoc`.

Nếu gộp ba trường này làm một, mã nguồn sẽ ngầm tuyên bố đã kiểm đủ mọi điều trong phạm
vi tầng — một lời nói dối im lặng. Tách ra thì biên bản mỗi bài ghi thẳng
`F2_khong_kiem_duoc`, và người đọc biết chính xác phần nào còn treo.

Tầng 3 là ví dụ rõ nhất: `ma_luat = (F1…F5)` nhưng `tieu_chi_tu = ()` — tầng có phạm vi
rộng mà **không sinh phán quyết nào**.

### 4.2. `trich_luat` — mỗi tiêu chí phải trích được từ tài liệu

Nguyên tắc **N1**: *không có chữ trong tài liệu thì không được có tiêu chí.*

Lý do có nguyên tắc này: trong một bản plan trước, một ngưỡng *"≥50% dòng khớp khuôn"*
được đặt ra và con số 0,5 được chọn **vì nó giữ lại 84,82% corpus**. Đó là uốn luật cho
vừa dữ liệu. Test `test_khong_tang_nao_dat_nguong_phan_tram_tu_bia` cấm mọi con số phần
trăm xuất hiện trong `trich_luat`, để chuyện đó không lặp lại một cách im lặng.

### 4.3. `HAM_KIEM_CUNG` — bảng luật và mã nguồn phải tương ứng

```python
HAM_KIEM_CUNG: dict[str, str] = {
    "H1": "kiem_tra_bai_tho -> ViPham(ma='H1') cho từng dòng lệch 7 tiếng",
    "H2": "kiem_tra_bai_tho duyệt TOÀN BỘ dòng, không có nhánh bỏ qua",
    "H3": "_tang1_hinh_thuc -> ViPham(ma='H3') khi văn bản dưới 4 dòng",
    "H4": "_tang1_hinh_thuc -> ViPham(ma='H4') khi số dòng không chia hết cho 4",
}
```

Test `test_moi_luat_cung_deu_co_ham_kiem_tuong_ung` đòi
`set(HAM_KIEM_CUNG) == MA_CUNG`. Thêm một luật cứng mà quên viết hàm kiểm thì test đỏ.

Chú ý mục **H2**: nó mô tả một **cấu trúc vòng lặp**, không phải một câu `if`. H2 là điều
luật về *lượng từ* (∀), nên nó được thi hành bằng việc mã duyệt hết mọi dòng và không có
nhánh miễn trừ. Vì thế **không bao giờ có `ViPham(ma="H2")`** — và `ma_luat_bi_vi_pham`
trong `tong_hop.json` không có H2, đúng như thiết kế.

---

## 5. Kiểu dữ liệu kết quả

### 5.1. `KetQuaTang`

```python
@dataclass(frozen=True, slots=True)
class KetQuaTang:
    so: int
    ten: str
    ma_luat: tuple[str, ...]
    muc: MucChan
    da_chay: bool          # FALSE = chưa kiểm, KHÔNG phải "đã kiểm và trượt"
    dat: bool
    trich_luat: str
    bang_chung: str                    # một câu NGƯỜI đọc kiểm lại được
    chi_tiet: Mapping[str, object]     # số liệu MÁY đọc được
    vi_pham: tuple[ViPham, ...]
```

Hai trường bằng chứng tách đôi là cố ý: `bang_chung` in ra biên bản cho người và cho mô
hình sửa bài; `chi_tiet` cho script thống kê. Một trường không phục vụ tốt cả hai.

### 5.2. `ViPham` — một lỗi, có địa chỉ

```python
ma: str            # mã điều luật bị phạm
dong: int | None   # dòng số mấy; None = lỗi mức bài
ky_vong: str       # cần gì
thuc_te: str       # đang có gì
goi_y: str         # sửa theo hướng nào
```

Bốn trường này rút ra từ các kiểu hỏng của vòng tự sửa: *"Sai rồi, viết lại đi"* gần như
vô dụng, còn *"D3 thừa 1 tiếng"* thì mô hình sửa được ngay.

`goi_y` cố ý **không đưa câu chữ thay thế** — bộ kiểm phán, mô hình sửa; đưa sẵn câu thay
thế là bộ kiểm đang viết thơ hộ. Và với luật cứng về **số dòng** (H3, H4), `goi_y` còn
cấm thẳng việc thêm/bớt dòng: sửa số dòng nghĩa là **xoá hoặc viết thêm một câu thơ**,
tức là đổi nội dung tác phẩm. Chủ dự án: *"không được sửa nội dung cho thêm hay xóa nội
dung thơ, phải giữ nguyên nội dung thơ"*.

### 5.3. `PoemVerdict` — hai cờ, cố ý không gộp

```python
v.thuoc_the      # chỉ T1+T2 (H1–H4)  -> câu trả lời của TÀI LIỆU §2   55.297
v.dat            # các tầng CHẶN      -> câu trả lời của DỰ ÁN         24.366
v.tang           # dấu vết đủ bảy tầng
v.tang_dung_lai  # trượt thì dừng ở tầng nào
```

Tài liệu §2 nói H1–H4 là *"điều kiện cần và đủ"*. Dự án chặt hơn ở ba chỗ (QĐ-1, QĐ-2,
QĐ-4b). Gộp hai câu trả lời làm một sẽ khiến mã nguồn ngầm sửa tài liệu.

---

## 6. Bốn quy ước mà cả bảy hàm tầng đều tuân

|   | Quy ước                                                                                             | Vì sao                                                                                        |
| - | ----------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| 1 | **Chữ ký giống nhau** — nhận dữ liệu đã phân tích sẵn, trả về một `KetQuaTang` | Bảy tầng không thể hiểu khác nhau về cùng một dòng                                   |
| 2 | **Không tầng nào gọi tầng khác**                                                          | Thứ tự do`kiem_tra_bai_tho` điều khiển; bỏ một tầng không làm gãy tầng còn lại |
| 3 | **Luôn nộp bằng chứng, kể cả khi đạt**                                                  | Yêu cầu gốc:*"thể hiện rõ vượt qua từng tầng thế nào"*                           |
| 4 | **Ghi công khai điều không kiểm được** (N3)                                             | Ghi khoá`<mã>_khong_kiem_duoc` vào `chi_tiet` thay vì lặng lẽ cho qua                |

---

## 7. BẢY TẦNG — luật nào, kiểm thế nào, bao nhiêu bài qua

| Tầng                          | Dòng trong file |
| ------------------------------ | ---------------- |
| 1. Hình thức và số dòng   | 1430–1536       |
| 2. Độ dài dòng             | 1539–1637       |
| 3. Đối chiếu Đường luật | 1640–1707       |
| 4. Thanh luật                 | 1710–1809       |
| 5. Vần                        | 1812–1919       |
| 6. Nhịp                       | 1922–1992       |
| 7. Khổ và bố cục           | 1995–2035       |
| `kiem_tra_bai_tho`           | 2038–2179       |

---

### 7.1. Tầng 1 — HÌNH THỨC VÀ SỐ DÒNG

|                              |                                                                               |
| ---------------------------- | ----------------------------------------------------------------------------- |
| **Điều luật**       | H3, H4 — cả hai đều là tiêu chí chặn                                  |
| **Tiêu chí**         | số dòng ≥ 4**và** số dòng % 4 == 0 ⟹ số dòng ∈ {4, 8, 12, …} |
| **Mức**               | ⛔ CHẶN                                                                      |
| **Vào / Qua / Chặn** | 62.034 / 57.366 /**4.668**                                              |

```python
n = len(cac_dong)
du = n % 4
co_phan_dong = n >= 4      # H3
boi_cua_bon  = du == 0     # H4
dat = co_phan_dong and boi_cua_bon
```

**Vì sao cần cả hai:** `0 % 4 == 0`, nên **H4 một mình không bắt được bài rỗng** — H3 mới
là điều chặn nó. Ngược lại H3 một mình cho qua bài 5, 6, 7 dòng. Hai điều bù nhau.

**H4 không chọi với F5 và S16:**

|         | Nói về              | Nội dung                                    |
| ------- | --------------------- | -------------------------------------------- |
| F5, S16 | **lượng**     | không có trần, không có sàn cố định |
| H4      | **hình dạng** | phải chia hết cho 4                        |

Tập hợp lệ `{4, 8, 12, 16, …}` vừa vô hạn vừa là bội của 4 — hai vế cùng đúng. Vì vậy F5
và S16 **không** nằm trong `GHI_DE_BOI_QUYET_DINH`: không có mâu thuẫn nào để ghi.

**H4 là ràng buộc CỨNG nên nó vào cả cờ `thuoc_the`.** Một bài 6 dòng nay *không còn
thuộc thể*, chứ không phải chỉ "không đạt chuẩn dự án". Đo được: `thuoc_the` giảm
**59.437 → 55.297**.

#### Ai bị chặn — 4.668 bài

| Dư khi chia 4 | Số bài | Tỷ lệ |
| -------------: | -------: | ------: |
|              2 |    2.043 |  43,77% |
|              3 |    1.388 |  29,73% |
|              1 |    1.237 |  26,50% |

|   Số dòng |      Số bài |          Tỷ lệ |
| ----------: | ------------: | ---------------: |
| **6** | **943** | **20,20%** |
|           3 |           548 |           11,74% |
|           7 |           502 |           10,75% |
|           5 |           473 |           10,13% |
|          10 |           309 |            6,62% |
|          14 |           243 |            5,21% |

**655 bài** vi phạm thêm H3 (dưới 4 dòng); chỉ **2 bài** bị H3 bắt mà không phạm H4.

Dạng bị loại nhiều nhất là **bài 6 dòng** — một phần năm. Nếu sau này muốn nhận khổ 6
dòng (S17 có nhắc *"dùng được khổ 2, 3, 5, 6 dòng"*), đó là chỗ cần xem lại trước tiên.

#### Biên bản của cổng này KHÔNG gợi ý sửa bài

Bản trước ghi *"bớt 2 dòng để về 4, hoặc thêm 2 dòng để lên 8"*. Đó là bảo người ta
**xoá một câu thơ**, hoặc **viết thêm một câu không có trong bài**. H4 là luật cứng: sai
là sai, và đó là phán quyết cuối. Với thơ do mô hình sinh, ràng buộc này thuộc về **đề
bài** (*"viết N dòng, N là bội của 4"*), không phải về vòng sửa một bản nháp đã có.

---

### 7.2. Tầng 2 — ĐỘ DÀI DÒNG

|                              |                                                                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **Điều luật**       | H1, H2                                                                                                                            |
| **Nguyên văn**       | *"Mỗi dòng phải có đúng 7 tiếng. Ràng buộc này áp dụng cho toàn bộ các dòng của bài, không có ngoại lệ."* |
| **Tiêu chí**         | **Mọi** dòng đúng 7 tiếng                                                                                              |
| **Mức**               | ⛔ CHẶN                                                                                                                          |
| **Vào / Qua / Chặn** | 57.366 / 55.297 /**2.069** (7.645 dòng hỏng)                                                                              |

```python
hong = [bc for bc in bao_cao if bc.so_tieng != SO_TIENG_MOI_DONG]
dat = not hong
```

Một dòng lệch là cả bài trượt — chủ dự án đã đính chính rõ: *"Chỉ cần một dòng 6 đến 8
tiếng sẽ làm hỏng cả bài thơ nên là bài này hỏng."*

Trung bình **3,7 dòng hỏng mỗi bài trượt**.

#### Chỗ khó thật sự nằm ở `tach_tieng()`, không ở tầng

Đếm tiếng **không** phải đếm từ cách nhau bởi dấu cách. Theo §2.1 tài liệu: dấu câu không
tính là tiếng, và chữ số phải quy về **cách đọc** — `1975` → *một nghìn chín trăm bảy
mươi lăm* = 7 tiếng.

Chính tài liệu tự mâu thuẫn: §2.1 nói tiếng *"tương ứng với đơn vị viết cách nhau bởi dấu
cách"*, nhưng lại cho ví dụ `"ra-đi-ô"` = 3 tiếng — trong khi đó là **một** đơn vị cách
nhau bởi dấu cách. Quyết định: **âm tiết là đơn vị đếm**, tách theo dấu cách chỉ là bước
đầu.

**🩸 Lỗi đã trả giá.** Bản trước liệt kê dấu câu bằng tay và **thiếu `—`, `–`**, khiến
một dòng 6 tiếng bị đếm thành 7 và **PASS oan** — sai theo hướng nguy hiểm nhất. Nay nhận
diện theo **phân loại Unicode**:

```python
def _la_dau_cau(ky_tu: str) -> bool:
    if ky_tu == _GACH_NOI:          # ngoại lệ DUY NHẤT
        return False
    return unicodedata.category(ky_tu).startswith(("P", "S"))
```

Gạch nối `-` là ngoại lệ duy nhất vì nó **mang thông tin tách âm tiết**. Lý do trong chú
thích: *"danh sách liệt kê luôn thiếu"*.

`chi_tiet` ghi `so_dau_cau_da_loai` và `quy_tac_dem` — nói *"dấu không tính"* mà không
đưa số thì người đọc phải tin suông; đưa số thì kiểm lại được.

**Vì sao đứng trước tầng 4:** P2/P4/P6 chỉ có nghĩa trên dòng đủ 7 tiếng.
`khuon_cua_dong()` trả `"khong_xac_dinh"` cho dòng sai số tiếng, và tỷ lệ khuôn không
tính chúng vào mẫu số.

---

### 7.3. Tầng 3 — ĐỐI CHIẾU ĐƯỜNG LUẬT ⚠️ ĐÃ SỬA

|                              |                                                                                                                                                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Điều luật**       | F1–F5                                                                                                                                                                                                         |
| **Nguyên văn (§3)** | *"Việc một bài thất ngôn tự do vẫn có niêm, có đối, có độc vận là **được phép**. Nhưng đó là **lựa chọn của tác giả, không phải tiêu chí nhận diện thể**."* |
| **Tiêu chí**         | **KHÔNG CÓ** — `tieu_chi_tu = ()`                                                                                                                                                                   |
| **Mức**               | ℹ️ GHI NHẬN                                                                                                                                                                                                 |
| **Vào / Qua / Chặn** | 55.297 / 55.297 /**0** · đánh dấu **4.288**                                                                                                                                                    |

Đây là **tầng ghi nhận duy nhất** trong bảy tầng. Mọi thứ về nó đều là ngoại lệ:
`dat=True` hard-coded, `vi_pham=()` luôn luôn, không chặn bài nào theo thiết kế.

#### 🩸 Lỗi đã sửa — nghiêm trọng nhất của dự án

Bản trước đặt tầng này là `muc="chan"` và **loại 4.288 bài**, mỗi bài mang tiếng *"vi
phạm F3"* — một điều luật thật ra chỉ nói rằng độc vận **không bắt buộc**.

Chủ dự án chỉ ra: *"là thể thơ tự do thì không bị ràng buộc về số dòng, bao nhiêu dòng
cũng được"*.

**Sai ở đâu:** §3 mang tiêu đề *"Điều bị loại bỏ khỏi thể"*. F1–F5 là những **ràng buộc
đã được gỡ bỏ**. Đọc thành *"có các thứ đó thì bị loại"* tức là **biến một câu nới thành
một câu cấm**.

#### Hai phần tài liệu mâu thuẫn nhau — nói rõ chứ không giấu

|                        |                                                                                            |
| ---------------------- | ------------------------------------------------------------------------------------------ |
| **§3**          | Có niêm/đối/độc vận là được phép,**không phải tiêu chí nhận diện** |
| **§9 Bước 2** | Nếu 4 hoặc 8 dòng + độc vận + niêm + đối thì thuộc Đường luật               |

Chọn theo §3 vì ba lẽ: (1) §3 nói thẳng về *tiêu chí nhận diện thể*, đúng câu hỏi đang
đặt ra; (2) F5 phủ định trực tiếp con số 4/8 mà §9 Bước 2 dựa vào; (3) chủ dự án — tác
giả của tài liệu — đã xác nhận cách đọc này.

Ngay cả khi theo §9 Bước 2 thì tầng cũng **không được chặn**, vì tài liệu đòi **bốn** vế
mà `nghi_la_duong_luat()` chỉ kiểm được **ba** (số dòng ∈ {4,8}, độc vận, niêm). Phép đối
là quan hệ từ loại và ngữ nghĩa. Chặn dựa trên ba phần tư điều kiện nghĩa là loại oan —
và đó là lý do hàm giữ chữ ***nghi*** trong tên.

#### Số phận 4.288 bài bị đánh dấu — đo trên corpus

|                                              |        Số bài |
| -------------------------------------------- | --------------: |
| Cổng 3 đánh dấu`nghi_duong_luat`       | **4.288** |
| … cuối cùng**ĐẠT** cả bảy tầng | **4.288** |
| … trượt ở cổng 4 (thanh luật)          |     **0** |
| … trượt ở cổng 5 (vần)                 |     **0** |

Toàn bộ qua cổng 4 — hợp lý, vì Đường luật vốn chặt về niêm luật. Trước QĐ-7b có 2.096
bài trượt cổng 5 vì độc vận `aaaa` không nằm trong bốn sơ đồ §5.2; nay không còn.

---

### 7.4. Tầng 4 — THANH LUẬT

|                              |                                                                                    |
| ---------------------------- | ---------------------------------------------------------------------------------- |
| **Điều luật**       | S1, S2, S3                                                                         |
| **Nguyên văn (S2)**  | *"P2, P4, P6 **nên** luân phiên bằng – trắc để tạo nhạc tính."* |
| **Tiêu chí**         | **Mọi** dòng khớp khuôn bằng `B T B` hoặc trắc `T B T`            |
| **Mức**               | ⛔ CHẶN                                                                           |
| **Vào / Qua / Chặn** | 55.297 / 24.726 /**30.571** (160.828 lần phạm S2)                          |

```python
pha = [bc for bc in bao_cao if bc.khuon == "pha"]
dat = not pha
```

**Đây là nút cổ chai của cả hệ thống: 30.571 bài — 99,86% toàn bộ bài trượt.**

#### Hai chỗ dự án chặt hơn tài liệu

| Tài liệu                                                                      | Quyết định dự án                                      |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| S2 dùng chữ***nên***, nói ở mức dòng                             | **QĐ-1**: bắt buộc, áp lên **mọi** dòng |
| ~~S4~~ (đã xoá): ***có thể*** phá khuôn khi dụng ý đòi hỏi | **QĐ-2**: không cho phá khuôn                    |

Phải nói thẳng: nếu đọc theo đúng câu chữ tài liệu, phần lớn trong 30.571 bài này **không
sai gì cả**. Chúng trượt vì QĐ-1 và QĐ-2. Con số này là cái giá đo được của yêu cầu
*"tuân thủ toàn bộ Rule"*.

Không có ngưỡng phần trăm nào ⟹ không phạm N1.

#### Phân bố dòng phá khuôn — lệch phải rất mạnh

| Số dòng phá |        Số bài |          Tỷ lệ |
| -------------: | --------------: | ---------------: |
|    **1** | **6.162** | **20,16%** |
|              2 |           4.295 |           14,05% |
|              3 |           3.626 |           11,86% |
|              4 |           3.005 |            9,83% |
|              5 |           2.382 |            7,79% |
|             6+ |          11.101 |           36,31% |

Trung bình 5,26 dòng/bài, nhưng **trung vị tỷ lệ là 40%** và **một phần năm số bài chỉ
lệch đúng một dòng**. Nới QĐ-1 thành *"cho phép 1 dòng phá"* sẽ cho 6.162 bài qua cổng 4.

*(Đối soát: `Σ k·n(k) = 160.828` — khớp đúng `ma_luat_bi_vi_pham["S2"]`.)*

#### Khuôn: hai trong tám tổ hợp

> Khuôn bằng: P2 B, P4 T, P6 B · Khuôn trắc: P2 T, P4 B, P6 T

Bộ ba (P2,P4,P6) có 2³ = 8 tổ hợp, chỉ **2** hợp lệ.

**`"khong_xac_dinh"` ≠ `"pha"`.** Dòng không đủ 7 tiếng trả `khong_xac_dinh`, vì *"gọi
một dòng sai luật là phá khuôn tức là gán cho nó một lựa chọn phong cách mà tác giả chưa
hề thực hiện"*. Cùng nguyên tắc với `da_chay=False` ≠ `dat=False`, áp xuống mức dòng.

**Cái bẫy Unicode được xử lý tường minh:** phân rã NFD thì **ă â ê ô ơ ư** cũng mang dấu
tổ hợp, nhưng đó là **dấu nền**, không phải dấu thanh. Không tách hai loại thì `"ơ"` bị
đọc nhầm thành tiếng có dấu và **toàn bộ tầng 4 sai**.

#### Bảng 16 tổ hợp khuôn của cụm bốn dòng (§6c, tài liệu §4.4)

Mỗi ô là **ba giá trị thanh ở P2, P4, P6 của một dòng** — `B-T-B` = khuôn bằng,
`T-B-T` = khuôn trắc. P1/P3/P5 không có mặt (S1 cho tự do), P7 cũng không (thuộc về vần).

**Bảng là tập ĐẦY ĐỦ** (2⁴ = 16), nên nó **không loại bài nào**: cụm nào có mọi dòng khớp
khuôn thì tất yếu nằm trong bảng. Vì vậy nó vào tầng 4 với vai trò **mô tả** —
`tieu_chi_tu` vẫn là `("S2",)`, và có test cấm biến nó thành tiêu chí chặn thứ hai.

Phân bố thật trên **73.106 cụm** của 24.366 bài đạt:

|  # | Tổ hợp (D1·D2·D3·D4, mỗi dòng P2-P4-P6) | Số cụm | Tỷ lệ |                                   |
| -: | ---------------------------------------------- | -------: | ------: | --------------------------------- |
| 10 | `T-B-T  B-T-B  B-T-B  T-B-T`                 |   41.227 |  56.39% | ← mẫu**đảo** §4.3      |
|  7 | `B-T-B  T-B-T  T-B-T  B-T-B`                 |   27.982 |  38.28% | ← mẫu**cổ điển** §4.3 |
|  6 | `B-T-B  T-B-T  B-T-B  T-B-T`                 |      999 |   1.37% |                                   |
| 11 | `T-B-T  B-T-B  T-B-T  B-T-B`                 |      561 |   0.77% |                                   |
|  2 | `B-T-B  B-T-B  B-T-B  T-B-T`                 |      328 |   0.45% |                                   |
|  9 | `T-B-T  B-T-B  B-T-B  B-T-B`                 |      326 |   0.45% |                                   |
|  4 | `B-T-B  B-T-B  T-B-T  T-B-T`                 |      216 |   0.30% |                                   |
|  5 | `B-T-B  T-B-T  B-T-B  B-T-B`                 |      213 |   0.29% |                                   |
| 13 | `T-B-T  T-B-T  B-T-B  B-T-B`                 |      207 |   0.28% |                                   |
| 14 | `T-B-T  T-B-T  B-T-B  T-B-T`                 |      195 |   0.27% |                                   |
|  1 | `B-T-B  B-T-B  B-T-B  B-T-B`                 |      180 |   0.25% |                                   |
| 12 | `T-B-T  B-T-B  T-B-T  T-B-T`                 |      180 |   0.25% |                                   |
|  8 | `B-T-B  T-B-T  T-B-T  T-B-T`                 |      178 |   0.24% | ← tổ hợp của ví dụ §11     |
|  3 | `B-T-B  B-T-B  T-B-T  B-T-B`                 |      159 |   0.22% |                                   |
| 15 | `T-B-T  T-B-T  T-B-T  B-T-B`                 |       88 |   0.12% |                                   |
| 16 | `T-B-T  T-B-T  T-B-T  T-B-T`                 |       67 |   0.09% |                                   |

**Hai mẫu §4.3 chiếm phần áp đảo**, nhưng chúng **không** phải ràng buộc: ví dụ §11 của
chính tài liệu cho tổ hợp **#8**, và nó vẫn đạt. Đây là phát hiện về **tập dữ liệu**,
không phải về **thể thơ**.

---

### 7.5. Tầng 5 — VẦN

|                                       |                                                                                |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| **Điều luật**                | S6, S9, S10, S11, S12                                                          |
| **Tiêu chí (QĐ-7 + QĐ-7b)** | ≥1 cụm**4 dòng liên tiếp** có ít nhất một cặp hiệp vần chân |
| **Mức**                        | ⛔ CHẶN                                                                       |
| **Vào / Qua / Chặn**          | 24.726 /**24.366** / **360**                                       |

#### QĐ-7 — quét cửa sổ bốn dòng

> *"trong bài phải có ít nhất là 4 dòng liên tiếp có cấu trúc như thế ở cuối"*

Cửa sổ trượt 4 dòng quét suốt bài; **một** cửa sổ đạt là đủ. Cửa sổ **vắt qua ranh giới
khổ** — chủ dự án nói *"trong bài"*, không nói *"trong một khổ"*.

Vì sao chỉ đòi một cửa sổ: §5.2 kết bằng *"**Vần hỗn hợp**: phối nhiều sơ đồ trên trong
cùng một bài"*. Đòi cả bài theo một sơ đồ duy nhất là **cấm vần hỗn hợp** — chặt hơn tài
liệu ở đúng chỗ tài liệu cho phép.

#### QĐ-7b — tiêu chí của cửa sổ, sửa 18/09/2026

> **Nguyên văn chủ dự án:** *"vần chân sẽ là như vậy trong phạm vi 4 câu (Nếu không có
> vần chân nào thì trượt)"*

Bản trước đòi cửa sổ khớp **đúng một trong bốn sơ đồ** §5.2, nên loại cả `aaaa` (độc vận),
`axax`, `xaxa`… Chủ dự án nêu danh sách mở *"aabb, abab, abba, aaxa, aaaa, aaba, …"* rồi
chốt bằng câu trong ngoặc — **câu ấy mới là luật**.

```python
so_do = "".join(suy_so_do_van(cum))
if any(nhan != "x" for nhan in so_do):   # có ít nhất một cặp hiệp vần
    ...
```

Cụm duy nhất bị loại là **`xxxx`**.

|                           | Trước QĐ-7b |       Sau QĐ-7b |
| ------------------------- | -------------: | ---------------: |
| Cổng 5 chặn             |          6.576 |    **360** |
| Bài đạt cả bảy tầng |         18.150 | **24.366** |

**Vì sao không giữ danh sách đóng:** liệt kê sơ đồ sẽ phải trả lời *"còn `xaax` thì sao,
`xxaa` thì sao"* cho từng trường hợp, mà tài liệu không cho căn cứ nào để phân biệt. Tiêu
chí hiện tại không có danh sách, không có ngưỡng phần trăm — không phạm N1.

**`aaba` không phải sơ đồ riêng.** Nhãn `b` đòi ít nhất **hai** dòng cùng lớp vần, nên
dòng lẻ loi luôn nhận `x`. `aaba` chính là `aaxa`.

**Nhãn `?` vẫn tính là có vần.** Cụm có quan hệ vần không bắc cầu (`vang / vương / vuông`)
không quy về một sơ đồ chữ cái được, nhưng nó **có** hiệp vần nên không bị loại.

**S8 bị xoá cùng ngày** — xem §3.1. Tầng 5 nay không ghi đè điều nào.

#### Vì sao tầng này chỉ chặn 1,46% — và vì sao đó là ĐÚNG

Con số nhỏ khiến người đọc dễ nghi tầng hỏng. Nó không hỏng. Ba phép đo giải thích trọn:

**1. Tiêu chí cho qua 14 trong 15 sơ đồ có thể có.** Một cụm bốn dòng có đúng 15 sơ đồ
chuẩn tắc. Luật chỉ loại một:

```
ĐI TIẾP (14):  aaaa  aaax  aabb  aaxa  aaxx  abab  abba
               axaa  axax  axxa  xaaa  xaax  xaxa  xxaa
BỊ CHẶN  (1):  xxxx
```

Chủ dự án xác nhận ngày 18/09: *"chỉ chặn trường hợp `xxxx` thôi"*. Đây là **quyết định
đã chốt**, không phải chỗ còn bỏ ngỏ.

**2. Thơ Việt gần như luôn có vần**, nên `xxxx` vốn đã hiếm. Chạy tiêu chí này trên **toàn
bộ 55.297 bài thuộc thể** — bỏ qua cổng 4 — thì cũng chỉ **1.636 bài** (2,96%) là `xxxx`.
Tầng không thể chặn nhiều hơn số bài thực sự không vần.

**3. Cổng 4 vét trước 78%.** Bài không gieo vần thường cũng không giữ khuôn thanh:

```
1.636  bài xxxx trên toàn bộ bài thuộc thể
−1.276  đã bị cổng 4 chặn trước          (78,0%)
=  360  còn lại cho cổng 5
```

**Và bảng vần KHÔNG dễ dãi** — đây là giả thuyết đã kiểm và bác bỏ:

| | |
|---|---:|
| Xác suất hai tiếng **ngẫu nhiên** hiệp vần | 7,60% |
| Nếu vần ngẫu nhiên, cụm 4 dòng có ≥1 cặp hiệp | 37,77% |
| **Thực đo** | **98,54%** |

Khoảng cách giữa 98,54% và đường cơ sở ngẫu nhiên 37,77% chính là **bằng chứng nhà thơ cố
ý gieo vần**, không phải bằng chứng bảng vần lỏng lẻo.

> **Kết luận:** tầng 5 đo một thứ mà corpus gần như luôn thoả. Nó chỉ tồn tại để **chặn
> dứt điểm bài không vần** — 360 bài, và đo lại xác nhận **cả 360 đều là `xxxx`**, không
> một ca nào khác. Đúng việc nó được giao.

#### Bốn sơ đồ §5.2 nay là BẢNG TÊN

`SO_DO_KHO_TAI_LIEU` thôi làm tập tiêu chí. Cụm nào tình cờ khớp một trong bốn thì biên
bản gọi đúng tên tài liệu đặt; cụm không có tên riêng thì `ten` là `None` — **không** phải
cụm hỏng.

| Sơ đồ | Tên tài liệu gọi                    |
| -------- | --------------------------------------- |
| `aabb` | vần liền                              |
| `abab` | vần cách                              |
| `abba` | vần ôm                                |
| `aaxa` | vần ba dòng, kế thừa Đường luật |

**Khớp nghiêm ngặt hai chiều** vẫn giữ cho việc gọi tên: cùng chữ cái thì bắt buộc hiệp,
khác chữ cái thì bắt buộc không hiệp. Nếu chỉ đòi chiều thuận thì `aaaa` sẽ bị gọi nhầm
tên là *"vần liền"*.

#### Bảng vần — và vì sao nó là ĐỒ THỊ

Nguồn (QĐ-5): **Trần Trọng Kim, *Việt thi*, mục I-6**, bản số hoá Wikisource; đối chiếu
**Bùi Kỷ, *Quốc văn cụ thể*, Tân Việt 1950**. Hồ sơ: `docs/Nguon_Bang_Van_Thong.md`.

|                             |        Cạnh |         Vần | Bộ ba vi phạm bắc cầu |
| --------------------------- | -----------: | -----------: | ------------------------: |
| Từ nguồn                  |           73 |           55 |                        16 |
| + 4 cạnh suy diễn 🔶 SD-2 | **77** | **62** |              **18** |

Quan hệ hiệp vần **không bắc cầu**, và chính tác giả nói ra điều đó:

> *"**ang** thông với **ương** (không thông được với **uông** vì **a** không thông được
> với **ô**)"* … rồi vài dòng sau: *"**uông** thông với **ương**"*

Ép bảng thành các lớp tương đương rời nhau sẽ **bịa thêm 18 cặp hiệp vần mà nguồn không
cho** — tức là nới luật, N1 cấm.

Dữ liệu giữ đúng **hai dạng liệt kê của tác giả** (`_NHOM_TTK` các cụm "…thông với nhau",
`_CAP_TTK` các phát biểu rời "X thông với Y"), vì gộp chúng lại là sai: *"ăn thông với
ân"* và *"ăn thông với uân"* là **hai câu rời** ⟹ `ân ≁ uân`.

Ba chỗ suy diễn được đánh dấu 🔶 tại chỗ trong mã: **SD-1** (quan hệ vần độc lập thanh
điệu), **SD-2** (4 cặp lấy từ phần vần trắc), **SD-3** (vần có âm đệm chỉ hiệp vần chính
— hướng **chặt**, không nới).

#### `suy_so_do_van()` — clique, không gom cụm

Vì quan hệ không bắc cầu, **gom cụm là phép sai**. Một sơ đồ chữ cái chỉ tồn tại khi quan
hệ hiệp vần *hạn chế trong cụm này* tình cờ là quan hệ tương đương — mỗi thành phần liên
thông phải là một **clique**. Không thoả thì mọi dòng trong thành phần nhận nhãn `?`, và
đó là **tình trạng thật của khổ thơ** chứ không phải lỗi phần mềm.

**🩸 Bug đã sửa: sơ đồ vần phụ thuộc thứ tự dòng.**

```
('ve', 'về', 'xa')   CŨ  -> một nhóm      |  MỚI -> [ve, xa], [về]
('về', 've', 'xa')   CŨ  -> hai nhóm      |  MỚI -> [về], [ve, xa]   <- giống trên
```

Sơ đồ vần mà phụ thuộc thứ tự dòng thì **mọi số liệu tầng 5 đều vô nghĩa**.

#### Phân bố sơ đồ trên các cụm có vần chân (7,77 cụm/bài)

| Sơ đồ | Số cụm |                                        |
| -------- | -------: | -------------------------------------- |
| `axax` |   37.314 |                                        |
| `aaxa` |   32.147 | ✓ §5.2                               |
| `xaxa` |   26.806 |                                        |
| `aaaa` |   19.923 | độc vận — trước QĐ-7b bị loại |
| `xaax` |   17.081 |                                        |
| `xxaa` |   17.004 |                                        |
| `aaax` |    7.396 |                                        |
| `xaaa` |    7.391 |                                        |
| `axaa` |    6.185 |                                        |
| `aaxx` |    5.710 |                                        |
| `axxa` |    4.198 |                                        |
| `abab` |    4.039 | ✓ §5.2                               |
| `aabb` |    2.441 | ✓ §5.2                               |
| `abba` |    1.176 | ✓ §5.2                               |

**Bốn sơ đồ §5.2 chỉ chiếm khoảng một phần năm số cụm.** Con số này là lý do QĐ-7b đúng:
giữ danh sách đóng thì gần bốn phần năm quan hệ vần thật trong corpus bị coi như không
tồn tại.

**Cả 360 bài trượt đều là `xxxx`** — đo được, không ước lượng.

---

### 7.6. Tầng 6 — NHỊP

|                              |                                                                             |
| ---------------------------- | --------------------------------------------------------------------------- |
| **Điều luật**       | S13, S14, S15                                                               |
| **Nguyên văn (S14)** | *"Nên có một nhịp chủ đạo để bài có xương sống âm thanh."* |
| **Tiêu chí**         | 6a mọi dòng thuộc bảy kiểu · 6b có nhịp chủ đạo phủ cả bài    |
| **Mức**               | ⛔ CHẶN (trên lý thuyết)                                                |
| **Vào / Qua / Chặn** | 24.366 / 24.366 /**0**                                                |

Tập bảy kiểu là tập **đóng**: `4/3, 3/4, 2/2/3, 2/5, 5/2, 1/6, 3/2/2`. Nhịp chủ đạo là
**giao** của các tập nhịp khả dĩ.

**Vì sao dùng phép giao thay vì "đa số dòng":** nói *"đa số"* thì phải định nghĩa đa số là
bao nhiêu, mà tài liệu không nói — đặt con số ở đó là tự chế luật, N1 cấm.

#### ⚠️ Tầng này hiện RỖNG NGHĨA

Ngắt nhịp là ngắt theo **ranh giới từ**, không phải theo vị trí tiếng. Chưa có bộ tách từ
tiếng Việt thì mọi dòng 7 tiếng đều "cắt được" thành 4/3, 3/4, 2/5… vì phép cắt chỉ là
đếm số.

```
Không có tách từ -> nhip_kha_di_cua_dong() trả CẢ BẢY kiểu cho MỌI dòng 7 tiếng
                 -> 6a luôn đạt, 6b luôn đạt (giao = cả bảy kiểu)
                 -> tầng 6 KHÔNG loại được bài nào
```

**Bằng chứng: 100,00% bài đạt được gán nhịp chủ đạo `4/3`.** Đó không phải phát hiện về
thơ Việt, mà là hiện vật đo đạc — giao luôn khác rỗng và `4/3` đứng đầu bảng.

Con số 24.366 là **chưa qua kiểm nhịp thật sự**. Tầng chỉ chặn được với thơ do mô hình
sinh kèm khai báo nhịp từng dòng (tham số `nhip_khai_bao`).

**Đây là lỗ hổng lớn nhất còn lại của cả kiến trúc.**

---

### 7.7. Tầng 7 — KHỔ VÀ BỐ CỤC

|                              |                              |
| ---------------------------- | ---------------------------- |
| **Điều luật**       | S16–S21                     |
| **Tiêu chí**         | Không có khổ rỗng        |
| **Mức**               | ⛔ CHẶN                     |
| **Vào / Qua / Chặn** | 24.366 / 24.366 /**0** |

Trong sáu điều S16–S21, phần lớn là **quyền** (*"không hạn định"*, *"có thể"*). Nguyên tắc
**N2**: điều loại quyền **không bao giờ** được dùng làm tiêu chí đánh trượt.

Đừng đọc *"tầng 7 chặn 0 bài"* là tầng thừa. Nó vẫn chạy, vẫn nộp bằng chứng về cấu trúc
khổ, và vẫn bắt được khổ rỗng — thứ duy nhất ở đây thực sự sai chứ không phải lựa chọn
phong cách.

**Không kiểm được:** S19 (*mạch cảm xúc / mạch tự sự*) đòi hiểu nội dung.

---

## 8. VÍ DỤ THẬT — ba bài mỗi loại

Toàn bộ ví dụ dưới đây là **bài thật trong corpus**, trích nguyên văn, kèm bằng chứng máy
sinh. Ký hiệu dùng chung:

| Ký hiệu              | Nghĩa                                                                                         |
| ---------------------- | ---------------------------------------------------------------------------------------------- |
| `B` · `T`         | thanh bằng · thanh trắc tại**P2, P4, P6**                                            |
| `bằng` · `trắc` | dòng khớp khuôn`B T B` · khuôn `T B T` (§4.2)                                        |
| ⛔                     | dòng vi phạm — nguyên nhân trực tiếp làm bài trượt                                  |
| `a` `b` `x`      | nhãn sơ đồ vần: cùng chữ = hiệp vần ·`x` = không hiệp với dòng nào trong cụm |

---

### 8.1. BA BÀI ĐẠT — đi qua bảy tầng như thế nào

Yêu cầu gốc của chủ dự án là *"từng bài thơ cần thể hiện rõ xem vượt qua từng tầng thế
nào — kiểu có bằng chứng nó vượt tầng đó thế nào"*. Ba bài dưới đây trình bày đúng thứ
đó: **mỗi tầng một hàng**, nêu tiêu chí phải đạt, số đo thật, và phán quyết.

**Cách đọc bảng bảy tầng:**

| Cột                      | Nghĩa                                                                                                      |
| ------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Điều luật**    | Mọi điều thuộc phạm vi tầng. In đậm = điều**thực sự sinh phán quyết** (`tieu_chi_tu`) |
| **Phải đạt**     | Tiêu chí chặn, trích từ`trich_luat` của tầng                                                       |
| **Đo được**     | Số liệu thật lấy từ`chi_tiet` — kiểm lại được bằng mắt trên bài thơ                       |
| **Ghi nhận thêm** | Điều máy không kiểm được (N3) và các lựa chọn mềm chỉ để mô tả                            |

Cả ba bài đều **8 dòng, 1 khổ**, nên chúng có `8 − 3 = 5` cụm bốn dòng liên tiếp và
`8 ÷ 4 = 2` cụm khuôn. Chọn cùng độ dài là cố ý — để khác biệt giữa ba bài nằm ở **chất
thơ**, không ở kích thước.

---

#### 8.1.1. id = 3 — *"QUÊ HƯƠNG"*

```
D1  Đã bấy lâu nay cứ miệt mài,          T B T  trắc   vần: ai ──┐
D2  Trong vòng luẩn quẩn kiếm sinh nhai. B T B  bằng   vần: ai ──┤ a
D3  Về bên giếng nước rêu phong kín,     B T B  bằng   vần: in   x
D4  Nép dưới hàng cau nắng đổ dài.       T B T  trắc   vần: ai ──┘
D5  Nhớ mãi đầu cha phơ mái tóc,         T B T  trắc   vần: oc
D6  Thương hoài áo mẹ bạc màu vai.       B T B  bằng   vần: ai
D7  Nhìn theo lối cũ vàng hoa cải,       B T B  bằng   vần: ai
D8  Thấy chậm bàn chân nặng gót hài.     T B T  trắc   vần: ai
```

| Tầng                         | Điều luật                   | Phải đạt                                              | Đo được                                                                                                                                       |  ✓  |
| ----------------------------- | ------------------------------ | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | :--: |
| **T1** Hình thức      | **H3**, **H4**     | ≥ 4 dòng**và** số dòng chia hết cho 4        | `so_dong = 8` · `du_khi_chia_4 = 0` · `co_phan_dong = True` → `8 = 4 × 2`                                                             |  ✅  |
| **T2** Độ dài dòng  | **H1**, **H2**     | **Mọi** dòng đúng 7 tiếng, không ngoại lệ  | `so_tieng_tung_dong = [7,7,7,7,7,7,7,7]` · nhỏ nhất = lớn nhất = **7** · đã loại **8** ký tự dấu câu trước khi đếm |  ✅  |
| **T3** Đối chiếu ĐL | F1–F5                         | *(ghi nhận — **không có tiêu chí chặn**)* | `nghi_duong_luat = False` — 8 dòng nhưng **không** độc vận (có `in`, `oc` xen vào) nên không đủ ba vế                   |  ✅  |
| **T4** Thanh luật      | S1,**S2**, S3            | **Mọi** dòng khớp `B T B` hoặc `T B T`     | `so_dong_pha_khuon = 0` · khuôn: `trắc·bằng·bằng·trắc` × 2 · `ma_phoi_khuon_tung_cum = [10, 10]`                                 |  ✅  |
| **T5** Vần             | S6, S9, S10,**S11**, S12 | ≥ 1 cụm 4 dòng liên tiếp**có vần chân**    | `so_cum_co_van_chan = 5/5` — mọi cụm đều có vần · cụm D1–D4 khớp sơ đồ `aaxa` có tên                                          |  ✅  |
| **T6** Nhịp            | S13,**S14**, S15         | Có một nhịp chủ đạo phủ mọi dòng                | `nhip_chu_dao = 4/3` · `nguon_nhip = khong_khai_bao`                                                                                         | ⚠️ |
| **T7** Khổ & bố cục  | S16–S21                       | Không có khổ rỗng                                    | `so_kho = 1` · `kich_thuoc_tung_kho = [8]`                                                                                                   |  ✅  |

**Năm cụm vần — bằng chứng tầng 5 đầy đủ:**

```
cụm D1–D4:  aaxa   vần ba dòng, kế thừa Đường luật    mài / nhai / kín / dài
cụm D2–D5:  axax   (không có tên riêng)               nhai / kín / dài / tóc
cụm D3–D6:  xaxa   (không có tên riêng)               kín / dài / tóc / vai
cụm D4–D7:  axaa   (không có tên riêng)               dài / tóc / vai / cải
cụm D5–D8:  xaaa   (không có tên riêng)               tóc / vai / cải / hài
```

Chỉ **1 trong 5** cụm khớp một sơ đồ có tên §5.2 (`so_cum_khop_so_do_tai_lieu = 1`). Bốn
cụm còn lại vẫn **có vần chân** nên vẫn đạt theo QĐ-7b — trước QĐ-7b chúng bị coi như
không tồn tại.

**Ghi nhận thêm** *(không góp vào phán quyết)*:

| Mục                          | Giá trị                                                          | Vì sao chỉ ghi nhận                                                         |
| ----------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| `F2_khong_kiem_duoc`        | *phép đối đòi so từ loại và ngữ nghĩa giữa hai dòng* | N3 — máy không kiểm được                                                |
| `F4_khong_kiem_duoc`        | *bố cục Khai–Thừa–Chuyển–Hợp đòi hiểu nội dung*      | N3                                                                             |
| `S1_p1_p3_p5_khong_bi_kiem` | `True`                                                           | S1 là**quyền** — P1/P3/P5 không bao giờ bị đọc để phán quyết |
| `so_vi_tri_van_lung`        | **1** — D1 vị trí P4 (`nay` ~ `mài`)                 | S1 (gộp S7) là quyền                                                        |
| `S3_khong_kiem_duoc`        | *P7 cần chọn có chủ đích — đòi ý đồ tác giả*       | N3                                                                             |
| `so_cap_van_lech_thanh`     | **5** cặp                                                   | S9**cho phép** phối vần bằng và trắc                               |
| `S15_khong_kiem_duoc`       | *đổi nhịp trùng chỗ chuyển ý — đòi ngữ nghĩa*        | N3                                                                             |
| `S19_khong_kiem_duoc`       | *mạch cảm xúc hoặc mạch tự sự đòi hiểu nội dung*      | N3                                                                             |
| `ty_le_theo_khuon`          | `1.0`                                                            | Chỉ mô tả —**không** phải tiêu chí (xem N1, §4.2)               |

**Ghi chú mức bài:** `Có 5 cặp hiệp vần lệch lớp thanh — được phép theo S9, ghi nhận để tham khảo.`

> ⚠️ **T6 mang dấu ⚠️ chứ không phải ✅ đầy đủ.** Bằng chứng tự khai: *"KHÔNG có khai báo
> nhịp nên chỉ kiểm được số học"*. `nhip_kha_di_tung_dong` cho thấy **mọi dòng đều nhận
> cả bảy kiểu nhịp** — vì chưa có bộ tách từ, phép cắt chỉ là đếm số. Tầng này **chưa
> thực sự kiểm gì**; xem §7.6.

---

#### 8.1.2. id = 7 — *"LẺ BÓNG"*

```
D1  Một sáng sương mù khẽ rảo bay,     T B T  trắc   vần: ay  ──┐ a
D2  Làm đau cái lạnh giữa thu gầy.     B T B  bằng   vần: ây ─┐ │ b
D3  Hoa cài ngọn cỏ thuyền trôi đấy,   B T B  bằng   vần: ây ─┘ │ b
D4  Gió thổi lưng trời dạ đỡ cay.      T B T  trắc   vần: ay  ──┘ a
D5  Cảnh cũ còn đây tình sống dậy,     T B T  trắc   vần: ây
D6  Người xưa đã vắng mộng dâng đầy.   B T B  bằng   vần: ây
D7  Đan vào nỗi nhớ nhờ sông chảy,     B T B  bằng   vần: ay
D8  Cuộn những tơ lòng gửi áng mây.    T B T  trắc   vần: ây
```

| Tầng                         | Điều luật                   | Phải đạt                         | Đo được                                                                                                                       |  ✓  |
| ----------------------------- | ------------------------------ | ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | :--: |
| **T1** Hình thức      | **H3**, **H4**     | ≥ 4 dòng**và** bội của 4 | `so_dong = 8` · `du_khi_chia_4 = 0` → `8 = 4 × 2`                                                                        |  ✅  |
| **T2** Độ dài dòng  | **H1**, **H2**     | Mọi dòng đúng 7 tiếng          | `[7,7,7,7,7,7,7,7]` · đã loại **8** dấu câu                                                                         |  ✅  |
| **T3** Đối chiếu ĐL | F1–F5                         | *(ghi nhận)*                     | `nghi_duong_luat = False` — 8 dòng, có niêm, nhưng **hai lớp vần** `ay`/`ây` nên **không độc vận** |  ✅  |
| **T4** Thanh luật      | S1,**S2**, S3            | Mọi dòng khớp khuôn             | `so_dong_pha_khuon = 0` · `ma_phoi_khuon_tung_cum = [10, 10]`                                                                |  ✅  |
| **T5** Vần             | S6, S9, S10,**S11**, S12 | ≥ 1 cụm có vần chân            | `so_cum_co_van_chan = 5/5` · **`so_cum_khop_so_do_tai_lieu = 4`**                                                      |  ✅  |
| **T6** Nhịp            | S13,**S14**, S15         | Có nhịp chủ đạo                | `nhip_chu_dao = 4/3` · `khong_khai_bao`                                                                                      | ⚠️ |
| **T7** Khổ & bố cục  | S16–S21                       | Không khổ rỗng                   | `so_kho = 1` · `[8]`                                                                                                         |  ✅  |

**Năm cụm vần — bài chặt nhất trong ba bài:**

```
cụm D1–D4:  abba   vần ôm                              bay / gầy / đấy / cay
cụm D2–D5:  aaxa   vần ba dòng, kế thừa Đường luật     gầy / đấy / cay / dậy
cụm D3–D6:  axaa   (không có tên riêng)                đấy / cay / dậy / đầy
cụm D4–D7:  abba   vần ôm                              cay / dậy / đầy / chảy
cụm D5–D8:  aaxa   vần ba dòng, kế thừa Đường luật     dậy / đầy / chảy / mây
```

**Bốn trong năm cụm khớp sơ đồ có tên §5.2** — cao nhất trong ba bài (id=3 và id=15 chỉ
có 1). Sơ đồ toàn bài là `abbabbab`: hai lớp vần `ay` và `ây` đan nhau đều đặn suốt tám
dòng.

**Đây là ca minh hoạ phép khớp NGHIÊM NGẶT hai chiều.** Sơ đồ `abba` chỉ đúng nếu đồng
thời:

```
bay ~ cay   (cùng lớp ay)        ✓ hiệp
gầy ~ đấy   (cùng lớp ây)        ✓ hiệp
ay  ≁ ây                          ✓ KHÔNG hiệp  ← vế bắt buộc thứ ba
```

Bảng Trần Trọng Kim **không nối `ay` với `ây`**. Nếu phép khớp chỉ đòi chiều thuận thì cả
bốn dòng sẽ bị gom làm một lớp và gọi nhầm là `aaaa`.

**Ghi nhận thêm:** `so_vi_tri_van_lung = 1` (D5, vị trí P4: `đây` ~ `dậy`) ·
`so_cap_van_lech_thanh = **8**` — nhiều nhất ba bài, đúng với việc bài dùng dày hai lớp
vần `ay`/`ây` ở cả thanh bằng lẫn trắc. Bốn khoá `khong_kiem_duoc` (F2, F4, S3, S15, S19)
ghi y như id=3.

**Ghi chú mức bài:** `Có 8 cặp hiệp vần lệch lớp thanh — được phép theo S9, ghi nhận để tham khảo.`

---

#### 8.1.3. id = 15 — *"GIẤC NGỦ TRẦN GIAN"*

```
D1  Hàng đêm ngủ lại dưới trăng trời,  B T B  bằng   vần: ơi  ──┐
D2  Mộng nửa canh giờ gió bỗng rơi.    T B T  trắc   vần: ơi  ──┤ a
D3  Chợt nghĩ trên đầu tinh tú chuyển, T B T  trắc   vần: uyên  x
D4  Hình như đối diện dải mây rời.     B T B  bằng   vần: ơi  ──┘
D5  Nơi nằm có sẵn vài gang mộ,        B T B  bằng   vần: ô
D6  Chỗ đẻ đâu thừa một tấc nôi.       T B T  trắc   vần: ôi
D7  Hiểu rõ càn khôn là ngục tối,      T B T  trắc   vần: ôi
D8  Thì xin ánh lửa phực ngang người.  B T B  bằng   vần: ươi
```

| Tầng                         | Điều luật                   | Phải đạt                         | Đo được                                                                                                              |  ✓  |
| ----------------------------- | ------------------------------ | ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | :--: |
| **T1** Hình thức      | **H3**, **H4**     | ≥ 4 dòng**và** bội của 4 | `so_dong = 8` · `du_khi_chia_4 = 0` → `8 = 4 × 2`                                                               |  ✅  |
| **T2** Độ dài dòng  | **H1**, **H2**     | Mọi dòng đúng 7 tiếng          | `[7,7,7,7,7,7,7,7]` · đã loại **8** dấu câu                                                                |  ✅  |
| **T3** Đối chiếu ĐL | F1–F5                         | *(ghi nhận)*                     | `nghi_duong_luat = False` — có `uyên`, `ô` xen vào nên không độc vận                                     |  ✅  |
| **T4** Thanh luật      | S1,**S2**, S3            | Mọi dòng khớp khuôn             | `so_dong_pha_khuon = 0` · khuôn `bằng·trắc·trắc·bằng` × 2 · **`ma_phoi_khuon_tung_cum = [7, 7]`** |  ✅  |
| **T5** Vần             | S6, S9, S10,**S11**, S12 | ≥ 1 cụm có vần chân            | `so_cum_co_van_chan = 5/5` · `so_cum_khop_so_do_tai_lieu = 1`                                                       |  ✅  |
| **T6** Nhịp            | S13,**S14**, S15         | Có nhịp chủ đạo                | `nhip_chu_dao = 4/3` · `khong_khai_bao`                                                                             | ⚠️ |
| **T7** Khổ & bố cục  | S16–S21                       | Không khổ rỗng                   | `so_kho = 1` · `[8]`                                                                                                |  ✅  |

**Khác id=3 ở đúng một chỗ, và đó là điểm đáng nói nhất của bài này: tổ hợp #7 thay vì
#10.**

```
id=15:   bằng → trắc → trắc → bằng    =  tổ hợp #7   =  mẫu "giữ âm hưởng cổ điển" §4.3
id=3 :   trắc → bằng → bằng → trắc    =  tổ hợp #10  =  mẫu "đảo" §4.3
```

Hai bài mở bằng hai khuôn ngược nhau, **cả hai đều đạt**. Bảng 16 tổ hợp (§6c) chốt rằng
**cả 16 đều hợp lệ**, không riêng hai mẫu §4.3. Và chính ví dụ §11 của tài liệu cho tổ
hợp **#8** — cũng đạt.

**Năm cụm vần:**

```
cụm D1–D4:  aaxa   vần ba dòng, kế thừa Đường luật     trời / rơi / chuyển / rời
cụm D2–D5:  axax   (không có tên riêng)                rơi / chuyển / rời / mộ
cụm D3–D6:  xaxa   (không có tên riêng)                chuyển / rời / mộ / nôi
cụm D4–D7:  axaa   (không có tên riêng)                rời / mộ / nôi / tối
cụm D5–D8:  xaaa   (không có tên riêng)                mộ / nôi / tối / người
```

**Một chỗ dễ đọc nhầm — và bảng vần nguồn quyết định:** nhìn mặt chữ thì bài như đổi
vần giữa chừng (`ơi` ở bốn dòng đầu, `ôi`/`ươi` ở bốn dòng sau). Nhưng sơ đồ máy suy ra
là `aaxaxaaa` — **D1, D2, D4, D6, D7, D8 cùng một nhãn `a`**, tức **một lớp vần duy
nhất**, không phải hai.

Lý do nằm ở nguồn: Trần Trọng Kim xếp `ai · oi · ôi · ơi · ươi · ui` **cùng một nhóm
thông vần**. Nên `trời ~ nôi ~ người` đều hiệp — bài này **không đổi vần**.

```
ơi ~ ôi   = True        nhóm TTK: (ai, oi, ôi, ơi, ươi, ui)
ơi ~ ươi  = True
ôi ~ ươi  = True
```

Hai dòng buông (`x`) là D3 `chuyển` (vần `uyên`) và D5 `mộ` (vần `ô`) — chúng không hiệp
với lớp `ơi`, và cũng không hiệp với nhau.

**Ghi nhận thêm:** `so_vi_tri_van_lung = **3**` — nhiều nhất ba bài:

```
D1 vị trí P4  (lại  ~ trời)
D1 vị trí P5  (dưới ~ trời)
D4 vị trí P5  (dải  ~ rời)
```

Vần lưng thuộc **S1** (phần gộp từ S7) và là **quyền** — đo rồi ghi vào `chi_tiet` của
tầng 4, không bao giờ làm bài trượt. `so_cap_van_lech_thanh = 5`.

**Ghi chú mức bài:** `Có 5 cặp hiệp vần lệch lớp thanh — được phép theo S9, ghi nhận để tham khảo.`

---

#### 8.1.4. Ba bài cạnh nhau — khác nhau ở đâu

|                                     | id=3*QUÊ HƯƠNG*       | id=7*LẺ BÓNG*               | id=15*GIẤC NGỦ TRẦN GIAN*          |
| ----------------------------------- | -------------------------- | ------------------------------- | --------------------------------------- |
| Số dòng / khổ                    | 8 / 1                      | 8 / 1                           | 8 / 1                                   |
| **Tổ hợp khuôn**           | **#10** (mẫu đảo) | **#10** (mẫu đảo)      | **#7** (mẫu cổ điển)          |
| Sơ đồ vần toàn bài            | `aaxaxaaa`               | `abbabbab`                    | `aaxaxaaa`                            |
| Cụm D1–D4                         | `aaxa` vần ba dòng     | `abba` **vần ôm**     | `aaxa` vần ba dòng                  |
| Cụm có vần chân                 | 5 / 5                      | 5 / 5                           | 5 / 5                                   |
| **Cụm khớp sơ đồ §5.2** | 1                          | **4**                     | 1                                       |
| Số lớp vần                       | 1 (`ai`)                 | **2** (`ay` · `ây`) | 1 (`ơi·ôi·ươi` cùng nhóm TTK) |
| Vần lưng                          | 1 vị trí                 | 1 vị trí                      | **3 vị trí**                    |
| Cặp lệch lớp thanh               | 5                          | **8**                     | 5                                       |

**Ba bài đạt theo ba cách khác nhau**, và đó là điều bảng này muốn cho thấy:

- **id=3** — một lớp vần duy nhất chạy suốt, gần độc vận nhưng có `kín`, `tóc` xen vào
  nên thoát khỏi vùng nghi Đường luật.
- **id=7** — chặt nhất về vần: hai lớp đan nhau đều đặn, 4/5 cụm khớp sơ đồ có tên.
- **id=15** — dùng khuôn ngược với hai bài kia (#7 thay vì #10), và là ca cho thấy
  **mặt chữ khác nhau chưa chắc là khác lớp vần**: `ơi`, `ôi`, `ươi` cùng một nhóm thông
  vần theo nguồn.

Không bài nào "đạt hơn" bài nào. `dat` là **một giá trị bool cho cả bài**, không phải
điểm số — mọi khác biệt trong bảng trên đều là **lựa chọn mềm được ghi nhận**, không phải
thứ hạng.

**Và cả ba đều mang cùng một cảnh báo:** tầng 6 chưa thực sự kiểm nhịp. Ba bài này qua
được sáu cổng có thật và một cổng đang rỗng nghĩa.
---------------------------------------------------------------

### 8.2. BA BÀI TRƯỢT Ở CỔNG 1 — số dòng không phải bội của 4 (H4)

> **4.668 bài.** Cổng chặn nhiều thứ hai. Biên bản ở cổng này **không gợi ý sửa**: thêm
> hay bớt dòng là sửa nội dung thơ.

#### 8.2.1. id = 7391 — *"UỐNG TRÀ"* · **6 dòng** ⛔

```
D1  Ghế đá thảnh thơi thưởng thức trà,   T B T  trắc  vần: a    ──┐ a
D2  Uống chè thanh nhiệt ẩm lòng ta.     B T B  bằng  vần: a    ──┘
D3  Nhâm nhi từng ngụm hồn phiêu lãng,   B T B  bằng  vần: ang  ──┐ b
D4  Nhìn ngắm mây trời đón xuân sang.    T B B  pha   vần: ang  ──┘
D5  Cảnh sắc tạo nên những mơ màng,      T B B  pha   vần: ang
D6  Hồn thơ lai láng hát tình tang.      B T B  bằng  vần: ang
```

```
⛔ BÀI 6 DÒNG — dư 2 khi chia 4
   H4: cần "số dòng là bội của 4" | đang "6 dòng, dư 2 khi chia 4"
       Luật cứng, không có ngoại lệ — bài không thuộc thể.
       KHÔNG thêm hay bớt dòng để ép qua: nội dung thơ phải giữ nguyên.
```

**Đáng chú ý:** cụm D1–D4 có sơ đồ `aabb` — **vần liền, đúng một trong bốn sơ đồ §5.2**.
Bài này gieo vần chỉnh, nhưng chết ở cổng 1 và **không bao giờ tới được cổng 5**. Bằng
chứng tầng 5 sẽ mang `da_chay = False` — *chưa kiểm*, không phải *đã kiểm và trượt*.

*(Nếu có tới cổng 4 thì nó cũng trượt: D4 và D5 phá khuôn.)*

#### 8.2.2. id = 7407 — *"BÀI HỌC ĐẦU TIÊN CHO CON"* · **6 dòng** ⛔

```
D1  Cho con cơ hội để trưởng thành,     B T T  pha   vần: anh   x
D2  Trao cho con năng lực tự học.       B B T  pha   vần: oc    x
D3  Dạy cho con tấm lòng nhân ái,       B T B  bằng  vần: ai    x
D4  Cho con tiếp xúc với thiên nhiên.   B T B  bằng  vần: iên   x
D5  Làm gương cho con từ việc nhỏ,      B B T  pha   vần: o
D6  Ứng xử ôn hòa khi dạy con.          T B T  trắc  vần: on
```

```
⛔ BÀI 6 DÒNG — dư 2 khi chia 4
   H4: cần "số dòng là bội của 4" | đang "6 dòng, dư 2 khi chia 4"
```

**Bài này hỏng ở cả ba cổng — nhưng chỉ cổng 1 được ghi.** Cụm D1–D4 là `xxxx` (không
cặp nào hiệp vần, sẽ trượt cổng 5), và ba dòng phá khuôn (sẽ trượt cổng 4). Dừng sớm
nghĩa là biên bản **chỉ nêu lý do đầu tiên**, các tầng sau mang `da_chay = False`.

Đây chính là lý do §2.1 nói *dừng sớm không phải để nhanh mà để đúng*: nếu cứ chạy tiếp
thì báo cáo sẽ đếm bài này vào thống kê tầng 4 và tầng 5, làm sai cả hai con số.

#### 8.2.3. id = 4389 — *"Mỹ nhân"* · **5 dòng** ⛔ · siêu dữ liệu lẫn vào thơ

```
D1  Giấu dải ngân hà trong vạt áo,      T B T  trắc  vần: ao   x
D2  Nàng đi thơ thẩn tựa làn mây.       B T B  bằng  vần: ây  ──┐ a
D3  Trăng sao òa vỡ thành quách đổ,     B T T  pha   vần: ô    x
D4  Gió gầy chuông nhạt ngẩn ngơ cây.   B T B  bằng  vần: ây  ──┘
D5  *Plei Ku, 27.9.2004*                 12 tiếng — KHÔNG phải câu thơ  ⛔
```

```
⛔ BÀI 5 DÒNG — dư 1 khi chia 4
   H4: cần "số dòng là bội của 4" | đang "5 dòng, dư 1 khi chia 4"
```

**Bốn dòng đầu là một bài tứ tuyệt hoàn chỉnh.** Dòng thứ năm là **nơi chốn và ngày
tháng sáng tác** bị gộp vào trường nội dung — lỗi dữ liệu, không phải lỗi bài thơ.

Bóc D5 ra thì bài còn 4 dòng, sơ đồ `xaxa` (D2 hiệp D4) — **có vần chân, đủ qua cổng 5**
theo QĐ-7b. Nó vẫn sẽ trượt cổng 4 vì D3 phá khuôn.

Ca này thuộc nhóm *"cứu bằng bóc dòng siêu dữ liệu"* — xem quy tắc **L1** ở báo cáo
corpus §6.4 (*bóc dòng bọc kín trong `*...*`*).

---

### 8.3. BA BÀI TRƯỢT Ở CỔNG 2 — dòng sai số tiếng (H1, H2)

> **2.069 bài, 7.645 dòng hỏng.** Một dòng lệch là cả bài trượt — H2 không có ngoại lệ.

#### 8.3.1. id = 4557 — *"Xuân bất tận"* · 8 dòng · **D1 thiếu 1 tiếng** ⛔

```
D1  Không quá khứ, không vị lai,        ⛔ 6 tiếng — THIẾU 1
D2  Thời gian xuân giữ thắm tươi hoài.     7 tiếng
D3  Từ lâu xanh vẫn mơn cành liễu,         7 tiếng
D4  Và mãi vàng luôn đượm cánh mai.        7 tiếng
D5  Cuộc thế mị thường cơn mộng lớn,       7 tiếng
D6  Nguồn xuân bất tận suối thơ dài.       7 tiếng
D7  Làm chi năm một lần khai bút,          7 tiếng
D8  Bút đã khai từ thiên địa khai.         7 tiếng
```

```
⛔ 1/8 dòng sai số tiếng: D1=6
   H1 tại D1: cần "7 tiếng" | đang "6 tiếng"
   gợi ý: thêm 1 tiếng; giữ vần "ai" ở tiếng cuối nếu dòng này đang gánh vần
```

**Bảy trên tám dòng hoàn hảo.** Đây là hình mẫu của nhóm **D — *"Đúng một dòng thiếu một
tiếng"*** (1.060 bài trong corpus), nhóm có tỉ lệ cứu-bằng-sửa-tay tốt nhất.

Vế thứ hai của `goi_y` là chỗ tinh tế: D1 kết bằng `lai` (vần `ai`), cùng lớp với D4
`mai`, D6 `dài`, D8 `khai`. Sửa độ dài mà làm hỏng vần thì bài sẽ trượt tầng 5 ở lượt
sau — vòng sửa quay vòng không hội tụ. Nên bộ kiểm nhắc trước.

#### 8.3.2. id = 7534 — *"MỪNG XUÂN MỚI"* · 8 dòng · **D1 thiếu 1 tiếng** ⛔

```
D1  Chào năm tới, tuổi con trâu,        ⛔ 6 tiếng — THIẾU 1
D2  Xã hội văn minh, nước mạnh giàu.       7 tiếng   T B T  trắc
D3  Tổ quốc đang đà trang đổi mới,         7 tiếng   T B T  trắc
D4  Buôn làng nhảy vọt hướng chiều sâu.    7 tiếng   B T B  bằng
D5  Nhà nhà phấn khởi nông thôn mới,       7 tiếng   B T B  bằng
D6  Phố phố vươn lên tốp dẫn đầu.          7 tiếng   T B T  trắc
D7  Tạo dáng quê hương đầy thắng lợi,      7 tiếng   T B T  trắc
D8  Vui mừng đất Việt vượng dài lâu.       7 tiếng   B T B  bằng
```

```
⛔ 1/8 dòng sai số tiếng: D1=6
   H1 tại D1: cần "7 tiếng" | đang "6 tiếng"
```

**Cùng dạng hỏng với 8.3.1, cùng ở D1.** Bảy dòng còn lại đều khớp khuôn — nếu D1 được
sửa thành 7 tiếng và giữ vần `âu`, bài này có triển vọng đi hết bảy tầng.

Chú ý: cột khuôn chỉ hiện từ D2, vì `khuon_cua_dong()` trả `khong_xac_dinh` cho dòng
không đủ 7 tiếng — **không** trả `pha`. Gọi một dòng sai luật cứng là *"phá khuôn"* tức
là gán cho tác giả một lựa chọn phong cách họ chưa hề thực hiện.

#### 8.3.3. id = 4458 — *"Thu điếu (II)"* · 4 dòng · **D4 là dòng ký tên** ⛔

```
D1  Cá đâu đớp động dưới chân bèo,         7 tiếng   B T B  bằng
D2  Liễu lim dim, nước không gợn sóng,     7 tiếng   B T T  pha
D3  Một ngờ liếc biếc động ao thu.         7 tiếng   B T B  bằng
D4  — Nguyễn Khuyến                     ⛔ 2 tiếng — tên tác giả
```

```
⛔ 1/4 dòng sai số tiếng: D4=2
   H1 tại D4: cần "7 tiếng" | đang "2 tiếng"
```

**Siêu dữ liệu lẫn vào thơ, dạng phổ biến nhất.** Dòng ký tên tác giả bị gộp vào trường
nội dung. Lưu ý gạch ngang dài `—` **không được tính là tiếng** (§2.1), nên `— Nguyễn Khuyến` đếm ra 2 tiếng chứ không phải 3 — đây là chỗ bản `rule.py` đầu tiên từng đếm sai
vì liệt kê dấu câu bằng tay và thiếu `—`.

Bóc D4 ra thì bài còn 3 dòng, và sẽ trượt **cổng 1** vì 3 không phải bội của 4.

---

### 8.4. BA BÀI TRƯỢT Ở CỔNG 4 — phá khuôn thanh luật (S2)

> **30.571 bài — 99,86% toàn bộ bài trượt.** Đây là nút cổ chai, và phần lớn số bài này
> **không sai gì theo câu chữ tài liệu** — chúng trượt vì QĐ-1 và QĐ-2.

#### 8.4.1. id = 27 — *"SAY"* · 8 dòng · **4/8 dòng phá khuôn** ⛔

```
D1  Góc sân trời đất cảnh thực hay,     ⛔ B T T  pha   cần B T B hoặc T B T
D2  Dao lẹ thịt nhân bác thái phay.        T B T  trắc
D3  Lạt mềm cong cớn ba ngồi chẻ,          B T B  bằng
D4  Lá dong tay má vuốt thẳng ngay.     ⛔ B T T  pha
D5  Tiêu cay đậu phộng thơm thơm nếp,      B T B  bằng
D6  Nội gói thít đòn đẹp mắt thay.         T B T  trắc
D7  Hương bánh lửa tràn reo xuân tới,   ⛔ T B B  pha
D8  Khói đậu nhành mai ngỡ mình say.    ⛔ T B B  pha
```

```
⛔ 4/8 dòng phá khuôn: D1, D4, D7, D8
   S2 tại D1: cần "P2/P4/P6 luân phiên theo khuôn bằng (B T B) hoặc khuôn trắc (T B T)"
              | đang "P2/P4/P6 = B T T"
              gợi ý: Đổi thanh ở P2, P4 hoặc P6 để dòng khớp một trong hai khuôn
   S2 tại D4: đang "P2/P4/P6 = B T T"
   S2 tại D7: đang "P2/P4/P6 = T B B"
   S2 tại D8: đang "P2/P4/P6 = T B B"
```

**Đọc bằng chứng để sửa:** D1 đang `B T T`. Chỉ cần đổi P6 (`thực`, thanh nặng = T) sang
một tiếng thanh bằng là dòng thành `B T B` — khuôn bằng. Đây là lý do `thuc_te` in ra ba
giá trị thanh thật: **mô hình đọc `B T T` là biết ngay phải sửa vị trí nào**, không cần
chạy lại bộ kiểm.

Bài này vẫn **thuộc thể** (`thuoc_the = True`, vì H1–H4 đều đạt) nhưng **không đạt chuẩn
dự án**. Ca minh hoạ rõ nhất vì sao hai cờ phán quyết phải tách rời.

#### 8.4.2. id = 3431 — *"Ý thơ"* · 4 dòng · **đúng 1 dòng phá khuôn** ⛔

```
D1  Em ở miền xa nghe gió đốt,             T B T  trắc  vần: ôt  ──┐ a
D2  Rát mặt lời yêu méo tháng chờ.         T B T  trắc  vần: ơ  ─┐ │ b
D3  Anh gom vuông nắng hong đột ngột,   ⛔ B T T  pha   vần: ôt  ─│─┘ a
D4  Giật thót mành che ngang ý thơ.        T B T  trắc  vần: ơ  ─┘   b
```

```
⛔ 1/4 dòng phá khuôn: D3
   S2 tại D3: cần "P2/P4/P6 luân phiên theo khuôn bằng (B T B) hoặc khuôn trắc (T B T)"
              | đang "P2/P4/P6 = B T T"
```

**Bài này có sơ đồ vần `abab` — vần cách, một trong bốn sơ đồ §5.2**, và chỉ hỏng **đúng
một dòng** ở P2. Nó thuộc nhóm **6.162 bài (20,16%) chỉ lệch một dòng** ở cổng 4.

Đổi P2 của D3 (`gom`, thanh ngang = B) sang một tiếng thanh trắc là dòng thành `T B T` —
khuôn trắc, và cả bài đi hết bảy tầng. Đây là tỉ lệ đổi lại tốt nhất trong corpus, và là
con số đáng nhìn lại nếu muốn cân nhắc nới QĐ-1.

#### 8.4.3. id = 3337 — *"Chia tay"* · 8 dòng · **đúng 1 dòng phá khuôn** ⛔

```
D1  Chúng mình gặp nhau trong chiến đấu, ⛔ B B T  pha   vần: âu
D2  Cũng vì chiến đấu lại xa nhau.          B T B  bằng  vần: au
D3  Biên giới mùa mưa nhiều thác lũ,        T B T  trắc  vần: u
D4  Bạn đi, tôi tiễn đến bên cầu.           B T B  bằng  vần: âu
D5  Sẻ thêm cho bạn mươi viên đạn,          B T B  bằng  vần: an
D6  Ở đấy hẳn cần hơn tuyến sau.            T B T  trắc  vần: au
D7  Khi gần, mới chỉ gần bên cạnh,          B T B  bằng  vần: anh
D8  Xa rồi, vào ở hẳn trong nhau.           B T B  bằng  vần: au
```

```
⛔ 1/8 dòng phá khuôn: D1
   S2 tại D1: đang "P2/P4/P6 = B B T"
```

**Bảy trên tám dòng khớp khuôn.** D1 đang `B B T` — lệch ở **cả P4 lẫn P6** so với khuôn
bằng, hoặc lệch ở **P2 và P6** so với khuôn trắc; sửa một vị trí là đủ về khuôn bằng
(`B T B`) nếu đổi P4.

Cụm D1–D4 có sơ đồ `axxa` (`đấu ~ cầu`, cùng lớp `âu`) — **có vần chân**, nên nếu qua
được cổng 4 thì cổng 5 cho đi tiếp theo QĐ-7b.

---

### 8.5. BA BÀI TRƯỢT Ở CỔNG 5 — không cụm bốn dòng nào có vần chân (S11)

> **360 bài — 1,46% số bài vào cổng.** Từ QĐ-7b, dạng **duy nhất** còn bị loại là `xxxx`:
> trong mọi cụm bốn dòng liên tiếp, không cặp tiếng cuối nào hiệp vần.

#### 8.5.1. id = 4051 — *"Xin ủ mùa thu"* · 4 dòng · `xxxx` ⛔

```
D1  Cho tôi ủ chút sương trăng trước,    B T B  bằng   vần: ươc   x
D2  Với lá vàng rơi cuối ngõ khuya.      T B T  trắc   vần: uya   x
D3  Nhỡ khi tiếc nuối người quay lại,    B T B  bằng   vần: ai    x
D4  Đã sẵn hương thu ướp tóc thề.        T B T  trắc   vần: ê     x
```

```
⛔ không cụm bốn dòng liên tiếp nào có vần chân — dòng 1–4: xxxx
   S11 (mức bài): cần "ít nhất 4 dòng liên tiếp có vần chân — trong cụm đó phải có
                  ít nhất một cặp tiếng cuối hiệp vần"
                  | đang "dòng 1–4: xxxx"
   gợi ý: Sửa tiếng cuối của hai dòng trong cùng một cụm bốn dòng cho hiệp vần;
          sơ đồ nào cũng được, không bắt buộc aabb/abab
```

**Bốn dòng đều 7 tiếng, đều khớp khuôn, thanh luật hoàn hảo (`bằng·trắc·bằng·trắc` = tổ
hợp #6).** Bài chết đúng ở vần: bốn vần `ươc · uya · ai · ê` đôi một không liên quan.

Chú ý `dong = None` trong `ViPham` — đây là **lỗi mức bài**, không phải mức dòng. Không
có dòng nào "sai"; cái sai là **quan hệ giữa chúng**.

#### 8.5.2. id = 4067 — *"Xa và gần"* · 4 dòng · `xxxx` ⛔

```
D1  Chẳng khuất xa nào xa khuất hơn,     T B T  trắc   vần: ơn    x
D2  Bàn tay ngoài cõi vẫy trên cồn.      B T B  bằng   vần: ôn    x
D3  Chẳng có gần nào gần gũi vậy,        T B T  trắc   vần: ây    x
D4  Chiếc lá vừa rơi cội đã ôm.          T B T  trắc   vần: ôm    x
```

```
⛔ không cụm bốn dòng liên tiếp nào có vần chân — dòng 1–4: xxxx
```

**Ca sát biên, đáng đọc kỹ.** `hơn` (vần `ơn`) và `cồn` (vần `ôn`) — tai người Việt nghe
rất gần, nhiều người sẽ coi là hiệp. Nhưng bảng Trần Trọng Kim **không nối `ơn` với
`ôn`**: nó có nhóm `on · ôn · uôn` và cặp rời `an ~ ơn`, và hai phát biểu ấy **không bắc
cầu**.

Đây là hệ quả trực tiếp của quyết định **không ép bảng vần thành lớp tương đương**. Nếu
gom bắc cầu thì `ơn ~ an ~ ...` sẽ kéo theo hàng loạt cặp mà nguồn không cho — bịa thêm
18 cặp hiệp vần. Bộ kiểm chọn **chặt và trung thành với nguồn**, và trả giá bằng những ca
như thế này.

#### 8.5.3. id = 4189 — *"Mùa xuân trên Thiên Cấm sơn"* · 4 dòng · `xxxx` ⛔

```
D1  Mây đáp sườn non cây hóa mộng,       T B T  trắc   vần: ông   x
D2  Nắng len đỉnh núi chạm hoa vàng.     B T B  bằng   vần: ang   x
D3  Hồn ai phơi giữa mùa mây trắng,      B T B  bằng   vần: ăng   x
D4  Én về mỏ ngậm một cành xuân.         B T B  bằng   vần: uân   x
```

```
⛔ không cụm bốn dòng liên tiếp nào có vần chân — dòng 1–4: xxxx
```

**Ca sát biên thứ hai.** `vàng` (`ang`) và `trắng` (`ăng`) chỉ khác nhau ở độ dài nguyên
âm. Bảng nguồn có nhóm `ăng · âng · ưng` và cặp `ang ~ ương`, nhưng **không** nối `ang`
với `ăng`.

Hai ca 8.5.2 và 8.5.3 cho thấy 360 bài ở cổng này **không phải toàn thơ không vần** —
một phần là thơ có vần *thông* mà bảng nguồn không công nhận. Nếu muốn nới, chỗ cần xem
là **bảng vần**, không phải tiêu chí tầng 5.

---

### 8.6. Không có ví dụ cho cổng 3, 6, 7

| Cổng                                    | Vì sao không có bài trượt                                                                                                                                                                     |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **3. Đối chiếu Đường luật** | `muc = "ghi_nhan"` — tầng này **không có tiêu chí chặn** theo thiết kế. Nó đánh dấu 4.288 bài `nghi_duong_luat` rồi cho đi tiếp; cả 4.288 bài đều vào tập đạt   |
| **6. Nhịp**                       | Tầng**rỗng nghĩa** — chưa có bộ tách từ tiếng Việt nên mọi dòng 7 tiếng đều cắt được theo cả bảy kiểu. Xem §7.6                                                      |
| **7. Khổ và bố cục**           | Tiêu chí là*"không có khổ rỗng"*, mà`tach_kho()` không bao giờ sinh khổ rỗng qua đường chạy thường. S16–S21 phần lớn là **quyền**, N2 cấm dùng để đánh trượt |

Ba cổng này vẫn **chạy và vẫn nộp bằng chứng** — xem bảng biên bản của id=3 ở §8.1.1.
Chặn 0 bài không có nghĩa là tầng thừa; với cổng 3 và 7 đó là **đúng thiết kế**, còn với
cổng 6 đó là **một lỗ hổng đã biết**.
-------------------------------------------

## 9. Cách kiến trúc tự bảo vệ

Bảy tầng đứng vững nhờ **107 test** (`test_rule_tang.py` 70, `test_rule.py` 37), trong đó
có các test **không kiểm một bài thơ nào** mà kiểm chính kiến trúc:

| Test                                                              | Chặn điều gì                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------------ |
| `test_moi_ma_luat_thuoc_DUNG_MOT_tang`                          | Thêm điều luật mà quên xếp tầng                      |
| `test_moi_luat_cung_deu_co_ham_kiem_tuong_ung`                  | Thêm luật cứng mà quên viết hàm kiểm                 |
| `test_khong_dieu_QUYEN_nao_lam_tieu_chi_chan`                   | **N2** — dùng quyền để đánh trượt             |
| `test_khong_tang_nao_dat_nguong_phan_tram_tu_bia`               | **N1** — ngưỡng phần trăm tự chế                |
| `test_dieu_KHONG_kiem_duoc_thi_KHONG_dong_thoi_la_tieu_chi`     | Một điều vừa "không kiểm được" vừa làm tiêu chí |
| `test_tang3_KHONG_duoc_chan_bai_nao`                            | Khôi phục nhầm lỗi tầng 3                               |
| `test_tang_GHI_NHAN_khong_gop_vao_phan_quyet_dat`               | Tầng ghi nhận lại đi đánh trượt                      |
| `test_S4_S5_S7_S8_da_xoa_khoi_bang_luat_va_KHONG_duoc_quay_lai` | Bốn mã đã xoá quay lại bảng luật                     |
| `test_so_hieu_dieu_luat_KHONG_duoc_danh_lai_sau_khi_xoa`        | Đánh số lại sau khi xoá                                 |
| `test_QD2_KHONG_con_ghi_de_dieu_nao_sau_khi_xoa_S4`             | Ghi bừa một mục ghi đè không còn đối tượng        |
| `test_moi_o_trong_bang_16_la_P2_P4_P6_cua_MOT_dong`             | Đọc lệch nghĩa bảng 16 tổ hợp                         |
| `test_P1_P3_P5_va_P7_KHONG_tham_gia_bang_16`                    | P1/P3/P5/P7 lọt vào phép tính khuôn                     |
| `test_bang_16_la_TAP_DAY_DU_chu_khong_phai_tap_con`             | Rút bảng 16 thành tiêu chí chặn ngầm                  |
| `test_QD7b_chi_xxxx_bi_loai`                                    | Siết lại tiêu chí tầng 5 mà không tuyên bố          |
| `test_hiep_van_KHONG_bac_cau_dung_nhu_nguon`                    | Ép bảng vần thành lớp tương đương                  |
| `test_bang_van_dung_dung_so_canh_cua_nguon`                     | Bảng vần lệch khỏi nguồn (73 + 4)                       |
| `test_so_do_van_KHONG_phu_thuoc_thu_tu_dong`                    | Bug thứ tự dòng quay lại                                 |
| `test_truot_tang_som_thi_cac_tang_sau_KHONG_chay`               | Dừng sớm bị phá                                          |
| `test_pha_khuon_van_THUOC_THE_nhung_KHONG_dat_chuan_du_an`      | Gộp hai cờ phán quyết                                    |

Ngoài test, còn **ba script đối soát** chạy được trong CI:

| Script                   | Kiểm gì                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `kiem_tra_toan_bo.py`  | Sinh lại toàn bộ số liệu, tự đối soát đầu vào — đầu ra, thoát ≠ 0 nếu lệch  |
| `doi_soat_ket_qua.py`  | Kiểm chứng**độc lập**: phân hoạch id, lấy mẫu chạy lại, nhất quán nội tại |
| `doi_soat_tai_lieu.py` | Mọi con số trong`.md` phải truy được về `tong_hop.json` hoặc `rule.py`           |

Script thứ ba ra đời sau một bài học đã trả giá: một con số (**3.975**) được gõ ra theo
cảm tính trong một lệnh thay-thế-hàng-loạt, lọt vào ba tài liệu và nằm đó cho tới khi
tình cờ bị phát hiện. Nó cũng tự đo quy mô `rule.py` bằng AST thay vì tin vào con số gõ
tay.

---

## 10. Đánh giá thẳng

### Mạnh

1. **Không tầng nào có thể nói dối im lặng.** `da_chay=False` tách bạch `dat=False`; điều
   không kiểm được ghi thẳng vào `chi_tiet`; tiêu chí phải trích được từ tài liệu.
2. **Luật là dữ liệu**, nên sửa luật không phải sửa thuật toán. Năm lần sửa bảng luật
   trong ngày 18/09 không đụng tới một dòng thuật toán nào.
3. **Hai cờ phán quyết** khiến mã nguồn không ngầm sửa tài liệu.
4. **Hai mức tầng** cho phép quan sát mà không kết án — đúng thứ tầng 3 cần.
5. **Bảng vần có nguồn thật**, ba chỗ suy diễn đánh dấu 🔶 tại chỗ, và xử lý đúng việc
   quan hệ vần không bắc cầu — chỗ hầu hết công cụ làm sai.
6. **Số hiệu điều luật không đánh lại sau khi xoá**, nên mọi tham chiếu cũ vẫn trỏ đúng.

### Yếu

1. **Tầng 6 rỗng nghĩa** — một trong bảy cổng đang giả vờ đã kiểm mà thực ra chưa kiểm gì.
   Cần bộ tách từ tiếng Việt. Đây là lỗ hổng lớn nhất còn lại.
2. **Cổng 4 chiếm 99,86% số bài trượt.** Sau QĐ-7b, cả bộ luật dồn vào một cổng duy nhất,
   và cổng ấy chặn vì hai quyết định chặt hơn tài liệu (QĐ-1, QĐ-2). Trong đó **6.162 bài
   chỉ lệch đúng một dòng**.
3. **Tầng 5 chỉ chặn 1,46%** — ít, nhưng **đúng thiết kế, không phải khiếm khuyết**.
   Chủ dự án đã xác nhận ngày 18/09: *"chỉ chặn trường hợp `xxxx` thôi"*. Xem §7.5 để
   biết vì sao con số nhỏ ấy là tất yếu chứ không phải dấu hiệu hỏng.
4. **`hiep_van()` chưa nối QĐ-3.** §5b tuyên bố phép so vần chính thức là *âm chính + âm
   cuối*, và `van_cua()` tự khai *"GIỮ LẠI để tương thích ngược"* — nhưng `hiep_van()` vẫn
   gọi `van_cua()`. Hệ quả: `hoa` không hiệp `ta`, `tuyết` không hiệp `biết`. 4,75% tiếng
   cuối dòng có âm đệm, và chúng là những vần phổ biến nhất (*hoa*, *qua*, *xuân*, *quê*,
   *duyên*). **Chưa sửa — cần đo lại tác động trên luật mới.**
5. **Bốn cạnh vần là suy diễn**, không trích từ nguồn (`o~ua`, `ia~uê`, `ac~ươc`, `ât~ưt`
   — đánh dấu 🔶 SD-2 tại chỗ). Chủ dự án duyệt nguồn nhưng chưa gật riêng ba chỗ suy diễn.
6. **`kiem_tra_bai_tho` dài 142 dòng** — phần chuẩn bị chung đang phình. Thêm tầng thứ tám
   thì nên tách phần chuẩn bị ra trước.
7. **Tầng 5 chỉ đòi một cửa sổ.** Đúng theo §5.2 *vần hỗn hợp*, nhưng nghĩa là bài 40 dòng
   chỉ cần 4 dòng có vần là qua tầng.

---

## 11. Tra cứu nhanh

| Cần tìm                                | Ở đâu                           |
| ---------------------------------------- | ---------------------------------- |
| Bảng 26 điều luật                    | `rule.py` §1, dòng 51          |
| Phân loại 17 điều mềm               | `rule.py` §1b, dòng 154        |
| **Khai báo bảy tầng**           | `rule.py` §1c, dòng 190        |
| Kiểu dữ liệu kết quả                | `rule.py` §2, dòng 296         |
| Đếm tiếng, đọc số                  | `rule.py` §3, dòng 396         |
| Thanh điệu B/T                         | `rule.py` §4, dòng 546         |
| Tách vần,`hiep_van()`                | `rule.py` §5, dòng 589         |
| Bảng vần Trần Trọng Kim              | `rule.py` banner con trong §5   |
| Phân tích âm tiết 5 thành phần     | `rule.py` §5b, dòng 793        |
| Khuôn bằng / trắc                     | `rule.py` §6, dòng 956         |
| **Bảng 16 tổ hợp cụm 4 dòng** | `rule.py` §6c, dòng 1008       |
| Bảy kiểu nhịp                         | `rule.py` §6b, dòng 1111       |
| Sơ đồ vần                            | `rule.py` §7, dòng 1182        |
| Loại trừ Đường luật                | `rule.py` §8, dòng 1308        |
| Chuẩn bị chung                         | `rule.py` §9, dòng 1342        |
| **Mã bảy tầng**                 | `rule.py` §9b, dòng 1404–2035 |
| Bảng hàm kiểm luật cứng             | `rule.py` §10, dòng 2183       |
| Hàm điều khiển                       | `kiem_tra_bai_tho`, dòng 2038   |

```bash
sed -n '190,290p'   src/application/rule.py   # khai báo bảy tầng
sed -n '1404,2035p' src/application/rule.py   # mã bảy tầng
sed -n '2038,2179p' src/application/rule.py   # hàm điều khiển

python datalake/scripts/kiem_tra_toan_bo.py   # sinh lại toàn bộ số liệu
python datalake/scripts/doi_soat_ket_qua.py 500
python datalake/scripts/doi_soat_tai_lieu.py  # mọi con số phải truy được về nguồn
```

---

## 12. Nhật ký thay đổi bộ luật — 18/09/2026

| Thay đổi                                                                                               | Tác động lên`dat`   |
| -------------------------------------------------------------------------------------------------------- | ------------------------- |
| Sửa tầng 3:`chan` → `ghi_nhan` (F1–F5 là điều đã gỡ, không phải điều kiện loại trừ) | 16.391 → 18.583          |
| Thêm**H4**: số dòng phải là bội của 4; nâng **H3** từ ≥2 lên ≥4 dòng            | 18.583 → 18.150          |
| Thêm**§6c**: bảng 16 tổ hợp khuôn cụm 4 dòng (mô tả, không chặn)                             | không đổi              |
| Sửa lời**S1** (*"có thể tự do"*); **gộp S7 vào S1**; **xoá S4, S5**          | không đổi              |
| **QĐ-7b**: cụm 4 dòng chỉ cần CÓ vần chân; **xoá S8**                               | 18.150 →**24.366** |

Bảng luật đi từ 30 điều xuống **26 điều**. `thuoc_the` giữ nguyên 55.297 trong ba thay đổi
cuối, vì cả ba đều không đụng tới H1–H4.

**Việc còn treo:** nối QĐ-3 vào `hiep_van()` (xem §10 mục 4) — chưa đo lại tác động trên
luật mới.

---

## 13. BẢNG PHÂN TÍCH BẢY CỔNG — vào, qua, chặn

Bảng tra nhanh toàn bộ dây chuyền. Số liệu sinh từ `datalake/analysis/tong_hop.json`,
đo trên **67.150 bản ghi** (**62.034** bài có nội dung).

| STT | Tên cổng | Mô tả ngắn — Rule của cổng | Bản ghi VÀO | Bản ghi ĐÃ QUA |
|:--:|---|---|---:|---:|
| 1 | **Hình thức và số dòng**<br>H3, H4 · ⛔ chặn | Bài phải có phân dòng, **từ 4 dòng trở lên**, và **số dòng là bội của 4** | **62.034** | **57.366**<br>92,48% · chặn **4.668** |
| 2 | **Độ dài dòng**<br>H1, H2 · ⛔ chặn | **Mọi** dòng phải đúng **7 tiếng** — một dòng lệch là cả bài trượt | **57.366** | **55.297**<br>96,39% · chặn **2.069** |
| 3 | **Đối chiếu Đường luật**<br>F1–F5 · ℹ️ ghi nhận | *(không có tiêu chí chặn)* — chỉ **ghi nhận** bài có dáng Đường luật rồi cho đi tiếp | **55.297** | **55.297**<br>100,00% · chặn 0 |
| 4 | **Thanh luật**<br>S1–S3 · ⛔ chặn | **Mọi** dòng phải khớp khuôn bằng `B T B` hoặc khuôn trắc `T B T` tại P2/P4/P6 | **55.297** | **24.726**<br>44,71% · chặn **30.571** |
| 5 | **Vần**<br>S6, S9–S12 · ⛔ chặn | Phải có **≥ 1 cụm 4 dòng liên tiếp có vần chân** — trong cụm đó ít nhất một cặp tiếng cuối hiệp vần | **24.726** | **24.366**<br>98,54% · chặn **360** |
| 6 | **Nhịp**<br>S13–S15 · ⛔ chặn | Phải có **một nhịp chủ đạo** phủ mọi dòng, thuộc bảy kiểu nhịp của tài liệu | **24.366** | **24.366**<br>100,00% · chặn 0 |
| 7 | **Khổ và bố cục**<br>S16–S21 · ⛔ chặn | **Không có khổ rỗng** | **24.366** | **24.366**<br>100,00% · chặn 0 |

**Đọc bảng cho đúng:**

- **Bản ghi VÀO** của cổng N = **bản ghi ĐÃ QUA** của cổng N−1. Bài phải qua cổng N mới
  sang cổng N+1; trượt cổng nào thì **dừng ngay**, các cổng sau mang `da_chay = False`
  — *chưa kiểm*, **không** phải *đã kiểm và trượt*.
- **Tỷ lệ % trong cột ĐÃ QUA** lấy mẫu số là số bài **vào chính cổng đó** — đây là độ
  khắt khe của **riêng** cổng ấy, không phải tỷ lệ trên toàn corpus.
- **Cổng 3 luôn cho qua 100%** vì nó là cổng **ghi nhận**, không phải cổng chặn. Nó đánh
  dấu **4.288** bài `nghi_duong_luat` rồi vẫn cho đi tiếp.
- **Cổng 6 và 7 cũng cho qua 100%**, nhưng vì hai lý do khác nhau: cổng 7 đúng thiết kế
  (S16–S21 phần lớn là **quyền**, N2 cấm dùng để đánh trượt), còn cổng 6 là **lỗ hổng đã
  biết** — chưa có bộ tách từ tiếng Việt nên phép kiểm nhịp rỗng nghĩa (§7.6).

**Kết quả cuối dây chuyền:**

| | Số bài |
|---|---:|
| Vào cổng 1 | 62.034 |
| Ra khỏi cổng 7 — **ĐẠT cả bảy tầng** | **24.366** (39,28%) |
| Bị chặn dọc đường | 37.668 |
| Không có nội dung để kiểm | 5.116 |
| **Thuộc thể** theo tài liệu (chỉ cổng 1 + 2, tức H1–H4) | 55.297 |

Sinh lại bảng này: `python datalake/scripts/kiem_tra_toan_bo.py`
