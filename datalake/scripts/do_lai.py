"""Đo lại nguyên nhân dòng hỏng, bỏ chỉ số 'có chữ Latin' vô nghĩa."""

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── Đường dẫn suy từ vị trí tệp, không đặt cứng: script chạy được ở máy khác.
GOC = Path(__file__).resolve().parents[2]
RA_BC = GOC / "datalake/analysis/reports"
RA_BC.mkdir(parents=True, exist_ok=True)

# Console Windows mặc định cp1252, không in được tiếng Việt có dấu.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(GOC / "src"))
from application.rule import kiem_tra_bai_tho  # noqa: E402

DUONG_DAN = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

# Chữ cái KHÔNG thuộc bảng chữ tiếng Việt -> dấu hiệu tên riêng/ngoại ngữ thật sự
NGOAI_BANG_CHU = re.compile(r"[fjwzFJWZ]")
CO_SO = re.compile(r"\d")
GACH_NOI = re.compile(r"\w-\w")
MO_DAU_KY_HIEU = re.compile(r"^\s*[(\[*\"'“]")
DE_TANG = re.compile(r"^\s*[*(\[]?\s*(gửi|tặng|kính tặng|thân tặng|viết cho|tiễn)\b", re.IGNORECASE)
CHU_KY = re.compile(r"^\s*[-–—]\s*\S")

dau_hieu = Counter()
vi_du = defaultdict(list)
tong_dong_hong = 0

ty_le_dong_8 = Counter()
bai_thuan_7_lech_mot_dong = 0
bai_truot = 0

with DUONG_DAN.open("r", encoding="utf-8") as fh:
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
        if v.dat:
            continue

        bai_truot += 1
        do_dai = [bc.so_tieng for bc in v.dong]
        so_8 = sum(1 for n in do_dai if n == 8)
        so_7 = sum(1 for n in do_dai if n == 7)
        ty_le_dong_8[round(so_8 / len(do_dai), 1)] += 1
        if so_7 == len(do_dai) - 1:
            bai_thuan_7_lech_mot_dong += 1

        for bc in v.dong:
            if bc.so_tieng == 7:
                continue
            tong_dong_hong += 1
            s = bc.van_ban
            co = []
            if bc.so_tieng == 0:
                co.append("dòng phân cách, không có tiếng nào")
            if bc.so_tieng > 15:
                co.append("văn xuôi lẫn vào trường thơ")
            if DE_TANG.match(s):
                co.append("đề tặng / lời đề từ")
            if CHU_KY.match(s):
                co.append("ký tên tác giả")
            if MO_DAU_KY_HIEU.match(s) and bc.so_tieng < 7:
                co.append("dòng phụ chú mở bằng ngoặc/dấu sao")
            if CO_SO.search(s):
                co.append("có chữ số (năm tháng, địa danh)")
            if GACH_NOI.search(s):
                co.append("tên phiên âm có gạch nối")
            if NGOAI_BANG_CHU.search(s):
                co.append("có chữ ngoài bảng chữ tiếng Việt (f, j, w, z)")
            if not co:
                co.append("KHÔNG có dấu hiệu bất thường — dòng thơ thật, chỉ sai số tiếng")
            for d in co:
                dau_hieu[d] += 1
                if len(vi_du[d]) < 3:
                    vi_du[d].append((rec.get("id"), bc.so, bc.so_tieng, s[:74]))

R = []
A = R.append
A("--- NGUYÊN NHÂN DÒNG HỎNG (đã bỏ chỉ số 'chữ Latin' vô nghĩa) ---")
A(f"  tổng dòng hỏng: {tong_dong_hong:,}")
A("")
for d, c in dau_hieu.most_common():
    A(f"  {c:>6,}  ({c/tong_dong_hong*100:5.2f}%)  {d}")
    for _id, so, n, s in vi_du[d]:
        A(f"            id={_id} D{so} ({n} tiếng): {s}")

A("")
A("--- BÀI TRƯỢT: TỶ LỆ DÒNG 8 TIẾNG TRONG BÀI ---")
for t, c in sorted(ty_le_dong_8.items()):
    A(f"  {int(t*100):>3}% số dòng là 8 tiếng : {c:>6,} bài  ({c/bai_truot*100:5.2f}%)")
A("")
A(f"  Bài chỉ lệch ĐÚNG MỘT dòng (còn lại 7 tiếng hết): {bai_thuan_7_lech_mot_dong:,} ({bai_thuan_7_lech_mot_dong/bai_truot*100:.1f}% số bài trượt)")

(RA_BC / "bao_cao5.txt").write_text("\n".join(R), encoding="utf-8")
print("XONG")
