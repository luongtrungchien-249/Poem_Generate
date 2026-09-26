"""Plan_PoeTone GĐ0.1 — tập 200 đề là THƯỚC ĐO, nên nó phải đứng yên.

Đổi tập đề giữa hai lần đo là đổi mẫu số: chênh lệch đo được lẫn cả chênh lệch đề.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[3]
if str(GOC) not in sys.path:
    sys.path.insert(0, str(GOC))

from evals.dung_tap_de import DO_DAI, RA, SO_DE, dung_tap_de  # noqa: E402

pytestmark = pytest.mark.unit

TAP_MAU = GOC / "datalake" / "corpus_tuyen" / "tho_mau.jsonl"


def _doc() -> list[dict]:
    return [json.loads(d) for d in RA.read_text(encoding="utf-8").splitlines() if d.strip()]


def test_tep_da_commit_khop_voi_ham_dung():
    """Ai sửa nguồn chủ đề mà quên dựng lại tệp thì đỏ ở đây."""
    assert _doc() == dung_tap_de()


def test_du_200_de_chia_deu_nam_do_dai():
    de = _doc()
    assert len(de) == SO_DE
    assert Counter(d["so_dong"] for d in de) == {n: SO_DE // len(DO_DAI) for n in DO_DAI}
    assert len({d["chu_de"].lower() for d in de}) == SO_DE


def test_chu_de_danh_gia_khong_nam_trong_kho_vi_du():
    """Đề đánh giá không được trùng tiêu đề của bài nào trong kho ví dụ mẫu."""
    tieu_de = {
        json.loads(d).get("tieu_de", "").strip().lower()
        for d in TAP_MAU.read_text(encoding="utf-8").splitlines()
        if d.strip()
    }
    trung = [d["chu_de"] for d in _doc() if d["chu_de"].strip().lower() in tieu_de]
    assert not trung, f"đề đánh giá trùng kho ví dụ: {trung}"
