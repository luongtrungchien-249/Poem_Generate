"""G10 — xác thực API key và tenant lấy từ khoá.

Tính chất phải chứng minh:

    Người gọi KHÔNG tự đặt được tenant của mình.

Mọi cô lập ở tầng dưới — khoá gộp, chữ ký bắt buộc, ADR-0003 — đều vô nghĩa nếu
danh tính do chính người gọi khai trong thân request.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from entrypoints.api.middleware.auth import (
    DUONG_CONG_KHAI,
    TEN_HEADER,
    AuthMiddleware,
    tenant_scope_cua,
)

pytestmark = pytest.mark.contract

KHOA = {"khoa-cua-A": "cong_ty_a", "khoa-cua-B": "cong_ty_b"}


def _app(khoa: dict[str, str] | None) -> TestClient:
    app = FastAPI()

    @app.post("/v1/thu")
    async def thu(request: Request) -> dict[str, str]:
        return {"tenant": tenant_scope_cua(request).tenant_id}

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    app.add_middleware(AuthMiddleware, khoa_tenant=khoa)
    return TestClient(app)


# ── Xác thực ─────────────────────────────────────────────────────────────────


def test_thieu_khoa_thi_401():
    assert _app(KHOA).post("/v1/thu", json={}).status_code == 401


def test_khoa_sai_thi_401():
    r = _app(KHOA).post("/v1/thu", json={}, headers={TEN_HEADER: "khoa-bia"})
    assert r.status_code == 401


def test_thong_bao_KHONG_phan_biet_thieu_khoa_voi_khoa_sai():
    """Phân biệt hai ca là nói cho người dò khoá biết họ đã đi được nửa đường."""
    c = _app(KHOA)
    a = c.post("/v1/thu", json={}).json()["detail"]
    b = c.post("/v1/thu", json={}, headers={TEN_HEADER: "sai"}).json()["detail"]
    assert a == b


def test_khoa_dung_thi_qua_va_nhan_dung_tenant():
    r = _app(KHOA).post("/v1/thu", json={}, headers={TEN_HEADER: "khoa-cua-A"})
    assert r.status_code == 200
    assert r.json()["tenant"] == "cong_ty_a"


def test_hai_khoa_cho_hai_tenant_khac_nhau():
    c = _app(KHOA)
    a = c.post("/v1/thu", json={}, headers={TEN_HEADER: "khoa-cua-A"}).json()["tenant"]
    b = c.post("/v1/thu", json={}, headers={TEN_HEADER: "khoa-cua-B"}).json()["tenant"]
    assert a == "cong_ty_a"
    assert b == "cong_ty_b"


# ── ⛔ Tính chất trung tâm ───────────────────────────────────────────────────


def test_than_request_KHONG_the_ghi_de_tenant_cua_khoa():
    """Chỗ dễ 'nới cho tiện khi test' nhất — và là chỗ làm hỏng toàn bộ G10.

    Người gọi cầm khoá của A nhưng khai `tenant_id` của B trong thân request.
    """
    r = _app(KHOA).post(
        "/v1/thu",
        json={"tenant_id": "cong_ty_b", "user_id": "quan_tri"},
        headers={TEN_HEADER: "khoa-cua-A"},
    )
    assert r.json()["tenant"] == "cong_ty_a", "thân request ghi đè được tenant của khoá"


def test_header_gia_mao_KHONG_duoc_tin():
    r = _app(KHOA).post(
        "/v1/thu",
        json={},
        headers={TEN_HEADER: "khoa-cua-A", "x-tenant-id": "cong_ty_b"},
    )
    assert r.json()["tenant"] == "cong_ty_a"


# ── Đường công khai ──────────────────────────────────────────────────────────


def test_duong_cong_khai_khong_can_khoa():
    assert _app(KHOA).get("/healthz").status_code == 200


def test_danh_sach_duong_cong_khai_la_DONG():
    """Mặc định phải là 'cần khoá'. Thêm một đường công khai là hành động có chủ ý,
    không phải tác dụng phụ của một phép khớp tiền tố."""
    assert "/v1/chat" not in DUONG_CONG_KHAI
    assert "/v1/poem" not in DUONG_CONG_KHAI
    assert "/v1/documents" not in DUONG_CONG_KHAI
    assert {
        "/healthz", "/readyz", "/metrics", "/docs", "/redoc", "/openapi.json"
    } >= DUONG_CONG_KHAI


# ── Chế độ dev ───────────────────────────────────────────────────────────────


def test_khong_cau_hinh_khoa_thi_TAT_xac_thuc():
    r = _app({}).post("/v1/thu", json={})
    assert r.status_code == 200
    assert r.json()["tenant"] == "default"


def test_che_do_dev_duoc_GHI_NHAN_chu_khong_giau():
    """Phải phân biệt được 'chưa bật xác thực' với 'đã bật và qua được'."""
    app = FastAPI()

    @app.get("/co_xac_thuc")
    async def co_xac_thuc(request: Request) -> dict[str, bool]:
        return {"da_xac_thuc": bool(getattr(request.state, "da_xac_thuc", False))}

    app.add_middleware(AuthMiddleware, khoa_tenant={})
    assert TestClient(app).get("/co_xac_thuc").json()["da_xac_thuc"] is False

    app2 = FastAPI()

    @app2.get("/co_xac_thuc")
    async def co_xac_thuc2(request: Request) -> dict[str, bool]:
        return {"da_xac_thuc": bool(getattr(request.state, "da_xac_thuc", False))}

    app2.add_middleware(AuthMiddleware, khoa_tenant=KHOA)
    r = TestClient(app2).get("/co_xac_thuc", headers={TEN_HEADER: "khoa-cua-A"})
    assert r.json()["da_xac_thuc"] is True


# ── Phân tích cấu hình khoá ──────────────────────────────────────────────────


def test_bang_khoa_bo_qua_muc_hong_nhung_KHONG_tao_khoa_rong():
    from bootstrap.settings import Secrets

    s = Secrets(API_KEYS="k1:t1, :t2, k3:, k4:t4, rac")
    bang = s.bang_khoa_tenant()
    assert bang == {"k1": "t1", "k4": "t4"}
    assert "" not in bang, "mục hỏng không được thành một khoá rỗng cho mọi người vào"
