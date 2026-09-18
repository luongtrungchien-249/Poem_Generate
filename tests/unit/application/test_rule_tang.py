"""Kiểm chứng kiến trúc tầng của rule.py — theo docs/Plan_Rule_Phan_Tang.md.

Các test ở đây không kiểm một bài thơ cụ thể. Chúng cưỡng chế những nguyên tắc mà
plan đặt ra, để mã nguồn không lặng lẽ trôi khỏi tài liệu luật:

    N1  tiêu chí mỗi tầng phải trích được từ câu chữ tài liệu
    N2  điều luật loại QUYỀN không bao giờ được đánh trượt bài
    N3  điều đòi ý đồ tác giả hoặc ngữ nghĩa phải được ghi công khai là không kiểm được
"""

import pytest

from application.rule import (
    GHI_DE_BOI_QUYET_DINH,
    LOAI_DIEU_MEM,
    LUAT,
    MA_LUAT,
    NHIP_TAI_LIEU,
    TANG,
    AmTiet,
    nhip_chu_dao,
    nhip_kha_di_cua_dong,
    phan_tich_am_tiet,
)

# ════════════════════ Bảng tầng phủ đúng bảng luật ════════════════════


def test_moi_ma_luat_thuoc_DUNG_MOT_tang():
    """Thêm một điều luật mà quên xếp tầng thì test này đỏ."""
    phu = [ma for t in TANG for ma in t.ma_luat]
    tat_ca = {d.ma for d in LUAT}

    assert len(phu) == len(set(phu)), "có mã luật bị xếp vào nhiều hơn một tầng"
    assert set(phu) == tat_ca, f"thiếu: {tat_ca - set(phu)} | thừa: {set(phu) - tat_ca}"


def test_tang_duoc_danh_so_lien_tuc_tu_mot():
    assert [t.so for t in TANG] == list(range(1, len(TANG) + 1))


def test_moi_tang_co_trich_dan_luat_KHONG_rong():
    """N1: không có chữ trong tài liệu thì không được có tiêu chí."""
    for t in TANG:
        assert t.trich_luat.strip(), f"tầng {t.so} thiếu trích dẫn luật"


def test_tieu_chi_cua_tang_phai_nam_trong_pham_vi_tang():
    for t in TANG:
        thua = set(t.tieu_chi_tu) - set(t.ma_luat)
        assert not thua, f"tầng {t.so} lấy tiêu chí từ điều luật ngoài phạm vi: {thua}"


# ════════════════════ N2 — quyền không được đánh trượt ════════════════════


def test_khong_dieu_QUYEN_nao_lam_tieu_chi_chan():
    """N2: trượt vì tác giả dùng một QUYỀN là mâu thuẫn tự thân.

    Ví dụ: S8 nói "bài có thể không gieo vần", nên tầng vần không được đòi bài
    phải có vần.
    """
    xau = [
        (t.so, ma)
        for t in TANG
        for ma in t.tieu_chi_tu
        if LOAI_DIEU_MEM.get(ma) == "quyen"
    ]
    assert not xau, f"điều luật loại QUYỀN bị dùng làm tiêu chí chặn: {xau}"


def test_moi_dieu_mem_deu_duoc_phan_loai():
    mem = {d.ma for d in LUAT if d.loai == "mem"}
    assert mem == set(LOAI_DIEU_MEM), (
        f"chưa phân loại: {mem - set(LOAI_DIEU_MEM)} | "
        f"phân loại thừa: {set(LOAI_DIEU_MEM) - mem}"
    )


@pytest.mark.parametrize("ma", ["S1", "S4", "S7", "S8", "S9", "S10", "S12", "S16", "S18", "S20", "S21"])
def test_cac_dieu_dung_chu_CO_THE_deu_la_quyen(ma):
    """Đối chiếu ngược: điều nào tài liệu dùng chữ cho phép thì phải xếp là quyền."""
    assert LOAI_DIEU_MEM[ma] == "quyen", f"{ma}: {MA_LUAT[ma].noi_dung}"


# ════════════════════ N3 — ghi công khai chỗ không kiểm được ════════════════════


def test_S3_va_S15_duoc_ghi_la_KHONG_kiem_duoc():
    """Hai điều này đòi ý đồ tác giả và ngữ nghĩa, không suy ra từ hình thức."""
    khong_kiem = {ma for t in TANG for ma in t.khong_kiem_duoc}
    assert "S3" in khong_kiem, "S3 'P7 cần chọn có chủ đích' phải được ghi là không kiểm được"
    assert "S15" in khong_kiem, "S15 'đổi nhịp nên trùng chỗ chuyển ý' phải được ghi là không kiểm được"


def test_dieu_KHONG_kiem_duoc_thi_KHONG_dong_thoi_la_tieu_chi():
    for t in TANG:
        chong = set(t.khong_kiem_duoc) & set(t.tieu_chi_tu)
        assert not chong, f"tầng {t.so}: {chong} vừa là tiêu chí vừa ghi là không kiểm được"


def test_moi_ghi_de_deu_tro_ve_mot_dieu_luat_co_that():
    """Quyết định dự án chặt hơn tài liệu phải ghi rõ ghi đè điều nào."""
    for ma in GHI_DE_BOI_QUYET_DINH:
        assert ma in MA_LUAT, f"ghi đè điều luật không tồn tại: {ma}"


def test_S4_duoc_ghi_nhan_la_bi_ghi_de():
    """QĐ-2 chặt hơn tài liệu. Ghi ra để mã nguồn và tài liệu không nói hai điều khác nhau."""
    assert "S4" in GHI_DE_BOI_QUYET_DINH
    assert LOAI_DIEU_MEM["S4"] == "quyen"




# ═══════════ QĐ-5 — bảng vần Trần Trọng Kim, "Việt thi" I-6 ═══════════
# Nguồn và hồ sơ duyệt: docs/Nguon_Bang_Van_Thong.md


def test_bang_van_dung_dung_so_canh_cua_nguon():
    """Tách bạch phần LẤY TỪ NGUỒN và phần SUY DIỄN, để ai cũng kiểm lại được.

    Nguồn (Việt thi I-6)  : 55 vần, 73 cạnh
    🔶 SD-2 thêm          : 4 cạnh (o~ua, ia~uê, ac~ươc, ât~ưt)
    Tổng                  : 62 vần, 77 cạnh

    Ba con số này lệch nghĩa là bảng đã bị sửa so với nguồn, hoặc phần suy diễn
    đã âm thầm phình ra. Cả hai đều phải làm đỏ test.
    """
    from itertools import combinations

    from application.rule import _CAP_TTK, _NHOM_TTK, CAP_VAN_THONG

    nguon: set[frozenset[str]] = set()
    for nhom in _NHOM_TTK:
        for a, b in combinations(nhom, 2):
            nguon.add(frozenset((a, b)))
    for a, b in _CAP_TTK[:-4]:
        nguon.add(frozenset((a, b)))

    assert len(nguon) == 73, "số cặp lệch với bảng Việt thi I-6"
    assert len({v for c in nguon for v in c}) == 55, "số vần lệch với Việt thi I-6"

    them = {frozenset(c) for c in _CAP_TTK[-4:]} - nguon
    assert len(them) == 4, "phần suy diễn SD-2 phải đúng 4 cặp, không hơn"

    assert len(CAP_VAN_THONG) == 77
    assert len({v for c in CAP_VAN_THONG for v in c}) == 62


def test_hiep_van_KHONG_bac_cau_dung_nhu_nguon():
    """Trần Trọng Kim: "ang thông với ương (không thông được với uông…)".

    Đây là test QUAN TRỌNG NHẤT của bảng vần. Nếu nó đỏ, nghĩa là ai đó đã ép
    bảng thành lớp tương đương và bịa thêm cặp hiệp vần mà nguồn không cho.
    """
    from application.rule import hiep_van

    assert hiep_van("vang", "vương").hiep is True
    assert hiep_van("vuông", "vương").hiep is True
    assert hiep_van("vang", "vuông").hiep is False, "nguồn ghi rõ ang ≁ uông"

    # a ~ ơ, ơ ~ ư là hai phát biểu RỜI ⇒ a ≁ ư
    assert hiep_van("ta", "tơ").hiep is True
    assert hiep_van("tơ", "tư").hiep is True
    assert hiep_van("ta", "tư").hiep is False

    # "ay" chỉ thông với "ai", không thông với nhóm oi/ôi/ơi/ươi/ui
    assert hiep_van("may", "mai").hiep is True
    assert hiep_van("mai", "moi").hiep is True
    assert hiep_van("may", "moi").hiep is False


def test_nhung_cap_tung_bi_toi_bia_ra_nay_phai_bi_tu_choi():
    """Bảng tôi tự liệt kê trước đây có cặp nguồn KHÔNG cho — phải bật ra."""
    from application.rule import hiep_van

    assert hiep_van("xe", "xa").hiep is False, "e~a là do tôi bịa"
    assert hiep_van("mây", "may").hiep is False, "ây~ay chỉ có ở bảng vô danh"


def test_nhung_cap_bang_cu_THIEU_nay_phai_duoc_nhan():
    from application.rule import hiep_van

    assert hiep_van("sao", "sau").hiep is True     # ao ~ au
    assert hiep_van("tăm", "tâm").hiep is True     # ăm ~ âm
    assert hiep_van("cười", "trời").hiep is True   # ươi ~ ơi


def test_kho_khong_bac_cau_thi_KHONG_co_so_do_van():
    """Khổ mà quan hệ vần không phải tương đương thì không gán nhãn bừa."""
    from application.rule import suy_so_do_van

    assert suy_so_do_van(("vang", "vương", "vuông")) == ("?", "?", "?")


def test_so_do_van_KHONG_phu_thuoc_thu_tu_dong():
    from itertools import permutations

    from application.rule import suy_so_do_van

    mau = ("xanh", "ve", "mảnh", "về")
    chuan = None
    for hoan_vi in permutations(range(4)):
        ds = tuple(mau[i] for i in hoan_vi)
        so_do = suy_so_do_van(ds)
        gom = {}
        for vi_tri, nhan in enumerate(so_do):
            gom.setdefault(f"x{vi_tri}" if nhan == "x" else nhan, set()).add(ds[vi_tri])
        hien_tai = frozenset(frozenset(v) for v in gom.values())
        chuan = hien_tai if chuan is None else chuan
        assert hien_tai == chuan, f"thứ tự {hoan_vi} cho cách gom khác"


def test_so_do_van_khop_cac_kieu_trong_tai_lieu():
    from application.rule import suy_so_do_van

    # vần ba dòng (Đường luật): mai/tai/cười cùng nhóm ai-ươi, "gió" buông
    assert "".join(suy_so_do_van(("mai", "tai", "gió", "cười"))) == "aaxa"
    # vần liền
    assert "".join(suy_so_do_van(("mai", "tai", "non", "con"))) == "aabb"
    # vần cách
    assert "".join(suy_so_do_van(("mai", "non", "tai", "con"))) == "abab"
    # vần ôm
    assert "".join(suy_so_do_van(("mai", "non", "con", "tai"))) == "abba"


# ════════════════════ N1 — tiêu chí phải trích được từ tài liệu ════════════════════
#
# ⚠️ GHI CHÚ TRUNG THỰC: mục N1 và ba mục dưới đây được VIẾT LẠI ngày 18/09/2026.
# Bản gốc bị tôi xoá nhầm khi cắt file bằng `str.index` trên một tiêu đề mục trùng
# nhau. Repo chưa commit nên không khôi phục được. Độ phủ có thể khác bản cũ.


def test_moi_tang_deu_neu_ro_dieu_nao_KHONG_kiem_duoc():
    """N1+N3: tầng nào bỏ qua điều gì thì phải nói ra, không im lặng."""
    for t in TANG:
        for ma in t.khong_kiem_duoc:
            assert ma in MA_LUAT, f"tầng {t.so} nêu mã luật không có thật: {ma}"
            assert ma not in t.tieu_chi_tu, (
                f"tầng {t.so}: {ma} vừa là tiêu chí vừa là không kiểm được"
            )


def test_khong_tang_nao_dat_nguong_phan_tram_tu_bia():
    """N1 cấm ngưỡng tự nghĩ. Tài liệu luật không có một con số phần trăm nào."""
    import re

    from application.rule import TANG

    for t in TANG:
        for txt in (t.ten, t.trich_luat):
            assert not re.search(r"\d+\s*%", txt), (
                f"tầng {t.so} nhắc tới một ngưỡng phần trăm: {txt!r}"
            )


# ════════════════════ Phân tích âm tiết ════════════════════


@pytest.mark.parametrize(
    "tieng,am_dau,am_dem,am_chinh,am_cuoi",
    [
        ("ta", "t", "", "a", ""),
        ("hoa", "h", "o", "a", ""),
        # "uyê" = âm đệm u + âm chính iê ("yê" chỉ là cách viết của iê sau âm đệm)
        ("nguyễn", "ng", "u", "iê", "n"),
        ("trời", "tr", "", "ơ", "i"),
        ("nghiêng", "ngh", "", "iê", "ng"),
        ("gì", "g", "", "i", ""),
        # "qu" tách thành âm đầu q + âm đệm u, đồng bộ với "hoa" = h + o
        ("quả", "q", "u", "a", ""),
        ("xanh", "x", "", "a", "nh"),
    ],
)
def test_phan_tich_am_tiet_tach_dung_bon_phan(
    tieng, am_dau, am_dem, am_chinh, am_cuoi
):
    """ÂM TIẾT = thanh + [âm đầu] + VẦN; VẦN = [âm đệm] + âm chính + [âm cuối]."""
    at = phan_tich_am_tiet(tieng)
    assert at.am_dau == am_dau
    assert at.am_dem == am_dem
    assert at.am_chinh == am_chinh
    assert at.am_cuoi == am_cuoi


def test_am_tiet_tra_ve_dung_kieu_AmTiet():
    at = phan_tich_am_tiet("trời")
    assert isinstance(at, AmTiet)
    assert at.goc == "trơi"
    assert at.van == "ơi"


# ════════════════════ Nhịp — QĐ-4, QĐ-4b, QĐ-6 ════════════════════


def test_bang_nhip_dung_BAY_kieu_cua_tai_lieu():
    """QĐ-6: tập nhịp là tập ĐÓNG. Thêm kiểu thứ tám là phá luật."""
    assert set(NHIP_TAI_LIEU) == {"4/3", "3/4", "2/2/3", "2/5", "5/2", "1/6", "3/2/2"}
    for ten, cac_ve in NHIP_TAI_LIEU.items():
        assert sum(cac_ve) == 7, f"nhịp {ten} không cộng đủ 7 tiếng"


def test_nhip_khai_bao_ngoai_bay_kieu_thi_khong_duoc_nhan():
    assert nhip_kha_di_cua_dong(7, "6/1") == frozenset()
    assert nhip_kha_di_cua_dong(7, "4/3") == frozenset({"4/3"})


def test_dong_khong_du_bay_tieng_thi_khong_co_nhip_nao():
    assert nhip_kha_di_cua_dong(6) == frozenset()
    assert nhip_kha_di_cua_dong(8) == frozenset()


def test_nhip_chu_dao_la_GIAO_cua_moi_dong():
    """QĐ-4b: phải tồn tại một kiểu phủ MỌI dòng."""
    assert nhip_chu_dao((
        frozenset({"2/2/3", "4/3"}),
        frozenset({"4/3"}),
        frozenset({"4/3", "3/4"}),
        frozenset({"4/3", "5/2"}),
    )) == "4/3"


def test_giao_rong_thi_KHONG_co_nhip_chu_dao():
    assert nhip_chu_dao((frozenset({"4/3"}), frozenset({"3/4"}))) is None


def test_bai_khong_co_dong_nao_thi_khong_co_nhip_chu_dao():
    assert nhip_chu_dao(()) is None


# ════════════════════ Thực thi tuần tự và dừng sớm ════════════════════


def test_truot_tang_som_thi_cac_tang_sau_KHONG_chay():
    """Mỗi bài phải qua tầng N mới tới tầng N+1 — yêu cầu gốc của chủ dự án."""
    from application.rule import kiem_tra_bai_tho

    # Tầng 1 là H3 (đủ số dòng) nên bài này qua; tầng 2 là H1 (đúng 7 tiếng) nên trượt.
    v = kiem_tra_bai_tho("Một dòng sáu tiếng thôi mà\nDòng hai cũng sáu tiếng mà thôi")
    assert v.dat is False
    assert v.tang_dung_lai == 2
    sau_khi_dung = [t for t in v.tang if t.so > v.tang_dung_lai]
    assert sau_khi_dung, "phải vẫn liệt kê các tầng sau để biên bản đầy đủ"
    assert all(not t.da_chay for t in sau_khi_dung)


def test_bai_dat_thi_MOI_tang_deu_da_chay():
    from application.rule import kiem_tra_bai_tho
    from tests.unit.application.test_rule import VI_DU_TAI_LIEU

    v = kiem_tra_bai_tho(VI_DU_TAI_LIEU)
    if v.dat:
        assert all(t.da_chay for t in v.tang)
        assert v.tang_dung_lai is None


def test_tang_duoc_bao_cao_theo_dung_thu_tu_tang_dan():
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("Ta đi ta đi ta đi ta\nTa đi ta đi ta đi ta")
    assert [t.so for t in v.tang] == sorted(t.so for t in v.tang)


# ════════════════════ QĐ-7 — tiêu chí chặn của tầng 5 ════════════════════
#
# Nguyên văn chủ dự án: "trong bài phải có ít nhất là 4 dòng liên tiếp có cấu
# trúc như thế ở cuối" — bốn sơ đồ ở §5.2 tài liệu luật.


def test_bon_so_do_dung_bang_tai_lieu_khong_hon_khong_kem():
    """§5.2 có ĐÚNG bốn sơ đồ bốn dòng. Thêm một cái nữa là tự chế luật."""
    from application.rule import SO_DO_KHO_TAI_LIEU

    assert set(SO_DO_KHO_TAI_LIEU) == {"aabb", "abab", "abba", "aaxa"}


@pytest.mark.parametrize(
    "cuoi,ma",
    [
        (("mai", "tai", "non", "con"), "aabb"),   # vần liền
        (("mai", "non", "tai", "con"), "abab"),   # vần cách
        (("mai", "non", "con", "tai"), "abba"),   # vần ôm
        (("mai", "tai", "gió", "cười"), "aaxa"),  # vần ba dòng
    ],
)
def test_nhan_dung_tung_so_do_cua_tai_lieu(cuoi, ma):
    from application.rule import khop_so_do_bon_dong

    assert khop_so_do_bon_dong(cuoi) == ma


def test_bon_dong_cung_MOT_van_KHONG_phai_so_do_nao():
    """Khớp phải nghiêm ngặt hai chiều.

    Nếu chỉ đòi "dòng cùng chữ cái thì hiệp" mà không đòi "dòng khác chữ cái thì
    không hiệp", thì bốn dòng cùng một vần sẽ bị nhận nhầm là "aabb".
    """
    from application.rule import khop_so_do_bon_dong

    assert khop_so_do_bon_dong(("mai", "tai", "cai", "vai")) is None


def test_cua_so_truot_suot_bai_va_duoc_vat_qua_kho():
    """QĐ-7 nói "trong bài", không nói "trong một khổ"."""
    from application.rule import cua_so_khop_so_do

    # dòng 1 buông; cụm khớp nằm ở dòng 2–5
    cuoi = ("bàn", "mai", "tai", "non", "con")
    assert cua_so_khop_so_do(cuoi) == ((2, "aabb"),)


def test_bai_duoi_bon_dong_thi_TRUOT_tang_5():
    """Hệ quả trực tiếp của QĐ-7, ghi lại để không ai tưởng là lỗi.

    H3 chỉ đòi từ hai dòng, nên bài hai dòng vẫn THUỘC THỂ; nhưng không đủ một
    cụm bốn dòng nên không ĐẠT chuẩn dự án.
    """
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho(
        "Trời cao mây biếc xanh ngời cành\nGọi một mùa xa chẳng dám về"
    )
    assert v.thuoc_the is True
    assert v.dat is False
    assert v.tang_dung_lai == 5


def test_van_hon_hop_van_duoc_qua_vi_chi_can_MOT_cum_khop():
    """§5.2: "Vần hỗn hợp: phối nhiều sơ đồ trên trong cùng một bài".

    Đòi cả bài theo một sơ đồ duy nhất là chặt hơn tài liệu ở chỗ tài liệu cho
    phép — test này chặn việc siết nhầm như thế.
    """
    from application.rule import cua_so_khop_so_do

    # 1–4 là abab, 5–8 là aabb: hai sơ đồ khác nhau trong cùng một bài
    cuoi = ("mai", "non", "tai", "con", "bè", "tre", "mưa", "thưa")
    khop = cua_so_khop_so_do(cuoi)
    assert ("aabb" in [m for _, m in khop]) or ("abab" in [m for _, m in khop])
    assert khop, "vần hỗn hợp vẫn phải qua được tầng 5"


def test_tang_5_truot_thi_bang_chung_noi_ro_bai_van_the_nao():
    """Nói "không khớp" mà không nói khớp cái gì thì không phải bằng chứng."""
    from application.rule import kiem_tra_bai_tho

    # Qua tầng 1–4, trượt đúng tại tầng 5: sơ đồ thật là "axax", không nằm trong
    # bốn sơ đồ của §5.2.
    v = kiem_tra_bai_tho(
        "Trời cao mây biếc xanh ngời cành\n"
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh mưa"
    )
    assert v.tang_dung_lai == 5
    t5 = next(t for t in v.tang if t.so == 5)
    assert t5.da_chay is True and t5.dat is False
    assert "axax" in t5.bang_chung, "bằng chứng phải nói bài VẦN THẾ NÀO"
    assert t5.vi_pham and t5.vi_pham[0].ma == "S11"
