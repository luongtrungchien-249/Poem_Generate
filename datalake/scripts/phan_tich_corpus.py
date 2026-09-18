"""Phân tích corpus final_data_7_chu.jsonl bằng chính bộ luật application/rule.py."""

import hashlib
import json
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

from application.rule import kiem_tra_bai_tho, tach_kho, tach_tieng  # noqa: E402

DUONG_DAN = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

# --- bộ đếm ---
tong = 0
loi_json = 0
khoa_cap_1 = Counter()
khoa_result = Counter()
status = Counter()
poem_type = Counter()
source_file = Counter()
score = Counter()
thieu_tho = 0
tho_rong = 0

bam_tho = Counter()
tieu_de = Counter()

dat = 0
khong_dat = 0
so_dong_hist = Counter()
so_kho_hist = Counter()
kich_thuoc_kho = Counter()
so_tieng_hist = Counter()
ly_do_truot = Counter()
so_dong_hong_hist = Counter()

so_do_van = Counter()
phoi_khuon = Counter()
ty_le_khuon_hist = Counter()
nghi_duong_luat = 0
co_van_lech_thanh = 0
co_van_lung = 0

vi_du_truot = []
vi_du_sat_sao = []

with DUONG_DAN.open("r", encoding="utf-8") as fh:
    for dong in fh:
        dong = dong.strip()
        if not dong:
            continue
        tong += 1
        try:
            rec = json.loads(dong)
        except json.JSONDecodeError:
            loi_json += 1
            continue

        khoa_cap_1.update(rec.keys())
        status[rec.get("status")] += 1
        source_file[rec.get("source_file")] += 1
        tieu_de[(rec.get("original_title") or "").strip().lower()] += 1

        res = rec.get("result") or {}
        if isinstance(res, dict):
            khoa_result.update(res.keys())
            poem_type[res.get("poem_type")] += 1
            score[res.get("score")] += 1

        tho = (res.get("markdown_poem") if isinstance(res, dict) else None) or ""
        if not isinstance(tho, str) or not tho.strip():
            if not isinstance(tho, str) or tho == "":
                thieu_tho += 1
            else:
                tho_rong += 1
            continue

        bam_tho[hashlib.md5(" ".join(tho.split()).encode("utf-8")).hexdigest()] += 1

        v = kiem_tra_bai_tho(tho)
        so_dong_hist[v.so_dong] += 1
        so_kho_hist[v.so_kho] += 1
        for k in tach_kho(tho):
            kich_thuoc_kho[len(k)] += 1
        for bc in v.dong:
            so_tieng_hist[bc.so_tieng] += 1

        if v.dat:
            dat += 1
            so_do_van.update("".join(k) for k in v.so_do_van_theo_kho)
            phoi_khuon.update(v.phoi_khuon_theo_kho)
            ty_le_khuon_hist[round(v.ty_le_theo_khuon, 1)] += 1
            if v.nghi_duong_luat:
                nghi_duong_luat += 1
            if v.van_lech_thanh:
                co_van_lech_thanh += 1
            if v.van_lung:
                co_van_lung += 1
        else:
            khong_dat += 1
            ma = sorted({vp.ma for vp in v.vi_pham})
            ly_do_truot["+".join(ma)] += 1
            n_hong = len({vp.dong for vp in v.vi_pham if vp.dong is not None})
            so_dong_hong_hist[n_hong] += 1
            if n_hong == 1 and len(vi_du_sat_sao) < 8:
                vp = next(x for x in v.vi_pham if x.dong is not None)
                bc = v.dong[vp.dong - 1]
                vi_du_sat_sao.append(
                    (rec.get("id"), vp.dong, bc.so_tieng, bc.van_ban, tach_tieng(bc.van_ban))
                )
            elif len(vi_du_truot) < 6:
                vi_du_truot.append((rec.get("id"), v.so_dong, [vp.ma for vp in v.vi_pham][:3]))

R = []
A = R.append
A("=" * 78)
A(f"CORPUS: {DUONG_DAN.name}   |   {tong:,} bản ghi   |   {DUONG_DAN.stat().st_size/1e6:.1f} MB")
A("=" * 78)

A("")
A("--- 1. CẤU TRÚC BẢN GHI ---")
A(f"  JSON hỏng            : {loi_json}")
A(f"  khoá cấp 1           : {dict(khoa_cap_1)}")
A(f"  khoá trong result    : {dict(khoa_result)}")
A(f"  status               : {dict(status)}")
A(f"  poem_type            : {dict(poem_type.most_common(10))}")
A(f"  source_file          : {dict(source_file.most_common(10))}")
A(f"  score                : {dict(sorted(score.items(), key=lambda x: (x[0] is None, x[0])))}")
A(f"  thiếu markdown_poem  : {thieu_tho}")
A(f"  markdown_poem rỗng   : {tho_rong}")

A("")
A("--- 2. TRÙNG LẶP ---")
trung = [(h, c) for h, c in bam_tho.items() if c > 1]
A(f"  bài duy nhất         : {len(bam_tho):,}")
A(f"  bài bị trùng nội dung: {sum(c for _, c in trung) - len(trung):,} bản dư ({len(trung):,} nhóm)")
tt = [(t, c) for t, c in tieu_de.items() if c > 1 and t]
A(f"  tiêu đề trùng        : {sum(c for _, c in tt) - len(tt):,} bản dư ({len(tt):,} nhóm)")
A(f"  top tiêu đề trùng    : {tieu_de.most_common(5)}")

tong_tho = dat + khong_dat
A("")
A("--- 3. TUÂN THỦ LUẬT THẤT NGÔN TỰ DO (H1–H3) ---")
A(f"  số bài đã kiểm       : {tong_tho:,}")
A(f"  ĐẠT                  : {dat:,}  ({dat/tong_tho*100:.2f}%)")
A(f"  TRƯỢT                : {khong_dat:,}  ({khong_dat/tong_tho*100:.2f}%)")
A(f"  lý do trượt          : {dict(ly_do_truot.most_common())}")
A(f"  số dòng hỏng mỗi bài : {dict(sorted(so_dong_hong_hist.items())[:10])}")

A("")
A("--- 4. PHÂN BỐ SỐ TIẾNG TRÊN TỪNG DÒNG ---")
tong_dong = sum(so_tieng_hist.values())
for n, c in sorted(so_tieng_hist.items()):
    if c / tong_dong > 0.0001 or n <= 12:
        A(f"  {n:>3} tiếng : {c:>9,}  ({c/tong_dong*100:6.3f}%)")

A("")
A("--- 5. HÌNH THỨC BÀI ---")
A(f"  số dòng/bài (top)    : {dict(so_dong_hist.most_common(12))}")
A(f"  số khổ/bài (top)     : {dict(so_kho_hist.most_common(8))}")
A(f"  kích thước khổ (top) : {dict(kich_thuoc_kho.most_common(8))}")

A("")
A("--- 6. VẦN, KHUÔN (chỉ tính trên bài ĐẠT) ---")
A(f"  sơ đồ vần phổ biến   : {dict(so_do_van.most_common(12))}")
A(f"  phối khuôn khổ §4.3  : {dict(phoi_khuon.most_common())}")
A(f"  tỷ lệ dòng theo khuôn: {dict(sorted(ty_le_khuon_hist.items()))}")
A(f"  nghi là Đường luật   : {nghi_duong_luat:,} ({nghi_duong_luat/max(dat,1)*100:.2f}% số bài đạt)")
A(f"  có vần lệch thanh    : {co_van_lech_thanh:,} ({co_van_lech_thanh/max(dat,1)*100:.2f}%)")
A(f"  có vần lưng (S7)     : {co_van_lung:,} ({co_van_lung/max(dat,1)*100:.2f}%)")

A("")
A("--- 7. VÍ DỤ BÀI TRƯỢT CHỈ VÌ MỘT DÒNG ---")
for _id, dong, n, van_ban, tieng in vi_du_sat_sao:
    A(f"  id={_id} D{dong} ({n} tiếng): {van_ban}")
    A(f"      tách: {tieng}")

A("")
A("--- 8. VÍ DỤ BÀI TRƯỢT NHIỀU DÒNG ---")
for _id, sd, ma in vi_du_truot:
    A(f"  id={_id}  {sd} dòng  mã: {ma}")

(RA_BC / "bao_cao.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
