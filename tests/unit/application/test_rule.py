"""Kiểm chứng `application/rule.py` đối chiếu trực tiếp với docs/Luat_Tho_That_Ngon_Tu_Do.md.

Ngữ liệu vàng chính là ví dụ §11 của tài liệu — nếu bộ kiểm không tái tạo được
phân tích mà tài liệu tự đưa ra thì bộ kiểm sai, không phải tài liệu sai.
"""

import pytest

from application.rule import (
    CAP_VAN_THONG,
    HAM_KIEM_CUNG,
    MA_CUNG,
    dem_tieng,
    doc_so,
    hiep_van,
    khuon_cua_dong,
    kiem_tra_bai_tho,
    suy_so_do_van,
    tach_kho,
    tach_tieng,
    thanh_cua,
    van_cua,
)

# Ví dụ §11 của tài liệu luật
VI_DU_TAI_LIEU = """Chiều rơi chậm xuống mái rêu xanh
Con ngõ nhỏ dài hơn tiếng ve
Ai đứng bên kia bờ nắng mảnh
Gọi một mùa xa chẳng dám về"""


# ─────────────────────────── §3. Đếm âm tiết (H1) ───────────────────────────


def test_dem_tieng_theo_dung_vi_du_cua_tai_lieu():
    # Tài liệu §2.1: "long lanh" = 2 tiếng, "ra-đi-ô" = 3 tiếng
    assert dem_tieng("long lanh") == 2
    assert dem_tieng("ra-đi-ô") == 3


def test_dau_cau_KHONG_duoc_tinh_la_tieng():
    assert dem_tieng("Chiều rơi chậm xuống, mái rêu xanh!") == 7
    assert dem_tieng('"Gọi một mùa xa chẳng dám về"') == 7


def test_chu_so_duoc_quy_ve_cach_doc_truoc_khi_dem():
    # Đ2: chuẩn miền Bắc văn viết
    assert doc_so(1975) == ["một", "nghìn", "chín", "trăm", "bảy", "mươi", "lăm"]
    assert doc_so(21) == ["hai", "mươi", "mốt"]
    assert doc_so(24) == ["hai", "mươi", "tư"]
    assert doc_so(15) == ["mười", "lăm"]
    assert doc_so(105) == ["một", "trăm", "linh", "năm"]
    assert doc_so(0) == ["không"]
    # "năm 1975" = năm + 7 tiếng đọc số = 8 tiếng, KHÔNG phải 2
    assert dem_tieng("năm 1975") == 8


def test_bon_dong_vi_du_deu_dung_bay_tieng():
    for dong in VI_DU_TAI_LIEU.splitlines():
        assert dem_tieng(dong) == 7, dong


# ─────────────────────────── §4. Thanh điệu ───────────────────────────


@pytest.mark.parametrize(
    "tieng,mong_doi",
    [
        ("rơi", "B"),  # ngang
        ("dài", "B"),  # huyền
        ("xuống", "T"),  # sắc
        ("nhỏ", "T"),  # hỏi
        ("ngõ", "T"),  # ngã
        ("một", "T"),  # nặng
        ("ơ", "B"),  # dấu nền horn, KHÔNG phải dấu thanh
        ("ă", "B"),  # dấu nền breve
        ("ê", "B"),  # dấu nền circumflex
    ],
)
def test_phan_lop_thanh_bang_trac(tieng, mong_doi):
    assert thanh_cua(tieng) == mong_doi


# ─────────────────────────── §5. Vần ───────────────────────────


def test_tach_van_bo_phu_am_dau_theo_khop_dai_nhat():
    assert van_cua("xanh") == "anh"
    assert van_cua("mảnh") == "anh"  # dấu thanh đã bỏ
    assert van_cua("nghiêng") == "iêng"  # "ngh" phải được thử trước "ng"
    assert van_cua("về") == "ê"  # bỏ dấu thanh, GIỮ dấu nền
    assert van_cua("ve") == "e"


def test_khong_cat_phu_am_dau_den_muc_rong():
    # "gì" là g + ì, không phải "gi" + rỗng
    assert van_cua("gì") == "i"


def test_hiep_van_chinh_va_van_thong_duoc_phan_biet():
    # Tài liệu §11 gọi chung là "vần thông"; ở đây tách bạch hai hiện tượng
    chinh = hiep_van("xanh", "mảnh")
    assert chinh.hiep and chinh.kieu == "chinh"

    thong = hiep_van("ve", "về")
    assert thong.hiep and thong.kieu == "thong"


def test_cap_van_lech_lop_thanh_van_duoc_coi_la_hiep_nhung_co_ghi_nhan():
    # Đ3: "xanh" thanh ngang (B), "mảnh" thanh hỏi (T)
    kq = hiep_van("xanh", "mảnh")
    assert kq.hiep is True
    assert kq.dong_thanh is False

    kq2 = hiep_van("ve", "về")  # cả hai đều bằng
    assert kq2.dong_thanh is True


def test_hai_tieng_khong_lien_quan_thi_KHONG_hiep_van():
    assert hiep_van("xanh", "mùa").hiep is False


def test_moi_canh_van_thong_noi_dung_HAI_van_khac_nhau():
    """Cạnh là một CẶP vần khác nhau — không có cạnh tự nối hay cạnh lẻ."""
    for cap in CAP_VAN_THONG:
        assert len(cap) == 2


# ─────────────────────────── §6. Khuôn luân phiên ───────────────────────────


def test_khuon_cua_bon_dong_vi_du():
    # Kiểm P2/P4/P6 từng dòng của ví dụ §11
    khuon = [khuon_cua_dong(tach_tieng(d)) for d in VI_DU_TAI_LIEU.splitlines()]
    # D1 rơi(B) xuống(T) rêu(B) -> bằng
    # D2 ngõ(T) dài(B) tiếng(T) -> trắc
    # D3 đứng(T) kia(B) nắng(T) -> trắc
    # D4 một(T) xa(B) dám(T) -> trắc  (LỆCH khỏi mẫu cổ điển vốn đòi D4 khuôn bằng)
    assert khuon == ["bang", "trac", "trac", "trac"]


def test_dong_du_bay_tieng_khong_khop_khuon_nao_thi_la_pha():
    # P2 B, P4 B, P6 B: không phải khuôn bằng cũng không phải khuôn trắc
    assert khuon_cua_dong(tach_tieng("Ta đi ta đi ta đi ta")) == "pha"


def test_dong_KHONG_du_bay_tieng_thi_khuon_khong_xac_dinh():
    """Gọi dòng sai luật là "phá khuôn" tức gán cho nó một lựa chọn phong cách
    mà tác giả chưa hề thực hiện."""
    assert khuon_cua_dong(tach_tieng("Ta đi ta đi ta đi")) == "khong_xac_dinh"
    assert khuon_cua_dong(tach_tieng("Ta đi")) == "khong_xac_dinh"


# ─────────────────────────── §7. Sơ đồ vần ───────────────────────────


def test_suy_so_do_van_cach_abab_dung_nhu_tai_lieu_phan_tich():
    so_do = suy_so_do_van(("xanh", "ve", "mảnh", "về"))
    assert so_do == ("a", "b", "a", "b")


def test_dong_khong_hiep_voi_dong_nao_nhan_nhan_x():
    # Sơ đồ a a x a của tài liệu §5.2
    so_do = suy_so_do_van(("xanh", "mảnh", "mùa", "cành"))
    assert so_do == ("a", "a", "x", "a")


# ─────────────────────────── §9. Hàm kiểm tổng ───────────────────────────


def test_vi_du_cua_tai_lieu_DAT_va_tai_tao_dung_phan_tich():
    v = kiem_tra_bai_tho(VI_DU_TAI_LIEU)

    assert v.dat is True
    assert v.vi_pham == ()
    assert v.so_dong == 4
    assert v.so_kho == 1
    assert v.so_do_van_theo_kho == (("a", "b", "a", "b"),)
    assert v.van_lech_thanh == ((1, 3),)  # xanh B – mảnh T
    assert v.nghi_duong_luat is False  # không độc vận nên không nghi


def test_mot_dong_lech_bay_tieng_thi_bai_KHONG_thuoc_the():
    bai = VI_DU_TAI_LIEU.replace(
        "Ai đứng bên kia bờ nắng mảnh",
        "Ai đứng bên kia bờ nắng mảnh xa",  # 8 tiếng
    )
    v = kiem_tra_bai_tho(bai)

    assert v.dat is False
    assert len(v.vi_pham) == 1
    vp = v.vi_pham[0]
    assert vp.ma == "H1"
    assert vp.dong == 3  # địa chỉ dòng, đếm từ 1
    assert vp.thuc_te == "8 tiếng"
    assert "bỏ 1 tiếng" in vp.goi_y


def test_dong_thieu_tieng_cung_bi_bat_va_goi_y_them_tieng():
    v = kiem_tra_bai_tho("Chiều rơi chậm xuống mái rêu xanh\nGió về")
    assert v.dat is False
    vp = [x for x in v.vi_pham if x.dong == 2][0]
    assert vp.thuc_te == "2 tiếng"
    assert "thêm 5 tiếng" in vp.goi_y


def test_khoi_lien_mach_khong_xuong_dong_vi_pham_H3():
    v = kiem_tra_bai_tho("Chiều rơi chậm xuống mái rêu xanh")
    assert v.dat is False
    assert any(vp.ma == "H3" for vp in v.vi_pham)


def test_H2_khong_co_ngoai_le_moi_dong_sai_deu_bi_ghi_nhan():
    bai = "Một hai ba bốn năm sáu\nBảy tám\nChín mười một hai ba bốn năm sáu bảy"
    v = kiem_tra_bai_tho(bai)
    assert {vp.dong for vp in v.vi_pham if vp.ma == "H1"} == {1, 2, 3}


def test_tach_kho_theo_dong_trong():
    kho = tach_kho("a\nb\n\nc\nd\n\n\ne")
    assert len(kho) == 3
    assert kho[0] == ("a", "b")
    assert kho[2] == ("e",)


def test_moi_kho_co_so_do_van_rieng_vi_S12_cho_phep_doi_van():
    bai = (
        "Chiều rơi chậm xuống mái rêu xanh\n"
        "Ai đứng bên kia bờ nắng mảnh\n"
        "\n"
        "Con ngõ nhỏ dài hơn tiếng ve\n"
        "Gọi một mùa xa chẳng dám về"
    )
    v = kiem_tra_bai_tho(bai)
    assert v.dat is True
    assert v.so_kho == 2
    # Ký hiệu §5.2: "K1: a a x a, K2: b b x b" — khổ sau đổi vần thì ĐỔI CHỮ CÁI
    assert v.so_do_van_theo_kho == (("a", "a"), ("b", "b"))


def test_pha_khuon_van_THUOC_THE_nhung_KHONG_dat_chuan_du_an():
    """Ca minh hoạ rõ nhất vì sao `thuoc_the` và `dat` phải là hai cờ riêng.

    Tài liệu luật (S4): *"Có thể phá khuôn ở bất kỳ dòng nào"* → bài vẫn THUỘC
    THỂ thất ngôn tự do.
    Quyết định dự án (QĐ-2): không cho phá khuôn → bài KHÔNG ĐẠT chuẩn dự án.

    Gộp hai cờ làm một thì bộ kiểm sẽ trả lời sai một trong hai câu hỏi.
    Test này trước đây ghim chính sách cũ (`dat is True`); QĐ-2 đã đổi chính sách,
    nên nó được viết lại chứ không phải bị nới ra.
    """
    bai = "Ta đi ta đi ta đi ta\nTa đi ta đi ta đi ta"
    v = kiem_tra_bai_tho(bai)

    assert v.thuoc_the is True, "H1–H3 đều đạt nên bài vẫn thuộc thể"
    assert v.dat is False, "QĐ-2 không cho phá khuôn"
    assert v.tang_dung_lai == 4, "phải dừng đúng ở tầng thanh luật"
    assert v.ty_le_theo_khuon == 0.0

    tang4 = v.tang[3]
    assert tang4.da_chay and not tang4.dat
    assert "2/2 dòng phá khuôn" in tang4.bang_chung
    assert {vp.ma for vp in tang4.vi_pham} == {"S2"}


def test_canh_bao_duong_luat_KHONG_lam_bai_truot():
    v = kiem_tra_bai_tho(VI_DU_TAI_LIEU)
    # dù nghi_duong_luat có bật hay không, `dat` không được phụ thuộc vào nó (Đ1)
    assert v.dat is True


# ─────────────────────── §10. Tài liệu cưỡng chế được ───────────────────────


def test_moi_luat_cung_deu_co_ham_kiem_tuong_ung():
    """Thêm một luật cứng vào bảng mà quên viết hàm kiểm thì test này đỏ."""
    assert set(HAM_KIEM_CUNG.keys()) == MA_CUNG


# ═══════════ Các chỗ tài liệu quy định mà bản đầu tiên bỏ sót ═══════════


def test_gach_ngang_dai_va_ngan_KHONG_duoc_tinh_la_tieng():
    """§2.1: dấu câu không tính là tiếng.

    Bản đầu dùng danh sách dấu câu liệt kê tay và thiếu "—", "–", nên một dòng
    6 tiếng có gạch ngang bị đếm thành 7 và LỌT qua H1 — sai theo hướng nguy hiểm
    nhất. Nay nhận diện theo phân loại Unicode.
    """
    assert dem_tieng("Chiều rơi — chậm xuống mái rêu") == 6
    assert dem_tieng("Chiều rơi – chậm xuống mái rêu") == 6
    assert dem_tieng("Chiều rơi «chậm» xuống mái rêu xanh") == 7
    assert dem_tieng("Chiều rơi… chậm xuống mái rêu xanh") == 7


def test_dong_sau_dau_KHONG_lot_qua_H1():
    """Kiểm ở mức cả bài, không chỉ ở hàm đếm."""
    v = kiem_tra_bai_tho("Chiều rơi — chậm xuống mái rêu\nGọi một mùa xa chẳng dám về")
    assert v.dat is False
    assert v.vi_pham[0].dong == 1
    assert v.vi_pham[0].thuc_te == "6 tiếng"


def test_so_thap_phan_va_so_khong_dung_dau_doc_dung_chuan_D2():
    assert tach_tieng("3,5") == ("ba", "phẩy", "năm")
    assert tach_tieng("3.5.") == ("ba", "phẩy", "năm")
    assert tach_tieng("007") == ("không", "không", "bảy")


def test_nhan_van_danh_lien_tuc_qua_cac_kho():
    from application.rule import suy_so_do_van_toan_bai

    # Khổ 1 vần "anh", khổ 2 vần "e/ê" -> phải là a a rồi b b
    assert suy_so_do_van_toan_bai(
        (("xanh", "mảnh"), ("ve", "về"))
    ) == (("a", "a"), ("b", "b"))

    # Khổ 2 quay lại đúng lớp vần của khổ 1 -> dùng lại chữ "a"
    assert suy_so_do_van_toan_bai(
        (("xanh", "mảnh"), ("cành", "tranh"))
    ) == (("a", "a"), ("a", "a"))


def test_nhan_van_vuot_qua_hai_muoi_sau_lop():
    from application.rule import _nhan_van

    assert _nhan_van(0) == "a"
    assert _nhan_van(25) == "z"
    assert _nhan_van(26) == "aa"


def test_phoi_khuon_kho_bon_dong_theo_dung_hai_mau_cua_muc_4_3():
    from application.rule import phoi_khuon_cua_kho

    assert phoi_khuon_cua_kho(("bang", "trac", "trac", "bang")) == "co_dien"
    assert phoi_khuon_cua_kho(("trac", "bang", "bang", "trac")) == "dao"
    assert phoi_khuon_cua_kho(("bang", "trac", "trac", "trac")) == "khac"
    # Hai mẫu của tài liệu đều là mẫu 4 dòng
    assert phoi_khuon_cua_kho(("bang", "trac")) == "khong_xac_dinh"


def test_vi_du_tai_lieu_KHONG_theo_mau_co_dien():
    """D4 chạy khuôn trắc, trong khi mẫu cổ điển đòi khuôn bằng — S4 cho phép."""
    v = kiem_tra_bai_tho(VI_DU_TAI_LIEU)
    assert v.phoi_khuon_theo_kho == ("khac",)
    assert v.dat is True  # phá khuôn KHÔNG làm bài trượt


def test_bay_kieu_nhip_cua_tai_lieu_deu_cong_dung_bay():
    from application.rule import NHIP_TAI_LIEU, nhip_hop_le

    assert len(NHIP_TAI_LIEU) == 7
    for ten, cach_ngat in NHIP_TAI_LIEU.items():
        assert nhip_hop_le(cach_ngat), ten
        assert "/".join(str(v) for v in cach_ngat) == ten


def test_nhip_khong_cong_du_bay_thi_khong_hop_le():
    from application.rule import nhip_hop_le

    assert nhip_hop_le((4, 4)) is False
    assert nhip_hop_le((4, 0, 3)) is False
    assert nhip_hop_le(()) is False


def test_van_lung_duoc_DO_chu_khong_lam_bai_truot():
    from application.rule import van_lung_cua_dong

    # P5 "xanh" hiệp với P7 "cành"
    tieng = tach_tieng("Trời cao mây biếc xanh ngời cành")
    assert 5 in van_lung_cua_dong(tieng)

    # Bài phải đủ 4 dòng vì QĐ-7 đòi một cụm bốn dòng liên tiếp khớp §5.2.
    # Ở đây là sơ đồ abab (vần cách): cành / về / chanh / tre.
    v = kiem_tra_bai_tho(
        "Trời cao mây biếc xanh ngời cành\n"
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh tre"
    )
    assert v.dat is True, "S7 là QUYỀN — vần lưng không được làm bài trượt"
    assert any(dong == 1 and vi_tri == 5 for dong, vi_tri in v.van_lung)


def test_ty_le_khuon_KHONG_tinh_tren_dong_sai_so_tieng():
    """Trộn dòng sai luật vào mẫu số là trộn hai chuyện khác nhau."""
    bai = "Chiều rơi chậm xuống mái rêu xanh\nGió về"  # D1 khuôn bằng, D2 sai luật
    v = kiem_tra_bai_tho(bai)
    assert v.dat is False
    assert v.ty_le_theo_khuon == 1.0  # chỉ tính trên D1
