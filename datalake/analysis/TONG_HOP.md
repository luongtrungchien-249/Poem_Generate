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
67,150 bản ghi = 16,391 đạt + 45,643 trượt + 5,116 không có nội dung
62,034 lần gọi luật = 16,391 đạt + 45,643 trượt
```

---

## 2. Phễu theo từng cổng

Bài phải qua cổng N mới sang cổng N+1. Cột *chưa chạy* là số bài không được
kiểm ở cổng này vì đã bị một cổng trước chặn — **chưa kiểm, không phải đạt**.

| Cổng | Điều luật | Vào | Qua | Chặn tại đây | Chưa chạy |
|---|---|---:|---:|---:|---:|
| 1. Hình thức | H3 | 62,034 | 62,032 | 2 | 0 |
| 2. Độ dài dòng | H1, H2 | 62,032 | 59,437 | 2,595 | 2 |
| 3. Loại trừ Đường luật | F1, F2, F3, F4, F5 | 59,437 | 55,149 | 4,288 | 2,597 |
| 4. Thanh luật | S1, S2, S3, S4, S5 | 55,149 | 21,374 | 33,775 | 6,885 |
| 5. Vần | S6, S7, S8, S9, S10, S11, S12 | 21,374 | 16,391 | 4,983 | 40,660 |
| 6. Nhịp | S13, S14, S15 | 16,391 | 16,391 | 0 | 45,643 |
| 7. Khổ và bố cục | S16, S17, S18, S19, S20, S21 | 16,391 | 16,391 | 0 | 45,643 |

## 3. Kết quả

| | Số bài |
|---|---:|
| Thuộc thể theo **tài liệu** (chỉ H1–H3) | 59,437 |
| **Đạt theo chuẩn dự án** (cả 7 tầng) | **16,391** |
| Trượt | 45,643 |
| Không có nội dung | 5,116 |
| Tỉ lệ đạt trên bài có nội dung | 26.42% |

## 4. Vì sao trượt — theo từng cổng

Số bên cạnh mã luật là **số lần vi phạm**, không phải số bài: một bài có thể
phạm cùng một điều ở nhiều dòng.

**Cổng 1 — Hình thức**

- `2` H3: văn bản có phân dòng, từ 2 dòng trở lên

**Cổng 2 — Độ dài dòng**

- `9,015` H1: 7 tiếng

**Cổng 3 — Loại trừ Đường luật**

- `4,288` F3: không phải Đường luật

**Cổng 4 — Thanh luật**

- `177,405` S2: P2/P4/P6 luân phiên theo khuôn bằng (B T B) hoặc khuôn trắc (T B T)

**Cổng 5 — Vần**

- `4,983` S11: ít nhất 4 dòng liên tiếp khớp một sơ đồ §5.2 (aabb / abab / abba / aaxa)

## 5. Nhóm nguyên nhân trượt

| Nhóm | Số bài |
|---|---:|
| A. Thơ 8 chữ bị gán nhãn 7 chữ | 135 |
| B. Lẫn văn xuôi trong trường thơ | 22 |
| C. Có dòng phân cách không chứa tiếng | 34 |
| D. Đúng một dòng thiếu một tiếng | 1,060 |
| E. Đúng một dòng thừa một tiếng | 338 |
| F. Đúng một dòng lệch nhiều tiếng | 242 |
| G. Hai dòng lệch | 43,287 |
| H. Lệch nhiều dòng | 525 |

Bài rỗng có thể cứu được: **1,934**

## 6. Tệp kết quả

| Tệp | Nội dung |
|---|---|
| `bai_dat.jsonl` | Bài đạt, kèm dấu vết 7 tầng |
| `bai_truot.jsonl` | Bài trượt, kèm tầng dừng và vi phạm |
| `bai_truot_chi_tiet.jsonl` | Bản trích có bằng chứng từng dòng |
| `bai_khong_co_noi_dung.jsonl` | Bản ghi rỗng |
| `bai_rong_cuu_duoc.jsonl` | Bản ghi rỗng nhưng còn cứu được |
| `tong_hop.json` | Chính số liệu của tệp này, dạng máy đọc |

