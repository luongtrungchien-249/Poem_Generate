"""Hợp đồng HTTP của `POST /v1/poem`.

Điều phải chứng minh ở đây KHÔNG phải "endpoint chạy được", mà là điều mạnh hơn và
là điều kiện nghiệm thu số 2 của `Plan_Thi_Cong_DeepAgent.md` §9:

    KHÔNG TỒN TẠI ĐƯỜNG NÀO từ HTTP trả về một bài thơ có `dat == False`.

Provider trong test là `mock` (xem `tests/conftest.py`), và `MockLLMClient` trả về
một câu tiếng Anh chứ không phải thơ. Nhờ vậy đường thật bị ép vào đúng nhánh đáng
lo nhất: mô hình trả rác ở mọi lượt. Đáp án đúng là 422, không phải 200 kèm rác.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from application.rule import kiem_tra_bai_tho
from entrypoints.api.app import app

pytestmark = pytest.mark.contract

client = TestClient(app)


def _yeu_cau_du(**ghi_de: object) -> dict[str, object]:
    goc: dict[str, object] = {
        "yeu_cau": "Viết bài thất ngôn tự do về quê hương, giọng hoài niệm.",
        "chu_de": "quê hương",
        "so_dong": 8,
        "cam_xuc": "hoài niệm",
        "max_repair_rounds": 0,
    }
    goc.update(ghi_de)
    return goc


# ── Tính chất cốt lõi: cổng không rò ──────────────────────────────────────────


def test_KHONG_BAO_GIO_tra_200_kem_bai_sai_luat():
    """Điều kiện nghiệm thu số 2 — không thương lượng.

    Dù mô hình trả gì, nếu có `poem` trong response thì bài đó PHẢI đúng luật.
    """
    resp = client.post("/v1/poem", json=_yeu_cau_du())
    assert resp.status_code in (200, 422)
    data = resp.json()

    if resp.status_code == 200 and "poem" in data:
        v = kiem_tra_bai_tho(data["poem"])
        assert v.dat, f"API trả ra bài sai luật:\n{data['poem']}"
        assert data["dat"] is True
        assert data["dat_luat"] is True


def test_mo_hinh_tra_rac_thi_422_va_KHONG_co_van_ban_tho():
    """Fail closed. Mock trả một câu tiếng Anh — không được có bài thơ nào đi ra."""
    resp = client.post("/v1/poem", json=_yeu_cau_du())
    assert resp.status_code == 422, f"lẽ ra phải fail closed, nhận {resp.status_code}"

    data = resp.json()
    assert data["ma_the"] == "that_ngon_tu_do"
    assert data["chan_doan"], "phải có chẩn đoán để nói thật với người dùng"
    assert "trace_id" in data
    # Không trường nào được chứa văn bản thơ.
    assert "poem" not in data
    assert not any(k in data for k in ("text", "ban_nhap", "draft"))


# ── Chỉ thị 5: đủ thông tin mới cho thơ ───────────────────────────────────────


def test_thieu_chu_de_thi_HOI_LAI_chu_khong_doan():
    resp = client.post(
        "/v1/poem", json={"yeu_cau": "Viết cho tôi một bài thơ.", "max_repair_rounds": 0}
    )
    # Hỏi lại KHÔNG phải lỗi của người dùng, nên 200.
    assert resp.status_code == 200
    data = resp.json()
    assert data["can_lam_ro"] is True
    assert data["ca"] == 1
    assert "chủ đề" in data["cau_hoi"]
    assert "poem" not in data


def test_so_dong_khong_boi_4_thi_HOI_LAI_chu_khong_tu_lam_tron():
    """QĐ-D5. Làm tròn im lặng là quyết định thay người dùng."""
    resp = client.post("/v1/poem", json=_yeu_cau_du(so_dong=6))
    assert resp.status_code == 200
    data = resp.json()
    assert data["can_lam_ro"] is True
    assert data["ca"] == 4
    assert "bội của 4" in data["cau_hoi"]
    assert "4 dòng hay 8 dòng" in data["cau_hoi"]


def test_chi_thieu_so_dong_thi_KHONG_goi_model_lan_nao():
    """Chặn sớm phải thật sự rẻ.

    `so_dong` do regex tất định lo — H4 là luật cứng nên không giao cho mô hình.
    Vì vậy khi thứ duy nhất còn thiếu là số dòng, một lượt gọi mô hình là tiền vứt
    đi: cổng B1 sẽ hỏi lại y hệt.
    """
    from adapters.llm.mock import MockLLMClient

    goc = MockLLMClient.generate
    so_lan = 0

    async def dem(self, *a, **kw):  # type: ignore[no-untyped-def]
        nonlocal so_lan
        so_lan += 1
        return await goc(self, *a, **kw)

    MockLLMClient.generate = dem  # type: ignore[assignment, method-assign]
    try:
        client.post(
            "/v1/poem",
            json={
                "yeu_cau": "Viết bài thơ về biển",
                "chu_de": "biển",
                "cam_xuc": "nhớ",
                "phong_cach": "mộc mạc",
                "rang_buoc_van": "vần chân",
                "rang_buoc_thanh": "luân phiên",
                "max_repair_rounds": 3,
            },
        )
    finally:
        MockLLMClient.generate = goc  # type: ignore[method-assign]

    assert so_lan == 0, f"lẽ ra không gọi model lần nào, nhưng đã gọi {so_lan} lần"


def test_thieu_chu_de_thi_chi_goi_model_de_TRICH_chu_khong_de_SINH_THO():
    """Khi chủ đề nằm trong câu nói tự nhiên thì phải đọc mới biết — một lượt gọi
    để TRÍCH là chính đáng. Nhưng KHÔNG được có lượt nào để SINH THƠ.
    """
    from adapters.llm.mock import MockLLMClient

    goc = MockLLMClient.generate
    so_lan = 0

    async def dem(self, *a, **kw):  # type: ignore[no-untyped-def]
        nonlocal so_lan
        so_lan += 1
        return await goc(self, *a, **kw)

    MockLLMClient.generate = dem  # type: ignore[assignment, method-assign]
    try:
        resp = client.post(
            "/v1/poem", json={"yeu_cau": "Viết bài thơ.", "max_repair_rounds": 3}
        )
    finally:
        MockLLMClient.generate = goc  # type: ignore[method-assign]

    assert so_lan <= 1, f"chỉ được một lượt TRÍCH, nhưng đã gọi {so_lan} lần"
    data = resp.json()
    assert data.get("can_lam_ro") is True
    assert "poem" not in data, "không được sinh thơ khi chưa đủ thông tin"


# ── Bằng chứng ────────────────────────────────────────────────────────────────


def test_endpoint_co_trong_openapi_va_khai_bao_du_ba_dang_tra_ve():
    spec = client.get("/openapi.json").json()
    assert "/v1/poem" in spec["paths"]


def test_payload_sai_thi_422_cua_pydantic():
    resp = client.post("/v1/poem", json={})
    assert resp.status_code == 422


# ── Nhánh thuận: chứng minh 200 chạy được qua HTTP thật ───────────────────────

BAI_DAT_8_DONG = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh\n"
    "Đường cũ chân ai còn vọng lại\n"
    "Bờ tre nghiêng bóng nắng chưa đành\n"
    "Người đi để lại mùa hương cũ\n"
    "Khói bếp chiều nay vẫn quẩn quanh"
)


@pytest.fixture
def mo_hinh_tra_bai_dat(monkeypatch: pytest.MonkeyPatch):
    """Ép provider mock trả một bài ĐÚNG LUẬT.

    Không sửa `MockLLMClient` thật: mock đó cố ý trả văn bản không phải thơ, và
    chính nhờ vậy mà test fail-closed ở trên mới có nghĩa. Ở đây chỉ thay hành vi
    cho riêng một test.
    """
    from adapters.llm.mock import MockLLMClient
    from application.ports.llm_client import LLMResponse

    async def tra_bai(self, messages, model="mock-gpt", **kw):  # type: ignore[no-untyped-def]
        return LLMResponse(
            content=BAI_DAT_8_DONG,
            model=model,
            usage={"prompt_tokens": 10, "completion_tokens": 20},
        )

    monkeypatch.setattr(MockLLMClient, "generate", tra_bai)
    return BAI_DAT_8_DONG


def test_bai_dat_thi_200_kem_du_bang_chung_bay_tang(mo_hinh_tra_bai_dat: str):
    resp = client.post("/v1/poem", json=_yeu_cau_du())
    assert resp.status_code == 200, resp.text
    data = resp.json()

    assert data["poem"].strip() == mo_hinh_tra_bai_dat
    assert data["dat"] is True
    assert data["thuoc_the"] is True
    assert data["dat_luat"] is True
    assert data["dat_chat_luong"] is True
    assert data["so_dong"] == 8
    assert data["so_luot_sua"] == 0

    # §3.4 và §19.2: mọi bài trả ra đều phải kèm bằng chứng, không phải tin suông.
    tang = data["bang_chung_bay_tang"]
    assert len(tang) == 7
    assert all(t["da_chay"] for t in tang), "bài đạt thì cả bảy tầng phải đã chạy"
    assert all(t["bang_chung"].strip() for t in tang)
    assert all(t["trich_luat"].strip() for t in tang)

    # Chất lượng: đủ bảy chiều, và hai chiều ngữ nghĩa tự khai là không đo được.
    chieu = data["chat_luong"]
    assert len(chieu) == 7
    khong_do = [c["ma"] for c in chieu if not c["do_duoc"]]
    assert {"CL6", "CL7"} <= set(khong_do)


def test_bai_dat_van_bi_chan_neu_thieu_thong_tin(mo_hinh_tra_bai_dat: str):
    """Chỉ thị 5 mạnh hơn cả việc mô hình viết đúng.

    Mô hình trả bài hoàn hảo, nhưng yêu cầu thiếu chủ đề — vẫn phải hỏi lại.
    """
    resp = client.post("/v1/poem", json={"yeu_cau": "Viết bài thơ.", "max_repair_rounds": 0})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("can_lam_ro") is True
    assert "poem" not in data
