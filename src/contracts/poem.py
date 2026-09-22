"""Hợp đồng HTTP của đường sinh thơ.

NGUYÊN TẮC CỦA HỢP ĐỒNG NÀY: mọi bài thơ trả ra đều phải đi kèm BẰNG CHỨNG bảy
tầng. §3.4 và §19.2 của tài liệu đích đòi evidence; ở đây evidence không phải thứ
thêm vào cho đẹp mà là một phần bắt buộc của response.

Hệ quả: người dùng không phải tin lời hệ thống. Họ đọc được từng tầng đã kiểm gì,
bằng chứng ra sao, và tầng nào chưa chạy.
"""

from typing import Any

from pydantic import BaseModel, Field


class PoemRequest(BaseModel):
    """Yêu cầu sinh thơ.

    `so_dong` phải là bội của 4 (H4, luật cứng). Không thoả thì API KHÔNG tự làm
    tròn — nó hỏi lại, vì làm tròn im lặng là quyết định thay người dùng.
    """

    yeu_cau: str = Field(..., description="Yêu cầu bằng lời của người dùng", min_length=1)
    chu_de: str | None = Field(None, description="Chủ đề; thiếu thì API sẽ hỏi lại")
    so_dong: int | None = Field(None, description="Số dòng mong muốn, phải là bội của 4")
    cam_xuc: str | None = None
    phong_cach: str | None = None
    rang_buoc_van: str | None = None
    rang_buoc_thanh: str | None = None
    max_repair_rounds: int = Field(3, ge=0, le=10)
    session_id: str | None = None


class BangChungTang(BaseModel):
    """Một tầng trong dấu vết kiểm định.

    `da_chay=False` nghĩa là tầng CHƯA ĐƯỢC KIỂM vì một tầng trước đã chặn — KHÔNG
    phải "đã kiểm và đạt". Đọc nhầm hai thứ này là hiểu ngược cả biên bản.
    """

    tang: int
    ten: str
    ma_luat: list[str]
    muc: str
    da_chay: bool
    dat: bool
    trich_luat: str
    bang_chung: str
    chi_tiet: dict[str, Any] = Field(default_factory=dict)


class BangChungChieu(BaseModel):
    """Một chiều chất lượng. `do_duoc=False` -> `dat` không mang ý nghĩa gì."""

    ma: str
    ten: str
    do_duoc: bool
    dat: bool
    so_do: float | None
    nguong: str
    bang_chung: str


class PoemResponse(BaseModel):
    """Bài thơ đã qua cổng.

    HAI CỜ, CỐ Ý KHÔNG GỘP:
        `thuoc_the`  chỉ H1–H4 — câu trả lời của TÀI LIỆU LUẬT
        `dat_luat`   qua cả bảy tầng — câu trả lời của DỰ ÁN
    Cộng thêm `dat_chat_luong` là chuẩn chất lượng, KHÔNG phải luật thơ.
    """

    poem: str
    # QĐ-TD-1. Chuỗi rỗng là giá trị HỢP LỆ: tiêu đề đặt bằng một lượt gọi phụ SAU
    # cổng kiểm, và lượt đó hỏng thì bài vẫn trả ra bình thường, chỉ không có tên.
    # Client phải chịu được rỗng — đừng dựng giao diện giả định luôn có tiêu đề.
    tieu_de: str = ""
    dat: bool
    thuoc_the: bool
    dat_luat: bool
    dat_chat_luong: bool
    so_dong: int
    so_kho: int
    so_luot_sua: int
    chien_luoc_cuoi: str | None = None
    bang_chung_bay_tang: list[BangChungTang]
    chat_luong: list[BangChungChieu]
    so_do_van: list[str] = Field(default_factory=list)
    ghi_chu: list[str] = Field(default_factory=list)
    # §22 — máy tự trả lời, hay bài này cần người xem?
    quyet_dinh_hitl: str = "AUTO_RESPOND"
    ly_do_hitl: str = ""
    # §23 — reviewer cần thấy đường đi và nguồn ví dụ, không chỉ thấy bài thơ.
    duong_di: list[str] = Field(default_factory=list)
    che_do_vi_du: str = "zero_shot"
    id_vi_du: list[str] = Field(default_factory=list)
    trace_id: str


class CanLamRo(BaseModel):
    """Chưa đủ thông tin để sinh thơ — thi hành chỉ thị 5.

    Đây KHÔNG phải lỗi. Nó là một bước hợp lệ của hội thoại: hệ thống hỏi lại thay
    vì đoán. Vì vậy nó trả HTTP 200, không phải 4xx.
    """

    can_lam_ro: bool = True
    ca: int
    cau_hoi: str
    ly_do: str
    truong_thieu: list[str] = Field(default_factory=list)
    duong_di: list[str] = Field(default_factory=list)
    trace_id: str


class PoemKhongDat(BaseModel):
    """Hết lượt sửa mà bài vẫn chưa đạt — fail closed.

    KHÔNG có trường nào chứa văn bản thơ. Đó là chủ ý: hết lượt thì không trả bài
    sai, kể cả khi bản nháp cuối trông có vẻ ổn.
    """

    ma_the: str
    so_luot_da_sua: int
    chan_doan: str
    trace_id: str
