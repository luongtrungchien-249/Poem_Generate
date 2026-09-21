"""Cưỡng chế ADR-0005 — dùng CỔNG HẸP, không dùng cổng gộp.

    bootstrap/   và  adapters/    ĐƯỢC dùng `LLMClient` (gộp cả ba)
    application/ và  entrypoints/ phải dùng đúng cổng hẹp mình cần

VÌ SAO PHẢI CÓ TEST NÀY. Tách port mà không cưỡng chế thì việc tách bị xói mòn
trong vài tuần: người viết code mới thấy `LLMClient` có đủ mọi thứ, import nó cho
tiện, và sáu tháng sau mọi module lại phụ thuộc vào cổng gộp như cũ — chỉ khác là
giờ có thêm ba tệp port không ai dùng.

Cái mất khi xói mòn không trừu tượng: một `HybridRetriever` nhận `LLMClient` thì
KHÔNG thay được bằng bộ nhúng cục bộ, dù nó chỉ gọi đúng `embed()`.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"

# Chỉ hai vòng này được biết tới cổng gộp: composition root (phải dựng client thật)
# và adapter (phải hiện thực cả ba).
VONG_DUOC_PHEP = ("bootstrap", "adapters")

CONG_GOP = "LLMClient"

CONG_HEP = {"EmbeddingPort", "StreamingPort", "GenerationPort"}


def _cac_import(tep: Path) -> list[tuple[str, str, int]]:
    """Trả về (module, tên được import, dòng)."""
    cay = ast.parse(tep.read_text(encoding="utf-8"), filename=str(tep))
    ra: list[tuple[str, str, int]] = []
    for nut in ast.walk(cay):
        if isinstance(nut, ast.ImportFrom) and nut.module:
            for ten in nut.names:
                ra.append((nut.module, ten.name, nut.lineno))
    return ra


@pytest.mark.architecture
def test_chi_bootstrap_va_adapters_duoc_dung_cong_gop():
    vi_pham: list[str] = []
    for tep in SRC.rglob("*.py"):
        vong = tep.relative_to(SRC).parts[0]
        if vong in VONG_DUOC_PHEP:
            continue
        # Bản thân tệp định nghĩa cổng gộp thì được nhắc tên nó.
        if tep.relative_to(SRC).as_posix() == "application/ports/llm_client.py":
            continue
        for module, ten, dong in _cac_import(tep):
            if ten == CONG_GOP:
                vi_pham.append(
                    f"{tep.relative_to(SRC)}:{dong} import {CONG_GOP} từ {module}"
                )

    assert not vi_pham, (
        "ADR-0005: application/ và entrypoints/ phải dùng CỔNG HẸP "
        "(EmbeddingPort · StreamingPort · GenerationPort), không dùng LLMClient.\n"
        + "\n".join(f"  - {v}" for v in vi_pham)
    )


@pytest.mark.architecture
def test_ba_cong_hep_deu_that_su_co_nguoi_dung():
    """Cổng không ai dùng là cổng thừa — và là dấu hiệu việc tách chỉ nằm trên giấy."""
    dem = dict.fromkeys(CONG_HEP, 0)
    for tep in SRC.rglob("*.py"):
        if tep.relative_to(SRC).parts[:2] == ("application", "ports"):
            continue
        for _module, ten, _dong in _cac_import(tep):
            if ten in dem:
                dem[ten] += 1

    khong_ai_dung = [ten for ten, n in dem.items() if n == 0]
    assert not khong_ai_dung, (
        f"Các cổng hẹp sau không có nơi nào dùng: {khong_ai_dung}. "
        "Hoặc nối chúng vào, hoặc xoá đi — đừng để port chết trong repo."
    )


@pytest.mark.architecture
def test_retriever_chi_phu_thuoc_vao_kha_nang_nhung():
    """Ràng buộc cụ thể mà ADR-0005 muốn bảo vệ, viết thành một test đọc được."""
    from application.ports.embedding import EmbeddingPort
    from application.rag.retriever import HybridRetriever

    class BoNhungCucBo:
        """Không có `reply`, không có `stream`, không có `generate`."""

        async def embed(self, texts: list[str], model: str | None = None) -> list[list[float]]:
            return [[0.0] * 8 for _ in texts]

    bo_nhung: EmbeddingPort = BoNhungCucBo()

    class KhoVectorRong:
        async def search(self, *a: object, **kw: object) -> list[object]:
            return []

    # Điều phải chứng minh: dựng được retriever bằng một thứ CHỈ biết nhúng.
    r = HybridRetriever(vector_repo=KhoVectorRong(), embedder=bo_nhung)  # type: ignore[arg-type]
    assert r.embedder is bo_nhung
