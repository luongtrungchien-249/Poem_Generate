"""Ba việc trong một lượt quét:
1. Chi tiết dòng hỏng kèm TÊN BÀI
2. Truy 5.116 bài rỗng: nội dung có nằm ở khoá khác không
3. Đo điểm mù H1: dòng chú thích lọt vào bài ĐẠT
"""

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
from application.rule import kiem_tra_bai_tho, tach_kho, tach_tieng  # noqa: E402

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"
RA = GOC / "datalake/analysis"
RA.mkdir(parents=True, exist_ok=True)

# ---------- mẫu nhận diện dòng KHÔNG PHẢI thơ ----------
CHI_SO = re.compile(r"^[\s(\[*\-–—]*\d{1,4}([.,/\-]\d{1,4})*[\s)\]*.,;:]*$")
DE_TANG = re.compile(r"^\s*[*(\[]?\s*(gửi|tặng|kính tặng|thân tặng|kính dâng|viết cho|tiễn|nhớ về)\b", re.IGNORECASE)
CHU_KY = re.compile(r"^\s*[-–—]\s*[A-ZĐÀ-Ỹ]")
BOC_NGOAC = re.compile(r"^\s*[(\[*].*[)\]*]\s*$")
DIA_DANH_NGAY = re.compile(r"^[^,]{2,30},\s*(ngày\s+)?\d{1,2}[./-]?\d{0,2}[./-]?\d{2,4}\s*$", re.IGNORECASE)
KET_BANG_HAI_CHAM = re.compile(r":\s*$")
TOAN_HOA = re.compile(r"^[^a-zà-ỹ]+$")

KHOA_THO_KHAC = (
    "markdown_poem_content", "markdown_poem_fixed", "markdown_poem_final",
    "markdown_poem_full", "markdown_content", "poem_content", "content",
    "content_fix", "content_fixed", "content_processed", "content_correction",
    "content_details", "content_analysis",
)


BOC_KIN = re.compile(r"^\s*[(\[].*[)\]]\s*$|^\s*\*[^*]+\*\s*$")


def dau_hieu_khong_phai_tho(s: str, so_tieng: int) -> list[str]:
    """Nhận diện dòng siêu dữ liệu bằng tín hiệu CẤU TRÚC.

    LỊCH SỬ — đọc trước khi sửa lại:
    Bản đầu của hàm này dùng tín hiệu TỪ VỰNG (dòng bắt đầu bằng *gửi · tặng ·
    nhớ · tiễn*, dòng kết thúc bằng dấu hai chấm). Đo trên corpus thì nó gắn cờ
    2.828 dòng mà **phần lớn là dòng thơ thật**:

        "Gửi hương hoa cải, bướm lang thang."   <- thơ, không phải đề tặng
        "Tiễn một người yêu một buổi chiều."    <- thơ
        "Nhớ về chuyện cũ dạ buồn hơn."         <- thơ

    Lý do thất bại rất căn bản: *gửi, tặng, nhớ, tiễn* chính là từ vựng của thơ
    trữ tình. Bộ lọc dựa vào chúng sẽ cắt mất đúng phần dữ liệu tốt nhất.

    Vì vậy hàm này CHỈ dùng hình thức và vị trí. Các mẫu từ vựng bên trên được
    giữ lại trong tệp nhưng KHÔNG dùng ở đây — xem §6.3 và §6.4 của
    docs/Report_analyst_17-09_pass-notpass.md.
    """
    ra = []
    if BOC_KIN.match(s):
        ra.append("bọc kín trong ngoặc hoặc dấu sao")
    if CHI_SO.match(s):
        ra.append("chỉ gồm chữ số")
    return ra


# ---------- bộ đếm ----------
# Việc 1
truot_chi_tiet = []
truot_theo_nguyen_nhan = defaultdict(list)
tieu_de_bai_truot = Counter()
co_tieu_de_truot = 0

# Việc 2
rong_tong = 0
rong_co_khoa_khac = Counter()
cuu_duoc = []
rong_khong_cuu_duoc = 0
khoa_cua_bai_rong = Counter()

# Việc 3
dat_co_dong_nghi_ngo = 0
dong_nghi_ngo = []
nghi_ngo_theo_loai = Counter()
tong_bai_dat = 0
dong_chi_so_7_tieng = []

with NGUON.open("r", encoding="utf-8") as fh:
    for dj in fh:
        dj = dj.strip()
        if not dj:
            continue
        rec = json.loads(dj)
        res = rec.get("result") or {}
        _id = rec.get("id")
        tieu_de = (rec.get("original_title") or "").strip()
        tho = res.get("markdown_poem") if isinstance(res, dict) else None

        # ===== VIỆC 2: bài rỗng =====
        if not isinstance(tho, str) or not tho.strip():
            rong_tong += 1
            khoa_cua_bai_rong.update(k for k in res if k != "markdown_poem")
            ung_vien = None
            khoa_nguon = None
            for k in KHOA_THO_KHAC:
                gt = res.get(k)
                if isinstance(gt, str) and gt.strip() and "\n" in gt.strip():
                    ung_vien, khoa_nguon = gt, k
                    break
            if ung_vien:
                rong_co_khoa_khac[khoa_nguon] += 1
                v = kiem_tra_bai_tho(ung_vien)
                cuu_duoc.append({
                    "id": _id,
                    "tieu_de": tieu_de,
                    "khoa_nguon": khoa_nguon,
                    "so_dong": v.so_dong,
                    "dat_luat": v.dat,
                    "tho": ung_vien,
                })
            else:
                rong_khong_cuu_duoc += 1
            continue

        v = kiem_tra_bai_tho(tho)

        # ===== VIỆC 3: điểm mù trên bài ĐẠT =====
        if v.dat:
            tong_bai_dat += 1
            nghi = []
            for bc in v.dong:
                dh = dau_hieu_khong_phai_tho(bc.van_ban, bc.so_tieng)
                if dh:
                    nghi.append((bc.so, bc.so_tieng, bc.van_ban, dh))
                    if CHI_SO.match(bc.van_ban) and len(dong_chi_so_7_tieng) < 40:
                        dong_chi_so_7_tieng.append((_id, bc.so, bc.van_ban, tach_tieng(bc.van_ban)))
            # Khổ đầu chỉ một dòng: tín hiệu ĐỘ TIN CẬY THẤP, ghi nhận nhưng
            # gắn nhãn rõ. "Bâng khuâng trời rộng nhớ sông dài." là câu thơ Huy
            # Cận nhưng vẫn khớp mẫu này — đừng dùng nó để tự động cắt bỏ.
            kho = tach_kho(tho)
            if len(kho) > 1 and len(kho[0]) == 1:
                nghi.append((1, len(tach_tieng(kho[0][0])), kho[0][0], ["khổ đầu chỉ một dòng"]))

            if nghi:
                dat_co_dong_nghi_ngo += 1
                for loai_list in (x[3] for x in nghi):
                    nghi_ngo_theo_loai.update(loai_list)
                dong_nghi_ngo.append({
                    "id": _id, "tieu_de": tieu_de,
                    "dong_nghi_ngo": [
                        {"so": s, "so_tieng": n, "text": t, "dau_hieu": d}
                        for s, n, t, d in nghi
                    ],
                })
            continue

        # ===== VIỆC 1: chi tiết bài trượt =====
        if tieu_de:
            co_tieu_de_truot += 1
            tieu_de_bai_truot[tieu_de] += 1

        hong = [(bc.so, bc.so_tieng, bc.van_ban) for bc in v.dong if bc.so_tieng != 7]
        do_dai = [bc.so_tieng for bc in v.dong]
        so_8 = sum(1 for n in do_dai if n == 8)

        if so_8 >= len(do_dai) * 0.8 and len(do_dai) >= 4:
            nn = "A. Thơ 8 chữ bị gán nhãn 7 chữ"
        elif any(n > 15 for n in do_dai):
            nn = "B. Lẫn văn xuôi trong trường thơ"
        elif any(n == 0 for n in do_dai):
            nn = "C. Có dòng phân cách không chứa tiếng"
        elif len(hong) == 1 and hong[0][1] == 6:
            nn = "D. Đúng một dòng thiếu một tiếng (nghi rơi chữ)"
        elif len(hong) == 1 and hong[0][1] == 8:
            nn = "E. Đúng một dòng thừa một tiếng"
        elif len(hong) == 1:
            nn = "F. Đúng một dòng lệch nhiều tiếng"
        elif len(hong) <= 2:
            nn = "G. Hai dòng lệch"
        else:
            nn = "H. Lệch nhiều dòng, thể không thuần nhất"

        ban_ghi = {
            "id": _id, "tieu_de": tieu_de, "nguyen_nhan": nn,
            "so_dong": v.so_dong, "so_dong_hong": len(hong),
            "dong_hong": [{"so": s, "so_tieng": n, "text": t} for s, n, t in hong],
        }
        truot_chi_tiet.append(ban_ghi)
        if len(truot_theo_nguyen_nhan[nn]) < 12:
            truot_theo_nguyen_nhan[nn].append(ban_ghi)

# ---------- ghi tệp ----------
with (RA / "bai_truot_chi_tiet.jsonl").open("w", encoding="utf-8") as f:
    for r in truot_chi_tiet:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with (RA / "bai_rong_cuu_duoc.jsonl").open("w", encoding="utf-8") as f:
    for r in cuu_duoc:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with (RA / "dong_nghi_ngo_trong_bai_dat.jsonl").open("w", encoding="utf-8") as f:
    for r in dong_nghi_ngo:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

# ---------- báo cáo ----------
R = []
A = R.append

A("=" * 76)
A("VIỆC 1 — CHI TIẾT BÀI TRƯỢT (kèm tên bài)")
A("=" * 76)
A(f"  tổng bài trượt        : {len(truot_chi_tiet):,}")
A(f"  có tiêu đề            : {co_tieu_de_truot:,}")
A("")
A("  Phân nhóm nguyên nhân:")
dem_nn = Counter(r["nguyen_nhan"] for r in truot_chi_tiet)
for nn, c in sorted(dem_nn.items()):
    A(f"    {c:>6,} ({c/len(truot_chi_tiet)*100:5.1f}%)  {nn}")
A("")
for nn in sorted(truot_theo_nguyen_nhan):
    A(f"  ── {nn} ──")
    for r in truot_theo_nguyen_nhan[nn][:6]:
        ten = r["tieu_de"] or "(không tiêu đề)"
        A(f"    id={r['id']:<6} \"{ten[:44]}\"  {r['so_dong']} dòng, {r['so_dong_hong']} dòng hỏng")
        for d in r["dong_hong"][:3]:
            A(f"        D{d['so']} ({d['so_tieng']} tiếng): {d['text'][:66]}")
    A("")

A(f"  Tiêu đề xuất hiện nhiều nhất trong nhóm trượt: {tieu_de_bai_truot.most_common(8)}")

A("")
A("=" * 76)
A("VIỆC 2 — TRUY 5.116 BÀI RỖNG")
A("=" * 76)
A(f"  tổng bài rỗng                    : {rong_tong:,}")
A(f"  CỨU ĐƯỢC từ khoá khác            : {len(cuu_duoc):,}")
A(f"  không có nội dung ở đâu cả       : {rong_khong_cuu_duoc:,}")
A("")
A("  Nguồn cứu được:")
for k, c in rong_co_khoa_khac.most_common():
    A(f"    {c:>5,}  {k}")
A("")
A("  Các khoá khác có mặt trong bài rỗng (top 15):")
for k, c in khoa_cua_bai_rong.most_common(15):
    A(f"    {c:>5,}  {k}")
if cuu_duoc:
    dat_cuu = sum(1 for r in cuu_duoc if r["dat_luat"])
    A("")
    A(f"  Trong số cứu được, đạt luật ngay: {dat_cuu:,}/{len(cuu_duoc):,}")
    A("  Ví dụ:")
    for r in cuu_duoc[:5]:
        A(f"    id={r['id']} [{r['khoa_nguon']}] {r['so_dong']} dòng, đạt={r['dat_luat']}")
        A(f"        {r['tho'].splitlines()[0][:66] if r['tho'].splitlines() else ''}")

A("")
A("=" * 76)
A("VIỆC 3 — ĐIỂM MÙ H1: DÒNG CHÚ THÍCH LỌT VÀO BÀI ĐẠT")
A("=" * 76)
A(f"  tổng bài đạt                     : {tong_bai_dat:,}")
A(f"  bài đạt CÓ dòng đáng ngờ         : {dat_co_dong_nghi_ngo:,}  ({dat_co_dong_nghi_ngo/tong_bai_dat*100:.2f}%)")
A("")
A("  Loại dấu hiệu (đếm theo dòng, có chồng lấn):")
for loai, c in nghi_ngo_theo_loai.most_common():
    A(f"    {c:>6,}  {loai}")
A("")
A("  Dòng chỉ gồm chữ số mà vẫn lọt qua H1:")
for _id, so, txt, tieng in dong_chi_so_7_tieng[:15]:
    A(f"    id={_id} D{so}: {txt!r} -> {len(tieng)} tiếng {tieng}")

A("")
A("  Ví dụ dòng đáng ngờ trong bài ĐẠT:")
for r in dong_nghi_ngo[:12]:
    ten = r["tieu_de"] or "(không tiêu đề)"
    A(f"    id={r['id']} \"{ten[:40]}\"")
    for d in r["dong_nghi_ngo"][:2]:
        A(f"        D{d['so']} ({d['so_tieng']} tiếng): {d['text'][:60]}")
        A(f"            dấu hiệu: {', '.join(d['dau_hieu'])}")

A("")
A(f"  Tệp đã ghi: {RA}")

(RA_BC / "bao_cao6.txt").write_text(
    "\n".join(R), encoding="utf-8"
)
print("XONG")
