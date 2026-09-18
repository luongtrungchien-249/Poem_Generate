"""Truy nguyên nhân ở mức TỪNG DÒNG hỏng, và dựng chân dung bài vượt qua được luật."""

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

CO_SO = re.compile(r"\d")
CO_LATIN = re.compile(r"[a-zA-Z]")
CO_GACH_NOI = re.compile(r"\w-\w")
MO_DAU_NGOAC = re.compile(r"^\s*[(\[*\"'“]")
DE_TANG = re.compile(r"^\s*[*(\[]?\s*(gửi|tặng|kính tặng|thân tặng|viết cho|nhớ|tiễn)\b", re.IGNORECASE)
CHU_KY = re.compile(r"^\s*[-–—]\s*\S")
CHI_HOA = re.compile(r"^[^a-zà-ỹ]*$")

# --- dòng hỏng ---
do_dai_dong_hong = Counter()
vi_tri_dong_hong = Counter()
co_dac_diem = Counter()
vi_du_theo_dac_diem = defaultdict(list)
dong_8_mau = []

# --- bài đạt ---
dat_so_dong = Counter()
dat_cau_truc_kho = Counter()
dat_so_do_van_ho = Counter()
dat_khuon = Counter()
dat_theo_score = Counter()
truot_theo_score = Counter()

tong_dong_hong = 0

with DUONG_DAN.open("r", encoding="utf-8") as fh:
    for dong_json in fh:
        dong_json = dong_json.strip()
        if not dong_json:
            continue
        rec = json.loads(dong_json)
        res = rec.get("result") or {}
        tho = res.get("markdown_poem") if isinstance(res, dict) else None
        if not isinstance(tho, str) or not tho.strip():
            continue

        v = kiem_tra_bai_tho(tho)
        sc = res.get("score")

        if v.dat:
            dat_theo_score[sc] += 1
            dat_so_dong[v.so_dong] += 1
            kich_thuoc = tuple(sorted({len(k) for k in __import__("application.rule", fromlist=["x"]).tach_kho(tho)}))
            dat_cau_truc_kho[kich_thuoc] += 1
            for so_do in v.so_do_van_theo_kho:
                if len(so_do) == 4:
                    # quy về họ sơ đồ, bỏ qua chữ cái cụ thể
                    anh_xa: dict[str, str] = {}
                    ho = ""
                    for nh in so_do:
                        if nh == "x":
                            ho += "x"
                        else:
                            if nh not in anh_xa:
                                anh_xa[nh] = "abcd"[len(anh_xa)]
                            ho += anh_xa[nh]
                    dat_so_do_van_ho[ho] += 1
            dat_khuon.update(bc.khuon for bc in v.dong)
            continue

        truot_theo_score[sc] += 1
        n = len(v.dong)
        for bc in v.dong:
            if bc.so_tieng == 7:
                continue
            tong_dong_hong += 1
            do_dai_dong_hong[bc.so_tieng] += 1

            if bc.so == 1:
                vi_tri_dong_hong["dòng đầu bài"] += 1
            elif bc.so == n:
                vi_tri_dong_hong["dòng cuối bài"] += 1
            else:
                vi_tri_dong_hong["giữa bài"] += 1

            s = bc.van_ban
            dac_diem = []
            if DE_TANG.match(s):
                dac_diem.append("đề tặng / lời đề từ")
            if CHU_KY.match(s):
                dac_diem.append("ký tên tác giả")
            if MO_DAU_NGOAC.match(s):
                dac_diem.append("mở đầu bằng ngoặc / dấu nháy")
            if CO_SO.search(s):
                dac_diem.append("có chữ số")
            if CO_LATIN.search(s):
                dac_diem.append("có chữ Latin")
            if CO_GACH_NOI.search(s):
                dac_diem.append("có gạch nối giữa chữ")
            if bc.so_tieng == 0:
                dac_diem.append("dòng phân cách, không có tiếng nào")
            if bc.so_tieng > 15:
                dac_diem.append("văn xuôi lẫn vào")
            if not dac_diem:
                dac_diem.append("KHÔNG có dấu hiệu bất thường — lệch tiếng thật sự")

            for d in dac_diem:
                co_dac_diem[d] += 1
                if len(vi_du_theo_dac_diem[d]) < 4:
                    vi_du_theo_dac_diem[d].append((rec.get("id"), bc.so, bc.so_tieng, s[:76]))

            if bc.so_tieng == 8 and len(dong_8_mau) < 200:
                dong_8_mau.append(s)

R = []
A = R.append

A("=" * 78)
A("PHẦN I — BÀI VƯỢT QUA ĐƯỢC LUẬT: CHÂN DUNG")
A("=" * 78)
tong_dat = sum(dat_so_dong.values())
A(f"  tổng bài đạt: {tong_dat:,}")
A("")
A("  Số dòng mỗi bài (top 12):")
for n, c in dat_so_dong.most_common(12):
    A(f"    {n:>4} dòng : {c:>7,}  ({c/tong_dat*100:5.2f}%)")
A("")
A("  Cấu trúc khổ (các kích thước khổ xuất hiện trong bài):")
for k, c in dat_cau_truc_kho.most_common(10):
    ten = "liên hoàn / không chia khổ" if k == (0,) else f"khổ {k} dòng"
    A(f"    {str(k):>14} : {c:>7,}  ({c/tong_dat*100:5.2f}%)  {ten}")
A("")
A("  Họ sơ đồ vần của khổ 4 dòng (đã chuẩn hoá chữ cái):")
tong_so_do = sum(dat_so_do_van_ho.values())
for ho, c in dat_so_do_van_ho.most_common(12):
    ten = {
        "aaxa": "vần ba dòng, kế thừa Đường luật (§5.2)",
        "abab": "vần cách",
        "aabb": "vần liền",
        "abba": "vần ôm",
        "xaxa": "vần cách, hai dòng lẻ buông",
        "aaaa": "độc vận cả khổ",
        "xxxx": "khổ không gieo vần (S8)",
        "aaxx": "hai dòng đầu hiệp, hai dòng sau buông",
    }.get(ho, "")
    A(f"    {ho:>6} : {c:>7,}  ({c/tong_so_do*100:5.2f}%)  {ten}")
A("")
tong_khuon = sum(dat_khuon.values())
A("  Khuôn luân phiên từng dòng (S2):")
for k, c in dat_khuon.most_common():
    A(f"    {k:>16} : {c:>8,}  ({c/tong_khuon*100:5.2f}%)")

A("")
A("=" * 78)
A("PHẦN II — BÀI KHÔNG VƯỢT QUA: NGUYÊN NHÂN Ở MỨC DÒNG")
A("=" * 78)
A(f"  tổng số dòng hỏng: {tong_dong_hong:,}")
A("")
A("  Hỏng theo độ dài:")
for n, c in sorted(do_dai_dong_hong.items()):
    dau = "thiếu" if n < 7 else "thừa"
    A(f"    {n:>3} tiếng ({dau} {abs(n-7)}) : {c:>6,}  ({c/tong_dong_hong*100:5.2f}%)")
A("")
A("  Hỏng theo vị trí trong bài:")
for vt, c in vi_tri_dong_hong.most_common():
    A(f"    {vt:>14} : {c:>6,}  ({c/tong_dong_hong*100:5.2f}%)")
A("")
A("  Dấu hiệu trên dòng hỏng (một dòng có thể dính nhiều dấu hiệu):")
for d, c in co_dac_diem.most_common():
    A(f"    {c:>6,}  ({c/tong_dong_hong*100:5.2f}%)  {d}")
    for _id, so, n, s in vi_du_theo_dac_diem[d][:3]:
        A(f"            id={_id} D{so} ({n} tiếng): {s}")

A("")
A("  20 dòng 8 tiếng lấy mẫu (để đối chiếu bằng mắt):")
for s in dong_8_mau[:20]:
    A(f"    {s}")

A("")
A("=" * 78)
A("PHẦN III — ĐIỂM SỐ CÓ DỰ BÁO ĐƯỢC VIỆC ĐẠT LUẬT KHÔNG?")
A("=" * 78)
moi_score = sorted(set(dat_theo_score) | set(truot_theo_score), key=lambda x: (x is None, x))
for sc in moi_score:
    d, t = dat_theo_score.get(sc, 0), truot_theo_score.get(sc, 0)
    if d + t < 20:
        continue
    A(f"    score={str(sc):>4} : {d+t:>7,} bài | đạt {d/(d+t)*100:6.2f}%")

(RA_BC / "bao_cao4.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
