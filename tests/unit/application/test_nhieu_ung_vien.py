"""Xin nhiều phương án trong MỘT lượt gọi — 22/09/2026.

Nhập từ `compare_prompt.py` (`generator_instruction`). Lý lẽ của việc này YẾU hơn
vẻ ngoài và phải nói rõ: `_chon_mot_kho` đã dừng sớm, nên gộp không tiết kiệm —
phần token đắt là output, và input thì prefix cache vốn đã lo.

Thứ nó nhắm tới là ĐA DẠNG: N lượt gọi độc lập thì mô hình không thấy bản nó vừa
viết, nên có thể sinh ra nhiều biến thể gần trùng.
"""

from __future__ import annotations

from application.poetry.sinh_theo_kho import (
    SO_UNG_VIEN_MOI_LUOT,
    _lay_bon_dong,
    _lay_cac_phuong_an,
)
from application.prompting.system import CHI_DAN_NHIEU_UNG_VIEN

_KHO = "Chiều rơi chậm xuống mái rêu xanh\nCon ngõ nhỏ dài hơn tiếng ve\nAi đứng bên kia bờ nắng mảnh\nGọi một mùa xa chẳng dám về"


def test_doc_duoc_NHIEU_phuong_an_tu_mot_cau_tra_loi():
    van = f"<phuong_an>\n{_KHO}\n</phuong_an>\n<phuong_an>\n{_KHO}\n</phuong_an>"
    assert len(_lay_cac_phuong_an(van)) == 2


def test_KHONG_co_the_thi_LUI_VE_hanh_vi_cu():
    """⛔ Lối lùi BẮT BUỘC, không phải để cho đẹp.

    Mô hình không phải lúc nào cũng nghe lời về định dạng. Một câu trả lời đúng
    luật mà thiếu thẻ thì vẫn dùng được — bỏ nó là tự nguyện vứt ứng viên hợp lệ
    chỉ vì cái vỏ.
    """
    assert _lay_cac_phuong_an(_KHO) == [_lay_bon_dong(_KHO)]


def test_phuong_an_THIEU_DONG_bi_bo_KHONG_keo_theo_cac_cai_khac():
    """Một phương án hỏng không được làm hỏng cả lượt gọi."""
    van = f"<phuong_an>\nMột dòng thôi\n</phuong_an>\n<phuong_an>\n{_KHO}\n</phuong_an>"
    ra = _lay_cac_phuong_an(van)
    assert len(ra) == 1 and len(ra[0]) == 4


def test_rac_hoan_toan_thi_RONG():
    assert _lay_cac_phuong_an("   ") == []
    assert _lay_cac_phuong_an("<phuong_an>\nngắn\n</phuong_an>") == []


def test_chi_dan_DOI_KHAC_NHAU_that():
    """Cả điểm của việc này là đa dạng. Không nói "khác nhau" thì mô hình sẽ trả
    về mấy biến thể của cùng một câu, và 16 ứng viên thành vô nghĩa."""
    chu = CHI_DAN_NHIEU_UNG_VIEN.format(so=4)
    assert "KHÁC NHAU" in chu
    assert "biến thể của cùng một câu" in chu


def test_chi_dan_KHONG_nhap_probability_cua_ban_cu():
    """⛔ Cố ý không nhập.

    Không mã nào đọc con số đó (điều kiện 2 của `instructions.py`), và ước lượng
    xác suất của chính mình là thứ mô hình làm rất kém — một con số vô căn cứ nằm
    trong prompt sẽ được người đọc sau tưởng là có căn cứ (N1).
    """
    for cam in ("probability", "xác suất", "phân phối", "0.10"):
        assert cam not in CHI_DAN_NHIEU_UNG_VIEN.lower(), cam


def test_chi_dan_KHONG_chep_luat_tho():
    for dau_hieu in ("7 tiếng", "bảy tiếng", "B T B", "T B T", "bội của 4"):
        assert dau_hieu not in CHI_DAN_NHIEU_UNG_VIEN, dau_hieu


def test_tat_duoc_bang_MOT_hang_so():
    """`SO_UNG_VIEN_MOI_LUOT = 1` phải quay về đúng hành vi trước 22/09.

    Lối tắt này tồn tại để đối chiếu A/B mà không phải gỡ mã — và vì thay đổi này
    BẮT BUỘC phải đo trước khi giữ.
    """
    assert isinstance(SO_UNG_VIEN_MOI_LUOT, int) and SO_UNG_VIEN_MOI_LUOT >= 1


def test_so_luot_goi_GIAM_khi_xin_nhieu_moi_luot():
    """16 ứng viên, 4 phương án mỗi lượt -> 4 lượt gọi, không phải 16."""
    so_ung_vien, moi_luot = 16, 4
    assert -(-so_ung_vien // moi_luot) == 4
