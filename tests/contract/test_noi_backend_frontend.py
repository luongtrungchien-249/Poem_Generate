"""Những gì phải đúng để frontend và backend thật sự nối được nhau.

Ba hành vi dưới đây đều hỏng theo kiểu KHÔNG ai thấy ngay: người dùng vẫn nhận
được câu trả lời, chỉ là mở lại hội thoại thì nó không còn ở đó, hoặc sidebar sắp
xếp sai, hoặc trần ngân sách tồn tại trên giấy mà không chặn được gì.
"""

from __future__ import annotations

import asyncio

import pytest

from adapters.persistence.memory.relational import InMemoryRelationalRepository
from application.conversation import luu_luot, tieu_de_tu_cau
from contracts.chat import Message, Role
from domain.conversation.tenant import TenantScope

pytestmark = pytest.mark.contract


# ── Lưu lượt hội thoại ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_luu_luot_ghi_ca_cau_hoi_lan_cau_tra_loi():
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a)

    await luu_luot(kho, a, c.conversation_id, cau_hoi="thơ về thu", tra_loi="bài thơ")

    tn = await kho.get_messages(a, c.conversation_id)
    assert [(m.role, m.content) for m in tn] == [
        (Role.USER, "thơ về thu"),
        (Role.ASSISTANT, "bài thơ"),
    ]


@pytest.mark.asyncio
async def test_tra_loi_rong_VAN_ghi_cau_hoi():
    """Bài trượt luật thì không có gì để lưu, nhưng câu hỏi thì có.

    Bỏ luôn cả lượt sẽ để lại một khoảng trống khó hiểu: người dùng nhớ mình đã
    hỏi, mở lại hội thoại thì không thấy gì.
    """
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a)

    await luu_luot(kho, a, c.conversation_id, cau_hoi="thơ 7 dòng", tra_loi="")

    tn = await kho.get_messages(a, c.conversation_id)
    assert len(tn) == 1
    assert tn[0].role == Role.USER


@pytest.mark.asyncio
async def test_khong_co_conversation_id_thi_khong_ghi_gi():
    """Đường chat không bắt buộc gắn với một hội thoại."""
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    await luu_luot(kho, a, None, cau_hoi="x", tra_loi="y")
    assert await kho.danh_sach_hoi_thoai(a) == []


# ── Tiêu đề ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tieu_de_dat_tu_cau_dau_tien():
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a)
    assert c.tieu_de == ""

    await luu_luot(kho, a, c.conversation_id, cau_hoi="Thơ về mùa thu Hà Nội", tra_loi="x")

    sau = await kho.lay_hoi_thoai(a, c.conversation_id)
    assert sau is not None
    assert sau.tieu_de == "Thơ về mùa thu Hà Nội"


@pytest.mark.asyncio
async def test_tieu_de_nguoi_dung_dat_KHONG_bi_ghi_de():
    """Người dùng tự đặt tên rồi thì câu đầu tiên không được cướp chỗ."""
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a, tieu_de="Tên tôi tự đặt")

    await luu_luot(kho, a, c.conversation_id, cau_hoi="một câu hỏi khác", tra_loi="x")

    sau = await kho.lay_hoi_thoai(a, c.conversation_id)
    assert sau is not None and sau.tieu_de == "Tên tôi tự đặt"


@pytest.mark.asyncio
async def test_lượt_thu_hai_khong_doi_tieu_de():
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    c = await kho.tao_hoi_thoai(a)

    await luu_luot(kho, a, c.conversation_id, cau_hoi="câu đầu", tra_loi="x")
    await luu_luot(kho, a, c.conversation_id, cau_hoi="câu sau", tra_loi="y")

    sau = await kho.lay_hoi_thoai(a, c.conversation_id)
    assert sau is not None and sau.tieu_de == "câu đầu"


def test_tieu_de_cat_theo_TU_khong_cat_giua_tu():
    """Cắt giữa một từ tiếng Việt có thể làm mất dấu và tạo ra từ khác hẳn."""
    dai = "Viết cho tôi một bài thơ thất ngôn tự do nói về những buổi chiều mùa thu ở quê"
    t = tieu_de_tu_cau(dai)
    assert len(t) <= 61  # 60 + dấu …
    assert t.endswith("…")
    # Phần trước dấu … phải kết thúc đúng ở một ranh giới từ.
    assert dai.startswith(t[:-1])
    assert dai[len(t) - 1] == " "


def test_tieu_de_gom_khoang_trang_thua():
    assert tieu_de_tu_cau("  thơ   về    thu  ") == "thơ về thu"


# ── Làm mới `cap_nhat_luc` ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_gui_tin_nhan_day_hoi_thoai_len_dau_sidebar():
    """Sidebar sắp xếp theo `cap_nhat_luc`. Không làm mới nó thì "Gần đây" thực
    chất là thứ tự TẠO, và cuộc vừa nhắn xong vẫn nằm đáy danh sách."""
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    cu = await kho.tao_hoi_thoai(a, tieu_de="cũ")
    # Ngủ một nhịp để hai hội thoại có `cap_nhat_luc` KHÁC nhau. Không có nó thì
    # cả hai tạo trong cùng một tick và thứ tự do khoá phụ quyết định, nên phép
    # kiểm dưới đây không còn nói lên điều gì về việc làm mới.
    await asyncio.sleep(0.01)
    await kho.tao_hoi_thoai(a, tieu_de="mới")

    # Trước khi nhắn: "mới" đứng đầu vì tạo sau.
    assert (await kho.danh_sach_hoi_thoai(a))[0].tieu_de == "mới"

    await asyncio.sleep(0.01)

    await kho.save_message(a, cu.conversation_id, Message(role=Role.USER, content="hi"))

    # Sau khi nhắn vào "cũ": nó phải lên đầu.
    assert (await kho.danh_sach_hoi_thoai(a))[0].tieu_de == "cũ"


@pytest.mark.asyncio
async def test_session_id_khong_phai_hoi_thoai_thi_khong_sao():
    """Đường chat gửi `session_id` tuỳ ý — không được ném lỗi vì thiếu hội thoại."""
    kho = InMemoryRelationalRepository()
    a = TenantScope(tenant_id="t")
    await kho.save_message(a, "mot-session-bat-ky", Message(role=Role.USER, content="hi"))
    assert len(await kho.get_messages(a, "mot-session-bat-ky")) == 1


@pytest.mark.asyncio
async def test_kho_SQL_hanh_xu_giong_kho_in_memory(tmp_path):
    from adapters.persistence.sql import (
        SqlRelationalRepository,
        dung_dsn_sqlite,
        tao_bang,
        tao_engine,
    )

    e = tao_engine(dung_dsn_sqlite(tmp_path / "n.sqlite3"))
    await tao_bang(e)
    kho = SqlRelationalRepository(e)
    a = TenantScope(tenant_id="t")

    cu = await kho.tao_hoi_thoai(a, tieu_de="")
    await kho.tao_hoi_thoai(a, tieu_de="mới")

    await luu_luot(kho, a, cu.conversation_id, cau_hoi="câu đầu tiên", tra_loi="đáp")

    sau = await kho.lay_hoi_thoai(a, cu.conversation_id)
    assert sau is not None
    assert sau.tieu_de == "câu đầu tiên"
    assert sau.so_tin_nhan == 2
    # Đã được đẩy lên đầu danh sách.
    assert (await kho.danh_sach_hoi_thoai(a))[0].conversation_id == cu.conversation_id

    # Tiêu đề đã có thì không bị ghi đè.
    await luu_luot(kho, a, cu.conversation_id, cau_hoi="câu thứ hai", tra_loi="đáp")
    lai = await kho.lay_hoi_thoai(a, cu.conversation_id)
    assert lai is not None and lai.tieu_de == "câu đầu tiên"


@pytest.mark.asyncio
async def test_dat_tieu_de_khong_vuot_sang_tenant_khac(tmp_path):
    from adapters.persistence.sql import (
        SqlRelationalRepository,
        dung_dsn_sqlite,
        tao_bang,
        tao_engine,
    )

    e = tao_engine(dung_dsn_sqlite(tmp_path / "m.sqlite3"))
    await tao_bang(e)
    kho = SqlRelationalRepository(e)
    a, b = TenantScope(tenant_id="a"), TenantScope(tenant_id="b")

    c = await kho.tao_hoi_thoai(a)
    await kho.dat_tieu_de_neu_trong(b, c.conversation_id, "B chiếm chỗ")

    con = await kho.lay_hoi_thoai(a, c.conversation_id)
    assert con is not None and con.tieu_de == ""


# ── Trần ngân sách ngày ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tran_ngan_sach_khoa_theo_TENANT_khong_theo_request():
    """⛔ Lỗi đã vá 21/09/2026.

    Đường thơ truyền `thread_id = session_id or trace_id`, và `trace_id` là DUY
    NHẤT cho mỗi request. Mỗi yêu cầu không kèm `session_id` vì thế tự mở một
    ngăn ngân sách riêng, đếm lên 1, rồi không bao giờ chạm trần — trần tồn tại
    trên giấy nhưng không chặn được gì.

    Test này ghim rằng nhiều request khác `trace_id` của CÙNG một tenant dùng
    chung một ngăn.
    """
    from adapters.rate_limit import InMemoryRateLimiter
    from entrypoints.api.ngan_sach import pham_vi_ngan_sach

    gioi_han = InMemoryRateLimiter(so_lan_goi_model_moi_ngay=3)
    pv = pham_vi_ngan_sach("cong_ty_a")

    assert await gioi_han.within_daily_budget(pv) is True
    assert await gioi_han.within_daily_budget(pv) is True
    assert await gioi_han.within_daily_budget(pv) is True
    # Lượt thứ tư của CÙNG tenant phải bị chặn.
    assert await gioi_han.within_daily_budget(pv) is False

    # Tenant khác vẫn còn nguyên hạn mức của mình.
    assert await gioi_han.within_daily_budget(pham_vi_ngan_sach("cong_ty_b")) is True


@pytest.mark.asyncio
async def test_ngan_sach_het_thi_429_khong_phai_500():
    """429 chứ không phải 402: hạn mức theo NGÀY, mai là hết hạn chế."""
    from fastapi import HTTPException

    from adapters.rate_limit import InMemoryRateLimiter
    from entrypoints.api.ngan_sach import chan_neu_het_ngan_sach

    gioi_han = InMemoryRateLimiter(so_lan_goi_model_moi_ngay=1)
    await chan_neu_het_ngan_sach(gioi_han, "t")  # lượt đầu: qua

    with pytest.raises(HTTPException) as e:
        await chan_neu_het_ngan_sach(gioi_han, "t")
    assert e.value.status_code == 429


def test_ngan_ngan_sach_tach_khoi_ngan_theo_thread():
    """Một hội thoại tình cờ mang id trùng tên tenant không được ăn chung ngăn."""
    from domain.conversation.thread import ThreadScope
    from entrypoints.api.ngan_sach import pham_vi_ngan_sach

    ngan_sach = pham_vi_ngan_sach("abc")
    theo_thread = ThreadScope(platform="web", thread_id="abc")
    assert ngan_sach.make_key() != theo_thread.make_key()


# ── CORS ─────────────────────────────────────────────────────────────────────


def test_CORS_khong_echo_origin_la():
    """⛔ Lỗi đã vá 21/09/2026.

    Bản trước đặt `allow_origins=["*"]` KÈM `allow_credentials=True`. Starlette
    xử lý cặp đó bằng cách echo lại mọi Origin, nên bất kỳ website nào cũng gọi
    được API này kèm credential.
    """
    from fastapi.testclient import TestClient

    from entrypoints.api.app import app

    r = TestClient(app).get("/healthz", headers={"Origin": "https://ke-tan-cong.example"})
    assert "access-control-allow-origin" not in {k.lower() for k in r.headers}


def test_CORS_tu_choi_dau_sao():
    """`"*"` phải bị từ chối TƯỜNG MINH, không âm thầm nhận rồi mở toang."""
    from bootstrap.settings import _danh_sach

    with pytest.raises(ValueError, match=r"\*"):
        _danh_sach("https://a.example,*", [])


def test_CORS_doc_duoc_danh_sach_cu_the():
    from bootstrap.settings import _danh_sach

    assert _danh_sach("https://a.example, https://b.example", []) == [
        "https://a.example",
        "https://b.example",
    ]
    assert _danh_sach(None, ["https://c.example"]) == ["https://c.example"]
    assert _danh_sach(None, []) == []


# ── Hợp đồng luồng SSE ───────────────────────────────────────────────────────


def _doc_su_kien(than: str) -> list[dict]:
    import json as _json

    ra = []
    for dong in than.splitlines():
        d = dong.strip()
        if not d.startswith("data:"):
            continue
        tai = d[5:].strip()
        ra.append({"__done__": True} if tai == "[DONE]" else _json.loads(tai))
    return ra


def test_DONE_la_dau_ket_thuc_DUY_NHAT_cua_luong():
    """⛔ `finish_reason` KHÔNG phải dấu chấm hết. Client dừng ở nó sẽ mất chữ.

    Rào chắn đầu ra giữ chữ trong một cửa sổ đệm rồi mới xả ở bước kết thúc, nên
    sự kiện mang `finish_reason` có thể tới TRƯỚC sự kiện mang nội dung:

        {"delta": "", "finish_reason": "stop"}
        {"delta": "…nội dung…", "finish_reason": null}
        [DONE]

    Test này ghim hai điều: `[DONE]` luôn là sự kiện cuối, và nội dung có thể
    nằm SAU một `finish_reason`.
    """
    from fastapi.testclient import TestClient

    from entrypoints.api.app import app

    with TestClient(app) as client:
        r = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "xin chào"}], "stream": True},
        )
    assert r.status_code == 200
    sk = _doc_su_kien(r.text)

    assert sk, "luồng không phát sự kiện nào"
    assert sk[-1] == {"__done__": True}, "sự kiện cuối phải là [DONE]"
    # Không sự kiện nào khác được mang cờ kết thúc của luồng.
    assert sum(1 for s in sk if s.get("__done__")) == 1

    toan_van = "".join(str(s.get("delta", "")) for s in sk if not s.get("__done__"))
    assert toan_van, "luồng không mang chữ nào — client sẽ hiện ô trống"


def test_moi_su_kien_deu_mang_trace_id():
    """§24 — "Error ID" mà UI hiện chính là `trace_id` này."""
    from fastapi.testclient import TestClient

    from entrypoints.api.app import app

    with TestClient(app) as client:
        r = client.post(
            "/v1/chat",
            json={"messages": [{"role": "user", "content": "xin chào"}], "stream": True},
        )
    sk = [s for s in _doc_su_kien(r.text) if not s.get("__done__")]
    assert sk and all(s.get("trace_id") for s in sk)


def test_ca_HAI_duong_chat_va_tho_deu_dat_tieu_de():
    """Hai đường cùng làm một việc thì phải làm giống nhau.

    Trước 21/09/2026 `/v1/chat` ghi tin nhắn TRỰC TIẾP qua `session_memory`, bỏ
    qua phần đặt tiêu đề — nên hội thoại tạo từ chat không bao giờ có tên, trong
    khi hội thoại tạo từ thơ thì có. Người dùng thấy sidebar toàn "Cuộc trò
    chuyện mới" mà không hiểu vì sao có cái có tên, có cái không.
    """
    from fastapi.testclient import TestClient

    from entrypoints.api.app import app

    with TestClient(app) as client:
        ma = client.post("/v1/conversations", json={}).json()["conversation_id"]
        r = client.post(
            "/v1/chat",
            json={
                "messages": [{"role": "user", "content": "Thủ đô Việt Nam là gì?"}],
                "stream": False,
                "session_id": ma,
            },
        )
        assert r.status_code == 200
        chi_tiet = client.get(f"/v1/conversations/{ma}").json()

    assert chi_tiet["tieu_de"] == "Thủ đô Việt Nam là gì?"
    assert chi_tiet["so_tin_nhan"] == 2
