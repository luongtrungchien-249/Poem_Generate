"""SCRIPT CHẤM CHUNG — Plan_PoeTone GĐ0.3.

    python evals/cham_diem.py <vao.jsonl> [--ra <ra.jsonl>] [--truong-tho poem]

Đọc một JSONL bài thơ, thêm cột điểm vào từng bản ghi, in bảng tổng hợp theo độ dài
bài. Cột được bổ sung dần qua các giai đoạn sau (GĐ1: điểm liên tục, chép, Reviewer;
GĐ4: bám đề) — mỗi cột mới là một hàm `_cot_*` thêm vào `COT`.

════ KHÔNG VIẾT BỘ ĐẾM THỨ HAI ════

Luật do `rule.kiem_tra_bai_tho` phán, chất lượng do `quality.danh_gia_chat_luong`
phán, tổng hợp do `evals.metrics.poetry.do_luong_tho`. File này chỉ gọi, không tính
lại gì. Đơn vị phán quyết là BÀI (docstring `DoLuongTho`).

Bài rỗng hoặc thiếu trường thơ vẫn nằm trong mẫu số — loại chúng ra là làm đẹp số.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Callable
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "src"))
sys.path.insert(0, str(GOC))

from evals.metrics.poetry import do_luong_tho  # noqa: E402

from application.poetry.quality import danh_gia_chat_luong  # noqa: E402
from application.rule import PoemVerdict, kiem_tra_bai_tho  # noqa: E402

# Tên trường thơ hay gặp trong các tệp của repo, thử theo thứ tự.
TRUONG_THO_MAC_DINH = ("bai_tho", "poem", "tho", "content")


def _lay_tho(rec: dict, truong: str | None) -> str:
    if truong:
        return str(rec.get(truong) or "")
    for t in TRUONG_THO_MAC_DINH:
        if rec.get(t):
            return str(rec[t])
    return ""


def _chu_de(rec: dict) -> str | None:
    for t in ("chu_de", "topic"):
        if rec.get(t):
            return str(rec[t])
    return None


def _cot_luat(tho: str, v: PoemVerdict, rec: dict) -> dict[str, object]:  # noqa: ARG001
    return {
        "dat_luat": v.dat,
        "thuoc_the": v.thuoc_the,
        "tang_dung_lai": v.tang_dung_lai,
        "so_dong": v.so_dong,
    }


def _cot_chat_luong(tho: str, v: PoemVerdict, rec: dict) -> dict[str, object]:  # noqa: ARG001
    kq = danh_gia_chat_luong(v, chu_de=_chu_de(rec))
    return {"dat_chat_luong": kq.dat, "chieu_hong": [c.ma for c in kq.chieu_hong]}


COT: tuple[Callable[[str, PoemVerdict, dict], dict[str, object]], ...] = (
    _cot_luat,
    _cot_chat_luong,
)


def cham(rec: dict, truong: str | None = None) -> dict:
    tho = _lay_tho(rec, truong)
    v = kiem_tra_bai_tho(tho)
    ra = dict(rec)
    for cot in COT:
        ra.update(cot(tho, v, rec))
    return ra


def _in_bang(cac_bai: list[str], nhom: list[int]) -> None:
    theo: dict[int, list[str]] = {}
    for bai, n in zip(cac_bai, nhom, strict=True):
        theo.setdefault(n, []).append(bai)
    print(f"{'dòng':>5} {'số bài':>7} {'đạt':>7} {'thuộc thể':>10} {'đủ tiếng':>9} "
          f"{'khuôn':>7} {'vần':>7} {'chất lượng':>11}")
    for n, ds in sorted(theo.items()):
        m = do_luong_tho(ds)
        print(f"{n:>5} {m.so_bai:>7} {m.ty_le_dat:>7.1%} {m.ty_le_thuoc_the:>10.1%} "
              f"{m.ty_le_dung_so_tieng:>9.1%} {m.ty_le_dung_khuon:>7.1%} "
              f"{m.ty_le_co_van_chan:>7.1%} {m.ty_le_dat_chat_luong:>11.1%}")
    m = do_luong_tho(cac_bai)
    print(f"{'tổng':>5} {m.so_bai:>7} {m.ty_le_dat:>7.1%}  · chặn theo tầng {m.chan_theo_tang}")


def main() -> int:
    p = argparse.ArgumentParser(description="Chấm một JSONL bài thơ, thêm cột điểm.")
    p.add_argument("vao", type=Path)
    p.add_argument("--ra", type=Path, default=None, help="mặc định <vao>.cham.jsonl")
    p.add_argument("--truong-tho", default=None, help=f"mặc định thử {TRUONG_THO_MAC_DINH}")
    a = p.parse_args()

    ra = a.ra or a.vao.with_suffix(".cham.jsonl")
    cac_bai: list[str] = []
    nhom: list[int] = []
    hong = 0
    with a.vao.open(encoding="utf-8") as f, ra.open("w", encoding="utf-8") as g:
        for dong in f:
            if not dong.strip():
                continue
            try:
                rec = json.loads(dong)
            except json.JSONDecodeError:
                # Bản ghi hỏng vẫn vào mẫu số, như một bài rỗng.
                hong += 1
                rec = {}
            kq = cham(rec, a.truong_tho)
            g.write(json.dumps(kq, ensure_ascii=False) + "\n")
            cac_bai.append(_lay_tho(rec, a.truong_tho))
            nhom.append(int(rec.get("so_dong_yc") or rec.get("so_dong") or kq["so_dong"]))

    print(f"{len(cac_bai)} bản ghi ({hong} hỏng JSON) -> {ra}")
    _in_bang(cac_bai, nhom)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
