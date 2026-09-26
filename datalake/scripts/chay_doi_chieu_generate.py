"""ĐỐI CHIẾU `datalake/generate/generate_poem.jsonl` QUA `src/application/rule.py`.

CÂU HỎI: bộ thơ vừa sinh ra đạt bao nhiêu phần trăm, và phần trượt hỏng ở TẦNG NÀO.

════ ĐỌC TRƯỚC KHI TIN SỐ ════

`rule.py` ĐÓNG BĂNG và script này chỉ ĐỌC nó — không một dòng nào ở đây sửa luật
hay sửa văn bản thơ. Mọi phán quyết lấy nguyên từ `kiem_tra_bai_tho`.

Bộ kiểm chạy TUẦN TỰ bảy tầng và DỪNG ở tầng chặn đầu tiên bị trượt. Hệ quả phải
nhớ khi đọc bảng thống kê: một bài chỉ được quy cho MỘT tầng — tầng nó chết. Các
tầng sau mang `da_chay=False`, nghĩa là CHƯA KIỂM, không phải "đã kiểm và đạt".
Vì vậy "tầng 5 chặn 0 bài" KHÔNG có nghĩa là mọi bài đều đúng vần.

════ MỘT BẢN GHI HỎNG ĐỊNH DẠNG ════

Dòng 19 của tệp nguồn không phải JSON hợp lệ: bài thơ chứa dấu nháy kép chưa được
escape (`:\n"Người ơi, còn nhớ thuở ta chung?"`). Đây là lỗi của bộ SINH, không
phải của bài thơ.

Script vá đúng ca đó để không mất một bản ghi, và GHI LẠI việc vá vào báo cáo.
Lặng lẽ bỏ qua thì mẫu số bị hụt mà không ai biết; lặng lẽ vá mà không ghi thì
người sau tưởng tệp nguồn vốn sạch.

CHẠY
    python datalake/scripts/chay_doi_chieu_generate.py
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import (  # noqa: E402
    kiem_tra_bai_tho,
    mo_ta_luat,
    tach_tieng,
    thanh_cua,
)

NGUON = GOC / "datalake/generate/generate_poem.jsonl"
RA_DAT = GOC / "datalake/analysis/generate_dat.jsonl"
RA_TRUOT = GOC / "datalake/analysis/generate_truot.jsonl"
# Báo cáo `docs/analysis_generate.md` viết TAY từ số liệu script này in ra — cố ý
# không sinh tự động. Một bản tường thuật có nhận định thì phải có người ký tên,
# không phải một template điền số. Script chỉ chịu trách nhiệm về CON SỐ.


# ══════════════════════════════════════════════════════════════════════════════
# §1. ĐỌC NGUỒN
# ══════════════════════════════════════════════════════════════════════════════


def _va_nhay_kep(dong: str) -> str | None:
    """Vá đúng MỘT kiểu hỏng: dấu nháy kép chưa escape bên trong trường `poem`.

    Cắt lấy phần giữa `"poem": "` và `"}` ở cuối, escape mọi dấu nháy trong đó.
    Trả None nếu vá xong vẫn không đọc được — không đoán thêm kiểu hỏng nào khác.
    """
    m = re.match(r'^(.*"poem":\s*")(.*)("\}\s*)$', dong, re.DOTALL)
    if not m:
        return None
    dau, than, cuoi = m.groups()
    sua = dau + than.replace('"', '\\"') + cuoi
    try:
        json.loads(sua)
    except json.JSONDecodeError:
        return None
    return sua


def doc_nguon() -> tuple[list[dict], list[int], list[int]]:
    """Trả (bản ghi, dòng đã vá, dòng bỏ hẳn)."""
    ban_ghi: list[dict] = []
    da_va: list[int] = []
    bo: list[int] = []
    for so, dong in enumerate(NGUON.read_text(encoding="utf-8").splitlines(), 1):
        if not dong.strip():
            continue
        try:
            ban_ghi.append(json.loads(dong))
            continue
        except json.JSONDecodeError:
            pass
        sua = _va_nhay_kep(dong)
        if sua is None:
            bo.append(so)
        else:
            ban_ghi.append(json.loads(sua))
            da_va.append(so)
    return ban_ghi, da_va, bo


# ══════════════════════════════════════════════════════════════════════════════
# §2. BẰNG CHỨNG CHO MỘT BÀI
#
# Dựng lại bằng CHÍNH tầng ngữ âm của bộ kiểm (`tach_tieng`, `thanh_cua`), không
# chép từ trường có sẵn: muốn giải thích vì sao bộ kiểm phán thế nào thì bằng
# chứng phải lấy từ đúng cái nó đã nhìn.
# ══════════════════════════════════════════════════════════════════════════════


def bang_chung_dong(so: int, van_ban: str) -> dict:
    t = tach_tieng(van_ban)
    ra: dict = {"so": so, "van_ban": van_ban, "so_tieng": len(t), "tieng": list(t)}
    if len(t) >= 6:
        ra["vi_tri_2_4_6"] = [
            {"vi_tri": v, "tieng": t[v - 1], "thanh": thanh_cua(t[v - 1])} for v in (2, 4, 6)
        ]
        ra["khuon_2_4_6"] = "".join(thanh_cua(t[v - 1]) for v in (2, 4, 6))
    if t:
        ra["tieng_cuoi"] = t[-1]
    return ra


def phan_tich(r: dict) -> dict:
    """Chạy một bài qua bảy tầng, giữ lại đủ dấu vết để giải thích phán quyết."""
    v = kiem_tra_bai_tho(r["poem"])
    dong = [d for d in r["poem"].splitlines() if d.strip()]

    tang = [
        {
            "tang": kq.so,
            "ten": kq.ten,
            "muc": kq.muc,
            "da_chay": kq.da_chay,
            "dat": kq.dat,
            "bang_chung": kq.bang_chung,
        }
        for kq in v.tang
    ]

    return {
        "id": r.get("id"),
        "title": r.get("title", ""),
        "topic": r.get("topic", ""),
        "poem": r["poem"],
        "dat": v.dat,
        "thuoc_the": v.thuoc_the,
        "tang_dung_lai": v.tang_dung_lai,
        "so_dong": v.so_dong,
        "so_kho": v.so_kho,
        "so_do_van_theo_kho": ["".join(k) for k in v.so_do_van_theo_kho],
        "ty_le_theo_khuon": v.ty_le_theo_khuon,
        "tang": tang,
        "vi_pham": [
            {
                "ma": vp.ma,
                "dong": vp.dong,
                "noi_dung_luat": mo_ta_luat(vp.ma),
                "ky_vong": vp.ky_vong,
                "thuc_te": vp.thuc_te,
            }
            for vp in v.vi_pham
        ],
        "dong_chi_tiet": [bang_chung_dong(i + 1, d) for i, d in enumerate(dong)],
    }


# ══════════════════════════════════════════════════════════════════════════════
# §3. CHẠY
# ══════════════════════════════════════════════════════════════════════════════


def main() -> int:
    ban_ghi, da_va, bo = doc_nguon()
    kq = [phan_tich(r) for r in ban_ghi]
    dat = [x for x in kq if x["dat"]]
    truot = [x for x in kq if not x["dat"]]

    RA_DAT.parent.mkdir(parents=True, exist_ok=True)
    for duong, ds in ((RA_DAT, dat), (RA_TRUOT, truot)):
        with duong.open("w", encoding="utf-8") as f:
            for x in ds:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")

    theo_tang = Counter(x["tang_dung_lai"] for x in truot)
    theo_ma = Counter(vp["ma"] for x in truot for vp in x["vi_pham"])
    # Bài dính mã nào (đếm BÀI, không đếm lượt vi phạm) — hai con số rất khác nhau.
    bai_dinh_ma = Counter(ma for x in truot for ma in {vp["ma"] for vp in x["vi_pham"]})
    do_dai = Counter(st for x in kq for st in [d["so_tieng"] for d in x["dong_chi_tiet"]])

    tom = {
        "tong_ban_ghi": len(kq),
        "dong_da_va_dinh_dang": da_va,
        "dong_bo_han": bo,
        "so_dat": len(dat),
        "so_truot": len(truot),
        "ti_le_dat": round(len(dat) / len(kq), 4) if kq else 0.0,
        "truot_theo_tang": dict(sorted(theo_tang.items(), key=lambda x: (x[0] is None, x[0]))),
        "bai_dinh_theo_ma_luat": dict(bai_dinh_ma.most_common()),
        "luot_vi_pham_theo_ma_luat": dict(theo_ma.most_common()),
        "phan_bo_so_tieng_moi_dong": dict(sorted(do_dai.items())),
    }
    print(json.dumps(tom, ensure_ascii=False, indent=2))
    print(f"\n-> {RA_DAT}\n-> {RA_TRUOT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
