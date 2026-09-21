"""`TenantScope` — danh tính người thuê, đi theo MỌI thao tác chạm dữ liệu.

════ VÌ SAO LÀ MỘT KIỂU RIÊNG, KHÔNG PHẢI MỘT CHUỖI ════

ADR-0003 đặt ra ràng buộc: *"mọi phương thức port chạm dữ liệu phải nhận
`TenantScope` ở tham số đầu tiên, để việc cô lập tenant được bảo đảm bằng chữ ký
hàm chứ không bằng review."*

Lý do có thật, và đã trả giá. Bản trước truyền tenant qua một `dict` filter:

    filters={"tenant_id": tenant_id}

và lọc nó trên `chunk.metadata` — trong khi `tenant_id` là **field của `Chunk`**,
không nằm trong `metadata`. Kết quả: mọi chunk bị loại, **RAG luôn trả về rỗng**.

Kiểu hỏng ấy im lặng theo cả hai chiều:
  - gõ sai khoá -> lọc hụt -> RÒ dữ liệu sang tenant khác
  - gõ sai chỗ  -> lọc trượt -> MẤT hết kết quả, trông như "không có tài liệu"

Một `dict` không có cách nào chặn cả hai. Một tham số bắt buộc, đúng kiểu, thì có:
quên nó là không chạy nổi, và không có khoá nào để gõ sai.
"""

from __future__ import annotations

from dataclasses import dataclass

TENANT_MAC_DINH = "default"


@dataclass(frozen=True, slots=True)
class TenantScope:
    """Người thuê đang thực hiện thao tác.

    KHÔNG có giá trị mặc định trong constructor. Đó là chủ ý: `TenantScope()` gọi
    được nghĩa là có thể vô tình chạm dữ liệu dưới danh nghĩa "default" mà không ai
    chọn điều đó. Muốn tenant mặc định thì phải gọi `TenantScope.mac_dinh()` — nói
    ra bằng lời.
    """

    tenant_id: str

    def __post_init__(self) -> None:
        if not self.tenant_id or not self.tenant_id.strip():
            raise ValueError("tenant_id rỗng — không có tenant thì không có quyền đọc gì")

    @classmethod
    def mac_dinh(cls) -> TenantScope:
        """Tenant mặc định cho dev và test. Gọi tường minh, không tự rơi vào."""
        return cls(tenant_id=TENANT_MAC_DINH)

    def khop(self, tenant_id: str | None) -> bool:
        """Một bản ghi có thuộc tenant này không."""
        return tenant_id == self.tenant_id
