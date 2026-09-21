"""Lược đồ bảng — SQLAlchemy Core, KHÔNG dùng ORM.

VÌ SAO CORE CHỨ KHÔNG PHẢI ORM. Repo này đã có kiểu miền riêng (`Message`,
`Document`, `FeedbackRecord` — Pydantic). Thêm một tầng entity ORM nữa là **hai bộ
kiểu cho cùng một khái niệm**, và một bộ ánh xạ ở giữa để chúng khỏi lệch nhau.

Core cho câu SQL tường minh, đọc là biết chạy gì, và không có lazy-loading âm thầm
sinh ra truy vấn N+1 ở một chỗ xa nơi viết.

════ CÔ LẬP TENANT NẰM TRONG KHOÁ CHÍNH ════

`tenant_id` là cột ĐẦU của mọi khoá chính. Không phải cột phụ để lọc sau — lọc sau
thì quên một truy vấn là rò, còn nằm trong khoá thì hai tenant không thể đụng nhau
kể cả khi trùng `session_id`, mà `session_id` do client tự đặt nên rất hay trùng.

════ HAI DIALECT, MỘT LƯỢC ĐỒ ════

Chỉ dùng kiểu có mặt ở cả SQLite lẫn PostgreSQL: `String`, `Integer`, `Float`,
`Text`. Không `JSONB`, không `ARRAY`, không `SERIAL` — mỗi kiểu riêng của một bên
là một nhánh mã phải kiểm chứng riêng, và nhánh Postgres thì CI không chạy được.

Nội dung phức tạp lưu dưới dạng JSON trong cột `Text`: Pydantic đã lo tuần tự hoá,
và cách này đúng như nhau ở hai dialect.
"""

from __future__ import annotations

from sqlalchemy import Column, Float, Integer, MetaData, String, Table, Text

metadata = MetaData()

tin_nhan = Table(
    "tin_nhan",
    metadata,
    Column("tenant_id", String(128), primary_key=True),
    Column("session_id", String(256), primary_key=True),
    Column("thu_tu", Integer, primary_key=True),
    Column("noi_dung", Text, nullable=False),
)

tai_lieu = Table(
    "tai_lieu",
    metadata,
    Column("tenant_id", String(128), primary_key=True),
    Column("doc_id", String(256), primary_key=True),
    Column("noi_dung", Text, nullable=False),
)

phan_hoi = Table(
    "phan_hoi",
    metadata,
    Column("tenant_id", String(128), primary_key=True),
    Column("thu_tu", Integer, primary_key=True),
    Column("noi_dung", Text, nullable=False),
)

bo_nho_dem = Table(
    "bo_nho_dem",
    metadata,
    Column("khoa", String(512), primary_key=True),
    Column("gia_tri", Text, nullable=False),
    # Mốc hết hạn TUYỆT ĐỐI, không phải thời gian còn lại: mốc thì so một lần là
    # xong và vẫn đúng sau khi tiến trình khởi động lại.
    Column("het_han", Float, nullable=False),
)

# G12.2 — bộ đếm rate-limit DÙNG CHUNG giữa các tiến trình.
#
# Đây là phần đóng đúng khoảng trống còn lại của Bước 5: kho quan hệ đã bền vững,
# nhưng bộ đếm vẫn nằm trong RAM từng tiến trình, nên chạy N worker thì hạn mức
# thực tế bị nhân lên N lần. Đó là lỗ kiểm soát CHI PHÍ, không phải lỗ tiện nghi.
dau_vet_goi = Table(
    "dau_vet_goi",
    metadata,
    Column("khoa", String(512), primary_key=True),
    Column("moc", Float, primary_key=True),
)

ngan_sach_ngay = Table(
    "ngan_sach_ngay",
    metadata,
    Column("khoa", String(512), primary_key=True),
    Column("ngay", String(16), primary_key=True),
    Column("so_lan", Integer, nullable=False),
)

# Kho VECTOR. `noi_dung` giữ nguyên `EnrichedChunk` dạng JSON, kể cả embedding.
#
# Vì sao không tách embedding ra cột riêng: ở SQL thường, vector chỉ dùng để TÍNH
# chứ không dùng để LỌC hay SẮP XẾP bằng SQL — nên tách ra không giúp gì, mà lại
# thêm một chỗ có thể lệch với phần còn lại của chunk.
#
# Khi chuyển sang pgvector thì cột `vector(N)` sẽ thay chỗ này, và lúc đó tách là
# bắt buộc vì chỉ mục ANN cần một cột kiểu vector thật.
doan_van = Table(
    "doan_van",
    metadata,
    Column("tenant_id", String(128), primary_key=True),
    Column("chunk_id", String(256), primary_key=True),
    Column("doc_id", String(256), nullable=False),
    Column("noi_dung", Text, nullable=False),
)

# G13 — khoá API. `bam` là KHOÁ CHÍNH; khoá nguyên văn KHÔNG bao giờ được lưu.
khoa_api = Table(
    "khoa_api",
    metadata,
    Column("bam", String(64), primary_key=True),
    Column("tenant_id", String(128), nullable=False),
    Column("ten", String(256), nullable=False, default=""),
    Column("tao_luc", Float, nullable=False),
    # None = không hết hạn. Lưu 0.0 cho "không hết hạn" sẽ lẫn với "hết hạn từ 1970".
    Column("het_han_luc", Float, nullable=True),
    Column("thu_hoi_luc", Float, nullable=True),
)
