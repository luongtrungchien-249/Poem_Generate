"""So sánh phán quyết giữa BẢN ĐẦU và BẢN HIỆN TẠI của rule.py.

Sinh ra §8.1 của docs/Report_analyst_17-09_pass-notpass.md — mục duy nhất trước
đây chạy bằng lệnh trực tiếp nên không tái lập được.

Câu hỏi cần trả lời: hai lần sửa `rule.py` ngày 17/09/2026 làm luật CHẶT hơn hay
LỎNG hơn, và bao nhiêu bài đổi phán quyết theo từng chiều.

BẢN ĐẦU khác bản hiện tại ĐÚNG HAI CHỖ, và chỉ hai chỗ đó được mô phỏng lại:
  1. Dấu câu nhận diện bằng DANH SÁCH LIỆT KÊ TAY, thiếu gạch ngang dài "—" và
     gạch ngang ngắn "–".
  2. Chữ số: chỉ đọc số nguyên, CHƯA có số thập phân và số 0 đứng đầu.

CẢNH BÁO VỀ CÁCH ĐO — bài học đã trả giá:
    Lần mô phỏng đầu tiên bỏ sót phần đọc số nguyên vốn ĐÃ CÓ trong bản đầu, nên
    ra kết quả sai (10 siết / 13 nới thay vì 0 siết / 8 nới). Đường cơ sở phải
    giống bản đầu ở MỌI thứ trừ đúng hai chỗ đã sửa, nếu không phép so sánh đo
    nhầm sang thứ khác.

CHẠY
    python datalake/scripts/so_sanh_ban_luat.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
RA_BC = GOC / "datalake/analysis/reports"
RA_BC.mkdir(parents=True, exist_ok=True)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(GOC / "src"))
from application.rule import doc_so, kiem_tra_bai_tho, tach_kho, tach_tieng  # noqa: E402

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"

# ── BẢN ĐẦU: danh sách dấu câu liệt kê tay (thiếu — và –) ──
_DAU_CAU_CU = re.compile(r"[.,;:!?…\"'“”‘’()\[\]{}<>«»/\\|*_~`#+=%$@^&]")
_CHU_SO = re.compile(r"^\d+$")


def tach_tieng_ban_dau(dong: str) -> list[str]:
    """Tái dựng đúng bộ tách tiếng của rule.py bản đầu.

    Giữ nguyên phần đọc số nguyên (`doc_so`) vì bản đầu đã có. Chỉ thiếu:
    nhận diện dấu câu theo Unicode, số thập phân, số 0 đứng đầu.
    """
    ra: list[str] = []
    for tu in _DAU_CAU_CU.sub(" ", dong).split():
        for phan in tu.split("-"):
            if not phan:
                continue
            if _CHU_SO.match(phan):
                ra.extend(doc_so(int(phan)))
            else:
                ra.append(phan)
    return ra


def dat_theo_ban_dau(tho: str) -> bool:
    """Phán quyết của bản đầu: H3 (>=2 dòng) và H1 (mọi dòng đúng 7 tiếng)."""
    dong = [d for k in tach_kho(tho) for d in k]
    if len(dong) < 2:
        return False
    return all(len(tach_tieng_ban_dau(d)) == 7 for d in dong)


def main() -> int:
    n_cu = n_moi = 0
    siet: list[tuple] = []   # ĐẠT -> TRƯỢT
    noi: list[tuple] = []    # TRƯỢT -> ĐẠT

    with NGUON.open("r", encoding="utf-8") as fh:
        for dj in fh:
            dj = dj.strip()
            if not dj:
                continue
            rec = json.loads(dj)
            tho = (rec.get("result") or {}).get("markdown_poem")
            if not isinstance(tho, str) or not tho.strip():
                continue

            cu = dat_theo_ban_dau(tho)
            moi = kiem_tra_bai_tho(tho).dat
            n_cu += cu
            n_moi += moi

            if cu != moi:
                dong = [d for k in tach_kho(tho) for d in k]
                khac = [
                    (d, len(tach_tieng_ban_dau(d)), len(tach_tieng(d)))
                    for d in dong
                    if len(tach_tieng_ban_dau(d)) != len(tach_tieng(d))
                ]
                muc = (rec.get("id"), (rec.get("original_title") or "").strip(), khac[:2])
                (siet if cu and not moi else noi).append(muc)

    R: list[str] = []
    A = R.append
    A("=" * 74)
    A("SO SÁNH BẢN ĐẦU vs BẢN HIỆN TẠI CỦA rule.py")
    A("=" * 74)
    A("")
    A(f"  ĐẠT theo bản đầu    : {n_cu:,}")
    A(f"  ĐẠT theo bản hiện tại: {n_moi:,}")
    A(f"  Chênh lệch          : {n_moi - n_cu:+,}")
    A("")
    A(f"  ĐẠT -> TRƯỢT (luật siết lại) : {len(siet)}")
    A(f"  TRƯỢT -> ĐẠT (luật nới ra)   : {len(noi)}")
    A("")

    for ten, ds in (("ĐẠT -> TRƯỢT", siet), ("TRƯỢT -> ĐẠT", noi)):
        A(f"--- {ten} ---")
        if not ds:
            A("  (không có ca nào)")
        for _id, tieu_de, khac in ds:
            A(f'  id={_id}  "{tieu_de or "(không tiêu đề)"}"')
            for van_ban, cu_n, moi_n in khac:
                A(f"      {van_ban[:64]}")
                A(f"      bản đầu {cu_n} tiếng  ->  hiện tại {moi_n} tiếng")
        A("")

    A("KẾT LUẬN")
    if not siet and noi:
        A(f"  Hai sửa chữa khiến corpus có THÊM {len(noi)} bài đạt, không bớt bài nào.")
        A(f"  Cả {len(noi)} ca đều là sửa cho ĐÚNG §2.1 của tài liệu luật:")
        A('    "dấu câu không tính là tiếng" và "chữ số phải quy về cách đọc".')
    elif siet and not noi:
        A(f"  Hai sửa chữa siết corpus lại {len(siet)} bài.")
    else:
        A(f"  Hai chiều: siết {len(siet)} bài, nới {len(noi)} bài.")

    van_ban = "\n".join(R)
    (RA_BC / "so_sanh_ban_luat.txt").write_text(van_ban, encoding="utf-8")
    print(van_ban)
    return 0


if __name__ == "__main__":
    sys.exit(main())
