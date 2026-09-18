"""Phân loại nguyên nhân trượt và ước lượng tập dữ liệu sạch dùng được."""

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
from application.rule import kiem_tra_bai_tho  # noqa: E402

DUONG_DAN = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

NAM = re.compile(r"^[\s(*\[]*\d{4}[\s)*\].,]*$")
CHU_KY = re.compile(r"^\s*[-–—]\s*\S")

nguyen_nhan = Counter()
vi_du = {}
da_thay = set()
sach_va_duy_nhat = 0
sach_nhung_trung = 0
tho_8_chu_hoan_toan = 0
co_dong_van_xuoi = 0
co_dong_nam_don = 0
co_dong_sao = 0
co_dong_chu_ky = 0
sua_duoc_1_dong = 0

with DUONG_DAN.open("r", encoding="utf-8") as fh:
    for dong in fh:
        dong = dong.strip()
        if not dong:
            continue
        rec = json.loads(dong)
        res = rec.get("result") or {}
        tho = res.get("markdown_poem") if isinstance(res, dict) else None
        if not isinstance(tho, str) or not tho.strip():
            continue

        v = kiem_tra_bai_tho(tho)
        do_dai = [bc.so_tieng for bc in v.dong]
        pho_bien = Counter(do_dai).most_common(1)[0][0] if do_dai else 0

        if v.dat:
            bam = hashlib.md5(" ".join(tho.split()).encode("utf-8")).hexdigest()
            if bam in da_thay:
                sach_nhung_trung += 1
            else:
                da_thay.add(bam)
                sach_va_duy_nhat += 1
            continue

        van_ban_dong = [bc.van_ban for bc in v.dong]
        co_van_xuoi = any(n > 15 for n in do_dai)
        co_nam = any(NAM.match(s) for s in van_ban_dong)
        co_sao = any(bc.so_tieng == 0 for bc in v.dong)
        co_ky = any(CHU_KY.match(s) for s in van_ban_dong)
        so_dong_hong = sum(1 for n in do_dai if n != 7)

        if co_van_xuoi:
            co_dong_van_xuoi += 1
        if co_nam:
            co_dong_nam_don += 1
        if co_sao:
            co_dong_sao += 1
        if co_ky:
            co_dong_chu_ky += 1

        if pho_bien == 8 and do_dai.count(8) >= len(do_dai) * 0.8:
            loai = "A. Thực chất là THƠ 8 CHỮ (>=80% dòng 8 tiếng)"
            tho_8_chu_hoan_toan += 1
        elif co_van_xuoi:
            loai = "B. Lẫn văn xuôi (chú thích, tiểu dẫn) trong trường thơ"
        elif co_sao:
            loai = "C. Có dòng phân cách kiểu '*' hoặc dấu câu đơn lẻ"
        elif co_nam:
            loai = "D. Có dòng chỉ ghi năm / nơi chốn"
        elif co_ky:
            loai = "E. Có dòng ký tên tác giả"
        elif so_dong_hong <= 2:
            loai = "F. Thơ 7 chữ nhưng 1–2 dòng lệch (có thể sửa tay)"
            sua_duoc_1_dong += 1
        else:
            loai = "G. Lệch nhiều dòng, thể không thuần nhất"

        nguyen_nhan[loai] += 1
        if loai not in vi_du:
            hong = [
                (bc.so, bc.so_tieng, bc.van_ban) for bc in v.dong if bc.so_tieng != 7
            ][:3]
            vi_du[loai] = (rec.get("id"), hong)

R = []
A = R.append
A("--- PHÂN LOẠI NGUYÊN NHÂN TRƯỢT ---")
tong_truot = sum(nguyen_nhan.values())
for loai, c in nguyen_nhan.most_common():
    A(f"  {c:>6,}  ({c/tong_truot*100:5.1f}%)  {loai}")
    _id, hong = vi_du[loai]
    A(f"          ví dụ id={_id}:")
    for so, n, vb in hong:
        A(f"            D{so} ({n} tiếng): {vb[:80]}")
A(f"  TỔNG TRƯỢT: {tong_truot:,}")

A("")
A("--- DẤU HIỆU NHIỄU (đếm chồng lấn, một bài có thể dính nhiều loại) ---")
A(f"  bài có dòng văn xuôi (>15 tiếng) : {co_dong_van_xuoi:,}")
A(f"  bài có dòng chỉ ghi năm          : {co_dong_nam_don:,}")
A(f"  bài có dòng phân cách '*'        : {co_dong_sao:,}")
A(f"  bài có dòng ký tên               : {co_dong_chu_ky:,}")

A("")
A("--- TẬP DỮ LIỆU DÙNG ĐƯỢC ---")
A(f"  đạt luật + duy nhất : {sach_va_duy_nhat:,}")
A(f"  đạt luật nhưng trùng: {sach_nhung_trung:,}")
A(f"  có thể cứu (1-2 dòng lệch): {sua_duoc_1_dong:,}")

(RA_BC / "bao_cao3.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
