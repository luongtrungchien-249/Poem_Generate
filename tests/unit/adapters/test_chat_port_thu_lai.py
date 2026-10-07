"""QĐ-P9 — `ChatLlmAdapter` thử lại lỗi TẠM THỜI, không thử lại lỗi của chính yêu cầu.

Đo thật 26/09/2026: không có retry thì 8/20 đề trượt oan vì 429.
"""

from __future__ import annotations

import httpx
import pytest

from adapters.llm.chat_port import ChatLlmAdapter
from application.ports.generation import LLMResponse
from application.ports.llm import CallContext, UserMessage
from domain.common.errors import UpstreamError
from domain.common.result import Err, Ok
from domain.conversation.thread import ThreadScope

pytestmark = pytest.mark.unit

CTX = CallContext(scope=ThreadScope(platform="web", thread_id="t"), sender_id="u", trace_id="x")
MSG = (UserMessage(content="xin chào"),)


def _loi(ma: int, retry_after: str | None = None) -> httpx.HTTPStatusError:
    headers = {"retry-after": retry_after} if retry_after else {}
    req = httpx.Request("POST", "https://api.test/v1/chat/completions")
    return httpx.HTTPStatusError("lỗi", request=req, response=httpx.Response(ma, headers=headers, request=req))


class _ClientGia:
    def __init__(self, loi: list[BaseException]) -> None:
        self.loi = list(loi)
        self.so_lan_goi = 0

    async def generate(self, messages, model=None, tools=None):  # type: ignore[no-untyped-def]
        self.so_lan_goi += 1
        if self.loi:
            raise self.loi.pop(0)
        return LLMResponse(content="ok", model=model or "m", usage={"prompt_tokens": 1, "completion_tokens": 1})


def _adapter(client: _ClientGia, cho: list[float], **kw) -> ChatLlmAdapter:  # type: ignore[no-untyped-def]
    async def ngu(giay: float) -> None:
        cho.append(giay)

    return ChatLlmAdapter(client, ngu=ngu, **kw)  # type: ignore[arg-type]


async def test_429_duoc_thu_lai_roi_thanh_cong():
    c, cho = _ClientGia([_loi(429), _loi(429)]), []
    kq = await _adapter(c, cho).reply(MSG, (), CTX)
    assert isinstance(kq, Ok) and kq.value.text == "ok"
    assert c.so_lan_goi == 3 and len(cho) == 2


async def test_ton_trong_retry_after():
    c, cho = _ClientGia([_loi(429, retry_after="7")]), []
    await _adapter(c, cho).reply(MSG, (), CTX)
    assert cho == [7.0]


@pytest.mark.parametrize("ma", [400, 401, 404, 422])
async def test_loi_cua_chinh_yeu_cau_KHONG_thu_lai(ma):
    c, cho = _ClientGia([_loi(ma)]), []
    kq = await _adapter(c, cho).reply(MSG, (), CTX)
    assert isinstance(kq, Err) and isinstance(kq.error, UpstreamError)
    assert kq.error.status_code == ma
    assert c.so_lan_goi == 1 and cho == []


async def test_het_luot_thu_lai_thi_tra_loi_co_ma():
    c, cho = _ClientGia([_loi(503)] * 10), []
    kq = await _adapter(c, cho, so_lan_thu_lai=2).reply(MSG, (), CTX)
    assert isinstance(kq, Err) and kq.error.status_code == 503
    assert c.so_lan_goi == 3


async def test_loi_mang_duoc_thu_lai():
    c, cho = _ClientGia([httpx.ConnectTimeout("hết giờ")]), []
    kq = await _adapter(c, cho).reply(MSG, (), CTX)
    assert isinstance(kq, Ok) and c.so_lan_goi == 2


async def test_doc_retryDelay_trong_than_loi_cua_google():
    req = httpx.Request("POST", "https://generativelanguage.googleapis.com/v1beta/models/x:generateContent")
    than = {"error": {"code": 429, "details": [
        {"@type": "type.googleapis.com/google.rpc.RetryInfo", "retryDelay": "23s"}]}}
    loi = httpx.HTTPStatusError("429", request=req, response=httpx.Response(429, json=than, request=req))
    c, cho = _ClientGia([loi]), []
    await _adapter(c, cho).reply(MSG, (), CTX)
    assert len(cho) == 1 and 23.0 <= cho[0] < 24.0
