"""Tuyển một tập thơ mẫu NHỎ, COMMIT ĐƯỢC, từ 24.366 bài đã qua bảy tầng.

    python datalake/scripts/tuyen_tho_mau.py

VÌ SAO CẦN TỆP NÀY — rủi ro R4 của `Plan_Thi_Cong_DeepAgent.md`

`datalake/analysis/bai_dat.jsonl` nặng 266 MB và bị gitignore. Nếu few-shot chỉ
dựa vào nó thì trên mọi checkout sạch, cơ chế few-shot **im lặng tắt** — hệ thống
vẫn chạy (lùi về zero-shot đúng §32), nên không ai phát hiện. Tệp tuyển làm cho
tính năng này tái lập được trên máy mới.

════ PHƯƠNG PHÁP LẤY MẪU — ghi rõ để không bị nghi cherry-pick ════

Cám dỗ ở đây rất thật: chọn tay 300 bài "hay nhất" thì ví dụ few-shot đẹp hơn, số
liệu sinh thơ đẹp hơn, và không ai kiểm được. Đó đúng là kiểu sai lầm mà §1.1 của
`Plan_Rule_Phan_Tang.md` ghi lại — chọn ngưỡng theo số bài sống sót.

Vì vậy phép lấy mẫu ở đây là TẤT ĐỊNH và MÙ VỚI CHẤT LƯỢNG:

    1. Chia bài theo SỐ DÒNG (4, 8, 12, 16, còn lại) — đây là chiều duy nhất được
       phép ảnh hưởng tới việc chọn, vì bộ chọn few-shot ưu tiên cùng số dòng.
    2. Trong mỗi nhóm, lấy CÁCH ĐỀU theo thứ tự xuất hiện trong tệp gốc — không
       xếp hạng, không chấm điểm, không đọc nội dung.
    3. Hạn ngạch mỗi nhóm cố định, khai báo ở `HAN_NGACH` ngay dưới đây.

Không có bước nào nhìn vào "bài này hay không". Chạy lại trên cùng tệp gốc luôn
cho ra đúng tập ấy.
"""

from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import kiem_tra_bai_tho  # noqa: E402

NGUON = GOC / "datalake" / "analysis" / "bai_dat.jsonl"
DICH = GOC / "datalake" / "corpus_tuyen" / "tho_mau.jsonl"

# Hạn ngạch theo số dòng. Nghiêng về 8 dòng vì đó là cỡ phổ biến nhất của thể;
# vẫn giữ mặt 4/12/16 để bộ chọn có ví dụ cùng cỡ cho mọi yêu cầu thường gặp.
HAN_NGACH: dict[str, int] = {"4": 60, "8": 140, "12": 40, "16": 30, "khac": 30}


def _nhom(so_dong: int) -> str:
    return str(so_dong) if str(so_dong) in HAN_NGACH else "khac"


def main() -> int:
    if not NGUON.exists():
        print(f"Không thấy {NGUON.relative_to(GOC)}.")
        print("Chạy `python datalake/scripts/kiem_tra_toan_bo.py` để sinh lại trước.")
        return 1

    theo_nhom: dict[str, list[dict]] = defaultdict(list)
    doc = 0
    with NGUON.open(encoding="utf-8") as f:
        for dong in f:
            dong = dong.strip()
            if not dong:
                continue
            try:
                r = json.loads(dong)
            except json.JSONDecodeError:
                continue
            doc += 1
            tho = r.get("tho")
            if not isinstance(tho, str) or not tho.strip():
                continue
            n = len([d for d in tho.splitlines() if d.strip()])
            theo_nhom[_nhom(n)].append(r)

    print(f"Đọc {doc:,} bản ghi.")
    for k in sorted(theo_nhom):
        print(f"  nhóm {k:>5}: {len(theo_nhom[k]):,} bài")

    chon: list[dict] = []
    for nhom, han in HAN_NGACH.items():
        ds = theo_nhom.get(nhom, [])
        if not ds:
            continue
        # Lấy CÁCH ĐỀU: bước nhảy = tổng / hạn ngạch. Không xáo trộn, không random
        # seed — tất định tuyệt đối, chạy lại cho đúng tập cũ.
        buoc = max(1, len(ds) // han)
        chon.extend(ds[::buoc][:han])

    # Kiểm lại từng bài bằng rule.py TRƯỚC khi ghi. Tệp nguồn có thể được sinh từ
    # một bản luật cũ hơn; ghi bài không đạt vào tập mẫu là gieo mầm lỗi cho mọi
    # lần sinh thơ về sau.
    ra: list[dict] = []
    loai = 0
    for r in chon:
        tho = r["tho"]
        if not kiem_tra_bai_tho(tho).dat:
            loai += 1
            continue
        # Chỉ giữ trường CẦN cho few-shot. Bỏ `dong`/`tang` (chiếm >95% dung lượng)
        # vì `dataset.tu_ban_ghi` tự tính lại hết bằng rule.py.
        ra.append({"id": r.get("id"), "tieu_de": r.get("tieu_de", ""), "tho": tho})

    DICH.parent.mkdir(parents=True, exist_ok=True)
    with DICH.open("w", encoding="utf-8") as f:
        for r in ra:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    kb = DICH.stat().st_size / 1024
    print(f"\nĐã ghi {len(ra):,} bài vào {DICH.relative_to(GOC)} ({kb:.0f} KB)")
    if loai:
        print(f"⚠️  {loai} bài bị loại vì KHÔNG đạt khi chạy lại rule.py — "
              "tệp nguồn có thể cũ hơn bộ luật hiện tại.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
