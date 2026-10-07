import asyncio
from types import SimpleNamespace

from adapters.persistence.sql.engine import tao_bang, tao_engine
from adapters.persistence.sql.rate_limit import SqlRateLimiter
from adapters.rate_limit.memory import InMemoryRateLimiter
from application.poetry.budget import JobBudgetLlm
from application.poetry.tools import PoetryTools
from application.ports.llm import ToolCall, ToolResult
from application.ports.tools import ToolSpec
from domain.common.result import Err, Ok
from domain.conversation.thread import ThreadScope


async def test_job_call_ceiling_holds_under_concurrency():
    class Llm:
        calls = 0

        async def reply(self, **kwargs):
            self.calls += 1
            await asyncio.sleep(0)
            return Ok("safe")

    inner = Llm()
    meter = JobBudgetLlm(inner, InMemoryRateLimiter(), "a", 3)
    ctx = SimpleNamespace(scope=ThreadScope(platform="web", thread_id="a"))
    results = await asyncio.gather(*(meter.reply((), (), ctx) for _ in range(12)))
    assert inner.calls == 3
    assert sum(isinstance(result, Err) for result in results) == 9


async def test_shared_daily_budget_atomic_admission(tmp_path):
    dsn = f"sqlite+aiosqlite:///{(tmp_path / 'quota.db').as_posix()}"
    engines = [tao_engine(dsn), tao_engine(dsn)]
    try:
        await tao_bang(engines[0])
        limiters = [SqlRateLimiter(engine, so_lan_goi_model_moi_ngay=3) for engine in engines]
        scope = ThreadScope(platform="web", thread_id="ngansach:a")
        results = await asyncio.gather(
            *(limiters[i % 2].within_daily_budget(scope) for i in range(15))
        )
        assert sum(results) == 3
    finally:
        for engine in engines:
            await engine.dispose()


async def test_poetry_tools_deny_recursive_generation_and_external_io():
    class Tools:
        received = ()

        def specs(self):
            return tuple(
                ToolSpec(name=name, description="", parameters={})
                for name in ("kiem_tra_tho", "sinh_tho", "http_call")
            )

        async def call_many(self, calls, ctx):
            self.received = calls
            return tuple(ToolResult(call_id=call.id, content="ok") for call in calls)

    inner = Tools()
    tools = PoetryTools(inner)
    assert [spec.name for spec in tools.specs()] == ["kiem_tra_tho"]
    calls = tuple(
        ToolCall(id=str(i), name=name, arguments="{}")
        for i, name in enumerate(("sinh_tho", "kiem_tra_tho", "http_call"))
    )
    results = await tools.call_many(calls, None)
    assert [call.name for call in inner.received] == ["kiem_tra_tho"]
    assert [result.is_error for result in results] == [True, False, True]
