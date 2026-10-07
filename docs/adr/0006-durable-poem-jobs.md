# ADR-0006 — Poem job bền vững, worker độc lập

Ngày: 06/10/2026. Trạng thái: đã triển khai; nghiệm thu live và production còn mở.

## Bối cảnh

Sinh thơ gồm nhiều lượt model, kiểm và sửa. HTTP/SSE dài không bảo đảm tác vụ sống sau khi đóng trang hoặc proxy timeout. Luật đóng băng và fail-closed vẫn là điều kiện bắt buộc.

## Quyết định

Dùng queue SQL qua port `PoemJobStore`; SQLite cho dev, PostgreSQL DSN chung cho nhiều tiến trình. API chỉ admission/auth/input/idempotency và trả 202. Worker chạy cùng composition root, nhận job bằng compare-and-set lease, cập nhật heartbeat và ghi cuối bằng điều kiện owner + lease + deadline.

`Idempotency-Key` unique trong từng tenant. Gate row khóa admission và giới hạn active job giữa các kết nối. Tenant lấy từ API key; các thao tác người dùng luôn cần `TenantScope`. Chỉ worker tin cậy được claim toàn queue.

SSE phát snapshot an toàn: planning/generating/verifying/repairing hoặc kết quả cuối. Không ghi/phát nháp trung gian. Mất SSE không hủy worker. Hủy/deadline làm mất quyền ghi; worker kiểm heartbeat và dừng task model. Một request provider đã gửi có thể vẫn bị tính tiền, kể cả khi client hủy.

Kết quả và tin nhắn hội thoại được commit cùng transaction SQL, tránh cửa sổ crash giữa hai bước. Owner cũ không thể commit sau khi job được worker khác claim. Worker chết có thể làm job chạy lại từ đầu sau lease: **at-least-once execution**, không bảo đảm exactly-once provider billing. Không hứa tiếp tục tại khổ đang dở vì không lưu nháp.

Trần gọi/job và quota ngày/tenant đi qua LLM wrapper; tools của job chỉ cho kiểm luật/chất lượng, chặn sinh đệ quy và I/O ngoài để không vượt meter. Đây là trần lượt gọi logic, không phải trần token hoặc trần HTTP retry của provider.

## Tương thích và đánh đổi

`POST /v1/poem` cũ giữ nguyên; frontend thơ chuyển sang jobs. Worker nhúng chỉ dành cho dev. Production phải dùng SQL chung, migration và worker riêng. Job/model/config cần đồng bộ khi deploy; không đổi feature flag trong lúc còn job đang chạy.

SQL polling đơn giản, chưa có queue priority hoặc resume checkpoint. TTL xóa job terminal sau mặc định 24 giờ; lịch sử hội thoại không bị TTL xóa. SQLite phù hợp quy mô nhỏ; nhiều worker nên dùng PostgreSQL. Chưa có nghiệm thu PostgreSQL/load/browser trong lần triển khai này.

## Kiểm chứng

Test admission đồng thời, idempotency, tenant isolation, claim cạnh tranh, fencing, cancel, deadline, shutdown/heartbeat lỗi, quota đồng thời, history transaction và Alembic schema parity. Hash `rule.py` giữ nguyên. Xem [plan và trạng thái](../Plan_Improve_06_10.md) và [runbook](../Runbook_Improve_06_10.md).
