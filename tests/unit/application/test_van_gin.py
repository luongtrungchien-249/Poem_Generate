"""🩸 T8 — `gìn` không hiệp vần với `nhìn`. Lỗi có sẵn, chủ dự án duyệt sửa 21/09/2026.

════ LỖI ════

Cắt âm đầu theo khớp DÀI NHẤT nên `gìn` bị đọc thành `gi` + `n`, trong khi đúng
phải là `g` + `ìn`:

    van_cua("gìn")  = "n"     sai
    van_cua("nhìn") = "in"
    hiep_van("gìn", "nhìn") -> False

Một bài gieo `gìn` với `nhìn` bị chấm là không hiệp vần — ảnh hưởng tầng 5 chạy
hằng ngày, không liên quan gì tới TTS.

Chú thích §5 của `rule.py` đã lường trước ca này — *"'gì' không phải là 'gi' +
rỗng, mà là 'g' + 'ì'"* — nhưng phép lùi chỉ chạy khi phần dư RỖNG, không chạy khi
phần dư KHÔNG CÓ NGUYÊN ÂM.

════ VÌ SAO `gian`, `giết`, `giữ` KHÔNG HỎNG ════

Phần dư của chúng (`an`, `êt`, `ư`) tình cờ hợp lệ, nên khớp dài nhất cho kết quả
đúng. Đó cũng là rủi ro lớn nhất của bản vá: nới tay một chút thì `gian` thành
`g` + `ian`, và MỌI phép so vần có `gi` đổi kết quả cùng lúc. Nhóm test thứ hai ở
đây tồn tại để chặn đúng điều đó.
"""

from __future__ import annotations

import pytest

from application.rule import hiep_van, phan_tich_am_tiet, van_cua

# ── Ca hỏng ─────────────────────────────────────────────────────────────────


def test_gin_hiep_van_voi_nhin():
    assert van_cua("gìn") == "in"
    assert hiep_van("gìn", "nhìn").hiep
    assert hiep_van("gìn", "tin").hiep


def test_gin_tach_am_tiet_dung():
    a = phan_tich_am_tiet("gìn")
    assert (a.am_dau, a.am_chinh, a.am_cuoi) == ("g", "i", "n")


# ── ⛔ Kiểm soát âm: bản vá KHÔNG được phá các ca vốn đã đúng ───────────────


@pytest.mark.parametrize(
    "tieng, van",
    [("gian", "an"), ("giết", "êt"), ("giữ", "ư"), ("giờ", "ơ"), ("giàu", "au")],
)
def test_gi_van_la_am_dau_khi_phan_du_CO_nguyen_am(tieng, van):
    assert van_cua(tieng) == van


def test_cac_cap_hiep_van_cu_KHONG_doi():
    assert hiep_van("gian", "tan").hiep
    assert hiep_van("giết", "hết").hiep
    assert hiep_van("giữ", "chữ").hiep


def test_gi_khong_cat_den_muc_rong():
    """Phép lùi cũ vẫn nguyên: `gì` là `g` + `ì`, không phải `gi` + rỗng."""
    assert van_cua("gì") == "i"


@pytest.mark.parametrize(
    "tieng, van",
    [
        ("nghiêng", "iêng"),
        ("quà", "a"),
        ("hoa", "oa"),
        ("chuyện", "uyên"),
        ("thuở", "uơ"),
    ],
)
def test_cac_am_dau_dai_khac_KHONG_bi_dung_toi(tieng, van):
    """`ngh`, `qu`, `ch`, `th` — khớp dài nhất vẫn phải thắng ở mọi ca này."""
    assert van_cua(tieng) == van
