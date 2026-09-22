"""ĐỐI CHIẾU — cho 24.366 bài ĐẠT của `rule.py` chạy qua `compare_rule.py`.

CÂU HỎI: bài đã qua bảy tầng thất ngôn tự do thì bộ luật cổ điển chấm thế nào?

════ ĐỌC TRƯỚC KHI TIN SỐ ════

`compare_rule.py` giữ NGUYÊN VĂN logic luật của bản gốc (git HEAD); lượt sửa
22/09/2026 chỉ BÙ PHẦN LÕI còn thiếu (hai module `.constants`, `.rhyme` chưa bao
giờ tồn tại). Mọi khiếm khuyết thiết kế của bộ luật cũ VẪN CÒN — đó là chủ ý, hồ
sơ đối chiếu phải phản ánh đúng bộ luật thế hệ trước.

Tầng ngữ âm ở §0 của file ấy là cài đặt ĐỘC LẬP, không dùng chung với `rule.py`:
một ý kiến thứ hai phải độc lập, không thì chỉ là `rule.py` soi gương.

Nhưng độc lập thì chênh lệch có thể đến từ hai nguồn: khác LUẬT, hay khác cách
đọc ÂM TIẾT. §3 của script ĐO mức đồng thuận của hai tầng ngữ âm (đếm tiếng,
phân thanh, so vần) để tách hai nguồn ấy ra. Không đo thì mọi con số ở §4 đều
không diễn giải được.

`rule.py` KHÔNG BỊ ĐỘNG TỚI. Script chỉ đọc nó để so, không import ngược lại.

CHẠY
    python datalake/scripts/chay_doi_chieu_rule2.py
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))
sys.path.insert(0, str(GOC))

import compare_rule as r2  # noqa: E402
from application import rule as r1  # noqa: E402

NGUON = GOC / "datalake/analysis/bai_dat.jsonl"
RA_DAT = GOC / "datalake/analysis/bai_dat_rule2.jsonl"
RA_TRUOT = GOC / "datalake/analysis/bai_truot_rule2.jsonl"
RA_TT = GOC / "datalake/analysis/tong_hop_rule2.json"


# ══════════════════════════════════════════════════════════════════════════════
# §3. ĐỒNG THUẬN CỦA HAI TẦNG NGỮ ÂM
# ══════════════════════════════════════════════════════════════════════════════


def do_dong_thuan(mau_dong: list[str], mau_cap: list[tuple[str, str]]) -> dict:
    tach_khop = sum(
        1 for d in mau_dong if list(r1.tach_tieng(d)) == r2.clean_and_tokenize(d)
    )
    tieng = [t for d in mau_dong for t in r1.tach_tieng(d)]
    thanh_khop = sum(
        1 for t in tieng
        if (r1.thanh_cua(t) == "B") == (r2.get_tone(t) == "Bằng")
    )
    van_khop = sum(
        1 for a, b in mau_cap if r1.hiep_van(a, b).hiep == r2.is_rhyme_match(a, b)
    )
    return {
        "mau_dong": len(mau_dong),
        "tach_tieng_khop": tach_khop,
        "tach_tieng_ty_le": round(tach_khop / max(len(mau_dong), 1) * 100, 2),
        "mau_tieng": len(tieng),
        "phan_thanh_khop": thanh_khop,
        "phan_thanh_ty_le": round(thanh_khop / max(len(tieng), 1) * 100, 2),
        "mau_cap_van": len(mau_cap),
        "so_van_khop": van_khop,
        "so_van_ty_le": round(van_khop / max(len(mau_cap), 1) * 100, 2),
    }


# ══════════════════════════════════════════════════════════════════════════════
# §4. CHẠY
# ══════════════════════════════════════════════════════════════════════════════


def _nhom(e: str) -> str:
    for k in ("Sai Vần", "Lỗi Gieo Vần", "Vi phạm Bằng/Trắc", "Vi phạm Tiểu Đối",
              "Sai số tiếng", "Sai số dòng", "Bỏ kiểm"):
        if k in e:
            return k
    return e[:44]


def main() -> int:
    rng = random.Random(20260922)
    n = dat = truot = 0
    dat_modern = 0
    ly_do = Counter()
    so_loi = Counter()
    cach_doc = Counter()
    cach_doc_dat = Counter()
    theo_dong_dat = Counter()
    theo_dong_truot = Counter()
    vd_dat: list[dict] = []
    vd_truot: list[dict] = []
    mau_dong: list[str] = []
    mau_cap: list[tuple[str, str]] = []

    with (
        NGUON.open(encoding="utf-8") as f,
        RA_DAT.open("w", encoding="utf-8") as fd,
        RA_TRUOT.open("w", encoding="utf-8") as ft,
    ):
        for line in f:
            rec = json.loads(line)
            tho = rec["tho"]
            n += 1

            ok, loi, tc = r2.bay_chu_rule_check(tho)
            _sd = len([x for x in tho.splitlines() if x.strip()])
            cach = f"{_sd} dòng → {_sd // 4} khổ tứ tuyệt" if _sd % 4 == 0 else f"{_sd} dòng → KHÔNG chia hết cho 4"
            ok_m, loi_m, _ = r2.bay_chu_modern_rule_check(tho)
            nang, nhe = r2.evaluate_errors(loi, poem_type="bay_chu")
            sd = rec["bang_chung"]["so_dong"]

            cach_doc[cach] += 1
            so_loi[min(len(loi), 20)] += 1
            if ok_m:
                dat_modern += 1

            if len(mau_dong) < 4000:
                for d in tho.splitlines():
                    if d.strip() and len(mau_dong) < 4000 and rng.random() < 0.05:
                        mau_dong.append(d.strip())
            if len(mau_cap) < 4000 and rng.random() < 0.3:
                cuoi = [w[-1] for w in
                        (r2.clean_and_tokenize(d) for d in tho.splitlines() if d.strip()) if w]
                if len(cuoi) >= 2:
                    mau_cap.append((rng.choice(cuoi), rng.choice(cuoi)))

            ban = {
                "id": rec["id"],
                "tieu_de": rec.get("tieu_de"),
                "tho": tho,
                "so_dong": sd,
                "rule1_dat": True,
                "rule2_dat": ok,
                "rule2_cach_doc": cach,
                "rule2_modern_dat": ok_m,
                "rule2_so_loi": len(loi),
                "rule2_loi_nang": nang,
                "rule2_loi_nhe": nhe,
                "rule2_loi": loi,
                "rule2_dat_chuan": tc,
                "rule2_modern_loi": loi_m,
            }

            if ok:
                dat += 1
                theo_dong_dat[sd] += 1
                cach_doc_dat[cach] += 1
                fd.write(json.dumps(ban, ensure_ascii=False) + "\n")
                if len(vd_dat) < 8 and sd in (4, 8):
                    vd_dat.append(ban)
            else:
                truot += 1
                theo_dong_truot[sd] += 1
                for e in loi:
                    ly_do[_nhom(e)] += 1
                ft.write(json.dumps(ban, ensure_ascii=False) + "\n")
                if len(vd_truot) < 8 and sd in (4, 8):
                    vd_truot.append(ban)

    dong_thuan = do_dong_thuan(mau_dong, mau_cap)
    tt = {
        "tong": n,
        "rule2_dat": dat,
        "rule2_truot": truot,
        "ty_le_dat": round(dat / n * 100, 2) if n else 0.0,
        "ty_le_truot": round(truot / n * 100, 2) if n else 0.0,
        "rule2_modern_dat": dat_modern,
        "rule2_modern_ty_le": round(dat_modern / n * 100, 2) if n else 0.0,
        "dong_thuan_ngu_am": dong_thuan,
        "cach_doc": dict(cach_doc.most_common()),
        "cach_doc_dat": dict(cach_doc_dat.most_common()),
        "ly_do_truot": dict(ly_do.most_common()),
        "phan_bo_so_loi": {str(k): v for k, v in sorted(so_loi.items())},
        "theo_so_dong": {
            str(k): {"dat": theo_dong_dat.get(k, 0), "truot": theo_dong_truot.get(k, 0)}
            for k in sorted(set(theo_dong_dat) | set(theo_dong_truot))
        },
    }
    RA_TT.write_text(
        json.dumps({"thong_ke": tt, "vi_du_dat": vd_dat, "vi_du_truot": vd_truot},
                   ensure_ascii=False, indent=1), encoding="utf-8")

    print("=" * 68)
    print("  ĐỐI CHIẾU — bài ĐẠT của rule.py chạy qua compare_rule.py (bản 22/09)")
    print("=" * 68)
    print(f"  Đầu vào                        : {n:,}")
    print()
    print("  §3 ĐỒNG THUẬN NGỮ ÂM (hai cài đặt độc lập)")
    print(f"    tách tiếng  : {dong_thuan['tach_tieng_khop']:,}/{dong_thuan['mau_dong']:,}"
          f"  = {dong_thuan['tach_tieng_ty_le']}%")
    print(f"    phân thanh  : {dong_thuan['phan_thanh_khop']:,}/{dong_thuan['mau_tieng']:,}"
          f"  = {dong_thuan['phan_thanh_ty_le']}%")
    print(f"    so vần      : {dong_thuan['so_van_khop']:,}/{dong_thuan['mau_cap_van']:,}"
          f"  = {dong_thuan['so_van_ty_le']}%")
    print()
    print("  §4 PHÁN QUYẾT")
    print(f"    bay_chu_rule_check    ĐẠT    : {dat:,}  ({tt['ty_le_dat']}%)")
    print(f"    bay_chu_rule_check    TRƯỢT  : {truot:,}  ({tt['ty_le_truot']}%)")
    print(f"    bay_chu_modern        ĐẠT    : {dat_modern:,}  ({tt['rule2_modern_ty_le']}%)")
    print()
    print("  Cách đọc được chọn:")
    for k, v in cach_doc.most_common(6):
        print(f"    {v:>8,}  {k}   (đạt {cach_doc_dat.get(k, 0):,})")
    print()
    print("  Lý do trượt (lượt lỗi):")
    for k, v in ly_do.most_common(8):
        print(f"    {v:>8,}  {k}")
    print()
    print("  Theo số dòng:")
    for k in sorted(set(theo_dong_dat) | set(theo_dong_truot))[:8]:
        d, t = theo_dong_dat.get(k, 0), theo_dong_truot.get(k, 0)
        print(f"    {k:>4} dòng : đạt {d:>6,} | trượt {t:>6,} | {d/max(d+t,1)*100:5.1f}%")
    print()
    print(f"  Đã ghi: {RA_DAT.name}, {RA_TRUOT.name}, {RA_TT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
