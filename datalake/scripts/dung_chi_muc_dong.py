"""DỰNG CHỈ MỤC DÒNG THƠ — Plan_PoeTone GĐ1.3.

    python datalake/scripts/dung_chi_muc_dong.py

Đọc mọi nguồn trong `nguon_jsonl_mac_dinh` (tệp nào thiếu thì bỏ qua), ghi
`datalake/hf/chi_muc_dong.{bin,json}`. Chạy lại mỗi khi kho HF hay `bai_dat.jsonl`
đổi. Mất vài phút — đó là lý do nó chạy offline chứ không chạy lúc khởi động API.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from adapters.persistence.corpus.chi_muc_dong import (  # noqa: E402
    ChiMucDongTho,
    nguon_jsonl_mac_dinh,
    tep_dung_san_mac_dinh,
)


def main() -> int:
    t0 = time.monotonic()
    nguon = nguon_jsonl_mac_dinh(GOC)
    for tep, kho, _ in nguon:
        print(f"  {'✓' if tep.exists() else '·'} {kho:8} {tep.relative_to(GOC)}")
    cm = ChiMucDongTho.tu_jsonl(nguon)
    n = cm.so_dong
    ra = tep_dung_san_mac_dinh(GOC)
    cm.luu(ra)
    print(f"{n:,} dòng 7 tiếng -> {ra.relative_to(GOC)} ({time.monotonic() - t0:.0f} s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
