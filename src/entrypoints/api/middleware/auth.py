"""G10 — xác thực bằng API key, và tenant LẤY TỪ KHOÁ.

════ LỖ HỔNG ĐANG VÁ ════

Trước 21/09/2026, `tenant_id` lấy thẳng từ THÂN REQUEST:

    tenant_id = req.tenant_id or ...

Nghĩa là bất kỳ ai cũng tự khai mình thuộc tenant nào. Cô lập tenant ở tầng dưới có
chặt tới đâu — khoá gộp, chữ ký bắt buộc, ADR-0003 — cũng vô nghĩa nếu danh tính do
chính người gọi tự nhận. Khoá cửa rất chắc nhưng ai gõ cũng mở.

════ NGUYÊN TẮC: DANH TÍNH ĐẾN TỪ THỨ NGƯỜI GỌI KHÔNG TỰ ĐẶT ĐƯỢC ════

    tenant_id  <- tra từ API key       (người gọi KHÔNG đặt được)
    user_id    <- tra từ API key
    req.tenant_id  -> BỎ QUA hoàn toàn (người gọi đặt được -> không tin)

Có test riêng ghim điều cuối: gửi `tenant_id` khác trong thân request thì vẫn bị ép
về tenant của khoá. Đó là chỗ dễ "nới cho tiện khi test" nhất.

════ G13 — VÒNG ĐỜI KHOÁ, ĐÃ VÁ 21/09/2026 ════

Bản trước giữ bảng khoá trong bộ nhớ tiến trình, nạp một lần lúc khởi động. **Thu
hồi một khoá đòi restart** — khi một khoá bị lộ, cửa vẫn mở tới lần deploy sau.

Nay middleware tra `ApiKeyStorePort` ở MỖI request, nên thu hồi có hiệu lực ngay.
Bảng tĩnh vẫn dùng được (chế độ dev, không cần DB) và hai đường cùng tồn tại: kho
được hỏi trước, bảng tĩnh là đường lùi.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from application.ports.api_key import ApiKeyStorePort
from domain.conversation.tenant import TENANT_MAC_DINH, TenantScope
from domain.policy.api_key import KhoaHopLe, bam_khoa, kiem_khoa

logger = logging.getLogger("api.auth")

# Đường KHÔNG cần xác thực. Danh sách ĐÓNG và tường minh — mặc định là "phải có
# khoá", nên thêm một đường công khai là một hành động có chủ ý, không phải tác dụng
# phụ của một mẫu khớp tiền tố nào đó.
DUONG_CONG_KHAI: frozenset[str] = frozenset(
    {"/healthz", "/readyz", "/metrics", "/docs", "/redoc", "/openapi.json"}
)

TEN_HEADER = "x-api-key"


class AuthMiddleware(BaseHTTPMiddleware):
    """Tra API key -> tenant. Không có khoá hợp lệ thì không đi tiếp.

    `khoa_tenant` rỗng nghĩa là TẮT xác thực — chế độ dev. Khi tắt, mọi request
    nhận `TenantScope.mac_dinh()`, và điều đó được ghi vào `request.state` để tầng
    trên biết mình đang chạy không xác thực chứ không tưởng là đã xác thực.
    """

    def __init__(
        self,
        app: object,
        khoa_tenant: dict[str, str] | None = None,
        kho_khoa: ApiKeyStorePort | None = None,
    ) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._khoa = dict(khoa_tenant or {})
        self._kho = kho_khoa

    async def _tra_tenant(self, khoa: str) -> str | None:
        """Kho trước, bảng tĩnh sau. Trả None khi khoá không dùng được.

        Kho được hỏi TRƯỚC vì nó là nơi duy nhất biết về thu hồi và hết hạn. Hỏi
        bảng tĩnh trước thì một khoá đã thu hồi nhưng còn trong cấu hình sẽ vẫn
        vào được — đúng lỗ hổng vừa vá.
        """
        if self._kho is not None:
            kq = kiem_khoa(await self._kho.tra(bam_khoa(khoa)), bay_gio=time.time())
            if isinstance(kq, KhoaHopLe):
                return kq.tenant_id
            if kq.ly_do != "khong_ton_tai":
                # Ghi LOG lý do, nhưng KHÔNG trả nó cho người gọi: nói "khoá đã hết
                # hạn" là xác nhận khoá ấy từng tồn tại.
                logger.warning("Khoá bị từ chối: %s", kq.ly_do)
                return None
        return self._khoa.get(khoa)

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        duong = request.url.path

        if not self._khoa and self._kho is None:
            # Dev: không cấu hình khoá nào và không có kho -> không xác thực.
            request.state.tenant_scope = TenantScope.mac_dinh()
            request.state.tenant_id = TENANT_MAC_DINH
            request.state.da_xac_thuc = False
            return await call_next(request)

        if duong in DUONG_CONG_KHAI:
            request.state.tenant_scope = TenantScope.mac_dinh()
            request.state.tenant_id = TENANT_MAC_DINH
            request.state.da_xac_thuc = False
            return await call_next(request)

        khoa = request.headers.get(TEN_HEADER, "")
        tenant = await self._tra_tenant(khoa) if khoa else None
        if not tenant:
            # Cùng một thông báo cho "thiếu khoá" và "khoá sai": phân biệt hai ca
            # đó là nói cho người dò khoá biết họ đã đi được nửa đường.
            return JSONResponse(
                status_code=401,
                content={"detail": f"Thiếu hoặc sai {TEN_HEADER}."},
            )

        request.state.tenant_scope = TenantScope(tenant_id=tenant)
        request.state.tenant_id = tenant
        request.state.da_xac_thuc = True
        return await call_next(request)


def tenant_scope_cua(request: Request) -> TenantScope:
    """Lấy `TenantScope` mà middleware đã đặt.

    KHÔNG nhận tham số dự phòng từ thân request — cả điểm của G10 là danh tính
    không đến từ chỗ người gọi kiểm soát được. Thiếu middleware thì rơi về tenant
    mặc định, và đó là lỗi cấu hình cần lộ ra, không phải thứ để lặng lẽ vá.
    """
    scope = getattr(request.state, "tenant_scope", None)
    return scope if isinstance(scope, TenantScope) else TenantScope.mac_dinh()
