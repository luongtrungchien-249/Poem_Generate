"""Soi sâu các điểm nghi vấn của corpus."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

# ── Đường dẫn suy từ vị trí tệp, không đặt cứng: script chạy được ở máy khác.
GOC = Path(__file__).resolve().parents[2]
RA_BC = GOC / "datalake/analysis/reports"
RA_BC.mkdir(parents=True, exist_ok=True)

# Console Windows mặc định cp1252, không in được tiếng Việt có dấu.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(GOC / "src"))
from application.rule import kiem_tra_bai_tho, tach_tieng  # noqa: E402

DUONG_DAN = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

kieu_tho_thieu = Counter()
vi_du_thieu = []
dong_8 = []
dong_6 = []
dong_0 = []
co_chu_so = []
co_latin = []
score_vs_dat = Counter()
kho4_hoan_hao = 0
tong_dat = 0
dong_co_gach_ngang = 0
dong_co_dau_ba_cham = 0

LATIN = re.compile(r"[a-zA-Z]{3,}")

with DUONG_DAN.open("r", encoding="utf-8") as fh:
    for dong in fh:
        dong = dong.strip()
        if not dong:
            continue
        rec = json.loads(dong)
        res = rec.get("result") or {}
        tho = res.get("markdown_poem") if isinstance(res, dict) else None

        if not isinstance(tho, str) or not tho.strip():
            kieu_tho_thieu[type(tho).__name__] += 1
            if len(vi_du_thieu) < 5:
                vi_du_thieu.append((rec.get("id"), repr(tho)[:160], sorted(res.keys())[:8]))
            continue

        v = kiem_tra_bai_tho(tho)
        sc = res.get("score")
        score_vs_dat[(sc, v.dat)] += 1

        if v.dat:
            tong_dat += 1
            if v.so_dong % 4 == 0 and all(len(k) == 4 for k in __import__("application.rule", fromlist=["x"]).tach_kho(tho)):
                kho4_hoan_hao += 1

        for bc in v.dong:
            if "—" in bc.van_ban or "–" in bc.van_ban:
                dong_co_gach_ngang += 1
            if "…" in bc.van_ban or "..." in bc.van_ban:
                dong_co_dau_ba_cham += 1
            if re.search(r"\d", bc.van_ban) and len(co_chu_so) < 12:
                co_chu_so.append((bc.so_tieng, bc.van_ban))
            if LATIN.search(bc.van_ban) and len(co_latin) < 12:
                co_latin.append((bc.so_tieng, bc.van_ban))
            if bc.so_tieng == 8 and len(dong_8) < 25:
                dong_8.append((bc.van_ban, tach_tieng(bc.van_ban)))
            elif bc.so_tieng == 6 and len(dong_6) < 20:
                dong_6.append((bc.van_ban, tach_tieng(bc.van_ban)))
            elif bc.so_tieng == 0 and len(dong_0) < 12:
                dong_0.append(repr(bc.van_ban))

R = []
A = R.append
A("--- A. 5.116 BẢN GHI KHÔNG CÓ THƠ: giá trị kiểu gì? ---")
A(f"  {dict(kieu_tho_thieu)}")
for _id, val, keys in vi_du_thieu:
    A(f"  id={_id} markdown_poem={val}")
    A(f"       khoá khác trong result: {keys}")

A("")
A("--- B. DÒNG 8 TIẾNG: dữ liệu sai hay bộ đếm sai? ---")
for vb, t in dong_8[:20]:
    A(f"  ({len(t)}) {vb}")
    A(f"       {t}")

A("")
A("--- C. DÒNG 6 TIẾNG ---")
for vb, t in dong_6[:12]:
    A(f"  ({len(t)}) {vb}")

A("")
A("--- D. DÒNG 0 TIẾNG ---")
for x in dong_0:
    A(f"  {x}")

A("")
A("--- E. DÒNG CÓ CHỮ SỐ ---")
for n, vb in co_chu_so:
    A(f"  ({n}) {vb}")

A("")
A("--- F. DÒNG CÓ CHỮ LATIN ---")
for n, vb in co_latin:
    A(f"  ({n}) {vb}")

A("")
A("--- G. DẤU CÂU ĐẶC BIỆT ---")
A(f"  dòng chứa gạch ngang dài/ngắn : {dong_co_gach_ngang:,}")
A(f"  dòng chứa dấu ba chấm         : {dong_co_dau_ba_cham:,}")

A("")
A("--- H. ĐIỂM SỐ vs TUÂN THỦ LUẬT ---")
theo_score = {}
for (sc, ok), c in score_vs_dat.items():
    d = theo_score.setdefault(sc, [0, 0])
    d[0 if ok else 1] += c
for sc in sorted(theo_score, key=lambda x: (x is None, x)):
    dat_, truot = theo_score[sc]
    tong = dat_ + truot
    A(f"  score={str(sc):>4} : {tong:>7,} bài | đạt {dat_/tong*100:6.2f}%")

A("")
A("--- I. BÀI CHIA KHỔ 4 DÒNG HOÀN TOÀN VÀ ĐẠT LUẬT ---")
A(f"  {kho4_hoan_hao:,} / {tong_dat:,} bài đạt ({kho4_hoan_hao/max(tong_dat,1)*100:.1f}%)")

(RA_BC / "bao_cao2.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
