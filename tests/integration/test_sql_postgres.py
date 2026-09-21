"""Cùng một bộ kiểm, chạy trên MỌI dialect được hỗ trợ.

════ VÌ SAO GỘP CHUNG THAY VÌ VIẾT RIÊNG CHO POSTGRES ════

Một bộ test riêng cho Postgres sẽ lệch khỏi bộ test SQLite trong vài tháng: sửa một
bên rồi quên bên kia là chuyện sẽ xảy ra, không phải có thể xảy ra. Và bên bị quên
luôn là Postgres, vì nó không chạy trong CI.

Nên ở đây chỉ có MỘT bộ kiểm, `parametrize` theo dialect:

    sqlite+aiosqlite   luôn chạy
    postgresql+asyncpg chạy khi có DATABASE_URL, tự SKIP khi không

Nhờ vậy adapter Postgres được kiểm bằng đúng những khẳng định đã kiểm SQLite, và
khoảng chưa kiểm thu lại chỉ còn phương ngữ SQL — thứ SQLAlchemy lo.

════ CHẠY VỚI POSTGRES THẬT ════

    docker compose -f infra/docker/docker-compose.yml up -d
    DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db pytest tests/integration

⚠️ Test này XOÁ SẠCH các bảng của ứng dụng trong DB được trỏ tới. Đừng trỏ vào một
cơ sở dữ liệu có dữ liệu thật.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from adapters.persistence.sql import (
    SqlApiKeyStore,
    SqlRateLimiter,
    SqlRelationalRepository,
    SqlVectorRepository,
    dung_dsn_sqlite,
    tao_bang,
    tao_engine,
)
from adapters.persistence.sql.bang import metadata
from contracts.chat import Message, Role
from contracts.chunk import EnrichedChunk
from domain.conversation.tenant import TenantScope
from domain.conversation.thread import ThreadScope
from domain.policy.api_key import KhoaHopLe, KhoaKhongHopLe, bam_khoa, kiem_khoa

pytestmark = pytest.mark.integration

A = TenantScope(tenant_id="cong_ty_a")
B = TenantScope(tenant_id="cong_ty_b")

DSN_POSTGRES = os.environ.get("DATABASE_URL", "")


@pytest.fixture(params=["sqlite", "postgres"])
async def engine(request: pytest.FixtureRequest, tmp_path: Path):
    """Engine đã tạo bảng, dọn sạch trước mỗi test."""
    if request.param == "postgres":
        if not DSN_POSTGRES.startswith("postgresql"):
            pytest.skip("không có DATABASE_URL trỏ tới PostgreSQL")
        dsn = DSN_POSTGRES
    else:
        dsn = dung_dsn_sqlite(tmp_path / "tich_hop.sqlite3")

    e = tao_engine(dsn)
    # Dọn TRƯỚC, không phải sau: test trước có thể đã chết giữa chừng và để lại
    # rác. Dọn sau thì trạng thái bẩn ấy đi vào test kế tiếp.
    async with e.begin() as conn:
        await conn.run_sync(metadata.drop_all)
    await tao_bang(e)
    yield e
    await e.dispose()


# ── Kho quan hệ ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ghi_va_doc_tin_nhan(engine):
    kho = SqlRelationalRepository(engine)
    for i in range(3):
        await kho.save_message(A, "s1", Message(role=Role.USER, content=f"m{i}"))
    assert [m.content for m in await kho.get_messages(A, "s1")] == ["m0", "m1", "m2"]


@pytest.mark.asyncio
async def test_co_lap_tenant_o_kho_quan_he(engine):
    kho = SqlRelationalRepository(engine)
    await kho.save_message(A, "s1", Message(role=Role.USER, content="của A"))
    assert await kho.get_messages(B, "s1") == [], "B đọc được tin của A"


@pytest.mark.asyncio
async def test_limit_lay_ban_MOI_NHAT(engine):
    kho = SqlRelationalRepository(engine)
    for i in range(5):
        await kho.save_message(A, "s1", Message(role=Role.USER, content=f"m{i}"))
    assert [m.content for m in await kho.get_messages(A, "s1", limit=2)] == ["m3", "m4"]


# ── Kho vector ───────────────────────────────────────────────────────────────


def _chunk(cid: str, noi_dung: str, vec: list[float]) -> EnrichedChunk:
    return EnrichedChunk(
        id=cid, doc_id="d1", tenant_id="x", index=0,
        content=noi_dung, token_count=5, embedding=vec,
    )


@pytest.mark.asyncio
async def test_tim_vector_tra_ve_dung_thu_hang(engine):
    kho = SqlVectorRepository(engine)
    await kho.insert_chunks(A, [
        _chunk("gan", "rất giống", [1.0, 0.0, 0.0]),
        _chunk("xa", "khác hẳn", [0.0, 1.0, 0.0]),
    ])
    kq = await kho.search_vector(A, [1.0, 0.0, 0.0], top_k=2)
    assert [r.chunk_id for r in kq] == ["gan", "xa"]


@pytest.mark.asyncio
async def test_co_lap_tenant_o_kho_vector(engine):
    """Quên lọc tenant ở kho vector KHÔNG báo lỗi — nó trả tài liệu của người khác
    kèm điểm tương đồng trông rất thuyết phục."""
    kho = SqlVectorRepository(engine)
    await kho.insert_chunks(A, [_chunk("cua_a", "bí mật của A", [1.0, 0.0, 0.0])])
    await kho.insert_chunks(B, [_chunk("cua_b", "bí mật của B", [1.0, 0.0, 0.0])])

    assert [r.chunk_id for r in await kho.search_vector(A, [1.0, 0.0, 0.0])] == ["cua_a"]
    assert [r.chunk_id for r in await kho.search_vector(B, [1.0, 0.0, 0.0])] == ["cua_b"]


@pytest.mark.asyncio
async def test_ghi_de_chunk_cung_id(engine):
    kho = SqlVectorRepository(engine)
    await kho.insert_chunks(A, [_chunk("c1", "bản cũ", [1.0, 0.0, 0.0])])
    await kho.insert_chunks(A, [_chunk("c1", "bản mới", [1.0, 0.0, 0.0])])
    kq = await kho.search_vector(A, [1.0, 0.0, 0.0], top_k=10)
    assert len(kq) == 1 and kq[0].content == "bản mới"


@pytest.mark.asyncio
async def test_bm25_tim_theo_tu_khoa(engine):
    kho = SqlVectorRepository(engine)
    await kho.insert_chunks(A, [
        _chunk("co", "chiều sông quê hương", [0.0, 0.0, 0.0]),
        _chunk("khong", "tàu vũ trụ sao hoả", [0.0, 0.0, 0.0]),
    ])
    kq = await kho.search_bm25(A, "chiều sông", top_k=5)
    assert [r.chunk_id for r in kq] == ["co"]


# ── Bộ đếm và khoá API ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ngan_sach_ngay_dem_dung(engine):
    rl = SqlRateLimiter(engine, so_lan_goi_model_moi_ngay=2)
    scope = ThreadScope(platform="web", thread_id="t1")
    assert await rl.within_daily_budget(scope) is True
    assert await rl.within_daily_budget(scope) is True
    assert await rl.within_daily_budget(scope) is False


@pytest.mark.asyncio
async def test_vong_doi_khoa_api(engine):
    import time

    kho = SqlApiKeyStore(engine)
    khoa = await kho.phat_hanh("cong_ty_a", ten="ứng dụng A")
    bam = bam_khoa(khoa)

    assert isinstance(kiem_khoa(await kho.tra(bam), bay_gio=time.time()), KhoaHopLe)
    assert await kho.thu_hoi(bam) is True
    kq = kiem_khoa(await kho.tra(bam), bay_gio=time.time())
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "da_thu_hoi"
