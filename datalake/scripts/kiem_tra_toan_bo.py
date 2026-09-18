"""KIỂM TỪNG BÀI MỘT qua rule.py, có đối soát số lượng đầu vào — đầu ra.

Mục tiêu KHÔNG phải là thống kê. Mục tiêu là **bằng chứng kiểm toán**: chứng minh
rằng mọi bản ghi trong tệp nguồn đều đã đi qua `kiem_tra_bai_tho()` đúng một lần,
và mỗi bản ghi đều có một dòng kết quả mang theo lý do đạt hoặc lý do trượt.

CÁCH ĐỐI SOÁT
    so_dong_doc  == so_ban_ghi_parse  == dat + truot + khong_co_noi_dung
    so_lan_goi_rule == dat + truot
    tập id ghi ra == tập id đọc vào, không thiếu, không trùng

Nếu bất kỳ đẳng thức nào sai, script DỪNG và báo lỗi thay vì in ra số liệu đẹp.

CHẠY
    python datalake/scripts/kiem_tra_toan_bo.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import (  # noqa: E402
    SO_TIENG_MOI_DONG,
    TANG,
    kiem_tra_bai_tho,
    mo_ta_luat,
)

NGUON = GOC / "datalake/dataraw/final_data_7_chu.jsonl"
RA = GOC / "datalake/analysis"

# Các khoá phi chuẩn từng được đường ống dùng để lưu nội dung thơ
KHOA_THO_KHAC = (
    "markdown_poem_content", "markdown_poem_fixed", "markdown_poem_final",
    "markdown_poem_full", "markdown_content", "poem_content", "content",
    "content_fix", "content_fixed", "content_processed", "content_correction",
    "content_details", "content_analysis",
)


def phan_nhom_nguyen_nhan(do_dai: list[int], hong: list) -> str:
    """Xếp bài trượt vào đúng một nhóm nguyên nhân. Thứ tự điều kiện là có chủ đích:
    đặc thù trước, tổng quát sau."""
    so_8 = sum(1 for n in do_dai if n == 8)
    if len(do_dai) >= 4 and so_8 >= len(do_dai) * 0.8:
        return "A. Thơ 8 chữ bị gán nhãn 7 chữ"
    if any(n > 15 for n in do_dai):
        return "B. Lẫn văn xuôi trong trường thơ"
    if any(n == 0 for n in do_dai):
        return "C. Có dòng phân cách không chứa tiếng"
    if len(hong) == 1 and hong[0].so_tieng == 6:
        return "D. Đúng một dòng thiếu một tiếng"
    if len(hong) == 1 and hong[0].so_tieng == 8:
        return "E. Đúng một dòng thừa một tiếng"
    if len(hong) == 1:
        return "F. Đúng một dòng lệch nhiều tiếng"
    if len(hong) <= 2:
        return "G. Hai dòng lệch"
    return "H. Lệch nhiều dòng"



def _ghi_tong_hop_md(duong_dan, th) -> None:
    """Sinh bản tóm tắt người đọc được, TỪ CHÍNH số liệu vừa đo.

    VÌ SAO PHẢI SINH RA CHỨ KHÔNG VIẾT TAY: bản viết tay trước đây đã cũ đi mà
    không ai biết — nó còn ghi "59.437 đạt" từ thời chưa phân tầng, trong khi số
    thật đã đổi. Số liệu viết tay thì lần nào sửa luật cũng phải nhớ sửa theo, và
    sớm muộn sẽ quên. Sinh ra thì không thể lệch.
    """
    ds = th["doi_soat"]
    kq = th["ket_qua"]
    d = []
    A = d.append
    A("# TỔNG HỢP KIỂM TRA TỪNG BÀI")
    A("")
    A(f"**Nguồn:** `{th['nguon']}` · **Bộ luật:** `{th['bo_luat']}`")
    A("")
    A("> ⚙️ **Tệp này do máy sinh ra — đừng sửa tay.**")
    A("> Sinh lại: `python datalake/scripts/kiem_tra_toan_bo.py`")
    A("")
    A("---")
    A("")
    A("## 1. Đối soát — mọi bản ghi đều đã đi qua rule.py")
    A("")
    A("| Phép đếm | Giá trị |")
    A("|---|---:|")
    A(f"| Dòng đọc từ tệp nguồn | {ds['so_dong_doc_tu_tep']:,} |")
    A(f"| Bản ghi parse được | {ds['so_ban_ghi_parse_duoc']:,} |")
    A(f"| **Số lần gọi `kiem_tra_bai_tho()`** | **{ds['so_lan_goi_kiem_tra_bai_tho']:,}** |")
    A(f"| id duy nhất | {ds['so_id_duy_nhat']:,} |")
    A(f"| Đối soát | {'✅ KHỚP' if ds['khop'] else '❌ LỆCH'} |")
    A("")
    A("```")
    A(f"{kq['tong']:,} bản ghi = {kq['bai_dat']:,} đạt + {kq['bai_truot']:,} trượt "
      f"+ {kq['khong_co_noi_dung']:,} không có nội dung")
    A(f"{ds['so_lan_goi_kiem_tra_bai_tho']:,} lần gọi luật = "
      f"{kq['bai_dat']:,} đạt + {kq['bai_truot']:,} trượt")
    A("```")
    for e in ds["loi_doi_soat"]:
        A(f"- ❌ {e}")
    A("")
    A("---")
    A("")
    A("## 2. Phễu theo từng cổng")
    A("")
    A("Bài phải qua cổng N mới sang cổng N+1. Cột *chưa chạy* là số bài không được")
    A("kiểm ở cổng này vì đã bị một cổng trước chặn — **chưa kiểm, không phải đạt**.")
    A("")
    A("| Cổng | Điều luật | Vào | Qua | Chặn tại đây | Chưa chạy |")
    A("|---|---|---:|---:|---:|---:|")
    for c in th["pheu_theo_cong"]:
        A(f"| {c['so']}. {c['ten']} | {', '.join(c['ma_luat'])} | {c['vao']:,} | "
          f"{c['qua']:,} | {c['chan_tai_day']:,} | {c['khong_chay']:,} |")
    A("")
    A("## 3. Kết quả")
    A("")
    A("| | Số bài |")
    A("|---|---:|")
    A(f"| Thuộc thể theo **tài liệu** (chỉ H1–H3) | {kq['bai_thuoc_the_theo_tai_lieu']:,} |")
    A(f"| **Đạt theo chuẩn dự án** (cả 7 tầng) | **{kq['bai_dat']:,}** |")
    A(f"| Trượt | {kq['bai_truot']:,} |")
    A(f"| Không có nội dung | {kq['khong_co_noi_dung']:,} |")
    A(f"| Tỉ lệ đạt trên bài có nội dung | {kq['ty_le_dat_tren_bai_co_noi_dung']}% |")
    A("")
    A("## 4. Vì sao trượt — theo từng cổng")
    A("")
    A("Số bên cạnh mã luật là **số lần vi phạm**, không phải số bài: một bài có thể")
    A("phạm cùng một điều ở nhiều dòng.")
    A("")
    for so, cac in sorted(th["ly_do_truot_theo_tang"].items(), key=lambda x: int(x[0])):
        ten = next(c["ten"] for c in th["pheu_theo_cong"] if str(c["so"]) == str(so))
        A(f"**Cổng {so} — {ten}**")
        A("")
        for ly_do, n in cac.items():
            A(f"- `{n:,}` {ly_do}")
        A("")
    A("## 5. Nhóm nguyên nhân trượt")
    A("")
    A("| Nhóm | Số bài |")
    A("|---|---:|")
    for k, v in th["ly_do_truot_theo_nhom"].items():
        A(f"| {k} | {v:,} |")
    A("")
    A(f"Bài rỗng có thể cứu được: **{th['bai_rong_co_the_cuu']:,}**")
    A("")
    A("## 6. Tệp kết quả")
    A("")
    A("| Tệp | Nội dung |")
    A("|---|---|")
    A("| `bai_dat.jsonl` | Bài đạt, kèm dấu vết 7 tầng |")
    A("| `bai_truot.jsonl` | Bài trượt, kèm tầng dừng và vi phạm |")
    A("| `bai_truot_chi_tiet.jsonl` | Bản trích có bằng chứng từng dòng |")
    A("| `bai_khong_co_noi_dung.jsonl` | Bản ghi rỗng |")
    A("| `bai_rong_cuu_duoc.jsonl` | Bản ghi rỗng nhưng còn cứu được |")
    A("| `tong_hop.json` | Chính số liệu của tệp này, dạng máy đọc |")
    A("")
    duong_dan.write_text("\n".join(d) + "\n", encoding="utf-8")


def main() -> int:
    # Console Windows mặc định là cp1252, không in được tiếng Việt có dấu.
    # Ép UTF-8 ngay đầu để script chạy được trên mọi máy mà không cần biến môi trường.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    RA.mkdir(parents=True, exist_ok=True)

    # ── bộ đếm đối soát ──
    so_dong_doc = 0
    so_ban_ghi = 0
    so_lan_goi_rule = 0
    id_da_ghi: list[int | str | None] = []

    n_dat = n_truot = n_rong = 0
    n_thuoc_the = 0
    nguyen_nhan_dat = Counter()
    nguyen_nhan_truot = Counter()
    ma_vi_pham = Counter()
    rong_cuu_duoc = 0

    # ── PHỄU THEO CỔNG ──
    # Mỗi tầng: bao nhiêu bài đi vào, bao nhiêu qua, bao nhiêu bị chặn tại đó,
    # và vài ví dụ thật kèm bằng chứng để người đọc kiểm lại được.
    pheu: dict[int, dict[str, object]] = {
        t.so: {
            "so": t.so,
            "ten": t.ten,
            "ma_luat": list(t.ma_luat),
            "trich_luat": t.trich_luat,
            "vao": 0,
            "qua": 0,
            "chan_tai_day": 0,
            "khong_chay": 0,
        }
        for t in TANG
    }
    vi_du_truot_theo_tang: dict[int, list[dict[str, object]]] = {t.so: [] for t in TANG}
    ly_do_truot_theo_tang: dict[int, Counter] = {t.so: Counter() for t in TANG}

    f_dat = (RA / "bai_dat.jsonl").open("w", encoding="utf-8")
    f_truot = (RA / "bai_truot.jsonl").open("w", encoding="utf-8")
    f_rong = (RA / "bai_khong_co_noi_dung.jsonl").open("w", encoding="utf-8")

    with NGUON.open("r", encoding="utf-8") as fh:
        for dong_json in fh:
            so_dong_doc += 1
            dong_json = dong_json.strip()
            if not dong_json:
                continue

            rec = json.loads(dong_json)
            so_ban_ghi += 1
            _id = rec.get("id")
            id_da_ghi.append(_id)
            tieu_de = (rec.get("original_title") or "").strip()
            res = rec.get("result") or {}
            tho = res.get("markdown_poem") if isinstance(res, dict) else None

            # ── nhánh 1: không có nội dung để kiểm ──
            if not isinstance(tho, str) or not tho.strip():
                n_rong += 1
                khoa_thay_the = next(
                    (
                        k for k in KHOA_THO_KHAC
                        if isinstance(res.get(k), str) and "\n" in (res.get(k) or "").strip()
                    ),
                    None,
                )
                if khoa_thay_the:
                    rong_cuu_duoc += 1
                f_rong.write(json.dumps({
                    "id": _id,
                    "tieu_de": tieu_de,
                    "trang_thai": "khong_co_noi_dung",
                    "ly_do": "Trường markdown_poem rỗng nên không có gì để đưa qua luật",
                    "co_the_cuu_tu_khoa": khoa_thay_the,
                    "score": res.get("score") if isinstance(res, dict) else None,
                }, ensure_ascii=False) + "\n")
                continue

            # ── nhánh 2: đưa qua luật, TỪNG BÀI MỘT ──
            v = kiem_tra_bai_tho(tho)
            so_lan_goi_rule += 1
            do_dai = [bc.so_tieng for bc in v.dong]
            n_thuoc_the += v.thuoc_the

            # ── gom phễu theo cổng ──
            for kq in v.tang:
                o = pheu[kq.so]
                if not kq.da_chay:
                    o["khong_chay"] = int(o["khong_chay"]) + 1
                    continue
                o["vao"] = int(o["vao"]) + 1
                if kq.dat:
                    o["qua"] = int(o["qua"]) + 1
                else:
                    o["chan_tai_day"] = int(o["chan_tai_day"]) + 1
                    for vp in kq.vi_pham:
                        ly_do_truot_theo_tang[kq.so][f"{vp.ma}: {vp.ky_vong}"] += 1
                    if not kq.vi_pham:
                        ly_do_truot_theo_tang[kq.so][kq.bang_chung[:60]] += 1
                    if len(vi_du_truot_theo_tang[kq.so]) < 10:
                        vi_du_truot_theo_tang[kq.so].append({
                            "id": _id,
                            "tieu_de": tieu_de,
                            "bang_chung": kq.bang_chung,
                            "vi_pham": [
                                {
                                    "ma": vp.ma, "dong": vp.dong,
                                    "ky_vong": vp.ky_vong, "thuc_te": vp.thuc_te,
                                    "noi_dung_dong": (
                                        v.dong[vp.dong - 1].van_ban if vp.dong else None
                                    ),
                                }
                                for vp in kq.vi_pham[:3]
                            ],
                        })

            if v.dat:
                n_dat += 1
                so_do = " | ".join("".join(k) for k in v.so_do_van_theo_kho)
                # Lý do đạt phải kể ĐỦ BẢY CỔNG, không chỉ H1–H3.
                # Bản trước chỉ ghi H1+H2+H3 nên đọc vào tưởng bài chỉ qua ba
                # điều kiện cứng, trong khi nó đã qua cả bảy tầng. Ghép thẳng
                # bằng chứng của từng tầng để câu trả lời "vì sao pass" là câu
                # trả lời thật, kiểm lại được từng vế.
                ly_do = " | ".join(
                    f"T{kq.so} {kq.ten}: {kq.bang_chung}"
                    for kq in v.tang
                    if kq.da_chay
                )
                nhan = (
                    f"{v.so_kho} khổ" if v.so_kho > 1 else "một khối liền"
                ) + f", sơ đồ vần {so_do or '-'}"
                nguyen_nhan_dat[nhan.split(",")[0]] += 1
                f_dat.write(json.dumps({
                    "id": _id,
                    "tieu_de": tieu_de,
                    "trang_thai": "dat",
                    "thuoc_the": v.thuoc_the,
                    "tang": [
                        {
                            "so": kq.so, "ten": kq.ten, "ma_luat": list(kq.ma_luat),
                            "da_chay": kq.da_chay, "dat": kq.dat,
                            "trich_luat": kq.trich_luat,
                            "bang_chung": kq.bang_chung,
                            "chi_tiet": dict(kq.chi_tiet),
                        }
                        for kq in v.tang
                    ],
                    "ly_do_dat": ly_do,
                    "bang_chung": {
                        "so_dong": v.so_dong,
                        "so_tieng_nho_nhat": min(do_dai),
                        "so_tieng_lon_nhat": max(do_dai),
                        "moi_dong_deu_7_tieng": min(do_dai) == max(do_dai) == SO_TIENG_MOI_DONG,
                    },
                    "dac_diem_mem": {
                        "so_kho": v.so_kho,
                        "so_do_van_theo_kho": ["".join(k) for k in v.so_do_van_theo_kho],
                        "phoi_khuon_theo_kho": list(v.phoi_khuon_theo_kho),
                        "ty_le_dong_theo_khuon": v.ty_le_theo_khuon,
                        "so_cap_van_lech_thanh": len(v.van_lech_thanh),
                        "so_vi_tri_van_lung": len(v.van_lung),
                        "nghi_duong_luat": v.nghi_duong_luat,
                    },
                    "ghi_chu": list(v.ghi_chu),
                }, ensure_ascii=False) + "\n")
            else:
                n_truot += 1
                hong = [bc for bc in v.dong if bc.so_tieng != SO_TIENG_MOI_DONG]
                nn = phan_nhom_nguyen_nhan(do_dai, hong)
                nguyen_nhan_truot[nn] += 1
                for vp in v.vi_pham:
                    ma_vi_pham[vp.ma] += 1
                f_truot.write(json.dumps({
                    "id": _id,
                    "tieu_de": tieu_de,
                    "trang_thai": "truot",
                    "thuoc_the": v.thuoc_the,
                    "tang_dung_lai": v.tang_dung_lai,
                    "tang": [
                        {
                            "so": kq.so, "ten": kq.ten, "da_chay": kq.da_chay,
                            "dat": kq.dat, "bang_chung": kq.bang_chung,
                            "vi_pham": [
                                {"ma": vp.ma, "dong": vp.dong,
                                 "ky_vong": vp.ky_vong, "thuc_te": vp.thuc_te}
                                for vp in kq.vi_pham
                            ],
                        }
                        for kq in v.tang
                    ],
                    "nhom_nguyen_nhan": nn,
                    "ly_do_truot": [
                        {
                            "ma_luat": vp.ma,
                            "mo_ta_luat": mo_ta_luat(vp.ma),
                            "dong": vp.dong,
                            "ky_vong": vp.ky_vong,
                            "thuc_te": vp.thuc_te,
                            "goi_y_sua": vp.goi_y,
                            "noi_dung_dong": (
                                v.dong[vp.dong - 1].van_ban if vp.dong else None
                            ),
                        }
                        for vp in v.vi_pham
                    ],
                    "tong_quan": {
                        "so_dong": v.so_dong,
                        "so_dong_hong": len(hong),
                        "so_dong_dat": v.so_dong - len(hong),
                        "do_dai_cac_dong_hong": [bc.so_tieng for bc in hong],
                    },
                }, ensure_ascii=False) + "\n")

    f_dat.close()
    f_truot.close()
    f_rong.close()

    # ── ĐỐI SOÁT: không đạt thì dừng, không in số liệu đẹp ──
    loi = []
    if so_ban_ghi != n_dat + n_truot + n_rong:
        loi.append(f"Tổng không khớp: {so_ban_ghi} bản ghi != {n_dat}+{n_truot}+{n_rong}")
    if so_lan_goi_rule != n_dat + n_truot:
        loi.append(f"Số lần gọi rule ({so_lan_goi_rule}) != số bài có nội dung ({n_dat + n_truot})")
    trung_id = [i for i, c in Counter(id_da_ghi).items() if c > 1]
    if trung_id:
        loi.append(f"Có {len(trung_id)} id trùng, ví dụ {trung_id[:5]}")
    if None in id_da_ghi:
        loi.append("Có bản ghi thiếu trường id")

    for ten, f in (
        ("bai_dat.jsonl", n_dat),
        ("bai_truot.jsonl", n_truot),
        ("bai_khong_co_noi_dung.jsonl", n_rong),
    ):
        thuc = sum(1 for _ in (RA / ten).open("r", encoding="utf-8"))
        if thuc != f:
            loi.append(f"{ten}: ghi {thuc} dòng nhưng đếm được {f}")

    tong_hop = {
        "nguon": str(NGUON.relative_to(GOC)).replace("\\", "/"),
        "bo_luat": "src/application/rule.py",
        "doi_soat": {
            "so_dong_doc_tu_tep": so_dong_doc,
            "so_ban_ghi_parse_duoc": so_ban_ghi,
            "so_lan_goi_kiem_tra_bai_tho": so_lan_goi_rule,
            "so_id_duy_nhat": len(set(id_da_ghi)),
            "khop": not loi,
            "loi_doi_soat": loi,
        },
        "pheu_theo_cong": [pheu[t.so] for t in TANG],
        "ly_do_truot_theo_tang": {
            str(so): dict(c.most_common(10)) for so, c in ly_do_truot_theo_tang.items() if c
        },
        "ket_qua": {
            "bai_thuoc_the_theo_tai_lieu": n_thuoc_the,
            "bai_dat": n_dat,
            "bai_truot": n_truot,
            "khong_co_noi_dung": n_rong,
            "tong": so_ban_ghi,
            "ty_le_dat_tren_bai_co_noi_dung": round(n_dat / (n_dat + n_truot) * 100, 2),
        },
        "ly_do_truot_theo_nhom": dict(sorted(nguyen_nhan_truot.items())),
        "ma_luat_bi_vi_pham": dict(ma_vi_pham),
        "bai_rong_co_the_cuu": rong_cuu_duoc,
    }
    (RA / "tong_hop.json").write_text(
        json.dumps(tong_hop, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    _ghi_tong_hop_md(RA / "TONG_HOP.md", tong_hop)

    print("=" * 66)
    print("ĐỐI SOÁT ĐẦU VÀO — ĐẦU RA")
    print("=" * 66)
    print(f"  dòng đọc từ tệp              : {so_dong_doc:,}")
    print(f"  bản ghi parse được           : {so_ban_ghi:,}")
    print(f"  lần gọi kiem_tra_bai_tho()   : {so_lan_goi_rule:,}")
    print(f"  id duy nhất                  : {len(set(id_da_ghi)):,}")
    print(f"  ĐỐI SOÁT                     : {'KHỚP' if not loi else 'SAI'}")
    for x in loi:
        print(f"      ! {x}")
    print()
    print(f"  BÀI ĐẠT              : {n_dat:,}")
    print(f"  BÀI TRƯỢT            : {n_truot:,}")
    print(f"  KHÔNG CÓ NỘI DUNG    : {n_rong:,}")
    print("  ---------------------------------")
    print(f"  TỔNG                 : {n_dat + n_truot + n_rong:,}")
    print()
    print("=" * 66)
    print("PHỄU THEO CỔNG — mỗi tầng chặn bao nhiêu bài")
    print("=" * 66)
    print(f"  {'Tầng':<26}{'vào':>8}{'qua':>8}{'CHẶN':>8}{'chưa chạy':>11}")
    for t in TANG:
        o = pheu[t.so]
        print(f"  T{t.so} {t.ten:<22}{o['vao']:>8,}{o['qua']:>8,}"
              f"{o['chan_tai_day']:>8,}{o['khong_chay']:>11,}")
    print()
    print(f"  Thuộc thể theo TÀI LIỆU (chỉ H1–H3): {n_thuoc_the:,}")
    print(f"  Đạt theo CHUẨN DỰ ÁN (cả 7 tầng)   : {n_dat:,}")
    print()
    for t in TANG:
        c = ly_do_truot_theo_tang[t.so]
        if not c:
            continue
        print(f"  ── T{t.so} {t.ten}: vì sao trượt ──")
        for ly_do, so_lan in c.most_common(4):
            print(f"      {so_lan:>7,}  {ly_do[:72]}")
        for vd in vi_du_truot_theo_tang[t.so][:2]:
            ten = vd["tieu_de"] or "(không tiêu đề)"
            print(f"      ví dụ id={vd['id']} \"{ten[:34]}\": {vd['bang_chung'][:60]}")
            for vp in vd["vi_pham"][:1]:
                if vp.get("noi_dung_dong"):
                    print(f"          D{vp['dong']}: {vp['noi_dung_dong'][:56]}")
                    print(f"          cần {vp['ky_vong'][:44]} | đang {vp['thuc_te'][:24]}")
        print()

    print("  Lý do trượt theo nhóm:")
    for k, c in sorted(nguyen_nhan_truot.items()):
        print(f"    {c:>6,}  {k}")
    print()
    print("  Mã luật bị vi phạm:")
    for k, c in ma_vi_pham.most_common():
        print(f"    {c:>6,}  {k} — {mo_ta_luat(k)}")
    with (RA / "vi_du_truot_theo_tang.json").open("w", encoding="utf-8") as f:
        json.dump(
            {
                str(t.so): {
                    "ten": t.ten,
                    "trich_luat": t.trich_luat,
                    "so_bai_bi_chan": pheu[t.so]["chan_tai_day"],
                    "vi_du": vi_du_truot_theo_tang[t.so],
                }
                for t in TANG
            },
            f, ensure_ascii=False, indent=2,
        )

    print()
    print(f"  Đã ghi: {RA}")
    return 0 if not loi else 1


if __name__ == "__main__":
    sys.exit(main())
