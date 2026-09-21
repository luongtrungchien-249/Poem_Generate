"""Rút các PHÂN BỐ từ hai tệp kết quả .jsonl ra một tệp nhỏ, track được.

VÌ SAO CÓ SCRIPT NÀY — một lần CI đỏ đã dạy:

    `doi_soat_tai_lieu.py` lấy khoảng 100 con số bằng cách mở thẳng
    `bai_dat.jsonl` (33 MB) và `bai_truot.jsonl`. Hai tệp đó nằm trong
    `.gitignore` — cố ý, vì chúng quá lớn để đưa vào repo.

    Hệ quả: script chạy xanh trên máy có sẵn dữ liệu, nhưng trên một
    checkout sạch (CI) thì chết ngay ở dòng `open()`. Bước đối soát —
    thứ sinh ra để chặn số bịa — trở thành bước duy nhất làm đỏ CI.

    Bài học: một phép kiểm chỉ chạy được trên MỘT máy thì không phải
    phép kiểm, nó là thói quen cá nhân.

CÁCH SỬA: các con số ấy đều là PHÂN BỐ TỔNG HỢP (đếm bài theo số dòng, theo
số khổ, theo sơ đồ vần…), không phải dữ liệu thô. Chúng nhỏ. Rút ra một tệp
JSON vài KB rồi track tệp đó thì `doi_soat_tai_lieu.py` chạy được ở mọi nơi,
và vẫn kiểm đủ 100% số liệu thay vì phải bỏ bớt.

    bai_dat.jsonl      33 MB   .gitignore   ─┐
                                              ├─►  phan_bo.json   ~6 KB   ✅ track
    bai_truot.jsonl    ~MB     .gitignore   ─┘

KHÔNG ĐƯỢC SỬA TAY `phan_bo.json`. Nó là tệp máy sinh; sửa tay đúng vào chỗ
mà cả bộ đối soát dựng ra để chống.

CHẠY
    python datalake/scripts/xuat_phan_bo.py

`kiem_tra_toan_bo.py` gọi hàm `xuat()` ở cuối lượt chạy, nên hai tệp không thể
lệch nhau. Chỉ cần chạy tay khi đã có sẵn .jsonl mà chưa có phan_bo.json.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
THU_MUC = GOC / "datalake" / "analysis"
RA = THU_MUC / "phan_bo.json"


def _dem(duong_dan: Path) -> int:
    return sum(1 for _ in duong_dan.open(encoding="utf-8"))


def tinh_phan_bo() -> dict[str, dict[str, int]]:
    """Đếm mọi phân bố mà báo cáo trích dẫn, từ hai tệp kết quả.

    Trả về dict lồng: nhóm -> {nhãn: số đếm}. Giữ nhãn dạng chuỗi để tệp ra
    đọc được bằng mắt, và để `doi_soat_tai_lieu.py` dựng lại đúng câu mô tả
    nguồn gốc của từng con số.
    """
    bai_dat = THU_MUC / "bai_dat.jsonl"
    bai_truot = THU_MUC / "bai_truot.jsonl"
    for tep in (bai_dat, bai_truot):
        if not tep.exists():
            raise SystemExit(
                f"❌ Thiếu {tep.relative_to(GOC)}.\n"
                "   Chạy `python datalake/scripts/kiem_tra_toan_bo.py` để sinh lại."
            )

    dong: Counter[int] = Counter()
    kho: Counter[int] = Counter()
    sodo: Counter[str] = Counter()
    lung = lech = nghi_dat = 0

    for dg in bai_dat.open(encoding="utf-8"):
        r = json.loads(dg)
        t = {k["so"]: k for k in r["tang"]}
        dong[t[1]["chi_tiet"]["so_dong"]] += 1
        kho[t[7]["chi_tiet"]["so_kho"]] += 1
        # QĐ-7b (18/09/2026): khoá đổi từ "cum_bon_dong_khop" sang
        # "cum_co_van_chan" — tiêu chí nay là CÓ vần chân, không phải khớp sơ đồ.
        for c in t[5]["chi_tiet"]["cum_co_van_chan"]:
            sodo[c["so_do"]] += 1
        dm = r["dac_diem_mem"]
        lung += dm["so_vi_tri_van_lung"] > 0
        lech += dm["so_cap_van_lech_thanh"] > 0
        # Đọc từ chi_tiet của tầng 3, KHÔNG từ cờ cấp bài: cờ
        # `PoemVerdict.nghi_duong_luat` suy bằng `not tang3.dat`, mà tầng 3 nay
        # luôn dat=True, nên cờ ấy luôn False. chi_tiet mới là số thật.
        if t[3]["chi_tiet"].get("nghi_duong_luat"):
            nghi_dat += 1

    sd5: Counter[str] = Counter()
    sd1: Counter[int] = Counter()
    du1: Counter[int] = Counter()
    cong: Counter[int] = Counter()
    nghi_truot = 0

    for dg in bai_truot.open(encoding="utf-8"):
        r = json.loads(dg)
        c = r["tang_dung_lai"]
        cong[c] += 1
        t3 = next((k for k in r["tang"] if k["so"] == 3), None)
        if t3 and "giống khuôn Đường luật" in t3.get("bang_chung", ""):
            nghi_truot += 1
        if c == 5:
            bc = next(k for k in r["tang"] if k["so"] == 5)["bang_chung"]
            if "dòng 1–4: " in bc:
                sd5[bc.split("dòng 1–4: ")[1].split(";")[0]] += 1
        elif c == 1:
            sd = r["tong_quan"]["so_dong"]
            sd1[sd] += 1
            du1[sd % 4] += 1

    so_dong_tep = {
        ten: _dem(THU_MUC / f"{ten}.jsonl")
        for ten in (
            "bai_dat", "bai_truot", "bai_truot_chi_tiet", "bai_rong_cuu_duoc",
            "bai_khong_co_noi_dung", "dong_nghi_ngo_trong_bai_dat",
        )
        if (THU_MUC / f"{ten}.jsonl").exists()
    }

    return {
        "bai_dat_theo_so_dong": {str(k): v for k, v in sorted(dong.items())},
        "bai_dat_theo_so_kho": {str(k): v for k, v in sorted(kho.items())},
        "cum_co_van_chan_theo_so_do": dict(sodo.most_common()),
        "truot_cong5_theo_so_do": dict(sd5.most_common()),
        "truot_cong1_theo_so_dong": {str(k): v for k, v in sorted(sd1.items())},
        "truot_cong1_theo_du": {str(k): v for k, v in sorted(du1.items())},
        "truot_theo_cong_dung_lai": {str(k): v for k, v in sorted(cong.items())},
        "so_dong_tung_tep_ket_qua": so_dong_tep,
        "tong": {
            "cum_co_van_chan": sum(sodo.values()),
            "bai_dat_co_van_lung": lung,
            "bai_dat_co_van_lech_thanh": lech,
            "nghi_duong_luat_ma_dat": nghi_dat,
            "nghi_duong_luat_ma_truot": nghi_truot,
        },
    }


def xuat() -> Path:
    """Tính rồi ghi `phan_bo.json`. Trả về đường dẫn tệp đã ghi."""
    du_lieu = {
        "_ghi_chu": (
            "Tệp do máy sinh — ĐỪNG SỬA TAY. "
            "Sinh lại: python datalake/scripts/xuat_phan_bo.py"
        ),
        "nguon": ["datalake/analysis/bai_dat.jsonl", "datalake/analysis/bai_truot.jsonl"],
        **tinh_phan_bo(),
    }
    RA.write_text(
        json.dumps(du_lieu, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return RA


def main() -> int:
    # Console Windows mặc định cp1252, không in nổi ✅ hay tiếng Việt có dấu.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tep = xuat()
    du_lieu = json.loads(tep.read_text(encoding="utf-8"))
    so_muc = sum(
        len(v) for k, v in du_lieu.items() if isinstance(v, dict) and not k.startswith("_")
    )
    print(f"✅ Đã ghi {tep.relative_to(GOC)} — {so_muc} mục, {tep.stat().st_size:,} byte")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
