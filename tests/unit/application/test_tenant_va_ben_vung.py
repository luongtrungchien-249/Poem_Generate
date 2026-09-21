"""G9 — cô lập tenant thật sự, và dữ liệu sống qua restart.

Hai tính chất phải chứng minh, và cả hai đều từng SAI:

    1. Hai tenant không thấy dữ liệu của nhau — lỗi cũ lọc nhầm chỗ nên RAG rỗng
    2. Ghi xong, đóng, mở lại thì dữ liệu còn — lỗi cũ: mất sạch mỗi lần restart
"""

from __future__ import annotations

from pathlib import Path

import pytest

from adapters.persistence.memory.relational import InMemoryRelationalRepository
from adapters.persistence.memory.vector import InMemoryVectorRepository
from adapters.persistence.sql import (
    SqlCacheRepository,
    SqlRelationalRepository,
    dung_dsn_sqlite,
    tao_bang,
    tao_engine,
)
from application.rag.retriever import HybridRetriever
from contracts.chat import Message, Role
from contracts.chunk import Document, EnrichedChunk
from contracts.feedback import FeedbackRecord
from domain.conversation.tenant import TenantScope

pytestmark = pytest.mark.unit


async def _engine(duong_dan):
    """Engine đã tạo bảng. Mỗi lần gọi là một kết nối MỚI tới cùng tệp — đó chính
    là cách mô phỏng một tiến trình khác, hoặc cùng tiến trình sau khi restart."""
    e = tao_engine(dung_dsn_sqlite(duong_dan))
    await tao_bang(e)
    return e


A = TenantScope(tenant_id="cong_ty_a")
B = TenantScope(tenant_id="cong_ty_b")


def _chunk(cid: str, noi_dung: str, tenant: str) -> EnrichedChunk:
    return EnrichedChunk(
        id=cid, doc_id="d1", tenant_id=tenant, index=0,
        content=noi_dung, token_count=5, embedding=[1.0, 0.0, 0.0],
    )


class _BoNhungGia:
    async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
        return [[1.0, 0.0, 0.0] for _ in texts]


# ── TenantScope: kiểu chặn được cái mà chuỗi không chặn được ─────────────────


def test_tenant_rong_bi_tu_choi_ngay_luc_dung():
    with pytest.raises(ValueError):
        TenantScope(tenant_id="")
    with pytest.raises(ValueError):
        TenantScope(tenant_id="   ")


def test_tenant_mac_dinh_phai_goi_TUONG_MINH():
    """`TenantScope()` không gọi được — không ai vô tình rơi vào tenant mặc định."""
    with pytest.raises(TypeError):
        TenantScope()  # type: ignore[call-arg]
    assert TenantScope.mac_dinh().tenant_id == "default"


# ── 🩸 Lỗi cũ: RAG luôn trả rỗng ────────────────────────────────────────────


@pytest.mark.asyncio
async def test_RAG_tra_ve_KET_QUA_chu_khong_rong():
    """Bản trước lọc `tenant_id` trên `chunk.metadata` — nơi nó không nằm. Mọi chunk
    bị loại, RAG luôn rỗng, và trông như "không tìm thấy tài liệu"."""
    kho = InMemoryVectorRepository()
    await kho.insert_chunks(A, [_chunk("c1", "chiều sông quê", "cong_ty_a")])

    r = HybridRetriever(vector_repo=kho, embedder=_BoNhungGia())
    kq = await r.retrieve(A, query="chiều sông", top_k=3)
    assert kq, "RAG trả rỗng — lỗi lọc tenant đã quay lại"


@pytest.mark.asyncio
async def test_tenant_KHONG_thay_du_lieu_cua_tenant_khac():
    kho = InMemoryVectorRepository()
    await kho.insert_chunks(A, [_chunk("c1", "bí mật của A", "cong_ty_a")])
    await kho.insert_chunks(B, [_chunk("c2", "bí mật của B", "cong_ty_b")])

    r = HybridRetriever(vector_repo=kho, embedder=_BoNhungGia())
    cua_a = await r.retrieve(A, query="bí mật", top_k=10)
    assert {x.chunk_id for x in cua_a} == {"c1"}, "A thấy dữ liệu của B"

    cua_b = await r.retrieve(B, query="bí mật", top_k=10)
    assert {x.chunk_id for x in cua_b} == {"c2"}, "B thấy dữ liệu của A"


@pytest.mark.asyncio
async def test_client_KHONG_the_ghi_xuyen_tenant_bang_payload():
    """Payload khai `tenant_id` của người khác thì vẫn bị ghi về tenant của scope."""
    kho = InMemoryVectorRepository()
    # A gửi chunk tự nhận thuộc B.
    await kho.insert_chunks(A, [_chunk("c1", "chèn lén", "cong_ty_b")])

    r = HybridRetriever(vector_repo=kho, embedder=_BoNhungGia())
    assert not await r.retrieve(B, query="chèn lén", top_k=10), "ghi xuyên tenant lọt"
    assert await r.retrieve(A, query="chèn lén", top_k=10)


@pytest.mark.asyncio
async def test_kho_quan_he_cung_co_lap_theo_tenant():
    kho = InMemoryRelationalRepository()
    # Cùng `session_id` — client tự đặt nên rất hay trùng.
    await kho.save_message(A, "s1", Message(role=Role.USER, content="của A"))
    await kho.save_message(B, "s1", Message(role=Role.USER, content="của B"))

    assert [m.content for m in await kho.get_messages(A, "s1")] == ["của A"]
    assert [m.content for m in await kho.get_messages(B, "s1")] == ["của B"]

    await kho.save_feedback(A, FeedbackRecord(id="f1", trace_id="t", rating=1))
    assert await kho.get_feedbacks(B) == [], "B đọc được phản hồi của A"


# ── 🩸 Lỗi cũ: mất sạch khi restart ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_du_lieu_SONG_QUA_restart(tmp_path: Path):
    """Ca thử trung tâm của G9: ghi, vứt object, dựng lại từ cùng tệp."""
    tep = tmp_path / "app.sqlite3"

    kho1 = SqlRelationalRepository(await _engine(tep))
    await kho1.save_message(A, "s1", Message(role=Role.USER, content="còn không?"))
    await kho1.save_document_meta(A, Document(id="d1", title="T", content="nội dung"))
    del kho1  # mô phỏng tiến trình tắt

    kho2 = SqlRelationalRepository(await _engine(tep))
    assert [m.content for m in await kho2.get_messages(A, "s1")] == ["còn không?"]
    doc = await kho2.get_document_meta(A, "d1")
    assert doc is not None and doc.title == "T"


@pytest.mark.asyncio
async def test_sqlite_co_lap_tenant(tmp_path: Path):
    kho = SqlRelationalRepository(await _engine(tmp_path / "a.sqlite3"))
    await kho.save_message(A, "s1", Message(role=Role.USER, content="của A"))
    assert await kho.get_messages(B, "s1") == []


@pytest.mark.asyncio
async def test_sqlite_giu_dung_THU_TU_thoi_gian(tmp_path: Path):
    """`limit` phải lấy N bản MỚI NHẤT rồi trả theo thứ tự cũ→mới.

    Lấy N bản ĐẦU rồi cắt đuôi sẽ trả về phần cũ nhất — sai hẳn nghĩa "recent".
    """
    kho = SqlRelationalRepository(await _engine(tmp_path / "b.sqlite3"))
    for i in range(5):
        await kho.save_message(A, "s1", Message(role=Role.USER, content=f"m{i}"))
    assert [m.content for m in await kho.get_messages(A, "s1", limit=3)] == ["m2", "m3", "m4"]


@pytest.mark.asyncio
async def test_cache_sqlite_ton_trong_TTL(tmp_path: Path):
    c = SqlCacheRepository(await _engine(tmp_path / "c.sqlite3"))
    await c.set("k", "v", ttl_seconds=3600)
    assert await c.get("k") == "v"

    await c.set("het", "v", ttl_seconds=-1)
    assert await c.get("het") is None, "mục đã hết hạn vẫn đọc được"


@pytest.mark.asyncio
async def test_cache_sqlite_song_qua_restart(tmp_path: Path):
    tep = tmp_path / "d.sqlite3"
    c1 = SqlCacheRepository(await _engine(tep))
    await c1.set("k", "v", ttl_seconds=3600)
    del c1
    assert await SqlCacheRepository(await _engine(tep)).get("k") == "v"
