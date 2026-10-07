"""NHẬP KHO HF — Plan_PoeTone GĐ0.2 (QĐ-P6, 26/09/2026).

    python datalake/scripts/nhap_kho_hf.py

Nguồn: `phamson02/vietnamese-poetry-corpus` trên HuggingFace, giấy phép **CC-BY-4.0**.
Mọi báo cáo dùng dữ liệu này PHẢI ghi nguồn. Dữ liệu thô không commit
(`datalake/hf/` nằm trong `.gitignore`); chỉ `tong_hop.json` được commit.

Tải tệp nguồn trước (163 MB, chỉ cần một lần):

    curl -L -o datalake/hf/poems_dataset.csv \\
      https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus/resolve/main/poems_dataset.csv

════ KHÔNG TIN NHÃN ════

`specific_genre` là nhãn của trang nguồn, không phải phán quyết luật. Mọi bài đều
đi qua `rule.kiem_tra_bai_tho`; nhãn chỉ dùng để CHIA KHO:

    bay_chu      specific_genre == "bảy chữ"           kho chính, ứng viên làm ví dụ
    duong_luat   thất ngôn tứ tuyệt / bát cú / cổ phong /
                 đường luật biến thể (genre "bảy chữ")  chỉ để đối chiếu và probe,
                                                         KHÔNG dùng làm ví dụ

════ ĐỊNH DẠNG NGUỒN ════

Mỗi dòng thơ kết thúc bằng ` <`, dòng sau mở bằng `> `; một dòng chỉ còn `<` hay
`>` là chỗ ngắt khổ. Văn bản đã bị hạ chữ thường và dấu câu có khoảng trắng đứng
trước (`lạ , trong`). Script chỉ gỡ hai ký hiệu `<`/`>` — không sửa chữ nào khác:
`tach_tieng` của `rule.py` đã bỏ dấu câu đứng riêng.

════ KHỬ TRÙNG ════

Kho HF và `final_data_7_chu.jsonl` có thể cùng gốc. Mỗi bài được gắn cờ
`trung_final_data` (băm dãy tiếng đã hạ chữ thường) thay vì bị xoá: bỏ bài là
quyết định của người dùng kho, còn cờ thì cho phép đếm cả hai cách.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import kiem_tra_bai_tho, tach_tieng  # noqa: E402

THU_MUC = GOC / "datalake" / "hf"
NGUON = THU_MUC / "poems_dataset.csv"
FINAL_DATA = GOC / "datalake" / "dataraw" / "final_data_7_chu.jsonl"

KHO_DUONG_LUAT = frozenset(
    {"thất ngôn tứ tuyệt", "thất ngôn bát cú", "thất ngôn cổ phong", "đường luật biến thể"}
)
GHI_NGUON = (
    "phamson02/vietnamese-poetry-corpus (HuggingFace), CC-BY-4.0 — "
    "https://huggingface.co/datasets/phamson02/vietnamese-poetry-corpus"
)


def chuan_hoa_noi_dung(tho: str) -> str:
    """Gỡ ký hiệu `<` `>` của nguồn; dòng rỗng giữ lại làm ranh giới khổ."""
    ra: list[str] = []
    for dong in tho.split("\n"):
        d = dong.strip()
        if d.startswith(">"):
            d = d[1:]
        if d.endswith("<"):
            d = d[:-1]
        ra.append(d.strip())
    # Gộp dòng rỗng liên tiếp và cắt rỗng hai đầu.
    gon: list[str] = []
    for d in ra:
        if d or (gon and gon[-1]):
            gon.append(d)
    while gon and not gon[-1]:
        gon.pop()
    return "\n".join(gon)


def bam_noi_dung(tho: str) -> str:
    """Băm dãy tiếng đã hạ chữ thường — bỏ qua dấu câu, hoa thường, ngắt khổ."""
    tieng: list[str] = []
    for dong in tho.splitlines():
        tieng.extend(t.lower() for t in tach_tieng(dong))
    return hashlib.sha1(" ".join(tieng).encode("utf-8")).hexdigest()


def _bam_final_data() -> set[str]:
    if not FINAL_DATA.exists():
        return set()
    bam: set[str] = set()
    with FINAL_DATA.open(encoding="utf-8") as f:
        for dong in f:
            try:
                rec = json.loads(dong)
            except json.JSONDecodeError:
                continue
            res = rec.get("result")
            tho = res.get("markdown_poem") if isinstance(res, dict) else None
            if tho:
                bam.add(bam_noi_dung(tho))
    return bam


def main() -> int:
    if not NGUON.exists():
        print(f"Thiếu {NGUON.relative_to(GOC)} — xem lệnh tải trong docstring.")
        return 1

    csv.field_size_limit(10**9)
    bam_final = _bam_final_data()
    ra = {
        (kho, kq): (THU_MUC / f"{kho}_{kq}.jsonl").open("w", encoding="utf-8")
        for kho in ("bay_chu", "duong_luat")
        for kq in ("dat", "truot")
    }
    dem: Counter[str] = Counter()
    tang_chet: dict[str, Counter[int]] = {"bay_chu": Counter(), "duong_luat": Counter()}
    trung: Counter[str] = Counter()
    bam_da_gap: set[str] = set()

    try:
        with NGUON.open(encoding="utf-8", newline="") as f:
            for i, r in enumerate(csv.DictReader(f)):
                dem["tong_nguon"] += 1
                sg = r["specific_genre"]
                if sg == "bảy chữ":
                    kho = "bay_chu"
                elif r["genre"] == "bảy chữ" and sg in KHO_DUONG_LUAT:
                    kho = "duong_luat"
                else:
                    continue

                tho = chuan_hoa_noi_dung(r["content"])
                if not tho:
                    dem[f"{kho}_rong"] += 1
                    continue
                bam = bam_noi_dung(tho)
                if bam in bam_da_gap:
                    dem[f"{kho}_trung_noi_bo_hf"] += 1
                    continue
                bam_da_gap.add(bam)

                v = kiem_tra_bai_tho(tho)
                kq = "dat" if v.dat else "truot"
                dem[f"{kho}_{kq}"] += 1
                if not v.dat and v.tang_dung_lai:
                    tang_chet[kho][v.tang_dung_lai] += 1
                trung_fd = bam in bam_final
                if trung_fd:
                    trung[f"{kho}_{kq}"] += 1

                ra[(kho, kq)].write(
                    json.dumps(
                        {
                            "id": f"hf-{i}",
                            "title": r["title"],
                            "author": r["author"],
                            "url": r["url"],
                            "period": r["period"],
                            "specific_genre": sg,
                            "poem": tho,
                            "so_dong": v.so_dong,
                            "tang_dung_lai": v.tang_dung_lai,
                            "trung_final_data": trung_fd,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
    finally:
        for f in ra.values():
            f.close()

    tong_hop = {
        "nguon": GHI_NGUON,
        "so_ban_ghi_nguon": dem["tong_nguon"],
        "so_bai_final_data_de_khu_trung": len(bam_final),
        "kho": {
            kho: {
                "dat": dem[f"{kho}_dat"],
                "truot": dem[f"{kho}_truot"],
                "rong": dem[f"{kho}_rong"],
                "trung_noi_bo_hf_da_bo": dem[f"{kho}_trung_noi_bo_hf"],
                "dat_trung_final_data": trung[f"{kho}_dat"],
                "truot_trung_final_data": trung[f"{kho}_truot"],
                "tang_chet": dict(sorted(tang_chet[kho].items())),
            }
            for kho in ("bay_chu", "duong_luat")
        },
    }
    (THU_MUC / "tong_hop.json").write_text(
        json.dumps(tong_hop, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(tong_hop, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
