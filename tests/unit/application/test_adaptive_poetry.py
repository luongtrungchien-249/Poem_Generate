from types import SimpleNamespace

from application.poetry.prompt import khung_thanh_cap_dong
from application.poetry.sinh_theo_kho import _chon_mot_kho
from domain.common.result import Ok

VALID = "\n".join(
    (
        "Chiều rơi chậm xuống mái rêu xanh",
        "Con ngõ nhỏ dài hơn tiếng ve",
        "Ai đứng bên kia bờ nắng mảnh",
        "Gọi một mùa xa chẳng dám về",
    )
)


class Llm:
    def __init__(self, text):
        self.text, self.calls = text, 0

    async def reply(self, **kwargs):
        self.calls += 1
        return Ok(SimpleNamespace(text=self.text))


async def test_adaptive_stops_at_first_small_batch():
    fixed, adaptive = Llm(VALID), Llm(VALID)
    for llm, flag, calls in ((fixed, False, 8), (adaptive, True, 2)):
        result, used = await _chon_mot_kho(
            "request",
            [],
            llm=llm,
            ctx=None,
            so_ung_vien=32,
            default_model="mock",
            adaptive_candidates=flag,
        )
        assert result == VALID.splitlines()
        assert used == llm.calls == calls


async def test_adaptive_keeps_full_candidate_ceiling_when_no_candidate_passes():
    llm = Llm("not a poem")
    result, calls = await _chon_mot_kho(
        "request",
        [],
        llm=llm,
        ctx=None,
        so_ung_vien=32,
        default_model="mock",
        adaptive_candidates=True,
    )
    assert result is None and calls == llm.calls == 8


async def test_cancel_before_batch_never_calls_model():
    llm = Llm(VALID)
    result, calls = await _chon_mot_kho(
        "request",
        [],
        llm=llm,
        ctx=None,
        so_ung_vien=32,
        default_model="mock",
        adaptive_candidates=True,
        should_stop_hook=lambda: True,
    )
    assert result is None and calls == llm.calls == 0


def test_shared_line_frame_handles_entire_poem():
    text = khung_thanh_cap_dong(20)
    assert "D1 B-T-B" in text and "D20 T-B-T" in text
    assert text.count("B-T-B") == text.count("T-B-T") == 10
