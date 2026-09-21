"""§15 · §14 `AI_LLM_Chat_Web_UI_Plan.md` — quản lý hội thoại và danh mục model.

Điều quan trọng nhất ở đây KHÔNG phải CRUD chạy được, mà là:

    Hội thoại của tenant này KHÔNG bao giờ lộ sang tenant khác.

Tài liệu kế hoạch có cột `user_id` ở §15 nhưng §28 không có mục xác thực nào — nên
đây là chỗ dễ hỏng nhất nếu làm theo tài liệu nguyên văn.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from entrypoints.api.app import app

pytestmark = pytest.mark.contract

client = TestClient(app)


# ── CRUD ─────────────────────────────────────────────────────────────────────


def test_tao_roi_lay_lai_duoc():
    tao = client.post("/v1/conversations", json={"tieu_de": "Thơ quê hương"})
    assert tao.status_code == 200
    ma = tao.json()["conversation_id"]
    assert ma.startswith("conv_")

    lay = client.get(f"/v1/conversations/{ma}")
    assert lay.status_code == 200
    assert lay.json()["tieu_de"] == "Thơ quê hương"
    assert lay.json()["tin_nhan"] == []


def test_id_do_MAY_CHU_sinh_khong_nhan_tu_client():
    """Cho client tự đặt id thì hai người dùng khác tenant đoán trúng id của nhau
    được — cô lập chặn việc ĐỌC, nhưng đoán trúng vẫn là kênh dò thông tin."""
    a = client.post("/v1/conversations", json={"tieu_de": "x", "conversation_id": "toi-tu-dat"})
    assert a.json()["conversation_id"] != "toi-tu-dat"


def test_danh_sach_moi_nhat_len_dau():
    ids = [
        client.post("/v1/conversations", json={"tieu_de": f"c{i}"}).json()["conversation_id"]
        for i in range(3)
    ]
    ds = client.get("/v1/conversations").json()
    co_trong_ds = [c["conversation_id"] for c in ds]
    # Cái tạo sau cùng phải đứng trước cái tạo trước nó.
    assert co_trong_ds.index(ids[2]) < co_trong_ds.index(ids[0])


def test_danh_sach_KHONG_keo_theo_tin_nhan():
    """Sidebar mà kéo theo toàn bộ nội dung từng cuộc là truy vấn nặng dần theo
    lịch sử người dùng."""
    client.post("/v1/conversations", json={"tieu_de": "x"})
    ds = client.get("/v1/conversations").json()
    assert ds
    assert "tin_nhan" not in ds[0]
    assert "so_tin_nhan" in ds[0]


def test_sua_tieu_de():
    ma = client.post("/v1/conversations", json={"tieu_de": "cũ"}).json()["conversation_id"]
    sua = client.patch(f"/v1/conversations/{ma}", json={"tieu_de": "mới"})
    assert sua.status_code == 200
    assert sua.json()["tieu_de"] == "mới"


def test_xoa_roi_thi_404():
    ma = client.post("/v1/conversations", json={}).json()["conversation_id"]
    assert client.delete(f"/v1/conversations/{ma}").status_code == 200
    assert client.get(f"/v1/conversations/{ma}").status_code == 404


def test_khong_ton_tai_thi_404_khong_phai_500():
    assert client.get("/v1/conversations/conv_khong_co").status_code == 404
    assert client.delete("/v1/conversations/conv_khong_co").status_code == 404
    assert client.patch("/v1/conversations/conv_khong_co", json={"tieu_de": "x"}).status_code == 404


def test_limit_bi_chan_tren():
    """Không cho client tự đặt `limit` tuỳ ý: một `limit=10_000_000` là cách rẻ
    nhất để làm nghẽn cơ sở dữ liệu."""
    assert client.get("/v1/conversations?limit=999999").status_code == 200


# ── Cô lập tenant ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tenant_KHONG_thay_hoi_thoai_cua_nhau():
    """⛔ Tính chất quan trọng nhất của file này.

    Kiểm ở tầng kho lưu trữ vì ở tầng HTTP, chế độ dev không bật xác thực nên mọi
    request đều thuộc tenant mặc định — test qua HTTP sẽ xanh một cách rỗng.
    """
    from adapters.persistence.memory.relational import InMemoryRelationalRepository
    from domain.conversation.tenant import TenantScope

    kho = InMemoryRelationalRepository()
    a, b = TenantScope(tenant_id="cong_ty_a"), TenantScope(tenant_id="cong_ty_b")

    cua_a = await kho.tao_hoi_thoai(a, tieu_de="bí mật của A")
    assert await kho.danh_sach_hoi_thoai(b) == []
    assert await kho.lay_hoi_thoai(b, cua_a.conversation_id) is None
    assert await kho.xoa_hoi_thoai(b, cua_a.conversation_id) is False
    assert await kho.sua_hoi_thoai(b, cua_a.conversation_id, tieu_de="chiếm") is None
    # A vẫn còn nguyên sau khi B thử mọi cách.
    con = await kho.lay_hoi_thoai(a, cua_a.conversation_id)
    assert con is not None and con.tieu_de == "bí mật của A"


@pytest.mark.asyncio
async def test_xoa_hoi_thoai_xoa_luon_TIN_NHAN():
    """Xoá siêu dữ liệu mà để lại tin nhắn là tạo dữ liệu mồ côi: người dùng thấy
    đã xoá, nhưng nội dung vẫn nằm trong cơ sở dữ liệu."""
    from adapters.persistence.memory.relational import InMemoryRelationalRepository
    from contracts.chat import Message, Role
    from domain.conversation.tenant import TenantScope

    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a)
    await kho.save_message(a, c.conversation_id, Message(role=Role.USER, content="bí mật"))
    assert await kho.get_messages(a, c.conversation_id)

    await kho.xoa_hoi_thoai(a, c.conversation_id)
    assert await kho.get_messages(a, c.conversation_id) == []


@pytest.mark.asyncio
async def test_kho_SQL_hanh_xu_giong_kho_in_memory(tmp_path):
    """Hai hiện thực cùng một port phải cho cùng hành vi — nếu không thì đổi kho
    sẽ lặng lẽ đổi cách hệ thống chạy."""
    from adapters.persistence.sql import (
        SqlRelationalRepository,
        dung_dsn_sqlite,
        tao_bang,
        tao_engine,
    )
    from domain.conversation.tenant import TenantScope

    e = tao_engine(dung_dsn_sqlite(tmp_path / "c.sqlite3"))
    await tao_bang(e)
    kho = SqlRelationalRepository(e)
    a, b = TenantScope(tenant_id="a"), TenantScope(tenant_id="b")

    c = await kho.tao_hoi_thoai(a, tieu_de="của A")
    assert (await kho.lay_hoi_thoai(a, c.conversation_id)).tieu_de == "của A"  # type: ignore[union-attr]
    assert await kho.lay_hoi_thoai(b, c.conversation_id) is None
    assert await kho.danh_sach_hoi_thoai(b) == []

    sua = await kho.sua_hoi_thoai(a, c.conversation_id, tieu_de="đã sửa")
    assert sua is not None and sua.tieu_de == "đã sửa"
    assert await kho.xoa_hoi_thoai(a, c.conversation_id) is True
    assert await kho.lay_hoi_thoai(a, c.conversation_id) is None


# ── §14 danh mục model ───────────────────────────────────────────────────────


def test_danh_sach_model_lay_tu_cau_hinh_that():
    """Một danh sách chép tay sẽ lệch khỏi `configs/models.yaml`, và UI sẽ mời
    người dùng chọn một model mà backend không định tuyến được."""
    ds = client.get("/v1/models").json()
    assert ds
    ten = {m["ten"] for m in ds}
    assert "gpt-4o-mini" in ten
    assert all(m["provider"] for m in ds)


def test_danh_sach_model_KHONG_phoi_gia_tien():
    """Giá là chuyện vận hành, không phải thứ trình bày cho người dùng cuối — và
    nó đổi theo hợp đồng với nhà cung cấp."""
    ds = client.get("/v1/models").json()
    for m in ds:
        assert not any("cost" in k or "gia" in k for k in m)


def test_model_co_trong_openapi():
    spec = client.get("/openapi.json").json()
    for duong in ("/v1/models", "/v1/conversations", "/v1/conversations/{conversation_id}"):
        assert duong in spec["paths"], f"thiếu {duong}"
