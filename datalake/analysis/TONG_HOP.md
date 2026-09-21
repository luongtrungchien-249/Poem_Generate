# TỔNG HỢP KIỂM TRA TỪNG BÀI

**Nguồn:** `datalake/dataraw/final_data_7_chu.jsonl` · **Bộ luật:** `src/application/rule.py`

> ⚙️ **Tệp này do máy sinh ra — đừng sửa tay.**
> Sinh lại: `python datalake/scripts/kiem_tra_toan_bo.py`

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
67,150 bản ghi = 24,366 đạt + 37,668 trượt + 5,116 không có nội dung
62,034 lần gọi luật = 24,366 đạt + 37,668 trượt
```

---

## 2. Phễu theo từng cổng

Bài phải qua cổng N mới sang cổng N+1.

- **% qua** và **% chặn** lấy mẫu số là số bài **đi vào cổng đó** — đo độ khắt
  khe của riêng cổng.
- **Còn lại** lấy mẫu số là **toàn bộ bài có nội dung** — đường sống sót tích luỹ.
- **Đánh dấu** là số bài cổng ghi nhận có phát hiện nhưng **vẫn cho đi tiếp**.

| Cổng | Mức | Điều luật | Vào | Qua | % qua | Chặn | % chặn | Còn lại | Đánh dấu |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1. Hình thức và số dòng | ⛔ chặn | H3, H4 | 62,034 | 57,366 | 92.48% | 4,668 | 7.52% | 92.48% | 0 |
| 2. Độ dài dòng | ⛔ chặn | H1, H2 | 57,366 | 55,297 | 96.39% | 2,069 | 3.61% | 89.14% | 0 |
| 3. Đối chiếu Đường luật | ℹ️ ghi nhận | F1, F2, F3, F4, F5 | 55,297 | 55,297 | 100.00% | 0 | 0.00% | 89.14% | 4,288 |
| 4. Thanh luật | ⛔ chặn | S1, S2, S3 | 55,297 | 24,726 | 44.71% | 30,571 | 55.29% | 39.86% | 0 |
| 5. Vần | ⛔ chặn | S6, S9, S10, S11, S12 | 24,726 | 24,366 | 98.54% | 360 | 1.46% | 39.28% | 0 |
| 6. Nhịp | ⛔ chặn | S13, S14, S15 | 24,366 | 24,366 | 100.00% | 0 | 0.00% | 39.28% | 0 |
| 7. Khổ và bố cục | ⛔ chặn | S16, S17, S18, S19, S20, S21 | 24,366 | 24,366 | 100.00% | 0 | 0.00% | 39.28% | 0 |

## 3. Kết quả

| | Số bài |
|---|---:|
| Thuộc thể theo **tài liệu** (chỉ H1–H3) | 55,297 |
| **Đạt theo chuẩn dự án** (cả 7 tầng) | **24,366** |
| Trượt | 37,668 |
| Không có nội dung | 5,116 |
| Tỉ lệ đạt trên bài có nội dung | 39.28% |

## 4. Vì sao trượt — theo từng cổng

Số bên cạnh mã luật là **số lần vi phạm**, không phải số bài: một bài có thể
phạm cùng một điều ở nhiều dòng.

**Cổng 1 — Hình thức và số dòng**

- `4,668` H4: số dòng là bội của 4
- `655` H3: văn bản có phân dòng, từ 4 dòng trở lên

**Cổng 2 — Độ dài dòng**

- `7,645` H1: 7 tiếng

**Cổng 4 — Thanh luật**

- `160,828` S2: P2/P4/P6 luân phiên theo khuôn bằng (B T B) hoặc khuôn trắc (T B T)

**Cổng 5 — Vần**

- `360` S11: ít nhất 4 dòng liên tiếp có vần chân — trong cụm đó phải có ít nhất một cặp tiếng cuối hiệp vần

## 5. Nhóm nguyên nhân trượt

| Nhóm | Số bài |
|---|---:|
| A. Thơ 8 chữ bị gán nhãn 7 chữ | 135 |
| B. Lẫn văn xuôi trong trường thơ | 22 |
| C. Có dòng phân cách không chứa tiếng | 34 |
| D. Đúng một dòng thiếu một tiếng | 1,060 |
| E. Đúng một dòng thừa một tiếng | 338 |
| F. Đúng một dòng lệch nhiều tiếng | 242 |
| G. Hai dòng lệch | 35,312 |
| H. Lệch nhiều dòng | 525 |

Bài rỗng có thể cứu được: **1,934**

## 6. Tổ hợp khuôn của cụm bốn dòng — tài liệu §4.4

Đếm trên **24,366 bài đạt**, mẫu số là **cụm**, không phải
bài: một bài 12 dòng góp 3 cụm. Tổng **73,106 cụm**.

Bảng 16 tổ hợp là tập **đầy đủ** (2⁴), nên nó KHÔNG loại bài nào — đây là
số liệu mô tả, không phải tiêu chí chặn.

Mỗi ô là **ba giá trị thanh ở P2, P4, P6 của một dòng**: `B-T-B` = khuôn
bằng, `T-B-T` = khuôn trắc. P1/P3/P5 tự do (S1) và P7 thuộc về vần nên
không có mặt ở đây.

| # | D1 · D2 · D3 · D4 (mỗi dòng: P2-P4-P6) | Số cụm | Tỷ lệ | |
|---:|---|---:|---:|---|
| 10 | `T-B-T  B-T-B  B-T-B  T-B-T` | 41,227 | 56.39% | ← mẫu đảo §4.3 |
| 7 | `B-T-B  T-B-T  T-B-T  B-T-B` | 27,982 | 38.28% | ← mẫu cổ điển §4.3 |
| 6 | `B-T-B  T-B-T  B-T-B  T-B-T` | 999 | 1.37% |  |
| 11 | `T-B-T  B-T-B  T-B-T  B-T-B` | 561 | 0.77% |  |
| 2 | `B-T-B  B-T-B  B-T-B  T-B-T` | 328 | 0.45% |  |
| 9 | `T-B-T  B-T-B  B-T-B  B-T-B` | 326 | 0.45% |  |
| 4 | `B-T-B  B-T-B  T-B-T  T-B-T` | 216 | 0.30% |  |
| 5 | `B-T-B  T-B-T  B-T-B  B-T-B` | 213 | 0.29% |  |
| 13 | `T-B-T  T-B-T  B-T-B  B-T-B` | 207 | 0.28% |  |
| 14 | `T-B-T  T-B-T  B-T-B  T-B-T` | 195 | 0.27% |  |
| 1 | `B-T-B  B-T-B  B-T-B  B-T-B` | 180 | 0.25% |  |
| 12 | `T-B-T  B-T-B  T-B-T  T-B-T` | 180 | 0.25% |  |
| 8 | `B-T-B  T-B-T  T-B-T  T-B-T` | 178 | 0.24% |  |
| 3 | `B-T-B  B-T-B  T-B-T  B-T-B` | 159 | 0.22% |  |
| 15 | `T-B-T  T-B-T  T-B-T  B-T-B` | 88 | 0.12% |  |
| 16 | `T-B-T  T-B-T  T-B-T  T-B-T` | 67 | 0.09% |  |

Hai mẫu §4.3 chiếm **69,209/73,106 = 94.67%** số cụm.
Mười bốn tổ hợp còn lại: **5.33%**.

## 7. Tệp kết quả

| Tệp | Nội dung |
|---|---|
| `bai_dat.jsonl` | Bài đạt, kèm dấu vết 7 tầng |
| `bai_truot.jsonl` | Bài trượt, kèm tầng dừng và vi phạm |
| `bai_truot_chi_tiet.jsonl` | Bản trích có bằng chứng từng dòng |
| `bai_khong_co_noi_dung.jsonl` | Bản ghi rỗng |
| `bai_rong_cuu_duoc.jsonl` | Bản ghi rỗng nhưng còn cứu được |
| `tong_hop.json` | Chính số liệu của tệp này, dạng máy đọc |

