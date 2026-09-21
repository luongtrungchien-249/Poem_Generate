"""Tầng nghiệp vụ thơ — mọi thứ CỘNG THÊM quanh `rule.py`, không sửa `rule.py`.

Chỉ thị chủ dự án 21/09/2026: *"Rule của tôi phải là không được thay đổi."*

Vì vậy gói này chỉ ĐỌC `application.rule` và không bao giờ ghi vào nó. Quan hệ:

    rule.py              LUẬT THƠ — đóng băng, có test ghim SHA-256
    poetry/requirement   yêu cầu người dùng đã chuẩn hoá + cổng thông tin đầy đủ
    poetry/plan          kế hoạch sáng tác, phải khớp luật trước khi viết
    poetry/quality       chất lượng — chuẩn DỰ ÁN, tuyệt đối không đụng luật
    poetry/cot           khung suy luận có cấu trúc, bật khi chất lượng chưa đạt
    poetry/reasoning     kiểm SÁU BƯỚC suy luận của agent, dừng ở bước trượt đầu
    poetry/verifier      gộp luật + chất lượng thành một cổng chặn đầu ra

RANH GIỚI THẨM QUYỀN — đọc trước khi sửa gói này

    Luật loại bài. Chất lượng KHÔNG loại bài khỏi thể — nó chỉ chặn việc TRẢ RA.
    Trộn hai thứ là cách chắc chắn để một ngày nào đó một bài bị loại vì "thiếu
    hình ảnh" rồi được ghi lại như thể nó sai luật thơ.

    Vì vậy `KetQuaKiemDinh` của gói này mang hai cờ tách rời: `dat_luat` và
    `dat_chat_luong`. Không hàm nào được phép gộp chúng trước khi báo cáo.
"""
