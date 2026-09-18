from adapters.llm.resilience import CircuitBreaker
from adapters.llm.router import ModelRouter
from contracts.chat import Message, Role
from domain.llm.token import TokenManager


def test_model_router():
    router = ModelRouter()
    # Explicit override
    assert router.select_model(explicit_model="custom-vllm") == "custom-vllm"
    # Cheap tier
    cheap = router.select_model(tier="cheap")
    assert cheap in ["gpt-4o-mini", "claude-3-5-haiku", "mock-gpt"]
    # Reasoning tier
    assert router.select_model(tier="reasoning") in ["o1-preview", "gpt-4o", "mock-gpt"]


def test_circuit_breaker():
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout_sec=10.0)
    assert breaker.allow_request()

    breaker.record_failure()
    assert breaker.allow_request()

    breaker.record_failure()
    # Should trip to OPEN
    assert not breaker.allow_request()

    breaker.record_success()
    assert breaker.allow_request()


def test_token_manager_truncate():
    tm = TokenManager()
    sys_msg = Message(role=Role.SYSTEM, content="System prompt instructions.")
    m1 = Message(role=Role.USER, content="Tin nhắn số 1")
    m2 = Message(role=Role.ASSISTANT, content="Trả lời số 1")
    m3 = Message(role=Role.USER, content="Tin nhắn mới nhất cần trả lời")

    truncated = tm.truncate_context([sys_msg, m1, m2, m3], max_tokens=50)
    assert len(truncated) >= 2
    assert truncated[0].role == Role.SYSTEM
    assert truncated[-1].content == "Tin nhắn mới nhất cần trả lời"
