"""ĐỐI CHIẾU RULE3 — 24.366 bài ĐẠT của `rule.py` chạy qua `compare_rule.py` BẢN NỚI.

CÂU HỎI: sau khi nới luật Bằng/Trắc thất ngôn (chỉ câu đầu mỗi khổ phải giữ nhịp
2/4/6, xem §1.1 đầu `compare_rule.py`), tỉ lệ đạt đổi bao nhiêu — và phần trượt
còn lại nằm ở đâu?

════ ĐỌC TRƯỚC KHI TIN SỐ ════

Script này chạy CÙNG một corpus, CÙNG một hàm (`bay_chu_rule_check`) như
`chay_doi_chieu_rule2.py`. Khác biệt duy nhất là bản `compare_rule.py` đã nới luật.
Vì thế chênh lệch rule2 → rule3 quy được về ĐÚNG một nguyên nhân, không lẫn.

Số nền rule2 (đọc từ `tong_hop_rule2.json` nếu có): 3.146 đạt / 12,91%.

Mọi khiếm khuyết KHÁC của bộ luật cũ VẪN CÒN: bắt buộc câu 1 gieo vần, vần thông
dùng bắc cầu ở phép so 1↔2↔4, cắt bài dài thành từng khổ tứ tuyệt độc lập. Đó là
chủ ý — hồ sơ đối chiếu phải phản ánh bộ luật thật, không phải bản sửa hộ.

`rule.py` KHÔNG BỊ ĐỘNG TỚI.

CHẠY
    python datalake/scripts/chay_doi_chieu_rule3.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC))

import compare_rule as r  # noqa: E402

NGUON = GOC / "datalake/analysis/bai_dat.jsonl"
RA_DAT = GOC / "datalake/analysis/bai_dat_rule3.jsonl"
RA_TRUOT = GOC / "datalake/analysis/bai_truot_rule3.jsonl"
RA_TT = GOC / "datalake/analysis/tong_hop_rule3.json"
NEN_RULE2 = GOC / "datalake/analysis/tong_hop_rule2.json"


# ══════════════════════════════════════════════════════════════════════════════
# §1. BẰNG CHỨNG — dựng lại bằng CHÍNH tầng ngữ âm của bộ kiểm
#
# Cố ý KHÔNG đọc các trường `thanh`, `van_cuoi` có sẵn trong corpus: chúng do
# `rule.py` tính. Muốn giải thích vì sao `compare_rule.py` phán đạt hay trượt thì
# bằng chứng phải lấy từ tầng ngữ âm của chính nó.
# ══════════════════════════════════════════════════════════════════════════════


def bang_chung_dong(so: int, van_ban: str) -> dict:
    tieng = r.clean_and_tokenize(van_ban)
    thanh = [r.get_tone(t) for t in tieng]
    ra = {
        "so": so,
        "van_ban": van_ban,
        "so_tieng": len(tieng),
        "tieng": tieng,
        "thanh": ["B" if t == "Bằng" else "T" for t in thanh],
    }
    if len(tieng) >= 6:
        ra["vi_tri_2_4_6"] = [
            {"vi_tri": v, "tieng": tieng[v - 1], "thanh": thanh[v - 1]} for v in (2, 4, 6)
        ]
        ra["khuon_2_4_6"] = "-".join("B" if thanh[v - 1] == "Bằng" else "T" for v in (2, 4, 6))
    if tieng:
        ra["tieng_cuoi"] = tieng[-1]
        ra["van_cuoi"] = r.van_cua(tieng[-1])
        ra["thanh_cuoi"] = "B" if thanh[-1] == "Bằng" else "T"
    return ra


def bang_chung_bai(tho: str) -> dict:
    dong = [d.strip() for d in tho.splitlines() if d.strip()]
    bc = [bang_chung_dong(i + 1, d) for i, d in enumerate(dong)]

    # Ma trận hiệp vần đúng như hàm kiểm nhìn: trong mỗi khổ, so 1↔2 và 2↔4.
    cap_van = []
    for i in range(0, len(bc) - 3, 4):
        k = i // 4 + 1
        c = [bc[i + j] for j in range(4)]
        if all(x["so_tieng"] >= 7 for x in c):
            w1, w2, w4 = c[0]["tieng"][6], c[1]["tieng"][6], c[3]["tieng"][6]
            for nhan, a, b in (
                (f"Khổ {k}: dòng {i+1} ↔ dòng {i+2}", w1, w2),
                (f"Khổ {k}: dòng {i+2} ↔ dòng {i+4}", w2, w4),
            ):
                cap_van.append({
                    "cap": nhan,
                    "tieng": [a, b],
                    "van": [r.van_cua(a), r.van_cua(b)],
                    "hiep": r.is_rhyme_match(a, b, poem_type="bay_chu"),
                    "thanh": [
                        "B" if r.get_tone(a) == "Bằng" else "T",
                        "B" if r.get_tone(b) == "Bằng" else "T",
                    ],
                })
    return {"dong": bc, "cap_van_bo_kiem_nhin": cap_van}


# ══════════════════════════════════════════════════════════════════════════════
# §2. PHÂN LOẠI LÝ DO TRƯỢT
# ══════════════════════════════════════════════════════════════════════════════

_NHOM = (
    ("Sai Vần", "Sai Vần"),
    ("Lỗi Gieo Vần", "Lỗi Gieo Vần (thanh cuối không Bằng)"),
    ("Vi phạm Bằng/Trắc", "Vi phạm Bằng/Trắc câu đầu khổ"),
    ("Sai số tiếng", "Sai số tiếng"),
    ("Sai số dòng", "Sai số dòng"),
)


def nhom_loi(e: str) -> str:
    for khoa, ten in _NHOM:
        if khoa in e:
            return ten
    return e[:44]


# ══════════════════════════════════════════════════════════════════════════════
# §3. CHẠY
# ══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    n = dat = truot = 0
    ly_do = Counter()             # đếm theo LƯỢT lỗi
    ly_do_bai = Counter()         # đếm theo BÀI (một bài chỉ tính 1 lần mỗi nhóm)
    so_loi = Counter()
    theo_dong_dat = Counter()
    theo_dong_truot = Counter()
    vd_dat: list[dict] = []
    vd_truot: list[dict] = []
    truot_ly_do_da_lay: set[str] = set()
    dat_so_dong_da_lay: set[int] = set()

    with (
        NGUON.open(encoding="utf-8") as f,
        RA_DAT.open("w", encoding="utf-8") as fd,
        RA_TRUOT.open("w", encoding="utf-8") as ft,
    ):
        for line in f:
            rec = json.loads(line)
            tho = rec["tho"]
            n += 1

            ok, loi, tc = r.bay_chu_rule_check(tho)
            nang, nhe = r.evaluate_errors(loi, poem_type="bay_chu")
            sd = len([x for x in tho.splitlines() if x.strip()])

            so_loi[min(len(loi), 20)] += 1

            ban = {
                "id": rec["id"],
                "tieu_de": rec.get("tieu_de"),
                "tho": tho,
                "so_dong": sd,
                "rule1_dat": True,
                "rule3_dat": ok,
                "rule3_so_loi": len(loi),
                "rule3_loi_nang": nang,
                "rule3_loi_nhe": nhe,
                "rule3_loi": loi,
                "rule3_dat_chuan": tc,
            }

            if ok:
                dat += 1
                theo_dong_dat[sd] += 1
                fd.write(json.dumps(ban, ensure_ascii=False) + "\n")
                # Ví dụ ĐẠT: lấy mỗi độ dài một bài, ưu tiên bài ngắn cho dễ đọc.
                if len(vd_dat) < 3 and sd in (4, 8, 16) and sd not in dat_so_dong_da_lay:
                    dat_so_dong_da_lay.add(sd)
                    vd_dat.append({**ban, "bang_chung": bang_chung_bai(tho)})
            else:
                truot += 1
                theo_dong_truot[sd] += 1
                nhom_cua_bai = {nhom_loi(e) for e in loi}
                for e in loi:
                    ly_do[nhom_loi(e)] += 1
                for g in nhom_cua_bai:
                    ly_do_bai[g] += 1
                ft.write(json.dumps(ban, ensure_ascii=False) + "\n")
                # Ví dụ TRƯỢT: mỗi nhóm lý do lấy một bài, để 3 ví dụ khác hẳn nhau.
                if len(vd_truot) < 3 and sd in (4, 8) and len(loi) <= 2:
                    khoa = "|".join(sorted(nhom_cua_bai))
                    if khoa not in truot_ly_do_da_lay:
                        truot_ly_do_da_lay.add(khoa)
                        vd_truot.append({**ban, "bang_chung": bang_chung_bai(tho)})

    nen = {}
    if NEN_RULE2.exists():
        t2 = json.loads(NEN_RULE2.read_text(encoding="utf-8"))["thong_ke"]
        nen = {
            "rule2_dat": t2["rule2_dat"],
            "rule2_truot": t2["rule2_truot"],
            "rule2_ty_le_dat": t2["ty_le_dat"],
            "rule2_ly_do_truot": t2["ly_do_truot"],
        }

    tt = {
        "tong": n,
        "rule3_dat": dat,
        "rule3_truot": truot,
        "ty_le_dat": round(dat / n * 100, 2) if n else 0.0,
        "ty_le_truot": round(truot / n * 100, 2) if n else 0.0,
        "nen_rule2": nen,
        "ly_do_truot_theo_luot": dict(ly_do.most_common()),
        "ly_do_truot_theo_bai": dict(ly_do_bai.most_common()),
        "phan_bo_so_loi": {str(k): v for k, v in sorted(so_loi.items())},
        "theo_so_dong": {
            str(k): {
                "dat": theo_dong_dat.get(k, 0),
                "truot": theo_dong_truot.get(k, 0),
                "ty_le_dat": round(
                    theo_dong_dat.get(k, 0)
                    / (theo_dong_dat.get(k, 0) + theo_dong_truot.get(k, 0)) * 100, 2
                ),
            }
            for k in sorted(set(theo_dong_dat) | set(theo_dong_truot))
        },
    }
    RA_TT.write_text(
        json.dumps({"thong_ke": tt, "vi_du_dat": vd_dat, "vi_du_truot": vd_truot},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 70)
    print("  ĐỐI CHIẾU RULE3 — corpus ĐẠT của rule.py qua compare_rule.py BẢN NỚI")
    print("=" * 70)
    print(f"  Đầu vào                   : {n:,}")
    print(f"  ĐẠT                       : {dat:,}  ({tt['ty_le_dat']}%)")
    print(f"  TRƯỢT                     : {truot:,}  ({tt['ty_le_truot']}%)")
    if nen:
        print()
        print(f"  Nền rule2 (trước khi nới) : {nen['rule2_dat']:,}  ({nen['rule2_ty_le_dat']}%)")
        print(f"  Chênh lệch                : {dat - nen['rule2_dat']:+,} bài "
              f"({tt['ty_le_dat'] - nen['rule2_ty_le_dat']:+.2f} điểm %)")
    print()
    print("  LÝ DO TRƯỢT (số BÀI dính, một bài có thể dính nhiều nhóm)")
    for k, v in ly_do_bai.most_common():
        print(f"    {k:42} {v:>7,}  = {v / max(truot,1)*100:5.2f}% số bài trượt")
    print()
    print(f"  Ghi ra: {RA_DAT.name}, {RA_TRUOT.name}, {RA_TT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
