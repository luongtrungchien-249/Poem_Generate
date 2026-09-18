"""Đo lại điểm mù H1 bằng tín hiệu CẤU TRÚC, không dùng tín hiệu từ vựng.

Bài học từ lần đo trước: "Gửi hương hoa cải, bướm lang thang." khớp mẫu "đề tặng"
nhưng là dòng thơ thật. Mẫu từ vựng (gửi/tặng/nhớ/tiễn) báo nhầm hàng loạt vì đó
cũng là từ vựng thơ ca.

Tín hiệu cấu trúc đáng tin hơn: một dòng chú thích thường (a) không đủ 7 tiếng,
(b) đứng riêng một khổ, (c) bọc trong ngoặc, hoặc (d) chỉ gồm chữ số.
"""

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
from application.rule import kiem_tra_bai_tho, tach_kho, tach_tieng  # noqa: E402

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

CHI_SO = re.compile(r"^[\s(\[*\-–—]*\d{1,4}([.,/\-]\d{1,4})*[\s)\]*.,;:]*$")
BOC_KIN = re.compile(r"^\s*[(\[].*[)\]]\s*$|^\s*\*[^*]+\*\s*$")
CHU_KY = re.compile(r"^\s*[-–—]\s*[A-ZĐÀ-Ỹ][^,.!?]{1,30}\s*$")
SO_LA_MA = re.compile(r"^\s*[IVX]{1,5}\s*[.)]?\s*$")

dong_chi_so_tong = 0
dong_chi_so_7_tieng = 0
dong_chi_so_trong_bai_dat = []

dat_boc_kin = 0
dat_chu_ky = 0
dat_so_la_ma = 0
dat_kho_mot_dong_dau = 0
dat_kho_mot_dong_cuoi = 0
dat_bat_ky = 0
tong_dat = 0

vi_du = Counter()
vi_du_chi_tiet = {"boc_kin": [], "chu_ky": [], "so_la_ma": [], "kho_1_dong": []}

with NGUON.open("r", encoding="utf-8") as fh:
    for dj in fh:
        dj = dj.strip()
        if not dj:
            continue
        rec = json.loads(dj)
        res = rec.get("result") or {}
        tho = res.get("markdown_poem") if isinstance(res, dict) else None
        if not isinstance(tho, str) or not tho.strip():
            continue

        v = kiem_tra_bai_tho(tho)

        for bc in v.dong:
            if CHI_SO.match(bc.van_ban):
                dong_chi_so_tong += 1
                if bc.so_tieng == 7:
                    dong_chi_so_7_tieng += 1
                    if v.dat and len(dong_chi_so_trong_bai_dat) < 20:
                        dong_chi_so_trong_bai_dat.append(
                            (rec.get("id"), bc.so, bc.van_ban, tach_tieng(bc.van_ban))
                        )

        if not v.dat:
            continue
        tong_dat += 1

        kho = tach_kho(tho)
        co = False
        for bc in v.dong:
            s = bc.van_ban
            if BOC_KIN.match(s):
                dat_boc_kin += 1
                co = True
                if len(vi_du_chi_tiet["boc_kin"]) < 6:
                    vi_du_chi_tiet["boc_kin"].append((rec.get("id"), bc.so, bc.so_tieng, s))
            if CHU_KY.match(s):
                dat_chu_ky += 1
                co = True
                if len(vi_du_chi_tiet["chu_ky"]) < 6:
                    vi_du_chi_tiet["chu_ky"].append((rec.get("id"), bc.so, bc.so_tieng, s))
            if SO_LA_MA.match(s):
                dat_so_la_ma += 1
                co = True
                if len(vi_du_chi_tiet["so_la_ma"]) < 6:
                    vi_du_chi_tiet["so_la_ma"].append((rec.get("id"), bc.so, bc.so_tieng, s))

        if len(kho) > 1:
            if len(kho[0]) == 1:
                dat_kho_mot_dong_dau += 1
                co = True
                if len(vi_du_chi_tiet["kho_1_dong"]) < 8:
                    vi_du_chi_tiet["kho_1_dong"].append((rec.get("id"), 1, len(tach_tieng(kho[0][0])), kho[0][0]))
            if len(kho[-1]) == 1:
                dat_kho_mot_dong_cuoi += 1
                co = True
        if co:
            dat_bat_ky += 1

R = []
A = R.append
A("=" * 72)
A("ĐO LẠI ĐIỂM MÙ H1 BẰNG TÍN HIỆU CẤU TRÚC")
A("=" * 72)
A("")
A("--- 1. DÒNG CHỈ GỒM CHỮ SỐ (năm, ngày tháng) ---")
A(f"  tổng số dòng như vậy trong corpus        : {dong_chi_so_tong:,}")
A(f"  trong đó đọc ra ĐÚNG 7 tiếng (lọt H1)    : {dong_chi_so_7_tieng:,}")
A(f"  nằm trong bài ĐẠT (thật sự lọt lưới)     : {len(dong_chi_so_trong_bai_dat):,}")
for x in dong_chi_so_trong_bai_dat[:10]:
    A(f"      id={x[0]} D{x[1]}: {x[2]!r} -> {x[3]}")

A("")
A("--- 2. DÒNG PHI THƠ CÒN SÓT TRONG BÀI ĐẠT (tín hiệu cấu trúc) ---")
A(f"  tổng bài đạt                              : {tong_dat:,}")
A(f"  bài đạt có ÍT NHẤT MỘT dấu hiệu cấu trúc  : {dat_bat_ky:,}  ({dat_bat_ky/tong_dat*100:.3f}%)")
A("")
A(f"  dòng bọc kín trong ngoặc/dấu sao          : {dat_boc_kin:,}")
for x in vi_du_chi_tiet["boc_kin"]:
    A(f"      id={x[0]} D{x[1]} ({x[2]} tiếng): {x[3][:60]}")
A(f"  dòng ký tên tác giả                       : {dat_chu_ky:,}")
for x in vi_du_chi_tiet["chu_ky"]:
    A(f"      id={x[0]} D{x[1]} ({x[2]} tiếng): {x[3][:60]}")
A(f"  dòng đánh số La Mã (I, II, III)           : {dat_so_la_ma:,}")
for x in vi_du_chi_tiet["so_la_ma"]:
    A(f"      id={x[0]} D{x[1]} ({x[2]} tiếng): {x[3][:60]}")
A(f"  khổ ĐẦU chỉ có một dòng                   : {dat_kho_mot_dong_dau:,}")
for x in vi_du_chi_tiet["kho_1_dong"]:
    A(f"      id={x[0]} ({x[2]} tiếng): {x[3][:60]}")
A(f"  khổ CUỐI chỉ có một dòng                  : {dat_kho_mot_dong_cuoi:,}")

(RA_BC / "bao_cao7.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
