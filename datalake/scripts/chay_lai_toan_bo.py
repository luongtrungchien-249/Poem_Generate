"""Chạy lại TOÀN BỘ phép đo bằng rule.py hiện tại.

Nguyên tắc chi phối: ĐƠN VỊ PHÁN QUYẾT LÀ BÀI, KHÔNG PHẢI DÒNG.
Chỉ cần một dòng lệch khỏi 7 tiếng là cả bài rời khỏi thể (tài liệu luật §10).
Mọi thống kê mức dòng chỉ dùng để CHẨN ĐOÁN, không được dùng làm thước đo chất lượng.
"""

import hashlib
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
from application.rule import kiem_tra_bai_tho, tach_kho  # noqa: E402

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

NGOAI_BANG = re.compile(r"[fjwzFJWZ]")
CO_SO = re.compile(r"\d")
GACH_NOI = re.compile(r"\w-\w")
MO_KY_HIEU = re.compile(r"^\s*[(\[*\"'“]")
DE_TANG = re.compile(r"^\s*[*(\[]?\s*(gửi|tặng|kính tặng|thân tặng|viết cho|tiễn)\b", re.IGNORECASE)
CHU_KY = re.compile(r"^\s*[-–—]\s*\S")

KHOA_THO_KHAC = (
    "markdown_poem_content", "markdown_poem_fixed", "markdown_poem_final",
    "markdown_poem_full", "markdown_content", "poem_content", "content",
    "content_fix", "content_fixed", "content_processed", "content_correction",
    "content_details", "content_analysis",
)

# ── mức BÀI ──
tong_ban_ghi = rong = 0
bai_dat = bai_truot = 0
truot_theo_so_dong_hong = Counter()
nguyen_nhan_bai = Counter()
bai_theo_dau_hieu = Counter()          # mỗi bài đếm MỘT lần cho mỗi loại dấu hiệu
so_dong_bai_dat = Counter()
cau_truc_kho_dat = Counter()
so_do_van_ho = Counter()
khuon_dong = Counter()
phoi_khuon = Counter()
nghi_duong_luat = co_lech_thanh = co_van_lung = 0
bam = Counter()
score_dat = Counter()
score_truot = Counter()

# ── mức DÒNG (chỉ để chẩn đoán) ──
dong_tong = dong_dung = 0
do_dai_dong_hong = Counter()
dau_hieu_dong = Counter()
vi_tri_dong_hong = Counter()

# ── thiệt hại kéo theo ──
dong_trong_bai_truot = 0
dong_tot_trong_bai_truot = 0

# ── thu hồi ──
cuu_duoc = cuu_duoc_dat = 0
nguon_cuu = Counter()

with NGUON.open("r", encoding="utf-8") as fh:
    for dj in fh:
        dj = dj.strip()
        if not dj:
            continue
        tong_ban_ghi += 1
        rec = json.loads(dj)
        res = rec.get("result") or {}
        tho = res.get("markdown_poem") if isinstance(res, dict) else None
        sc = res.get("score")

        if not isinstance(tho, str) or not tho.strip():
            rong += 1
            for k in KHOA_THO_KHAC:
                gt = res.get(k)
                if isinstance(gt, str) and gt.strip() and "\n" in gt.strip():
                    cuu_duoc += 1
                    nguon_cuu[k] += 1
                    if kiem_tra_bai_tho(gt).dat:
                        cuu_duoc_dat += 1
                    break
            continue

        v = kiem_tra_bai_tho(tho)
        bam[hashlib.md5(" ".join(tho.split()).encode("utf-8")).hexdigest()] += 1
        dong_tong += v.so_dong
        dong_dung += sum(1 for bc in v.dong if bc.so_tieng == 7)

        if v.dat:
            bai_dat += 1
            score_dat[sc] += 1
            so_dong_bai_dat[v.so_dong] += 1
            cau_truc_kho_dat[tuple(sorted({len(k) for k in tach_kho(tho)}))] += 1
            khuon_dong.update(bc.khuon for bc in v.dong)
            phoi_khuon.update(v.phoi_khuon_theo_kho)
            for so_do in v.so_do_van_theo_kho:
                if len(so_do) == 4:
                    ax, ho = {}, ""
                    for nh in so_do:
                        if nh == "x":
                            ho += "x"
                        else:
                            ax.setdefault(nh, "abcd"[len(ax)])
                            ho += ax[nh]
                    so_do_van_ho[ho] += 1
            nghi_duong_luat += v.nghi_duong_luat
            co_lech_thanh += bool(v.van_lech_thanh)
            co_van_lung += bool(v.van_lung)
            continue

        # ===== BÀI TRƯỢT =====
        bai_truot += 1
        score_truot[sc] += 1
        hong = [bc for bc in v.dong if bc.so_tieng != 7]
        truot_theo_so_dong_hong[min(len(hong), 5)] += 1
        dong_trong_bai_truot += v.so_dong
        dong_tot_trong_bai_truot += v.so_dong - len(hong)

        do_dai = [bc.so_tieng for bc in v.dong]
        so_8 = sum(1 for n in do_dai if n == 8)
        if so_8 >= len(do_dai) * 0.8 and len(do_dai) >= 4:
            nguyen_nhan_bai["A. Thơ 8 chữ bị gán nhãn 7 chữ"] += 1
        elif any(n > 15 for n in do_dai):
            nguyen_nhan_bai["B. Lẫn văn xuôi trong trường thơ"] += 1
        elif any(n == 0 for n in do_dai):
            nguyen_nhan_bai["C. Có dòng phân cách không chứa tiếng"] += 1
        elif len(hong) == 1 and hong[0].so_tieng == 6:
            nguyen_nhan_bai["D. Đúng một dòng thiếu một tiếng"] += 1
        elif len(hong) == 1 and hong[0].so_tieng == 8:
            nguyen_nhan_bai["E. Đúng một dòng thừa một tiếng"] += 1
        elif len(hong) == 1:
            nguyen_nhan_bai["F. Đúng một dòng lệch nhiều tiếng"] += 1
        elif len(hong) <= 2:
            nguyen_nhan_bai["G. Hai dòng lệch"] += 1
        else:
            nguyen_nhan_bai["H. Lệch nhiều dòng"] += 1

        dh_cua_bai = set()
        n = v.so_dong
        for bc in hong:
            do_dai_dong_hong[bc.so_tieng] += 1
            vi_tri_dong_hong["dòng đầu" if bc.so == 1 else ("dòng cuối" if bc.so == n else "giữa bài")] += 1
            s = bc.van_ban
            dh = []
            if bc.so_tieng == 0:
                dh.append("dòng phân cách, không có tiếng")
            if bc.so_tieng > 15:
                dh.append("văn xuôi lẫn vào")
            if DE_TANG.match(s):
                dh.append("đề tặng / lời đề từ")
            if CHU_KY.match(s):
                dh.append("ký tên tác giả")
            if MO_KY_HIEU.match(s) and bc.so_tieng < 7:
                dh.append("phụ chú mở bằng ngoặc/dấu sao")
            if CO_SO.search(s):
                dh.append("có chữ số")
            if GACH_NOI.search(s):
                dh.append("tên phiên âm có gạch nối")
            if NGOAI_BANG.search(s):
                dh.append("chữ ngoài bảng chữ tiếng Việt")
            if not dh:
                dh.append("KHÔNG dấu hiệu bất thường — dòng thơ thật")
            dau_hieu_dong.update(dh)
            dh_cua_bai.update(dh)
        bai_theo_dau_hieu.update(dh_cua_bai)

tong_tho = bai_dat + bai_truot
R = []
A = R.append
A("=" * 74)
A("CHẠY LẠI TOÀN BỘ — ĐƠN VỊ PHÁN QUYẾT LÀ BÀI")
A("=" * 74)
A(f"  bản ghi                    : {tong_ban_ghi:,}")
A(f"  markdown_poem rỗng         : {rong:,}")
A(f"  bài đem kiểm               : {tong_tho:,}")
A(f"  BÀI ĐẠT                    : {bai_dat:,}  ({bai_dat/tong_tho*100:.2f}%)")
A(f"  BÀI TRƯỢT                  : {bai_truot:,}  ({bai_truot/tong_tho*100:.2f}%)")
A("")
A("--- SỐ DÒNG HỎNG ĐỦ ĐỂ GIẾT MỘT BÀI ---")
for k in sorted(truot_theo_so_dong_hong):
    ten = f"{k} dòng hỏng" if k < 5 else "5+ dòng hỏng"
    c = truot_theo_so_dong_hong[k]
    A(f"  {ten:>14} : {c:>6,} bài  ({c/bai_truot*100:5.2f}% số bài trượt)")
A("")
A("--- THIỆT HẠI KÉO THEO ---")
A(f"  tổng dòng trong corpus              : {dong_tong:,}")
A(f"  dòng đúng 7 tiếng                   : {dong_dung:,}  ({dong_dung/dong_tong*100:.2f}%)")
A(f"  dòng nằm trong bài TRƯỢT            : {dong_trong_bai_truot:,}")
A(f"  trong đó dòng ĐÚNG 7 tiếng bị mất theo: {dong_tot_trong_bai_truot:,}")
A(f"  -> tỷ lệ dòng tốt bị mất vì bài hỏng : {dong_tot_trong_bai_truot/dong_tong*100:.2f}% toàn corpus")
A("")
A("--- NGUYÊN NHÂN, ĐẾM THEO BÀI ---")
for nn, c in sorted(nguyen_nhan_bai.items()):
    A(f"  {c:>6,} ({c/bai_truot*100:5.2f}%)  {nn}")
A("")
A("--- DẤU HIỆU, ĐẾM THEO BÀI (mỗi bài một lần) ---")
for d, c in bai_theo_dau_hieu.most_common():
    A(f"  {c:>6,} ({c/bai_truot*100:5.2f}%)  {d}")
A("")
A("--- DẤU HIỆU, ĐẾM THEO DÒNG (chỉ để chẩn đoán) ---")
tong_hong = sum(do_dai_dong_hong.values())
for d, c in dau_hieu_dong.most_common():
    A(f"  {c:>6,} ({c/tong_hong*100:5.2f}%)  {d}")
A("")
A(f"--- ĐỘ DÀI DÒNG HỎNG (tổng {tong_hong:,}) ---")
for k in sorted(do_dai_dong_hong):
    c = do_dai_dong_hong[k]
    if c >= 5:
        A(f"  {k:>3} tiếng : {c:>6,} ({c/tong_hong*100:5.2f}%)")
A("")
A("--- VỊ TRÍ DÒNG HỎNG ---")
for d, c in vi_tri_dong_hong.most_common():
    A(f"  {d:>10} : {c:>6,} ({c/tong_hong*100:5.2f}%)")
A("")
A("--- BÀI ĐẠT: HÌNH THỨC ---")
for k, c in so_dong_bai_dat.most_common(8):
    A(f"  {k:>3} dòng : {c:>6,} ({c/bai_dat*100:5.2f}%)")
A("  cấu trúc khổ:")
for k, c in cau_truc_kho_dat.most_common(5):
    A(f"    {str(k):>12} : {c:>6,} ({c/bai_dat*100:5.2f}%)")
A("")
A("--- BÀI ĐẠT: VẦN (họ sơ đồ khổ 4 dòng) ---")
t = sum(so_do_van_ho.values())
for k, c in so_do_van_ho.most_common(8):
    A(f"  {k:>6} : {c:>7,} ({c/t*100:5.2f}%)")
A("")
A("--- BÀI ĐẠT: KHUÔN ---")
t = sum(khuon_dong.values())
for k, c in khuon_dong.most_common():
    A(f"  {k:>16} : {c:>8,} ({c/t*100:5.2f}%)")
A(f"  phối khuôn khổ: {dict(phoi_khuon.most_common())}")
A("")
A(f"  nghi Đường luật : {nghi_duong_luat:,} ({nghi_duong_luat/bai_dat*100:.2f}%)")
A(f"  vần lệch thanh  : {co_lech_thanh:,} ({co_lech_thanh/bai_dat*100:.2f}%)")
A(f"  vần lưng (S7)   : {co_van_lung:,} ({co_van_lung/bai_dat*100:.2f}%)")
A("")
A("--- TRÙNG LẶP ---")
trung = sum(c for c in bam.values() if c > 1) - sum(1 for c in bam.values() if c > 1)
A(f"  bài duy nhất  : {len(bam):,}")
A(f"  bản dư        : {trung:,}")
A("  ĐẠT + duy nhất: ?")
A("")
A("--- THU HỒI TỪ KHOÁ SAI ---")
A(f"  cứu được          : {cuu_duoc:,}")
A(f"  trong đó đạt luật : {cuu_duoc_dat:,}")
A(f"  nguồn             : {dict(nguon_cuu.most_common())}")
A("")
A("--- SCORE vs ĐẠT (theo bài) ---")
for sc in sorted(set(score_dat) | set(score_truot), key=lambda x: (x is None, x)):
    d, t2 = score_dat.get(sc, 0), score_truot.get(sc, 0)
    if d + t2 >= 100:
        A(f"  score={str(sc):>4} : {d+t2:>7,} bài | đạt {d/(d+t2)*100:6.2f}%")

(RA_BC / "bao_cao_moi.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
