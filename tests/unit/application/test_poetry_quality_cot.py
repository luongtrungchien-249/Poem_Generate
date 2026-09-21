"""Chất lượng (chỉ thị 3), Chain-of-thought, và sáu bước suy luận (chỉ thị 2).

Nguyên tắc quan trọng nhất được ghim ở đây: **chất lượng không bao giờ được loại
một bài khỏi thể**. Bài trượt chất lượng vẫn phải giữ `thuoc_the=True`.
"""

from __future__ import annotations

import pytest

from application.poetry.cot import (
    THE_CoT,
    can_bat_cot,
    da_dien_khung,
    dung_khung_suy_luan,
    tach_tho_khoi_khung,
)
from application.poetry.plan import KhoPlan, PoetryPlan
from application.poetry.quality import (
    SO_DONG_PHAN_BIET_TOI_THIEU,
    danh_gia_chat_luong,
)
from application.poetry.reasoning import kiem_tra_chuoi_suy_luan
from application.poetry.requirement import (
    PoetryRequirement,
    mac_dinh,
    nguoi_dung,
)
from application.poetry.verifier import PoemVerifierDayDu
from application.ports.verifier import OutputSpec
from application.rule import kiem_tra_bai_tho

pytestmark = pytest.mark.unit

# Bài 4 dòng lặp tối đa: đúng 7 tiếng/dòng nhưng chỉ dùng 3 tiếng khác nhau.
BAI_LAP = "\n".join(["Ta đi ta đi ta đi ta"] * 4)

# Bài trong tài liệu luật §11 — đã được test_rule.py xác nhận là ví dụ chuẩn.
BAI_TAI_LIEU = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh"
)

# Ca trung tâm của chỉ thị 3: luật KHÔNG bắt được, chất lượng phải bắt.
#
# Ví dụ CŨ ở đây là "lặp nguyên khổ". Nay nó QUA — và đúng ra phải qua: đó là
# *điệp khổ*, thứ S20 cho phép, nên chặn nó là vi phạm N2. Ca trung tâm nay là
# suy biến tuyệt đối: mọi dòng y hệt nhau, không còn gì để điệp xen giữa.
BAI_DUNG_LUAT_KEM_CHAT_LUONG = "\n".join(["Trời cao mây biếc xanh ngời cành"] * 4)


# ── Chất lượng ────────────────────────────────────────────────────────────────


def test_bai_MOI_DONG_Y_HET_NHAU_thi_truot():
    """Ca suy biến tuyệt đối: không phải điệp, mà là không có bài thơ."""
    v = kiem_tra_bai_tho(BAI_LAP)
    cl = danh_gia_chat_luong(v)
    assert not cl.dat
    assert "dong_phan_biet" in [c.ten for c in cl.chieu_hong]


def test_DIEP_DONG_co_chu_y_KHONG_bi_danh_truot():
    """⛔ N2 — S20 cho phép điệp dòng, nên chặn vì nó là mâu thuẫn tự thân.

    Đo trên 6.000 bài người viết: bản trước bắt 164 bài, TOÀN BỘ là điệp khúc
    hoặc kết cấu vòng tròn.
    """
    diep = "\n".join(
        [
            "Em là con hát ở bên sông",
            "Gió cuốn heo may lạc cuối ghềnh",
            "Một bóng con đò trôi lặng lẽ",
            "Em là con hát ở bên sông",
        ]
    )
    cl = danh_gia_chat_luong(kiem_tra_bai_tho(diep))
    assert cl.dat, "điệp dòng bị đánh trượt — vi phạm N2"
    cl2 = next(c for c in cl.chieu if c.ma == "CL2")
    assert cl2.so_do == 1.0, "vẫn phải ĐẾM để báo cho HITL"
    assert cl2.dat is True, "nhưng KHÔNG được chặn"


def test_chat_luong_KHONG_BAO_GIO_loai_bai_khoi_the():
    """Ranh giới thẩm quyền quan trọng nhất của gói `poetry`.

    Một bài có thể trượt chất lượng mà vẫn là thơ thất ngôn tự do hợp lệ. Nếu test
    này đỏ, nghĩa là ai đó đã để chuẩn dự án ghi đè tài liệu luật.
    """
    v = kiem_tra_bai_tho(BAI_LAP)
    cl = danh_gia_chat_luong(v)
    assert not cl.dat, "bài này phải trượt chất lượng thì test mới có nghĩa"
    assert v.thuoc_the is True, "chất lượng không được đụng tới cờ thuoc_the"


def test_hai_chieu_ngu_nghia_duoc_ghi_la_KHONG_KIEM_DUOC():
    """N3 — không chấm bừa hai chiều đòi hiểu nội dung."""
    v = kiem_tra_bai_tho(BAI_TAI_LIEU)
    cl = danh_gia_chat_luong(v)
    assert set(cl.chieu_khong_do_duoc) >= {"CL6", "CL7"}
    for c in cl.chieu:
        if not c.do_duoc:
            assert c.so_do is None, "chiều không đo được thì không được có số đo"


def test_bam_chu_de_chi_kiem_khi_co_chu_de():
    v = kiem_tra_bai_tho(BAI_TAI_LIEU)
    khong = danh_gia_chat_luong(v, chu_de=None)
    assert "CL3" in khong.chieu_khong_do_duoc

    co = danh_gia_chat_luong(v, chu_de="chiều sông")
    cl3 = next(c for c in co.chieu if c.ma == "CL3")
    assert cl3.do_duoc and cl3.dat


def test_bam_chu_de_truot_khi_bai_khong_nhac_chu_de():
    v = kiem_tra_bai_tho(BAI_TAI_LIEU)
    cl = danh_gia_chat_luong(v, chu_de="tàu vũ trụ")
    cl3 = next(c for c in cl.chieu if c.ma == "CL3")
    assert cl3.do_duoc and not cl3.dat


def test_KHONG_con_nguong_tuy_y_nao():
    """🩸 `lap_tieng >= 0,55` đã bị GỠ 21/09/2026.

    Nó là ngưỡng tuỳ ý duy nhất của hệ thống, THIÊN VỊ THEO ĐỘ DÀI (trung vị tụt
    từ 0,929 ở bài 4 dòng xuống 0,638 ở bài 56 dòng — số học, không phải chất
    lượng), và phạt đúng quyền S20 cho phép.

    Nay mọi ngưỡng còn lại đều là SỐ NGUYÊN hoặc suy ra từ một quyết định đã chốt.
    """
    assert isinstance(SO_DONG_PHAN_BIET_TOI_THIEU, int)
    v = kiem_tra_bai_tho(BAI_TAI_LIEU)
    for c in danh_gia_chat_luong(v).chieu:
        assert "tuỳ ý" not in c.nguong, f"{c.ten} còn mang ngưỡng tuỳ ý"


# ── Chain-of-thought ──────────────────────────────────────────────────────────


def test_cot_bat_khi_chat_luong_truot_khong_bat_khi_chi_luat_truot():
    assert can_bat_cot(dat_luat=True, dat_chat_luong=False) is True
    assert can_bat_cot(dat_luat=False, dat_chat_luong=True) is False
    assert can_bat_cot(dat_luat=True, dat_chat_luong=True) is False


def test_cot_bat_khi_lap_hoac_khong_tien_bo_bat_ke_loai_loi():
    assert can_bat_cot(dat_luat=False, dat_chat_luong=True, lap_lai=True) is True
    assert can_bat_cot(dat_luat=True, dat_chat_luong=True, khong_tien_bo=True) is True


def test_khung_cot_co_du_bon_o():
    """Bốn ô phải có mặt đủ, và ô 3 phải cấm viết thơ."""
    v = kiem_tra_bai_tho(BAI_LAP)
    cl = danh_gia_chat_luong(v)
    khung = dung_khung_suy_luan(cl, dong_dat=(1, 2, 3, 4))
    for o in ("1. CHIỀU CHƯA ĐẠT", "2. NGUYÊN NHÂN", "3. HƯỚNG SỬA", "4. DÒNG PHẢI GIỮ NGUYÊN"):
        assert o in khung
    assert "KHÔNG viết câu thơ" in khung
    # `dong_phan_biet` là lỗi cấp BÀI, không quy được cho dòng nào — ô 4 phải NÓI
    # THẲNG là không ghim được dòng nào, thay vì đưa một danh sách sai.
    assert "khuếch tán" in khung


def test_khung_cot_bi_go_truoc_khi_dem_tieng():
    """Để nguyên khung thì mấy dòng chẩn đoán bị đem đi đếm âm tiết và bài nào cũng
    trượt H1. Đây là ca hỏng dễ mắc nhất của cơ chế CoT."""
    van_ban = (
        f"<{THE_CoT}>\n"
        "1. CHIỀU CHƯA ĐẠT      : lap_tieng = 0.3\n"
        "2. NGUYÊN NHÂN         : dùng lại quá nhiều tiếng\n"
        "3. HƯỚNG SỬA           : thay hình ảnh ở hai dòng giữa\n"
        "4. DÒNG PHẢI GIỮ NGUYÊN: D1\n"
        f"</{THE_CoT}>\n\n" + BAI_TAI_LIEU
    )
    assert da_dien_khung(van_ban)
    tho = tach_tho_khoi_khung(van_ban)
    assert THE_CoT not in tho
    assert kiem_tra_bai_tho(tho).dat == kiem_tra_bai_tho(BAI_TAI_LIEU).dat


# ── Sáu bước suy luận ─────────────────────────────────────────────────────────


def _req_du() -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung("chiều sông"), so_dong=nguoi_dung(4),
        cam_xuc=nguoi_dung("lặng"), phong_cach=mac_dinh("cổ điển"),
        rang_buoc_van=mac_dinh("vần chân"), rang_buoc_thanh=mac_dinh("luân phiên"),
    )


def _req_8_dong() -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung("chiều sông"), so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("lặng"), phong_cach=mac_dinh("cổ điển"),
        rang_buoc_van=mac_dinh("vần chân"), rang_buoc_thanh=mac_dinh("luân phiên"),
    )


def _chay(van_ban: str, **kw):
    v = kiem_tra_bai_tho(van_ban)
    cl = danh_gia_chat_luong(v, chu_de=kw.pop("chu_de", None))
    return kiem_tra_chuoi_suy_luan(van_ban=van_ban, verdict=v, chat_luong=cl, **kw)


def test_sau_buoc_dung_o_buoc_truot_dau_tien_va_ghi_CHUA_KIEM():
    """Bước sau bước chặn phải mang da_chay=False — *chưa kiểm*, không phải *đạt*."""
    sl = _chay(BAI_LAP, yeu_cau=_req_du())
    assert not sl.dat
    assert sl.buoc_dung_lai is not None
    sau = [b for b in sl.buoc if b.ma > sl.buoc_dung_lai]
    assert sau, "phải có bước bị bỏ qua"
    assert all(not b.da_chay for b in sau)
    assert all("bỏ qua" in b.bang_chung for b in sau)


def test_B1_chan_khi_thieu_thong_tin_va_tra_ve_cau_hoi():
    """Chỉ thị 5 — thiếu thông tin thì HỎI, không sinh thơ."""
    sl = _chay(BAI_TAI_LIEU, yeu_cau=PoetryRequirement(van_ban_goc="Viết bài thơ."))
    assert not sl.dat
    assert sl.buoc_dung_lai == "B1"
    assert sl.cau_hoi is not None and "chủ đề" in sl.cau_hoi


def test_B3_bat_ban_nhap_lech_ke_hoach():
    """Bước tài liệu đích không có. Thiếu nó thì kế hoạch chỉ là trang trí."""
    plan = PoetryPlan(kho=(KhoPlan(so_dong=4), KhoPlan(so_dong=4)))  # 8 dòng
    req = PoetryRequirement(
        chu_de=nguoi_dung("chiều sông"), so_dong=nguoi_dung(8),
        cam_xuc=nguoi_dung("lặng"), phong_cach=mac_dinh("x"),
        rang_buoc_van=mac_dinh("y"), rang_buoc_thanh=mac_dinh("z"),
    )
    sl = _chay(BAI_TAI_LIEU, yeu_cau=req, ke_hoach=plan)  # bài chỉ 4 dòng
    assert sl.buoc_dung_lai == "B3"
    assert any("kế hoạch 8 dòng" in m for m in next(b for b in sl.buoc if b.ma == "B3").loi)


def test_B6_chan_tuyen_bo_dung_luat_khong_co_can_cu():
    """§19.4 — rail duy nhất chặn LỜI NÓI về kết quả."""
    xau = BAI_LAP + "\nBài trên đã đúng luật thất ngôn tự do."
    sl = _chay(xau, yeu_cau=_req_du())
    b6 = next(b for b in sl.buoc if b.ma == "B6")
    # B4/B5 chặn trước nên B6 chưa chạy — nhưng rail vẫn phải bắt được khi tới lượt.
    assert not sl.dat
    assert b6.da_chay is False or not b6.dat


def test_B6_bat_duoc_khi_chay_den_luot():
    from domain.guardrails.output.verification_claim import check_verification_claim

    kq = check_verification_claim(
        "Bài trên đã đúng luật thất ngôn tự do.", has_evidence=True, verdict_passed=False
    )
    assert not kq.allowed
    assert kq.claims_found

    ok = check_verification_claim(
        "Chiều rơi chậm xuống mái rêu xanh", has_evidence=True, verdict_passed=True
    )
    assert ok.allowed


def test_moi_buoc_da_chay_deu_nop_bang_chung():
    """Quy ước 2: luôn nộp bằng chứng, kể cả khi đạt."""
    sl = _chay(BAI_TAI_LIEU, yeu_cau=_req_du(), chu_de="chiều sông")
    for b in sl.buoc:
        if b.da_chay:
            assert b.bang_chung.strip(), f"bước {b.ma} chạy mà không nộp bằng chứng"


# ── Cổng chặn đầy đủ ──────────────────────────────────────────────────────────


def test_cong_day_du_bat_CoT_khi_luat_dat_nhung_chat_luong_truot():
    """Chỉ thị 3, ca trung tâm: luật KHÔNG bắt được, chất lượng phải bắt."""
    v = kiem_tra_bai_tho(BAI_DUNG_LUAT_KEM_CHAT_LUONG)
    assert v.dat, "bài này phải ĐÚNG LUẬT thì ca thử mới có nghĩa"

    kq = PoemVerifierDayDu().kiem(
        BAI_DUNG_LUAT_KEM_CHAT_LUONG,
        OutputSpec(ma_the="that_ngon_tu_do", tham_so={"yeu_cau": _req_du()}),
    )
    assert not kq.dat
    assert THE_CoT in kq.bien_ban, "chất lượng trượt thì biên bản phải kèm khung CoT"
    assert any(e.ma.startswith("CL") for e in kq.loi)


def test_cong_day_du_KHONG_bat_CoT_khi_chi_sai_luat():
    """Lỗi có địa chỉ rồi thì bắt suy luận thêm là tốn tiền vô ích."""
    sai = "\n".join(["Một dòng sáu tiếng thôi mà"] * 4)
    kq = PoemVerifierDayDu().kiem(sai, OutputSpec(ma_the="that_ngon_tu_do"))
    assert not kq.dat
    assert THE_CoT not in kq.bien_ban
    assert any(e.ma in ("H1", "H2") for e in kq.loi)


def test_cong_day_du_phan_biet_ma_luat_voi_ma_chat_luong():
    """Người đọc biên bản phải phân biệt được 'sai luật' với 'chưa đủ tốt'."""
    kq = PoemVerifierDayDu().kiem(
        BAI_DUNG_LUAT_KEM_CHAT_LUONG,
        OutputSpec(ma_the="that_ngon_tu_do", tham_so={"yeu_cau": _req_du()}),
    )
    ma = {e.ma for e in kq.loi}
    assert all(not m.startswith("H") for m in ma), "bài này đúng luật, không được có mã H"
    assert any(m.startswith("CL") for m in ma)


def test_cong_day_du_bao_cao_hai_co_tach_roi():
    kq = PoemVerifierDayDu().kiem(
        BAI_DUNG_LUAT_KEM_CHAT_LUONG,
        OutputSpec(ma_the="that_ngon_tu_do", tham_so={"yeu_cau": _req_du()}),
    )
    mo_ta = "\n".join(kq.mo_ta_mem)
    assert "thuộc thể (H1–H4): True" in mo_ta
    assert "đạt chất lượng (chuẩn dự án): False" in mo_ta
    assert "đúng luật (bảy tầng): True" in mo_ta


def test_cong_day_du_chan_khi_thieu_thong_tin():
    """Chỉ thị 5 nối vào cổng chặn đầu ra."""
    spec = OutputSpec(
        ma_the="that_ngon_tu_do",
        tham_so={"yeu_cau": PoetryRequirement(van_ban_goc="Viết bài thơ.")},
    )
    kq = PoemVerifierDayDu().kiem(BAI_TAI_LIEU, spec)
    assert not kq.dat
    assert "B1" in kq.bien_ban
    assert any(e.ma == "B1" for e in kq.loi)


def test_cong_day_du_cho_qua_bai_dat_ca_luat_lan_chat_luong():
    spec = OutputSpec(
        ma_the="that_ngon_tu_do",
        tham_so={"chu_de": "chiều sông", "yeu_cau": _req_du()},
    )
    kq = PoemVerifierDayDu().kiem(BAI_TAI_LIEU, spec)
    assert kq.dat, f"biên bản: {kq.bien_ban}"
    assert kq.bien_ban == ""
    assert kq.loi == ()


def test_cong_day_du_KHONG_BAO_GIO_sua_van_ban_tho():
    """P2 — bộ kiểm phán, mô hình sửa."""
    bb = PoemVerifierDayDu().lap_bien_ban(BAI_TAI_LIEU, OutputSpec(ma_the="that_ngon_tu_do"))
    assert bb.van_ban_tho == BAI_TAI_LIEU


def test_khong_co_yeu_cau_thi_KHONG_duoc_tra_tho_ra():
    """Chỉ thị 5, dạng mạnh nhất.

    Không có `PoetryRequirement` thì hệ thống KHÔNG THỂ xác nhận đã đủ thông tin,
    nên B1 chặn. Đây là hành vi CÓ CHỦ Ý, không phải thiếu sót: im lặng cho qua sẽ
    biến "đã hỏi đủ" và "chưa hỏi gì" thành cùng một kết quả.
    """
    kq = PoemVerifierDayDu().kiem(BAI_TAI_LIEU, OutputSpec(ma_the="that_ngon_tu_do"))
    assert not kq.dat
    assert "B1" in kq.bien_ban


# ── Ghim lỗi đã sửa: ô 4 không được tự mâu thuẫn ──────────────────────────────


def test_o4_KHONG_bao_giu_nguyen_dong_chinh_no_bat_phai_doi():
    """🩸 Bản đầu in "giữ nguyên cả 8 dòng" trong khi lỗi là trùng dòng.

    Chỉ dẫn tự mâu thuẫn: mô hình không có cách nào tuân theo. Test này ghim cả
    hai nhánh đã sửa.
    """
    v = kiem_tra_bai_tho(BAI_DUNG_LUAT_KEM_CHAT_LUONG)
    cl = danh_gia_chat_luong(v)
    assert not cl.dat, "ca thử chỉ có nghĩa khi bài này trượt chất lượng"

    # `dong_phan_biet` là lỗi CẤP BÀI: không quy được cho dòng nào, vì mọi dòng
    # đều y hệt nhau nên không dòng nào "sai hơn" dòng nào.
    assert cl.dong_bi_quy_trach_nhiem == frozenset()
    assert cl.co_loi_khuech_tan

    khung = dung_khung_suy_luan(cl, dong_dat=tuple(d.so for d in v.dong))
    o4 = next(d for d in khung.splitlines() if d.startswith("4."))
    # Thà nói "không ghim được dòng nào" còn hơn bảo giữ nguyên cả bài trong khi
    # cả bài chính là chỗ phải đổi — đó là chỉ dẫn mô hình không tuân theo được.
    assert "D1 D2 D3 D4" not in o4
    assert "khuếch tán" in o4


def test_o4_chi_ghim_dong_lanh_khi_loi_quy_duoc_cho_dong_cu_the():
    """Khi mọi chiều hỏng đều chỉ được tên dòng, ô 4 phải ghim dòng lành và nêu rõ
    dòng phải đổi."""
    from application.poetry.quality import ChieuChatLuong, KetQuaChatLuong

    cl = KetQuaChatLuong(
        dat=False,
        chieu=(
            ChieuChatLuong(
                ma="CL2", ten="lap_dong", do_duoc=True, dat=False, so_do=1.0,
                nguong="= 0", bang_chung="D3 trùng D1", dong_lien_quan=(3,),
            ),
        ),
    )
    assert not cl.co_loi_khuech_tan
    khung = dung_khung_suy_luan(cl, dong_dat=(1, 2, 3, 4))
    o4 = next(d for d in khung.splitlines() if d.startswith("4."))
    assert "D1 D2 D4" in o4
    assert "PHẢI ĐỔI: D3" in o4
