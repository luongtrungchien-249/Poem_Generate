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


@pytest.mark.parametrize(
    "ma", ["S1", "S9", "S10", "S12", "S16", "S18", "S20", "S21"]
)  # S4, S7, S8 đã xoá khỏi bảng luật 18/09/2026 — xem test_..._da_xoa_...
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


def test_S4_S5_S7_S8_da_xoa_khoi_bang_luat_va_KHONG_duoc_quay_lai():
    """Chủ dự án xoá bốn mã ngày 18/09/2026.

        S4  "Có thể phá khuôn khi dụng ý biểu đạt đòi hỏi"   — QĐ-2 đã cấm phá khuôn
        S5  "Phá khuôn nên tập trung ở dòng cần nhấn"        — không còn đối tượng
        S7  "Có thể dùng thêm vần lưng ở P4 hoặc P5"         — gộp vào S1
        S8  "Bài có thể không gieo vần"                      — QĐ-7b đòi phải có vần

    S8 là ca đáng chú ý nhất: giữ nó lại thì bảng luật vừa CHO PHÉP bài không
    gieo vần (S8) vừa ĐÁNH TRƯỢT bài không gieo vần (QĐ-7b) — vi phạm N2 ngay
    trong chính tầng 5. Chủ dự án chọn xoá thay vì ghi vào GHI_DE_BOI_QUYET_DINH.
    """
    for ma in ("S4", "S5", "S7", "S8"):
        assert ma not in MA_LUAT, f"{ma} đã bị xoá, không được quay lại bảng luật"
        assert ma not in LOAI_DIEU_MEM, f"{ma} đã bị xoá, không được còn phân loại"
        assert all(ma not in t.ma_luat for t in TANG), f"{ma} vẫn còn trong một tầng"


def test_QD2_KHONG_con_ghi_de_dieu_nao_sau_khi_xoa_S4():
    """S4 là điều DUY NHẤT mà QĐ-2 ghi đè. Xoá S4 thì QĐ-2 hết mâu thuẫn.

    Ghi bừa một mục ghi đè không còn đối tượng sẽ báo một mâu thuẫn không tồn tại
    — đúng loại sai lầm mà bảng GHI_DE_BOI_QUYET_DINH sinh ra để tránh.
    """
    assert "S4" not in GHI_DE_BOI_QUYET_DINH
    assert set(GHI_DE_BOI_QUYET_DINH) == {"S13", "S15"}, (
        "chỉ còn hai điều về NHỊP bị QĐ-4/QĐ-4b ghi đè"
    )


def test_so_hieu_dieu_luat_KHONG_duoc_danh_lai_sau_khi_xoa():
    """S4, S5, S7 để trống vĩnh viễn; S6 KHÔNG được dồn lên thành S4.

    Đánh số lại sẽ khiến mọi tham chiếu cũ trong báo cáo, dữ liệu đã xuất và test
    trỏ sai điều luật mà không ai biết — hỏng im lặng, không sửa được.
    """
    ma_s = [d.ma for d in LUAT if d.ma.startswith("S")]
    assert ma_s == [
        "S1", "S2", "S3", "S6", "S9", "S10", "S11", "S12",
        "S13", "S14", "S15", "S16", "S17", "S18", "S19", "S20", "S21",
    ]
    assert len(LUAT) == 26, "30 điều ban đầu trừ S4, S5, S7, S8"


def test_S1_nay_gom_ca_van_lung_va_van_la_QUYEN():
    """S7 gộp vào S1: cả hai vế đều là quyền, đo rồi ghi, không phán quyết."""
    from application.rule import kiem_tra_bai_tho

    assert LOAI_DIEU_MEM["S1"] == "quyen"
    noi_dung = MA_LUAT["S1"].noi_dung
    assert "có thể tự do" in noi_dung, "S1 dùng chữ CÓ THỂ, không phải 'hoàn toàn'"
    assert "vần lưng" in noi_dung, "vế gộp từ S7 phải nằm trong nội dung S1"

    # Vần lưng nay báo cáo ở TẦNG 4 (nơi S1 ở), không phải tầng 5.
    bai = (
        "Chiều rơi chậm xuống mái rêu xanh"
        "\n" "Con ngõ nhỏ dài hơn tiếng ve"
        "\n" "Ai đứng bên kia bờ nắng mảnh"
        "\n" "Gọi một mùa xa chẳng dám về"
    )
    v = kiem_tra_bai_tho(bai)
    t4 = next(k for k in v.tang if k.so == 4)
    t5 = next(k for k in v.tang if k.so == 5)
    assert "so_vi_tri_van_lung" in t4.chi_tiet
    assert "so_vi_tri_van_lung" not in t5.chi_tiet, "tầng 5 không còn giữ vần lưng"
    assert t4.chi_tiet["S1_p1_p3_p5_khong_bi_kiem"] is True




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

    # Tầng 1 là H3 + H4: bài 4 dòng nên có phân dòng và đúng bội 4 → qua.
    # Tầng 2 là H1: mọi dòng chỉ 6 tiếng → trượt ở đây.
    v = kiem_tra_bai_tho("\n".join(["Một dòng sáu tiếng thôi mà"] * 4))
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


def test_bai_duoi_bon_dong_bi_H4_bat_o_TANG_1():
    """H4 (18/09) đổi chỗ bắt bài ngắn — ghi lại để không ai tưởng là lỗi.

    TRƯỚC H4: bài 2 dòng qua tầng 1 (H3 chỉ đòi ≥2 dòng), `thuoc_the = True`,
    rồi trượt ở tầng 5 vì QĐ-7 đòi một cụm bốn dòng liên tiếp.

    SAU H4: bài 2 dòng trượt ngay tầng 1 vì 2 không chia hết cho 4. Và vì H4 là
    ràng buộc CỨNG nên `thuoc_the` cũng thành False — bài không còn thuộc thể.

    Hệ quả kiến trúc: nhánh "bài dưới 4 dòng" trong tầng 5 nay KHÔNG CÒN VỚI TỚI
    ĐƯỢC qua đường chạy bình thường. Mã đó vẫn giữ vì `_tang5_van` có thể được
    gọi trực tiếp, nhưng đừng trông đợi thấy nó trong số liệu corpus.
    """
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho(
        "Trời cao mây biếc xanh ngời cành\nGọi một mùa xa chẳng dám về"
    )
    assert v.thuoc_the is False, "H4 là luật CỨNG nên vào cả cờ thuoc_the"
    assert v.dat is False
    assert v.tang_dung_lai == 1
    vp = [x for x in v.vi_pham if x.ma == "H4"]
    assert vp, "phải có vi phạm H4"
    assert vp[0].thuc_te == "2 dòng, dư 2 khi chia 4"
    assert {x.ma for x in v.vi_pham} == {"H3", "H4"}, (
        "2 dòng vi phạm CẢ HAI: chưa đủ 4 dòng (H3) và không bội 4 (H4)"
    )


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
    """Nói "không có vần" mà không nói bài vần thế nào thì không phải bằng chứng."""
    from application.rule import kiem_tra_bai_tho

    # Bài thật trong corpus (id=4051): qua tầng 1-4, trượt tại tầng 5 vì KHÔNG
    # cặp tiếng cuối nào hiệp vần — sơ đồ "xxxx". Từ QĐ-7b (18/09/2026) đây là
    # dạng DUY NHẤT còn bị tầng 5 loại.
    bai = (
        "Cho tôi ủ chút sương trăng trước,"
        "\n" "Với lá vàng rơi cuối ngõ khuya."
        "\n" "Nhỡ khi tiếc nuối người quay lại,"
        "\n" "Đã sẵn hương thu ướp tóc thề."
    )
    v = kiem_tra_bai_tho(bai)
    assert v.tang_dung_lai == 5
    t5 = next(t for t in v.tang if t.so == 5)
    assert t5.da_chay is True and t5.dat is False
    assert "xxxx" in t5.bang_chung, "bằng chứng phải nói bài VẦN THẾ NÀO"
    assert t5.vi_pham and t5.vi_pham[0].ma == "S11"


# ═══════ Tầng 3 — F1–F5 là ràng buộc ĐÃ GỠ, không phải điều kiện loại trừ ═══════


def test_tang3_KHONG_duoc_chan_bai_nao():
    """§3: có niêm/đối/độc vận là ĐƯỢC PHÉP, không phải tiêu chí nhận diện thể.

    Bản trước đặt tầng này là `chan` và loại 4.288 bài — đọc ngược tài liệu.
    Test này chặn việc khôi phục nhầm hành vi cũ.
    """
    t3 = next(t for t in TANG if t.so == 3)
    assert t3.muc == "ghi_nhan", "tầng 3 không được là tầng chặn"
    assert t3.tieu_chi_tu == (), "tầng 3 không được có tiêu chí đánh trượt"


def test_bai_giong_duong_luat_van_DAT_nhung_co_ghi_nhan():
    """F5: 'Không giới hạn số dòng ở con số 4 hoặc 8'."""
    from application.rule import kiem_tra_bai_tho

    # 8 dòng, độc vận, đúng khuôn — dáng Đường luật
    bai = "\n".join([
        "Trời cao mây biếc xanh ngời cành",
        "Gọi một mùa xa chẳng dám nhanh",
        "Người xưa đứng lặng bên hàng chanh",
        "Nghe gió lùa qua những nhánh mành",
        "Chiều xuống trong veo bên mái tranh",
        "Vọng tiếng ai cười phía cuối ghềnh",
        "Đường về lặng lẽ qua rừng xanh",
        "Một thoáng hương xưa chợt hoá thành",
    ])
    v = kiem_tra_bai_tho(bai)
    t3 = next(k for k in v.tang if k.so == 3)
    assert t3.da_chay is True
    assert t3.dat is True, "tầng ghi nhận không bao giờ trượt"
    assert t3.vi_pham == (), "không được dựng ViPham cho điều luật chỉ nói 'không bắt buộc'"
    assert v.tang_dung_lai != 3, "tầng 3 không được làm bài dừng"


def test_tang_GHI_NHAN_khong_gop_vao_phan_quyet_dat():
    """Tầng ghi nhận trả dat=False cũng không được loại bài."""
    from dataclasses import replace

    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho(
        "Trời cao mây biếc xanh ngời cành\n"
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh tre"
    )
    assert v.dat is True
    # Mô phỏng một tầng ghi nhận trượt: phán quyết chung phải không đổi
    gia_lap = tuple(
        replace(k, dat=False) if k.muc == "ghi_nhan" else k for k in v.tang
    )
    assert all(k.dat for k in gia_lap if k.muc == "chan")


# ═══════ H4 (18/09/2026) — số dòng phải là bội của 4, luật CỨNG ═══════


def test_H4_la_luat_CUNG_va_thuoc_tang_1():
    from application.rule import HAM_KIEM_CUNG, MA_CUNG

    assert "H4" in MA_CUNG, "H4 phải là luật cứng"
    assert "H4" in HAM_KIEM_CUNG, "luật cứng phải có hàm kiểm tương ứng"
    t1 = next(t for t in TANG if t.so == 1)
    assert t1.ma_luat == ("H3", "H4")
    assert t1.tieu_chi_tu == ("H3", "H4"), "cả hai đều là tiêu chí chặn"


@pytest.mark.parametrize("so_dong,mong_doi", [(4, True), (8, True), (12, True), (40, True)])
def test_so_dong_la_boi_cua_4_thi_qua_tang_1(so_dong, mong_doi):
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * so_dong))
    t1 = next(k for k in v.tang if k.so == 1)
    assert t1.dat is mong_doi
    assert t1.chi_tiet["la_boi_cua_4"] is mong_doi


@pytest.mark.parametrize("so_dong,du", [(1, 1), (2, 2), (3, 3), (5, 1), (6, 2), (7, 3), (9, 1)])
def test_so_dong_KHONG_boi_cua_4_thi_truot_ngay_tang_1(so_dong, du):
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * so_dong))
    assert v.dat is False
    assert v.tang_dung_lai == 1
    assert v.thuoc_the is False, "H4 cứng nên bài không còn thuộc thể"
    t1 = next(k for k in v.tang if k.so == 1)
    assert t1.chi_tiet["du_khi_chia_4"] == du


def test_bai_RONG_bi_H3_bat_chu_khong_phai_H4():
    """0 chia hết cho 4, nên H4 một mình KHÔNG loại được bài rỗng.

    Đây là lý do H3 vẫn cần thiết sau khi có H4.
    """
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("")
    t1 = next(k for k in v.tang if k.so == 1)
    assert t1.chi_tiet["la_boi_cua_4"] is True, "0 % 4 == 0"
    assert t1.chi_tiet["co_phan_dong"] is False
    assert t1.dat is False
    assert {x.ma for x in v.vi_pham} == {"H3"}, "chỉ H3 bắt, không phải H4"


def test_F5_va_S16_da_hop_nhat_KHONG_con_mau_thuan_voi_H4():
    """Chủ dự án cho gộp: 'không giới hạn số dòng' + 'bội của 4' cùng đúng."""
    from application.rule import GHI_DE_BOI_QUYET_DINH

    for ma in ("F5", "S16"):
        noi_dung = MA_LUAT[ma].noi_dung
        assert "bội của 4" in noi_dung, f"{ma} phải nêu ràng buộc bội 4"
        assert ma not in GHI_DE_BOI_QUYET_DINH, (
            f"{ma} đã hợp nhất với H4, không còn bị ghi đè"
        )


def test_bang_chung_H4_noi_ro_so_dong_va_phan_du():
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * 8))
    t1 = next(k for k in v.tang if k.so == 1)
    assert "8 = 4 × 2" in t1.bang_chung

    v2 = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * 6))
    t2 = next(k for k in v2.tang if k.so == 1)
    assert "không phải bội của 4 (dư 2)" in t2.bang_chung


def test_H4_KHONG_duoc_goi_y_them_hay_bot_dong():
    """Luật cứng thì không có "cách sửa" — và sửa được cũng không được phép sửa.

    Bản trước gợi ý "bớt 2 dòng để về 4, hoặc thêm 2 dòng để lên 8". Đó là bảo
    xoá một câu thơ hoặc viết thêm câu không có trong bài. Chủ dự án bác thẳng:
    *"không được sửa nội dung cho thêm hay xóa nội dung thơ, phải giữ nguyên nội
    dung thơ"* và *"đây là luật cứng không thể sửa để cho bài thơ pass"*.

    Test này chặn việc gợi ý ấy quay lại dưới bất kỳ hình thức nào.
    """
    import re

    from application.rule import kiem_tra_bai_tho

    # Bắt đúng dạng CHỈ DẪN SỬA — "thêm 2 dòng", "bớt 3 dòng", "để lên 8".
    # Không bắt chữ "thêm" trần, vì chính câu CẤM cũng chứa nó:
    # "KHÔNG thêm hay bớt dòng để ép qua".
    CHI_DAN_SUA = re.compile(r"(thêm|bớt)\s+\d+\s+dòng|để (lên|về)\s+\d+", re.I)

    for n in (1, 2, 3, 5, 6, 7, 9, 10, 13, 22):
        v = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * n))
        vp = next(x for x in v.vi_pham if x.ma == "H4")
        khop = CHI_DAN_SUA.search(vp.goi_y)
        assert not khop, f"{n} dòng: gợi ý chỉ dẫn sửa bài — {khop.group(0)!r}"
        thap = vp.goi_y.lower()
        assert "giữ nguyên" in thap, f"{n} dòng: phải nói rõ giữ nguyên nội dung"
        assert "luật cứng" in thap, f"{n} dòng: phải nói rõ đây là luật cứng"


def test_H4_bang_chung_van_neu_du_so_de_truy_duoc():
    """Bỏ gợi ý sửa KHÔNG có nghĩa là bỏ bằng chứng.

    Người đọc vẫn phải biết bài bao nhiêu dòng và dư mấy — đó là dữ kiện, khác
    hẳn với lời khuyên sửa bài.
    """
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho("\n".join(["Trời cao mây biếc xanh ngời cành"] * 6))
    vp = next(x for x in v.vi_pham if x.ma == "H4")
    assert vp.thuc_te == "6 dòng, dư 2 khi chia 4"
    t1 = next(k for k in v.tang if k.so == 1)
    assert t1.chi_tiet["so_dong"] == 6
    assert t1.chi_tiet["du_khi_chia_4"] == 2


# ═══════ Cổng 2 — CHỈ TÍNH TIẾNG, DẤU CÂU KHÔNG TÍNH ═══════


def test_cong2_bien_ban_CHUNG_MINH_da_loai_dau_cau():
    """Nói "dấu không tính" mà không đưa số thì người đọc phải tin suông.

    Biên bản phải nộp `so_dau_cau_da_loai` để kiểm lại được, và nêu rõ quy tắc
    đếm chứ không để người đọc tự đoán.
    """
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho(
        "Chiều rơi chậm xuống, mái rêu xanh!\n"   # 2 dấu: phẩy, than
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh tre"
    )
    t2 = next(k for k in v.tang if k.so == 2)
    assert t2.dat is True, "dấu câu bị loại nên dòng 1 vẫn đúng 7 tiếng"
    assert t2.chi_tiet["so_dau_cau_da_loai"] == 2
    quy_tac = str(t2.chi_tiet["quy_tac_dem"])
    assert "Unicode" in quy_tac
    assert "gạch nối" in quy_tac


def test_cong2_BAT_dung_dong_6_tieng_co_gach_ngang_dai():
    """🩸 Ca đã trả giá: bản cũ đếm dòng này thành 7 và cho PASS OAN."""
    from application.rule import kiem_tra_bai_tho

    v = kiem_tra_bai_tho(
        "Chiều rơi — chậm xuống mái rêu\n"     # 6 tiếng thật
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh tre"
    )
    assert v.dat is False
    assert v.tang_dung_lai == 2
    t2 = next(k for k in v.tang if k.so == 2)
    assert t2.chi_tiet["so_tieng_tung_dong"] == [6, 7, 7, 7]
    assert t2.chi_tiet["so_dau_cau_da_loai"] == 1
    vp = next(x for x in v.vi_pham if x.ma == "H1")
    assert vp.dong == 1 and vp.thuc_te == "6 tiếng"


def test_cong2_gach_noi_KHONG_bi_loai_ma_dung_de_tach():
    """Ngoại lệ duy nhất: "-" mang thông tin âm tiết nên tách tiếp, không loại."""
    from application.rule import dem_tieng, kiem_tra_bai_tho

    assert dem_tieng("ra-đi-ô") == 3

    v = kiem_tra_bai_tho(
        "Nghe ra-đi-ô giữa chiều mưa\n"        # ra-đi-ô = 3 tiếng -> tổng 7
        "Gọi một mùa xa chẳng dám về\n"
        "Người xưa đứng lặng bên hàng chanh\n"
        "Nghe gió lùa qua những nhánh tre"
    )
    t2 = next(k for k in v.tang if k.so == 2)
    assert t2.chi_tiet["so_tieng_tung_dong"][0] == 7
    assert t2.chi_tiet["so_dau_cau_da_loai"] == 0, "gạch nối KHÔNG tính là dấu bị loại"


# ═══════ §6c — bảng 16 tổ hợp khuôn của cụm 4 dòng (bổ sung 18/09/2026) ═══════


def test_bang_16_dung_NGUYEN_VAN_bang_cua_chu_du_an():
    """Chép đúng 16 dòng bảng, đúng thứ tự. Lệch một dòng là test đỏ.

    Bảng viết lại ở đây theo ký hiệu B-T-B / T-B-T của chủ dự án, KHÔNG import
    từ rule.py — nếu cả hai cùng lấy từ một nguồn thì test không kiểm được gì.
    """
    from application.rule import PHOI_KHUON_16

    nguyen_van = [
        ("B-T-B", "B-T-B", "B-T-B", "B-T-B"),  # 1
        ("B-T-B", "B-T-B", "B-T-B", "T-B-T"),  # 2
        ("B-T-B", "B-T-B", "T-B-T", "B-T-B"),  # 3
        ("B-T-B", "B-T-B", "T-B-T", "T-B-T"),  # 4
        ("B-T-B", "T-B-T", "B-T-B", "B-T-B"),  # 5
        ("B-T-B", "T-B-T", "B-T-B", "T-B-T"),  # 6
        ("B-T-B", "T-B-T", "T-B-T", "B-T-B"),  # 7
        ("B-T-B", "T-B-T", "T-B-T", "T-B-T"),  # 8
        ("T-B-T", "B-T-B", "B-T-B", "B-T-B"),  # 9
        ("T-B-T", "B-T-B", "B-T-B", "T-B-T"),  # 10
        ("T-B-T", "B-T-B", "T-B-T", "B-T-B"),  # 11
        ("T-B-T", "B-T-B", "T-B-T", "T-B-T"),  # 12
        ("T-B-T", "T-B-T", "B-T-B", "B-T-B"),  # 13
        ("T-B-T", "T-B-T", "B-T-B", "T-B-T"),  # 14
        ("T-B-T", "T-B-T", "T-B-T", "B-T-B"),  # 15
        ("T-B-T", "T-B-T", "T-B-T", "T-B-T"),  # 16
    ]
    ky_hieu = {"B-T-B": "bang", "T-B-T": "trac"}
    mong_doi = tuple(tuple(ky_hieu[o] for o in hang) for hang in nguyen_van)

    assert mong_doi == PHOI_KHUON_16


def test_moi_o_trong_bang_16_la_P2_P4_P6_cua_MOT_dong():
    """Ghim nghĩa của từng ô: ba giá trị thanh ở P2, P4, P6 — không phải gì khác.

    Chủ dự án nhấn mạnh 18/09/2026: *"mỗi câu là giá trị của P2, P4, P6"*.

    Đây là chỗ dễ hiểu lệch nhất của cả bảng. Nếu ai đó đọc "B-T-B" thành ba
    tiếng đầu dòng, hoặc thành P1-P2-P3, bảng vẫn có 16 dòng và mọi test đếm vẫn
    xanh — nhưng mọi con số thống kê sẽ sai mà trông như đúng. Test này neo ánh
    xạ vào một dòng thơ THẬT, kiểm từng vị trí một.
    """
    from application.rule import (
        PHOI_KHUON_16,
        khuon_cua_dong,
        ma_phoi_khuon_cua_cum,
        tach_tieng,
        thanh_cua,
    )

    # Bốn dòng ví dụ §11 của tài liệu.
    bai = [
        "Chiều rơi chậm xuống mái rêu xanh",
        "Con ngõ nhỏ dài hơn tiếng ve",
        "Ai đứng bên kia bờ nắng mảnh",
        "Gọi một mùa xa chẳng dám về",
    ]
    mong_doi_p246 = [("B", "T", "B"), ("T", "B", "T"), ("T", "B", "T"), ("T", "B", "T")]

    khuon = []
    for dong, mong_doi in zip(bai, mong_doi_p246, strict=True):
        tieng = tach_tieng(dong)
        assert len(tieng) == 7
        thanh = [thanh_cua(t) for t in tieng]
        # Chỉ số 1, 3, 5 (0-based) ĐÚNG LÀ P2, P4, P6 (1-based).
        p2, p4, p6 = thanh[1], thanh[3], thanh[5]
        assert (p2, p4, p6) == mong_doi, f"{dong}: P2/P4/P6 = {p2}/{p4}/{p6}"
        khuon.append(khuon_cua_dong(tieng))

    # "bang" <-> P2-P4-P6 = B-T-B ; "trac" <-> T-B-T. Không hoán vị nào khác.
    assert khuon == ["bang", "trac", "trac", "trac"]
    assert khuon_cua_dong(tach_tieng(bai[0])) == "bang"
    assert mong_doi_p246[0] == ("B", "T", "B"), "khuôn bằng = P2 B, P4 T, P6 B"
    assert mong_doi_p246[1] == ("T", "B", "T"), "khuôn trắc = P2 T, P4 B, P6 T"

    # Ghép bốn ô lại ra đúng một hàng của bảng 16.
    assert ma_phoi_khuon_cua_cum(tuple(khuon)) == 8
    assert PHOI_KHUON_16[8 - 1] == ("bang", "trac", "trac", "trac")


def test_P1_P3_P5_va_P7_KHONG_tham_gia_bang_16():
    """Bảng xét ĐÚNG BA vị trí. Đổi thanh ở P1/P3/P5 không được đổi mã tổ hợp.

    S1 nói P1, P3, P5 có thể tự do; P7 thuộc về vần. Nếu một trong bốn vị trí ấy
    lọt vào phép tính khuôn thì test này đỏ.
    """
    from application.rule import khuon_cua_dong, tach_tieng, thanh_cua

    # Hai dòng khác nhau ở P1, P3, P5, P7 nhưng GIỐNG nhau ở P2, P4, P6.
    a = tach_tieng("Chiều rơi chậm xuống mái rêu xanh")
    b = tach_tieng("Nắng rơi khẽ xuống ngõ rêu mờ")
    ta = [thanh_cua(x) for x in a]
    tb = [thanh_cua(x) for x in b]
    assert (ta[1], ta[3], ta[5]) == (tb[1], tb[3], tb[5]), "P2/P4/P6 phải giống nhau"
    assert khuon_cua_dong(a) == khuon_cua_dong(b), (
        "khuôn chỉ phụ thuộc P2/P4/P6; khác ở P1/P3/P5/P7 không được đổi khuôn"
    )


def test_bang_16_la_TAP_DAY_DU_chu_khong_phai_tap_con():
    """2^4 = 16. Bảng không loại thêm bài nào so với tiêu chí "mọi dòng khớp khuôn".

    Test này ghim chính nhận định đó: nếu ai đó rút bảng xuống còn một tập con
    (ví dụ chỉ giữ hai mẫu §4.3), bảng sẽ thành tiêu chí CHẶN thứ hai mà không ai
    tuyên bố — và test này đỏ trước khi số liệu kịp đổi.
    """
    from itertools import product

    from application.rule import PHOI_KHUON_16

    assert len(PHOI_KHUON_16) == 16
    assert len(set(PHOI_KHUON_16)) == 16, "không được trùng dòng"
    assert set(PHOI_KHUON_16) == set(product(("bang", "trac"), repeat=4))


def test_ma_bang_16_dung_thu_tu_nhi_phan():
    """B-T-B = 0, T-B-T = 1, C1 là bit cao nhất, mã = giá trị + 1."""
    from application.rule import MA_PHOI_KHUON_16, PHOI_KHUON_16

    for i, bo in enumerate(PHOI_KHUON_16, start=1):
        gia_tri = sum(
            (1 if k == "trac" else 0) << (3 - vi_tri) for vi_tri, k in enumerate(bo)
        )
        assert gia_tri + 1 == i, f"tổ hợp #{i} sai thứ tự nhị phân"
        assert MA_PHOI_KHUON_16[bo] == i


def test_hai_mau_cua_muc_4_3_nam_trong_bang_16_va_KHONG_dac_quyen():
    """§4.3 nêu hai mẫu; bảng 16 chốt rằng 14 mẫu còn lại cũng hợp lệ.

    Chủ dự án bổ sung bảng này chính là để trả lời câu hỏi đó dứt khoát.
    """
    from application.rule import (
        MA_PHOI_KHUON_CO_DIEN,
        MA_PHOI_KHUON_DAO,
        PHOI_KHUON_16,
        PHOI_KHUON_CO_DIEN,
        PHOI_KHUON_DAO,
    )

    assert PHOI_KHUON_CO_DIEN in PHOI_KHUON_16
    assert PHOI_KHUON_DAO in PHOI_KHUON_16
    assert MA_PHOI_KHUON_CO_DIEN == 7
    assert MA_PHOI_KHUON_DAO == 10


def test_vi_du_TAI_LIEU_ra_to_hop_8_chu_khong_phai_hai_mau_4_3():
    """Bằng chứng mạnh nhất rằng hai mẫu §4.3 không phải ràng buộc:

    ví dụ minh hoạ của CHÍNH tài liệu (§11) cho tổ hợp #8, và nó vẫn ĐẠT.
    """
    from application.rule import kiem_tra_bai_tho
    from tests.unit.application.test_rule import VI_DU_TAI_LIEU

    v = kiem_tra_bai_tho(VI_DU_TAI_LIEU)
    assert v.ma_phoi_khuon_theo_cum == (8,)
    t4 = next(k for k in v.tang if k.so == 4)
    assert t4.dat is True


def test_cum_chia_theo_BON_DONG_LIEN_TIEP_khong_theo_kho():
    """`ma_phoi_khuon_theo_cum` chia theo cụm 4 dòng; `phoi_khuon_theo_kho` chia
    theo khổ. Bài 8 dòng một khổ có 2 cụm nhưng chỉ 1 khổ."""
    from application.rule import chia_cum_bon_dong, kiem_tra_bai_tho

    assert chia_cum_bon_dong(("bang",) * 8) == (("bang",) * 4, ("bang",) * 4)
    # Cụm thiếu 4 dòng ở cuối bị BỎ, không đệm cho đủ.
    assert chia_cum_bon_dong(("bang",) * 6) == (("bang",) * 4,)
    assert chia_cum_bon_dong(("bang",) * 3) == ()

    bai = "\n".join([
        "Chiều rơi chậm xuống mái rêu xanh",
        "Con ngõ nhỏ dài hơn tiếng ve",
        "Ai đứng bên kia bờ nắng mảnh",
        "Gọi một mùa xa chẳng dám về",
    ] * 2)
    v = kiem_tra_bai_tho(bai)
    assert v.so_kho == 1, "không có dòng trống nên cả bài là một khổ"
    assert len(v.ma_phoi_khuon_theo_cum) == 2, "nhưng có hai cụm 4 dòng"


def test_cum_co_dong_pha_khuon_thi_KHONG_co_ma():
    """None = cụm không nằm trong bảng, và đó đúng là lúc tầng 4 đã có việc."""
    from application.rule import kiem_tra_bai_tho, ma_phoi_khuon_cua_cum

    assert ma_phoi_khuon_cua_cum(("bang", "trac", "pha", "bang")) is None
    assert ma_phoi_khuon_cua_cum(("bang", "trac", "bang")) is None, "cụm thiếu dòng"

    v = kiem_tra_bai_tho("\n".join(["Ta đi ta đi ta đi ta"] * 4))
    assert v.dat is False
    assert v.ma_phoi_khuon_theo_cum == (None,)


def test_bang_16_KHONG_duoc_tro_thanh_tieu_chi_chan_thu_hai():
    """Bảng là MÔ TẢ. Tiêu chí chặn của tầng 4 vẫn chỉ là S2 (QĐ-1 + QĐ-2).

    Nếu ai đó thêm mã bảng vào `tieu_chi_tu`, bộ kiểm sẽ có hai tiêu chí nói cùng
    một điều — và báo cáo sẽ đếm trùng.
    """
    from application.rule import TANG

    t4 = next(t for t in TANG if t.so == 4)
    assert t4.tieu_chi_tu == ("S2",)
    assert "§6c" not in t4.trich_luat and "16" not in t4.trich_luat


# ═══════ QĐ-7b (18/09/2026) — cụm 4 dòng chỉ cần CÓ vần chân ═══════


def test_QD7b_moi_so_do_co_it_nhat_mot_cap_hiep_deu_DAT():
    """Nguyên văn: *"Nếu không có vần chân nào thì trượt"*.

    Bản trước đòi cụm khớp ĐÚNG một trong bốn sơ đồ §5.2, nên loại cả `aaaa`
    (độc vận), `axax`, `xaxa`… Nay chỉ cần một cặp tiếng cuối hiệp vần.
    """
    from application.rule import cua_so_co_van_chan

    # Mỗi bộ bốn tiếng cuối dưới đây có ÍT NHẤT một cặp hiệp vần.
    dat = [
        ("xanh", "ve", "mảnh", "về"),      # abab — vần cách
        ("xanh", "mảnh", "ve", "về"),      # aabb — vần liền
        ("xanh", "ve", "về", "mảnh"),      # abba — vần ôm
        ("xanh", "mảnh", "mưa", "tranh"),  # aaxa
        ("xanh", "mảnh", "tranh", "cành"), # aaaa — độc vận, TRƯỚC ĐÂY TRƯỢT
        ("xanh", "mưa", "mảnh", "thu"),    # axax — TRƯỚC ĐÂY TRƯỢT
        ("mưa", "xanh", "thu", "mảnh"),    # xaxa — TRƯỚC ĐÂY TRƯỢT
        ("mưa", "xanh", "mảnh", "thu"),    # xaax — TRƯỚC ĐÂY TRƯỢT
    ]
    for cuoi in dat:
        assert cua_so_co_van_chan(cuoi), f"{cuoi}: có cặp hiệp vần mà bị loại"


def test_QD7b_chi_xxxx_bi_loai():
    """Cụm duy nhất còn bị tầng 5 loại: không cặp nào hiệp."""
    from application.rule import cua_so_co_van_chan, suy_so_do_van

    cuoi = ("trước", "khuya", "lại", "thề")
    assert "".join(suy_so_do_van(cuoi)) == "xxxx"
    assert cua_so_co_van_chan(cuoi) == ()


def test_QD7b_nhan_hoi_cham_VAN_tinh_la_co_van_chan():
    """'?' nghĩa là có hiệp vần nhưng cụm không quy về một sơ đồ chữ cái.

    Quan hệ vần không bắc cầu (vang~vương, vương~vuông, vang ≁ vuông) nên khổ ấy
    không có sơ đồ xác định — nhưng nó VẪN CÓ vần chân, nên không được trượt.
    """
    from application.rule import cua_so_co_van_chan, suy_so_do_van

    cuoi = ("vang", "vương", "vuông", "mưa")
    so_do = "".join(suy_so_do_van(cuoi))
    assert "?" in so_do, f"cụm này phải cho nhãn '?', đang là {so_do}"
    assert cua_so_co_van_chan(cuoi), "'?' vẫn là có vần chân, không được loại"


def test_QD7b_bang_ten_so_do_52_van_duoc_giu_de_BAO_CAO():
    """Bốn sơ đồ §5.2 thôi làm tiêu chí, nhưng vẫn dùng để GỌI TÊN trong biên bản."""
    from application.rule import SO_DO_KHO_TAI_LIEU, TANG, kiem_tra_bai_tho

    t5 = next(t for t in TANG if t.so == 5)
    assert t5.tieu_chi_tu == ("S11",), "tiêu chí vẫn là S11, không phải danh sách sơ đồ"
    assert set(SO_DO_KHO_TAI_LIEU) == {"aabb", "abab", "abba", "aaxa"}

    bai = (
        "Chiều rơi chậm xuống mái rêu xanh"
        "\n" "Con ngõ nhỏ dài hơn tiếng ve"
        "\n" "Ai đứng bên kia bờ nắng mảnh"
        "\n" "Gọi một mùa xa chẳng dám về"
    )
    v = kiem_tra_bai_tho(bai)
    t5kq = next(k for k in v.tang if k.so == 5)
    assert "vần cách" in t5kq.bang_chung, "cụm khớp §5.2 phải được gọi đúng tên"
    assert t5kq.chi_tiet["cum_co_van_chan"][0]["ten"] == "vần cách"


def test_QD7b_cum_khong_co_ten_rieng_thi_ten_la_None_KHONG_phai_hong():
    """`ten = None` nghĩa là cụm không trùng sơ đồ §5.2 nào — không phải cụm hỏng."""
    from application.rule import kiem_tra_bai_tho

    # aaaa: độc vận, có vần chân, nhưng không phải sơ đồ §5.2 nào.
    bai = (
        "Trời cao mây biếc xanh ngời cành"
        "\n" "Người xưa đứng lặng bên hàng chanh"
        "\n" "Chiều xuống trong veo bên mái tranh"
        "\n" "Đường về lặng lẽ qua rừng xanh"
    )
    v = kiem_tra_bai_tho(bai)
    t5 = next(k for k in v.tang if k.so == 5)
    assert t5.dat is True, "độc vận aaaa nay ĐẠT (QĐ-7b)"
    cum = t5.chi_tiet["cum_co_van_chan"][0]
    assert cum["so_do"] == "aaaa"
    assert cum["ten"] is None
