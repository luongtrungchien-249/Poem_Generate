# Script phân tích corpus

Toàn bộ số liệu trong `docs/Report_analyst_17-09_pass-notpass.md` và
`datalake/analysis/TONG_HOP.md` đều do các script trong thư mục này sinh ra.
Trước đây chúng nằm ở thư mục tạm của phiên làm việc nên báo cáo không tái lập
được; nay chúng nằm trong repo.

Mọi script dùng **đường dẫn suy từ vị trí tệp**, không đặt cứng, nên chạy được từ
bất kỳ thư mục nào và trên máy khác:

```bash
python datalake/scripts/<tên>.py
```

## Hai script cần chạy trước

| Script | Việc | Đầu ra |
|---|---|---|
| `kiem_tra_toan_bo.py` | Kiểm **từng bài một** qua `rule.py`, có đối soát đầu vào — đầu ra. Dừng và báo lỗi nếu số liệu không khớp | `bai_dat.jsonl` · `bai_truot.jsonl` · `bai_khong_co_noi_dung.jsonl` · `tong_hop.json` |
| `doi_soat_ket_qua.py` | Kiểm chứng **độc lập** kết quả trên: phân hoạch id, lấy mẫu chạy lại, nhất quán nội tại | in ra màn hình, thoát mã 1 nếu sai |

```bash
python datalake/scripts/kiem_tra_toan_bo.py
python datalake/scripts/doi_soat_ket_qua.py 500
```

## Tám script phân tích

Chạy theo thứ tự nào cũng được; mỗi script độc lập, đọc thẳng tệp nguồn.
Báo cáo văn bản ghi vào `datalake/analysis/reports/`.

| Script | Trả lời câu hỏi gì | Mục báo cáo | Tệp ra |
|---|---|---|---|
| `phan_tich_corpus.py` | Corpus có gì: lược đồ bản ghi, khoá lạ, trùng lặp, tỷ lệ đạt, hình thức, vần, khuôn | §2 · §3 · §5 | `bao_cao.txt` |
| `soi_sau.py` | Soi các điểm nghi vấn: bài rỗng là kiểu gì, dòng 8 tiếng có thật là 8 không, điểm số có liên quan tới tuân thủ không | §4.2 · §5.2 | `bao_cao2.txt` |
| `phan_loai_loi.py` | Bài trượt vì lý do gì, và còn bao nhiêu dữ liệu sạch dùng được | §4.4 · §7 | `bao_cao3.txt` |
| `nguyen_nhan_dong.py` | Nguyên nhân ở **mức dòng**: độ dài, vị trí, dấu hiệu; kèm chân dung bài đạt | §3 · §4.1–4.3 | `bao_cao4.txt` |
| `do_lai.py` | Đo lại nguyên nhân dòng hỏng sau khi loại bỏ chỉ số "có chữ Latin" vô nghĩa | §1 · §4.1 | `bao_cao5.txt` |
| `ba_viec.py` | Ba việc: chi tiết bài trượt **kèm tên bài**, truy 5.116 bài rỗng, đo điểm mù H1 | §4.5 · §5.1.1 · §6 | `bao_cao6.txt` + 3 tệp JSONL |
| `do_diem_mu.py` | Đo điểm mù H1 bằng tín hiệu **cấu trúc** thay vì từ vựng | §6.2 | `bao_cao7.txt` |
| `chay_lai_toan_bo.py` | Chạy lại toàn bộ phép đo theo **đơn vị bài**, kèm thiệt hại kéo theo | §0 · §4.0 | `bao_cao_moi.txt` |

## Hai bài học đã đóng băng trong mã

**1. Tín hiệu từ vựng không phân biệt được thơ với siêu dữ liệu.**
`ba_viec.py` từng gắn cờ dòng bắt đầu bằng *gửi · tặng · nhớ · tiễn* là "đề tặng",
bắt nhầm 2.828 dòng mà phần lớn là thơ thật (`Gửi hương hoa cải, bướm lang thang.`).
Hàm `dau_hieu_khong_phai_tho()` nay chỉ dùng tín hiệu cấu trúc, và docstring của nó
ghi lại nguyên do để không ai vô tình khôi phục cách cũ.

**2. Tiếng Việt viết bằng chữ Latin.**
Một phép đo ban đầu dùng `[a-zA-Z]` để tìm "tên riêng nước ngoài" và khớp 99,19%
số dòng. `do_lai.py` là bản đo lại, dùng `f, j, w, z` — các chữ không thuộc bảng
chữ tiếng Việt.

## Lưu ý về `ba_viec.py`

Script này **ghi đè** ba tệp JSONL trong `datalake/analysis/`. Nếu bạn sửa tay các
tệp đó thì sao lưu trước khi chạy lại.

## Kích thước dữ liệu

`bai_dat.jsonl` khoảng 33 MB và tệp nguồn khoảng 60 MB. Cân nhắc đưa
`datalake/dataraw/` cùng các tệp `.jsonl` trong `datalake/analysis/` vào
`.gitignore`, chỉ giữ lại `TONG_HOP.md` và `tong_hop.json`.
