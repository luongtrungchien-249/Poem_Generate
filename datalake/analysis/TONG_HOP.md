# TỔNG HỢP KIỂM TRA TỪNG BÀI

**Nguồn:** `datalake/dataraw/final_data_7_chu.jsonl` · **Bộ luật:** `src/application/rule.py` · **Ngày:** 17/09/2026

Sinh ra bởi `datalake/scripts/kiem_tra_toan_bo.py`, kiểm chứng bởi `datalake/scripts/doi_soat_ket_qua.py`.

---

## 1. Đối soát — mọi bản ghi đều đã đi qua rule.py

| Phép đếm | Giá trị |
|---|---:|
| Dòng đọc từ tệp nguồn | 67,150 |
| Bản ghi parse được | 67,150 |
| **Số lần gọi `kiem_tra_bai_tho()`** | **62,034** |
| id duy nhất | 67,150 |
| Đối soát | ✅ KHỚP |

```
67,150 bản ghi = 59,437 đạt + 2,597 trượt + 5,116 không có nội dung
62,034 lần gọi luật = 59,437 đạt + 2,597 trượt
```

Kiểm chứng độc lập: ba tệp kết quả tạo thành **phân hoạch đúng** của tập id nguồn — 0 thiếu, 0 thừa, 0 chồng lấn. Lấy mẫu ngẫu nhiên 500 bài chạy lại `rule.py`: **0 lệch**.

---

## 2. Tổng số bài

| Trạng thái | Số bài | Tỷ lệ | Tệp chi tiết |
|---|---:|---:|---|
| ✅ **ĐẠT** | **59,437** | 88.51% toàn tệp · 95.81% bài có nội dung | `bai_dat.jsonl` |
| ❌ **TRƯỢT** | **2,597** | 3.87% toàn tệp · 4.19% bài có nội dung | `bai_truot.jsonl` |
| ⚪ Không có nội dung | 5,116 | 7.62% | `bai_khong_co_noi_dung.jsonl` |
| | **67,150** | 100% | |

---

## 3. VÌ SAO ĐẠT

Một bài đạt khi và chỉ khi thoả cả ba luật cứng. Với 59,437 bài đạt, lý do luôn cùng một dạng:

```
"ly_do_dat": "H1+H2: cả N/N dòng đều đúng 7 tiếng. H3: văn bản có phân dòng."
```

Kèm **bằng chứng số học** để kiểm lại được mà không cần chạy luật:

```json
"bang_chung": { "so_dong": 8, "so_tieng_nho_nhat": 7, "so_tieng_lon_nhat": 7, "moi_dong_deu_7_tieng": true }
```

Nhỏ nhất = lớn nhất = 7 thì không dòng nào lệch được. Kiểm lại toàn bộ 59.437 bài: **0 bài thiếu bằng chứng**.

### Hình thức của bài đạt

| Số dòng | Số bài | Tỷ lệ |
|---:|---:|---:|
| 8 | 20,625 | 34.70% |
| 4 | 10,141 | 17.06% |
| 16 | 9,243 | 15.55% |
| 12 | 4,705 | 7.92% |
| 20 | 3,926 | 6.61% |
| 24 | 2,166 | 3.64% |

### Đặc điểm mềm được ghi kèm (không ảnh hưởng phán quyết)

| Đặc điểm | Số bài | Tỷ lệ |
|---|---:|---:|
| Có cặp vần lệch lớp thanh (S9) | 18,561 | 31.23% |
| Có vần lưng ở P4/P5 (S7) | 23,432 | 39.42% |
| Nghi là Đường luật (§9 Bước 2) | 3,599 | 6.06% |

---

## 4. VÌ SAO TRƯỢT

### 4.1. Mã luật bị vi phạm

| Mã | Nội dung | Số lần |
|---|---|---:|
| H1 | Mỗi dòng phải có đúng 7 tiếng | 9,015 |
| H3 | Văn bản phải được phân dòng | 2 |

H2 không xuất hiện riêng vì nó là phạm vi áp dụng của H1, không phải phép kiểm độc lập.

### 4.2. Bao nhiêu dòng hỏng đủ giết một bài

| Số dòng hỏng | Số bài | Tỷ lệ bài trượt |
|---|---:|---:|
| 0 (vi phạm H3) | 2 | 0.08% |
| 1 | 1,679 | 64.65% |
| 2 | 243 | 9.36% |
| 3 | 95 | 3.66% |
| 4 | 218 | 8.39% |
| 5 trở lên | 360 | 13.86% |

**1,679 bài — 64.7% — chết vì đúng một dòng.**

### 4.3. Độ dài của dòng hỏng

| Số tiếng | Số dòng | Tỷ lệ |
|---:|---:|---:|
| 0 | 58 | 0.64% |
| 1 | 89 | 0.99% |
| 2 | 32 | 0.35% |
| 3 | 70 | 0.78% |
| 4 | 87 | 0.97% |
| 5 | 221 | 2.45% |
| 6 | 1,935 | 21.46% |
| 8 | 6,372 | 70.68% |
| 9 | 60 | 0.67% |
| 10 | 38 | 0.42% |

### 4.4. Nhóm nguyên nhân, kèm ví dụ thật

| Nhóm | Số bài | Tỷ lệ |
|---|---:|---:|
| A. Thơ 8 chữ bị gán nhãn 7 chữ | 135 | 5.20% |
| B. Lẫn văn xuôi trong trường thơ | 22 | 0.85% |
| C. Có dòng phân cách không chứa tiếng | 34 | 1.31% |
| D. Đúng một dòng thiếu một tiếng | 1,060 | 40.82% |
| E. Đúng một dòng thừa một tiếng | 338 | 13.02% |
| F. Đúng một dòng lệch nhiều tiếng | 242 | 9.32% |
| G. Hai dòng lệch | 241 | 9.28% |
| H. Lệch nhiều dòng | 525 | 20.22% |

**A. Thơ 8 chữ bị gán nhãn 7 chữ**
```
id=3330  "Gửi Tây Thi"
D3 (8 tiếng): Liễu tây tử cựa mình trong bóng tối,
```

**B. Lẫn văn xuôi trong trường thơ**
```
id=3308  "Xóm Ngự Viên"
D1 (16 tiếng): Xóm Ngự Viên ở cạnh đường Gia Hội (Huế), ngày xưa là khu vườn thượng uyển.
```

**C. Có dòng phân cách không chứa tiếng**
```
id=3310  "Xuân tha hương"
D1 (3 tiếng): *(Gửi chị Trúc)*
```

**D. Đúng một dòng thiếu một tiếng**
```
id=2729  "(không tiêu đề)"
D7 (6 tiếng): Bao giờ nước sông ngừng chảy,
```

**E. Đúng một dòng thừa một tiếng**
```
id=13  "QUA TÌM BẬU BẬU NƠI ĐÂU"
D17 (8 tiếng): Đường về ngơ ngác hỏi bậu vì đâu?
```

**F. Đúng một dòng lệch nhiều tiếng**
```
id=17  "THÀNH CỔ"
D5 (3 tiếng): — Lê Bá Dương
```

**G. Hai dòng lệch**
```
id=3741  "Thơ ghé bến người"
D1 (8 tiếng): Con chim bay không thấy bóng mình bay,
```

**H. Lệch nhiều dòng**
```
id=2728  "(không tiêu đề)"
D1 (8 tiếng): Bài thơ viết nửa đời còn dang dở,
```

---

## 5. Bài không có nội dung

5,116 bản ghi có `markdown_poem` rỗng nên **không thể đưa qua luật** — chúng không đạt cũng không trượt.

Trong số đó, **1,934 bài có nội dung nằm ở khoá khác** (`content_fix`, `markdown_poem_content`…). Trường `co_the_cuu_tu_khoa` trong `bai_khong_co_noi_dung.jsonl` ghi rõ khoá nào.

---

## 6. Tệp trong thư mục này

| Tệp | Dòng | Nội dung |
|---|---:|---|
| `bai_dat.jsonl` | 59,437 | Mỗi bài đạt: lý do đạt + bằng chứng + đặc điểm mềm |
| `bai_truot.jsonl` | 2,597 | Mỗi bài trượt: mã luật, số dòng, kỳ vọng, thực tế, nội dung dòng, gợi ý sửa |
| `bai_khong_co_noi_dung.jsonl` | 5,116 | Bản ghi rỗng + khoá có thể cứu |
| `tong_hop.json` | — | Số liệu tổng hợp dạng máy đọc |
| `bai_rong_cuu_duoc.jsonl` | 1.934 | Nội dung thu hồi từ khoá sai (lần chạy trước) |
| `bai_truot_chi_tiet.jsonl` | 2.597 | Bản rút gọn của bai_truot (lần chạy trước) |
| `dong_nghi_ngo_trong_bai_dat.jsonl` | 42 | Bài đạt nhưng còn dòng siêu dữ liệu |