"""Đối soát MỌI con số trong tài liệu .md với nguồn sự thật của nó.

VÌ SAO CÓ SCRIPT NÀY — một bài học đã trả giá:

    Ngày 18/09/2026 tôi chạy một lệnh thay-thế-hàng-loạt để cập nhật số liệu sau
    khi sửa luật, và trong danh sách thay thế có cặp `4.288 -> 3.975`. Con số
    3.975 **chưa từng được đo**; tôi gõ nó ra theo cảm tính. Nó lọt vào ba tài
    liệu và nằm đó cho tới khi tình cờ bị phát hiện.

    Số liệu gõ tay thì sớm muộn cũng lệch. Cách chặn duy nhất là đối chiếu bằng
    máy với tệp do máy sinh.

HAI NGUỒN SỰ THẬT
    datalake/analysis/tong_hop.json   số liệu corpus  (sinh bởi kiem_tra_toan_bo.py)
    src/application/rule.py           bảng luật + bảng tầng

CÁCH ĐỌC KẾT QUẢ
    ❌ THIẾU     tài liệu không nhắc một con số lẽ ra phải có  -> tài liệu cũ
    ❌ LẠC       tài liệu chứa con số KHÔNG khớp nguồn nào     -> nghi là bịa
    ❌ CỤM TỪ CŨ tài liệu còn câu chữ đã lỗi thời             -> quên cập nhật

    Mục "LẠC" chỉ xét các con số có dạng phân tách nghìn (12.345), vì đó là dạng
    dùng để đếm bài. Số trần như "4 dòng" hay "§5.2" không bị soi.

CHẠY
    python datalake/scripts/doi_soat_tai_lieu.py
Trả mã thoát khác 0 nếu có sai lệch, để cắm được vào CI.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.rule import LUAT, TANG  # noqa: E402

TAI_LIEU = (
    "docs/Report_stage_of_rule.md",
    "docs/Report_analyst_17-09_pass-notpass.md",
    "docs/Plan_Rule_Phan_Tang.md",
)

#: Con số lịch sử được phép xuất hiện dù không khớp số đo hiện tại.
#: Mỗi mục PHẢI kèm lý do — không có lý do thì không được vào đây.
SO_LICH_SU: dict[str, str] = {
    "59.437": "thuoc_the trước khi có H4 (nêu trong câu 'giảm 59.437 → 55.297')",
    "18.583": "bài đạt sau khi sửa tầng 3, trước khi có H4",
    "16.391": "bài đạt trước khi sửa tầng 3",
    "55.149": "cổng 4 nhận vào khi tầng 3 còn chặn",
    "84.82": "tỷ lệ corpus sống sót dưới ngưỡng 0,5 tự chế — nêu làm bài học N1",
    "15.526": "số bản sao nội dung, đo ở §5 chất lượng dữ liệu",
    "15.916": "số bản dư trùng nội dung, đo ở §5",
    "15.029": "số nhóm trùng nội dung, đo ở §5",
    "42.883": "số bản ghi thiếu original_title, đo ở §5",
    "65.978": "số bản ghi thiếu source_file, đo ở §5",
    "43.911": "tập dùng được của bản đo 17/09",
    "1.244": "bài thu hồi từ khoá sai, đo ở §5",
    # Nhóm dưới đây đo ở §5 "chất lượng dữ liệu" và §6 "điểm mù H1". Chúng nói về
    # BẢN GHI, không về phán quyết luật, nên không đổi khi bộ luật đổi — xem ghi
    # chú phạm vi ở đầu hai mục ấy trong report.
    "1.191": "§5/§6 — đo mức dòng trên toàn corpus, độc lập bộ luật",
    "1.398": "§7 — bài cứu bằng sửa tay, nhóm D+E",
    "2.182": "§5/§6 — đo mức dòng trên toàn corpus",
    "2.828": "§5/§6 — đo mức dòng trên toàn corpus",
    "3.168": "§5/§6 — đo mức dòng trên toàn corpus",
    "3.182": "§5/§6 — đo mức dòng trên toàn corpus",
    "9.167": "§5/§6 — đo mức dòng trên toàn corpus",
    "10.000": "§6 — cỡ mẫu rà tay",
    "17.407": "§5/§6 — đo mức dòng trên toàn corpus",
    "24.394": "§5/§6 — đo mức dòng trên toàn corpus",
    "59.429": "§5/§6 — đo mức dòng trên toàn corpus",
    "3.975": "con số BỊA đã bị phát hiện 18/09 — nêu làm bài học, xem §9 report",
    # ── Trạng thái TRƯỚC QĐ-7b (18/09/2026), khi cổng 5 còn đòi khớp đúng một
    # trong bốn sơ đồ §5.2. Các báo cáo nêu chúng để nói rõ thay đổi, nên chúng
    # là số LỊCH SỬ có thật, không phải số bịa.
    "18.150": "bài đạt trước QĐ-7b (cổng 5 còn đòi khớp sơ đồ §5.2)",
    "43.884": "bài trượt trước QĐ-7b",
    "6.576": "cổng 5 chặn trước QĐ-7b",
    "2.277": "cụm aaaa bị cổng 5 loại trước QĐ-7b",
    "1.531": "cụm xaxa bị cổng 5 loại trước QĐ-7b",
    "2.192": "bài nghi Đường luật vào tập đạt, đo trước QĐ-7b",
    "2.096": "bài nghi Đường luật trượt cổng 5, đo trước QĐ-7b",
    "37.147": "chênh thuoc_the − dat, đo trước QĐ-7b",
    # ── Số của lượt đo 17/09, nêu trong báo cáo để so trước/sau. Chúng KHÔNG
    # còn khớp tệp nào vì tệp đã sinh lại 18/09 — đó chính là điều báo cáo nói.
    "2.597": "bai_truot_chi_tiet.jsonl bản 17/09 (chỉ cổng 2) — §10.1 so trước/sau",
    "35.065": "kết quả SAI của so_sanh_ban_luat.py trước khi sửa — §8.3 ghi làm bài học",
}


def so_tu_corpus() -> dict[str, str]:
    """Mọi con số hợp lệ lấy từ tong_hop.json, kèm tên để báo lỗi cho rõ."""
    th = json.loads((GOC / "datalake/analysis/tong_hop.json").read_text(encoding="utf-8"))
    ra: dict[str, str] = {}

    def them(gia_tri: object, ten: str) -> None:
        if isinstance(gia_tri, int) and gia_tri:
            ra.setdefault(f"{gia_tri:,}".replace(",", "."), ten)

    for khoa, gia_tri in th["ket_qua"].items():
        them(gia_tri, f"ket_qua.{khoa}")
    for khoa, gia_tri in th["doi_soat"].items():
        them(gia_tri, f"doi_soat.{khoa}")
    for cong in th["pheu_theo_cong"]:
        for khoa in ("vao", "qua", "chan_tai_day", "khong_chay",
                     "ghi_nhan_nhung_khong_chan"):
            them(cong.get(khoa), f"cổng {cong['so']}.{khoa}")
    for cac in th["ly_do_truot_theo_tang"].values():
        for ly_do, n in cac.items():
            them(n, f"vi phạm: {ly_do[:40]}")
    for nhom, n in th["ly_do_truot_theo_nhom"].items():
        them(n, f"nhóm {nhom[:30]}")
    for ma, n in th["ma_luat_bi_vi_pham"].items():
        them(n, f"vi phạm {ma}")
    them(th.get("bai_rong_co_the_cuu"), "bai_rong_co_the_cuu")

    # Ba con số giải thích vì sao cổng 5 chỉ chặn 1,46% — xem §7.5 report.
    vs = th.get("vi_sao_cong5_chan_it") or {}
    for khoa, gt in vs.items():
        them(gt, f"vi_sao_cong5.{khoa}")

    # Phân bố theo `score`, kèm tổng gộp của hai cụm dồn lớn nhất mà báo cáo nêu.
    ps = th.get("phan_bo_score") or {}
    for diem, o in ps.items():
        them(o.get("so_bai"), f"score {diem}: số bài")
    if ps:
        lon = sorted(ps.values(), key=lambda o: -o["so_bai"])[:2]
        them(sum(o["so_bai"] for o in lon), "score: tổng hai cụm dồn lớn nhất")

    # §6c (18/09/2026): phân bố 16 tổ hợp khuôn của cụm 4 dòng. Kể cả tổng cụm và
    # tổng hai mẫu §4.3, vì báo cáo trích cả hai con số dẫn xuất ấy.
    tk = th.get("to_hop_khuon_cum_bon_dong") or {}
    theo_ma = tk.get("theo_ma") or {}
    them(tk.get("tong_so_cum"), "to_hop_khuon.tong_so_cum")

    # Phân bố số dòng phá khuôn ở cổng 4, kèm tổng gộp "6 dòng trở lên" mà báo
    # cáo dùng để rút gọn bảng.
    pk = th.get("pha_khuon_cua_bai_truot_tang4") or {}
    theo = pk.get("theo_so_dong_pha") or {}
    them(pk.get("tong_bai"), "pha_khuon.tong_bai")
    them(pk.get("tong_dong_pha"), "pha_khuon.tong_dong_pha")
    for k, n in theo.items():
        them(n, f"pha_khuon: {k} dòng phá")
    if theo:
        them(sum(n for k, n in theo.items() if int(k) >= 6), "pha_khuon: từ 6 dòng trở lên")
    for ma, n in theo_ma.items():
        them(n, f"tổ hợp khuôn #{ma}")
    if theo_ma:
        hai_mau = (
            theo_ma.get(str(tk.get("ma_co_dien")), 0)
            + theo_ma.get(str(tk.get("ma_dao")), 0)
        )
        them(hai_mau, "tổ hợp khuôn: tổng hai mẫu §4.3")

    ra.update(_so_tu_jsonl())
    ra.update(_so_tu_rule_py())
    return ra


def _so_tu_rule_py() -> dict[str, str]:
    """Quy mô của chính rule.py — đo tại chỗ, không gõ tay.

    Báo cáo mở đầu bằng "rule.py — N dòng, M hàm". Hai con số đó cũ đi mỗi lần
    thêm một tầng hay một hàm, và trước nay phải sửa tay nên đã lệch hai lần.
    Đo thẳng từ tệp thì chúng không thể lệch nữa.
    """
    import ast

    ma = (GOC / "src/application/rule.py").read_text(encoding="utf-8")
    cay = ast.parse(ma)
    so_dong = len(ma.splitlines())
    so_ham = sum(1 for n in ast.walk(cay) if isinstance(n, ast.FunctionDef))
    return {
        f"{so_dong:,}".replace(",", "."): "rule.py: số dòng",
        f"{so_ham:,}".replace(",", "."): "rule.py: số hàm",
    }


def _so_tu_jsonl() -> dict[str, str]:
    """Các phân bố mà report trích dẫn nhưng tong_hop.json không chứa.

    Tính lại từ chính hai tệp kết quả, để mọi bảng trong report đều truy được
    về một phép đếm thật.
    """
    from collections import Counter

    A = GOC / "datalake/analysis"
    ra: dict[str, str] = {}

    def them(x: int, ten: str) -> None:
        if x:
            ra.setdefault(f"{x:,}".replace(",", "."), ten)

    dong, kho, sodo = Counter(), Counter(), Counter()
    lung = lech = 0
    for dg in (A / "bai_dat.jsonl").open(encoding="utf-8"):
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
    for k, v in dong.items():
        them(v, f"bài đạt {k} dòng")
    for k, v in kho.items():
        them(v, f"bài đạt {k} khổ")
    for k, v in sodo.items():
        them(v, f"cụm có vần chân, sơ đồ {k}")
    them(sum(sodo.values()), "tổng cụm có vần chân")
    them(lung, "bài đạt có vần lưng")
    them(lech, "bài đạt có vần lệch thanh")

    sd5, sd1, du1 = Counter(), Counter(), Counter()
    cong = Counter()
    for dg in (A / "bai_truot.jsonl").open(encoding="utf-8"):
        r = json.loads(dg)
        c = r["tang_dung_lai"]
        cong[c] += 1
        if c == 5:
            bc = next(k for k in r["tang"] if k["so"] == 5)["bang_chung"]
            if "dòng 1–4: " in bc:
                sd5[bc.split("dòng 1–4: ")[1].split(";")[0]] += 1
        elif c == 1:
            sd = r["tong_quan"]["so_dong"]
            sd1[sd] += 1
            du1[sd % 4] += 1
    for k, v in sd5.items():
        them(v, f"trượt cổng 5, sơ đồ {k}")
    for k, v in sd1.items():
        them(v, f"trượt cổng 1, {k} dòng")
    for k, v in du1.items():
        them(v, f"trượt cổng 1, dư {k}")
    for k, v in cong.items():
        them(v, f"trượt dừng ở cổng {k}")

    # Số phận các bài bị cổng 3 đánh dấu
    nghi_dat = sum(
        1 for dg in (A / "bai_dat.jsonl").open(encoding="utf-8")
        if next(k for k in json.loads(dg)["tang"] if k["so"] == 3)["chi_tiet"].get("nghi_duong_luat")
    )
    them(nghi_dat, "bài nghi Đường luật mà vẫn ĐẠT")
    nghi_truot = sum(
        1 for dg in (A / "bai_truot.jsonl").open(encoding="utf-8")
        if "giống khuôn Đường luật"
        in (next((k for k in json.loads(dg)["tang"] if k["so"] == 3), {}) or {}).get("bang_chung", "")
    )
    them(nghi_truot, "bài nghi Đường luật mà trượt")

    # Số dòng của chính các tệp kết quả — report có trích ở bảng "Tệp kết quả".
    for ten in ("bai_dat", "bai_truot", "bai_truot_chi_tiet", "bai_rong_cuu_duoc",
                "bai_khong_co_noi_dung", "dong_nghi_ngo_trong_bai_dat"):
        tep = A / f"{ten}.jsonl"
        if tep.exists():
            them(sum(1 for _ in tep.open(encoding="utf-8")), f"số dòng {ten}.jsonl")

    # Quy mô mã nguồn — report có nêu "rule.py 1.816 dòng".
    rule = GOC / "src/application/rule.py"
    them(sum(1 for _ in rule.open(encoding="utf-8")), "số dòng rule.py")

    # Hiệu hai cờ phán quyết, report gọi là "khoảng cách giữa hai con số".
    th = json.loads((GOC / "datalake/analysis/tong_hop.json").read_text(encoding="utf-8"))
    k = th["ket_qua"]
    them(k["bai_thuoc_the_theo_tai_lieu"] - k["bai_dat"], "khoảng cách thuoc_the - dat")
    return ra


def phan_tram_phai_co() -> dict[str, str]:
    """Phần trăm của phễu — tài liệu nêu thì phải đúng tới hai chữ số thập phân."""
    th = json.loads((GOC / "datalake/analysis/tong_hop.json").read_text(encoding="utf-8"))
    ra: dict[str, str] = {}
    for c in th["pheu_theo_cong"]:
        for khoa in ("ty_le_qua", "ty_le_chan", "ty_le_con_lai"):
            ra[f"{c[khoa]:.2f}".replace(".", ",") + "%"] = f"cổng {c['so']}.{khoa}"
    tl = th["ket_qua"]["ty_le_dat_tren_bai_co_noi_dung"]
    ra[f"{tl:.2f}".replace(".", ",") + "%"] = "tỉ lệ đạt"
    return ra


def kiem_phan_tram(van_ban: str, ten_tep: str) -> list[str]:
    """Bắt phần trăm của phễu bị ghi sai trong tài liệu.

    Chỉ soi các mốc phễu. Phần trăm của bảng phân bố không soi ở đây vì chúng
    được SINH RA từ dữ liệu, không gõ tay.
    """
    loi = []
    for gia_tri, ten in phan_tram_phai_co().items():
        # Chỉ đòi có mặt nếu tài liệu có nhắc tới cổng tương ứng.
        if "Phễu" in van_ban and gia_tri not in van_ban:
            loi.append(f"{ten_tep}: THIẾU phần trăm {gia_tri} ({ten})")
    return loi


def kiem_bang_to_hop_khuon(van_ban: str, ten_tep: str) -> list[str]:
    """Tài liệu nào in bảng 16 tổ hợp khuôn thì phải in ĐỦ 16 con số, và đúng.

    VÌ SAO CÓ HÀM NÀY — một lỗi đã lọt lưới ngày 18/09/2026:

        Báo cáo ghi "#6 = 882" và "#11 = 517". Giá trị thật là 999 và 561. Hai
        con số bịa ấy đi qua được phép soi LẠC vì phép soi ấy CHỈ xét số có dấu
        phân tách nghìn (12.345) — số ba chữ số không bị soi.

    Bài học: "chỉ soi số lớn" là một lỗ hổng, vì phần đuôi của mọi bảng phân bố
    đều là số nhỏ. Cách bịt rẻ nhất không phải soi mọi số ba chữ số (sẽ báo nhầm
    "4 dòng", "§5.2"), mà là ĐÒI ĐỦ với những bảng máy sinh ra được — như bảng
    này. Tài liệu in thiếu một dòng, hoặc in sai một giá trị, đều bị bắt.
    """
    # Kích hoạt khi tài liệu in BẢNG thật, không phải khi nhắc chữ "tổ hợp" thoáng
    # qua. Bảng có 16 hàng, mỗi hàng bốn ô "B-T-B"/"T-B-T" -> đếm mốc an toàn.
    if van_ban.count("B-T-B") + van_ban.count("T-B-T") < 16:
        return []
    th = json.loads((GOC / "datalake/analysis/tong_hop.json").read_text(encoding="utf-8"))
    theo_ma = (th.get("to_hop_khuon_cum_bon_dong") or {}).get("theo_ma") or {}
    if not theo_ma:
        return []
    loi = []
    for ma in sorted(theo_ma, key=int):
        gia_tri = f"{theo_ma[ma]:,}".replace(",", ".")
        if gia_tri not in van_ban:
            loi.append(
                f"{ten_tep}: bảng 16 tổ hợp THIẾU hoặc SAI giá trị của #{ma} "
                f"— phải là {gia_tri}"
            )
    return loi


#: Cụm từ đã lỗi thời mà phép soi số KHÔNG bắt được, vì chúng là CHỮ chứ không
#: phải số. Mỗi mục kèm cụm đúng để người sửa biết thay bằng gì.
CUM_TU_CU: dict[str, str] = {
    "H1–H3": "H1–H4 (H4 bổ sung 18/09/2026)",
    "H1-H3": "H1-H4 (H4 bổ sung 18/09/2026)",
    "29 điều luật": "30 điều luật",
    "Không giới hạn số dòng ở 4 hoặc 8": "Số dòng không giới hạn về lượng, nhưng phải là bội của 4",
    "Số dòng trong bài không hạn định |": "Số dòng trong bài không hạn định về lượng, nhưng phải là bội của 4 |",
}


def kiem_cum_tu_cu(van_ban: str, ten_tep: str) -> list[str]:
    """Bắt các cụm từ lỗi thời mà phép soi con số không thấy.

    Phép soi số chỉ nhìn dạng 12.345, nên nó bỏ lọt hoàn toàn những câu như
    "chỉ H1–H3" hay "Bảng LUAT có 29 điều". Đây là lỗ hổng đã xảy ra thật ngày
    18/09: ba tài liệu còn nói H1–H3 sau khi H4 ra đời.
    """
    return [
        f"{ten_tep}: CỤM TỪ CŨ {cu!r} — thay bằng {moi!r}"
        for cu, moi in CUM_TU_CU.items()
        if cu in van_ban
    ]


def kiem_bang_luat(van_ban: str, ten_tep: str) -> list[str]:
    """Mọi điều luật phải có mặt nguyên văn; mã tiêu chí chặn phải được nhắc."""
    loi = []
    for d in LUAT:
        if d.noi_dung not in van_ban:
            loi.append(f"{ten_tep}: THIẾU nguyên văn {d.ma} — {d.noi_dung[:45]}")
    tieu_chi = {ma for t in TANG for ma in t.tieu_chi_tu}
    for ma in sorted(tieu_chi):
        if ma not in van_ban:
            loi.append(f"{ten_tep}: THIẾU mã tiêu chí chặn {ma}")
    return loi


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    hop_le = so_tu_corpus()
    mau_so = re.compile(r"\b\d{1,3}(?:\.\d{3})+\b")
    loi: list[str] = []

    print("=" * 70)
    print("ĐỐI SOÁT TÀI LIỆU .md  ←→  tong_hop.json + rule.py")
    print("=" * 70)
    print(f"  Số hợp lệ lấy từ corpus : {len(hop_le)}")
    print(f"  Số lịch sử được miễn    : {len(SO_LICH_SU)}")
    print()

    for ten in TAI_LIEU:
        tep = GOC / ten
        if not tep.exists():
            loi.append(f"{ten}: KHÔNG TỒN TẠI")
            continue
        van_ban = tep.read_text(encoding="utf-8")

        lac = sorted({
            s for s in mau_so.findall(van_ban)
            if s not in hop_le and s not in SO_LICH_SU
        })
        rieng = []
        for s in lac:
            rieng.append(f"{ten}: số LẠC {s} — không khớp nguồn nào, nghi là bịa")

        thieu_luat = kiem_bang_luat(van_ban, ten) if "Report_analyst" not in ten else []
        thieu_pt = kiem_phan_tram(van_ban, ten)
        cum_cu = kiem_cum_tu_cu(van_ban, ten)
        bang_th = kiem_bang_to_hop_khuon(van_ban, ten)

        tat_ca = rieng + thieu_luat + thieu_pt + cum_cu + bang_th
        print(f"  {'✅' if not tat_ca else '❌'} {ten}")
        for x in tat_ca:
            print(f"       {x}")
        loi += tat_ca

    print()
    if loi:
        print(f"❌ {len(loi)} sai lệch. Sửa tài liệu, hoặc nếu con số là LỊCH SỬ có thật")
        print("   thì thêm vào SO_LICH_SU kèm lý do.")
        return 1
    print("✅ Mọi con số trong tài liệu đều truy được về nguồn.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
