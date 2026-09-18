"""Kiểm chứng ĐỘC LẬP kết quả của kiem_tra_toan_bo.py.

Script này không tin bộ đếm của script kia. Nó đọc lại tệp nguồn và ba tệp kết quả,
rồi kiểm ba tính chất:

  1. PHÂN HOẠCH  — tập id trong ba tệp kết quả hợp lại đúng bằng tập id nguồn,
                   và ba tập đôi một rời nhau. Không bài nào bị bỏ sót hay đếm hai lần.
  2. LẤY MẪU     — chọn ngẫu nhiên N bài, chạy lại rule.py trên văn bản gốc và
                   đối chiếu phán quyết với những gì đã ghi.
  3. NHẤT QUÁN   — mọi bài trong bai_dat.jsonl phải có moi_dong_deu_7_tieng = true;
                   mọi bài trong bai_truot.jsonl phải có ít nhất một vi phạm.

CHẠY
    python datalake/scripts/doi_soat_ket_qua.py [số_mẫu]
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import SO_TIENG_MOI_DONG, kiem_tra_bai_tho  # noqa: E402

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"
RA = GOC / "datalake/analysis"


def nap_id(ten: str) -> set:
    return {
        json.loads(d)["id"]
        for d in (RA / ten).open("r", encoding="utf-8")
        if d.strip()
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    so_mau = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    loi: list[str] = []

    # ── 1. PHÂN HOẠCH ──
    id_nguon = set()
    van_ban_theo_id: dict = {}
    for d in NGUON.open("r", encoding="utf-8"):
        d = d.strip()
        if not d:
            continue
        rec = json.loads(d)
        id_nguon.add(rec["id"])
        tho = (rec.get("result") or {}).get("markdown_poem")
        if isinstance(tho, str) and tho.strip():
            van_ban_theo_id[rec["id"]] = tho

    id_dat = nap_id("bai_dat.jsonl")
    id_truot = nap_id("bai_truot.jsonl")
    id_rong = nap_id("bai_khong_co_noi_dung.jsonl")

    hop = id_dat | id_truot | id_rong
    thieu = id_nguon - hop
    thua = hop - id_nguon
    if thieu:
        loi.append(f"{len(thieu)} id có trong nguồn nhưng KHÔNG có trong kết quả: {list(thieu)[:5]}")
    if thua:
        loi.append(f"{len(thua)} id có trong kết quả nhưng KHÔNG có trong nguồn: {list(thua)[:5]}")
    for ten_a, a, ten_b, b in (
        ("đạt", id_dat, "trượt", id_truot),
        ("đạt", id_dat, "rỗng", id_rong),
        ("trượt", id_truot, "rỗng", id_rong),
    ):
        chung = a & b
        if chung:
            loi.append(f"{len(chung)} id nằm ở cả '{ten_a}' và '{ten_b}': {list(chung)[:5]}")

    print("=" * 66)
    print("1. PHÂN HOẠCH")
    print("=" * 66)
    print(f"  id trong nguồn        : {len(id_nguon):,}")
    print(f"  id trong bai_dat      : {len(id_dat):,}")
    print(f"  id trong bai_truot    : {len(id_truot):,}")
    print(f"  id trong bai_rong     : {len(id_rong):,}")
    print(f"  hợp ba tập            : {len(hop):,}")
    print(f"  thiếu / thừa / chồng  : {len(thieu)} / {len(thua)} / "
          f"{len(id_dat & id_truot) + len(id_dat & id_rong) + len(id_truot & id_rong)}")

    # ── 2. LẤY MẪU, CHẠY LẠI ──
    print()
    print("=" * 66)
    print(f"2. LẤY MẪU NGẪU NHIÊN {so_mau} BÀI — CHẠY LẠI rule.py")
    print("=" * 66)
    random.seed(20260917)
    ghi_nhan: dict = {}
    for ten, trang_thai in (("bai_dat.jsonl", "dat"), ("bai_truot.jsonl", "truot")):
        for d in (RA / ten).open("r", encoding="utf-8"):
            if d.strip():
                r = json.loads(d)
                ghi_nhan[r["id"]] = (trang_thai, r)

    ung_vien = [i for i in ghi_nhan if i in van_ban_theo_id]
    mau = random.sample(ung_vien, min(so_mau, len(ung_vien)))
    lech = 0
    for _id in mau:
        trang_thai_ghi, ban_ghi = ghi_nhan[_id]
        v = kiem_tra_bai_tho(van_ban_theo_id[_id])
        trang_thai_that = "dat" if v.dat else "truot"
        if trang_thai_that != trang_thai_ghi:
            lech += 1
            loi.append(f"id={_id}: ghi '{trang_thai_ghi}' nhưng chạy lại ra '{trang_thai_that}'")
            continue
        if v.dat:
            if ban_ghi["bang_chung"]["so_dong"] != v.so_dong:
                lech += 1
                loi.append(f"id={_id}: số dòng ghi khác số dòng chạy lại")
        else:
            hong_that = sum(1 for bc in v.dong if bc.so_tieng != SO_TIENG_MOI_DONG)
            if ban_ghi["tong_quan"]["so_dong_hong"] != hong_that:
                lech += 1
                loi.append(f"id={_id}: số dòng hỏng ghi khác số chạy lại")
    print(f"  mẫu kiểm              : {len(mau):,}")
    print(f"  lệch                  : {lech}")

    # ── 3. NHẤT QUÁN NỘI TẠI ──
    print()
    print("=" * 66)
    print("3. NHẤT QUÁN NỘI TẠI CỦA TỆP KẾT QUẢ")
    print("=" * 66)
    sai_dat = 0
    for d in (RA / "bai_dat.jsonl").open("r", encoding="utf-8"):
        if not d.strip():
            continue
        r = json.loads(d)
        bc = r["bang_chung"]
        if not bc["moi_dong_deu_7_tieng"] or bc["so_tieng_nho_nhat"] != SO_TIENG_MOI_DONG:
            sai_dat += 1
    sai_truot = 0
    for d in (RA / "bai_truot.jsonl").open("r", encoding="utf-8"):
        if not d.strip():
            continue
        r = json.loads(d)
        if not r["ly_do_truot"] or r["tong_quan"]["so_dong_hong"] < 0:
            sai_truot += 1
    if sai_dat:
        loi.append(f"{sai_dat} bài trong bai_dat.jsonl không chứng minh được mọi dòng 7 tiếng")
    if sai_truot:
        loi.append(f"{sai_truot} bài trong bai_truot.jsonl không có lý do trượt")
    print(f"  bài 'đạt' thiếu bằng chứng : {sai_dat}")
    print(f"  bài 'trượt' thiếu lý do    : {sai_truot}")

    print()
    print("=" * 66)
    print("KẾT LUẬN: " + ("TẤT CẢ ĐỀU KHỚP" if not loi else f"CÓ {len(loi)} VẤN ĐỀ"))
    print("=" * 66)
    for x in loi[:20]:
        print(f"  ! {x}")
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
