import pytest

from adapters.persistence.memory.relational import InMemoryRelationalRepository
from adapters.persistence.sql.engine import tao_bang, tao_engine
from adapters.persistence.sql.relational import SqlRelationalRepository
from application.conversation.cursor import decode_cursor, encode_cursor
from domain.conversation.tenant import TenantScope


@pytest.mark.parametrize("kind", ["memory", "sql"])
async def test_search_filters_before_limit_literal_wildcards_and_cursor(kind):
    engine = None
    if kind == "sql":
        engine = tao_engine("sqlite+aiosqlite:///:memory:")
        await tao_bang(engine)
        repository = SqlRelationalRepository(engine)
    else:
        repository = InMemoryRelationalRepository()
    a, b = TenantScope("a"), TenantScope("b")
    try:
        for title in ["Find 100%_done", "other", "Find next"]:
            await repository.tao_hoi_thoai(a, tieu_de=title)
        await repository.tao_hoi_thoai(b, tieu_de="Find secret")
        found = await repository.danh_sach_hoi_thoai(a, q="Find", limit=1)
        assert len(found) == 1
        cursor = found[0]._page_cursor or encode_cursor(
            found[0].cap_nhat_luc.timestamp(), found[0].conversation_id
        )
        following = await repository.danh_sach_hoi_thoai(a, q="Find", cursor=cursor)
        assert len(following) == 1 and following[0].conversation_id != found[0].conversation_id
        literal = await repository.danh_sach_hoi_thoai(a, q="%_")
        assert len(literal) == 1 and literal[0].tieu_de == "Find 100%_done"
        assert not await repository.danh_sach_hoi_thoai(a, q="secret")
    finally:
        if engine:
            await engine.dispose()


@pytest.mark.parametrize("cursor", ["garbage", "e30", "W05hTiwieCJd"])
def test_bad_cursor_is_rejected(cursor):
    with pytest.raises(ValueError):
        decode_cursor(cursor)
