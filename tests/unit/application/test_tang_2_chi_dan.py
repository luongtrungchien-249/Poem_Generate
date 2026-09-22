"""Tầng 2 — chỉ dẫn CÁCH LÀM VIỆC, tách khỏi tầng LUẬT.

    LUẬT THƠ nói bài thơ phải NHƯ THẾ NÀO  → nguồn duy nhất `rule.LUAT`
    TẦNG 2 nói mô hình phải LÀM VIỆC RA SAO → file `prompting/instructions.py`

Hai thứ độc lập. Trộn chúng lại là tạo nguồn thứ hai cho luật, và đến ngày bảng
luật đổi thì mô hình được dạy hai luật khác nhau tuỳ đường nó đi qua.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from application.poetry.prompt import CHI_DAN_SINH_THO
from application.prompting.instructions import (
    CACH_LAM_VIEC,
    CHI_DAN_CHAT_LUONG,
    CHI_DAN_SUA,
    CHI_DAN_TRO_GIUP_THO,
    CHI_DAN_VIET_TIEP_KHO,
    THANG_LEO_THANG,
)
from application.rule import LUAT

TAT_CA = (
    CACH_LAM_VIEC,
    CHI_DAN_CHAT_LUONG,
    CHI_DAN_TRO_GIUP_THO,
    CHI_DAN_VIET_TIEP_KHO,
    *CHI_DAN_SUA.values(),
)


# ── Ranh giới với tầng luật ─────────────────────────────────────────────────


@pytest.mark.parametrize("chi_dan", TAT_CA)
def test_tang_2_khong_chep_luat_tho(chi_dan):
    """⛔ Không một con số hay khuôn nào của luật được lặp lại ở tầng này.

    `rule.LUAT` là nguồn duy nhất, và `poetry/prompt.py` sinh chỉ dẫn từ bảng đó.
    Chép lại ở đây thì sửa luật một chỗ không kéo theo chỗ kia.
    """
    for dau_hieu in ("B T B", "T B T", "7 tiếng", "bảy tiếng", "bội của 4"):
        assert dau_hieu not in chi_dan, dau_hieu


@pytest.mark.parametrize("chi_dan", TAT_CA)
def test_tang_2_khong_nhac_ma_luat(chi_dan):
    """Nhắc mã luật (H1, S2…) là đang mô tả luật, không phải mô tả cách làm việc."""
    for d in LUAT:
        assert f" {d.ma} " not in f" {chi_dan} ", d.ma


def test_luat_cung_VAN_o_trong_chi_dan_sinh():
    """Kiểm soát dương: tách ra không có nghĩa là đánh rơi.

    Nếu test này đỏ thì việc tách đã làm mất phần luật khỏi prompt — tệ hơn hẳn
    việc trộn lẫn ban đầu.
    """
    ma_cung = [d.ma for d in LUAT if d.loai == "cung"]
    assert ma_cung
    for ma in ma_cung:
        assert ma in CHI_DAN_SINH_THO, ma


# ── Chỉ dẫn sinh phải THẬT SỰ nằm trong prompt gửi đi ───────────────────────


def test_cach_lam_viec_duoc_nhung_vao_chi_dan_sinh():
    """Hằng số không ai gọi thì chỉ làm bản kiểm kê trông đầy đủ."""
    assert CACH_LAM_VIEC.strip() in CHI_DAN_SINH_THO


def test_cach_lam_viec_cam_viet_loi_dan():
    """⛔ KHÔNG phải yêu cầu hình thức cho đẹp.

    Bộ đọc ứng viên chỉ lấy bốn dòng đầu không rỗng. Một dòng lời dẫn lọt vào đó
    là hỏng cả ứng viên, dù bài thơ bên dưới có thể đúng luật.
    """
    assert "Chỉ trả về bài thơ" in CACH_LAM_VIEC
    assert "Không lời dẫn" in CACH_LAM_VIEC


def test_cach_lam_viec_cam_tu_tuyen_bo_dung_luat():
    """Bộ kiểm là thẩm quyền duy nhất — nhắc lại ở tầng 2 là cố ý, vì đây là lúc
    mô hình bị cám dỗ nhất: ngay sau khi vừa viết xong một bài nó thấy hay."""
    assert "đúng luật" in CACH_LAM_VIEC
    assert "KHÔNG tuyên bố" in CACH_LAM_VIEC


# ── Chất lượng: chiều không đo được thì phải hướng dẫn ──────────────────────


def test_chi_dan_chat_luong_that_su_di_ra_mo_hinh():
    """Hằng số không ai nhúng vào prompt thì chỉ làm bản kiểm kê trông đầy đủ."""
    assert CHI_DAN_CHAT_LUONG.strip() in CHI_DAN_SINH_THO


def test_chat_luong_day_BANG_CAP_DOI_LAP():
    """⛔ Cách dạy, không phải nội dung, mới là thứ đáng nhập từ bản prompt cũ.

    Một ví dụ tốt chỉ cho biết MỘT điểm. Một cặp tốt/dở vẽ ra ĐƯỜNG PHÂN CHIA —
    và đó là thứ mô hình cần để tự phán đoán những ca chưa từng thấy.
    """
    assert "hẹp:" in CHI_DAN_CHAT_LUONG and "rộng:" in CHI_DAN_CHAT_LUONG
    assert "thấy được:" in CHI_DAN_CHAT_LUONG and "không thấy:" in CHI_DAN_CHAT_LUONG


def test_chat_luong_KHONG_phai_thang_diem():
    """⛔ Ranh giới với `quality.py`.

    Viết chỉ dẫn chất lượng thành tiêu chí chấm là dựng thẩm quyền thứ hai bên
    cạnh bộ đo — đúng lỗi của bản prompt cũ, nơi LLM chấm rồi sửa theo điểm chính
    nó vừa chấm. Tầng này chỉ được nói mô hình phải LÀM GÌ.
    """
    for dau_hieu in ("điểm", "thang", "trọng số", "w=", "/10"):
        assert dau_hieu not in CHI_DAN_CHAT_LUONG.lower(), dau_hieu


def test_chu_mon_chi_la_VI_DU_khong_co_ma_nao_chan():
    """Danh sách chữ mòn KHÔNG được biến thành danh sách cấm.

    Chặn một chữ vì nó hay bị dùng dở là phạt luôn lần nó được dùng đúng — cùng
    loại sai với `lap_tieng` và `lap_dong` đã bị gỡ khỏi `quality.py` (N2).
    """
    import application.poetry.quality as mod_quality

    for chu in ("lung linh", "bâng khuâng", "dạt dào", "chơi vơi", "miên man"):
        assert chu in CHI_DAN_CHAT_LUONG
        assert chu not in Path(mod_quality.__file__).read_text(encoding="utf-8")


# ── Ghim khuôn trong prompt — bản trước là lời hứa suông ─────────────────────


def test_khuon_trong_chi_dan_DOC_THAT_chuoi_prompt():
    """⛔ Bản trước: `KHUON_TRONG_CHI_DAN = KHUON_HOP_LE`, một bí danh.

    So bí danh với bản gốc là so một giá trị với chính nó — luôn xanh, không bao
    giờ bắt được sự lệch giữa bảng khuôn và chữ trong prompt. Nay nó rút từ chuỗi
    thật, nên phép so dưới đây mới có nghĩa.
    """
    from application.poetry.plan import KHUON_HOP_LE
    from application.poetry.prompt import _CHU_CUA_KHUON, KHUON_TRONG_CHI_DAN

    assert KHUON_TRONG_CHI_DAN == KHUON_HOP_LE

    # Mọi mã khuôn phải có nhịp cầu sang chữ tiếng Việt, và chữ đó phải có thật
    # trong prompt. Khai một nửa — có mã, quên chữ — cũng đỏ ở đây.
    for ma in KHUON_HOP_LE:
        assert ma in _CHU_CUA_KHUON, ma
        assert f"khuôn {_CHU_CUA_KHUON[ma]}" in CHI_DAN_SINH_THO, ma


def test_them_khuon_moi_ma_quen_sua_prompt_thi_BAT_DUOC():
    """Kiểm soát dương: chứng minh phép ghim thật sự bắt được lệch.

    Nếu test này xanh mà `KHUON_TRONG_CHI_DAN` vẫn là bí danh thì nó đã không
    kiểm gì cả — đây là chỗ phân biệt hai bản.
    """
    from application.poetry.prompt import _khuon_duoc_nhac_trong_chi_dan

    assert "khuôn xiên" not in CHI_DAN_SINH_THO
    # Khuôn thứ ba chưa có trong prompt -> phép rút KHÔNG nhặt nó lên.
    assert "xiên" not in _khuon_duoc_nhac_trong_chi_dan()


# ── Thang leo thang khi sửa ─────────────────────────────────────────────────


def test_moi_chien_luoc_deu_co_chi_dan():
    """Thiếu một mục thì vòng sửa ném KeyError giữa chừng, sau khi đã tốn tiền."""
    assert set(CHI_DAN_SUA) == set(THANG_LEO_THANG)


def test_thang_leo_thang_NOI_DAN_pham_vi():
    """Vì sao không cho viết lại cả bài ngay lượt đầu: sửa một dòng giữ được các
    dòng đã đạt, còn viết lại cả bài là gieo lại xúc xắc trên TOÀN BỘ dòng — kể
    cả dòng vốn đã đúng."""
    assert THANG_LEO_THANG == ("sua_dong", "sinh_lai_kho", "sinh_lai_ca_bai")
    assert "Chỉ viết lại đúng những dòng bị nêu" in CHI_DAN_SUA["sua_dong"]
    assert "cả khổ" in CHI_DAN_SUA["sinh_lai_kho"]
    assert "toàn bài" in CHI_DAN_SUA["sinh_lai_ca_bai"]


def test_lan_cuoi_coi_ban_nhap_la_PHAN_VI_DU():
    """Không nói rõ thì mô hình đọc bản nháp ở lượt `assistant` như một bài mẫu
    của chính nó, và lặp lại đúng cách triển khai đã hỏng."""
    assert "PHẢN VÍ DỤ" in CHI_DAN_SUA["sinh_lai_ca_bai"]


# ── Viết tiếp khổ ───────────────────────────────────────────────────────────


def test_cam_sua_cac_kho_da_chon():
    """⛔ Các khổ trước đã qua kiểm và được chọn từ 16 ứng viên.

    Để mô hình sửa chúng là vứt bỏ công chọn lọc đó, và bài ghép xong sẽ hỏng ở
    chỗ vốn đã đúng.
    """
    assert "KHÔNG chép lại" in CHI_DAN_VIET_TIEP_KHO
    assert "KHÔNG sửa các dòng đã có" in CHI_DAN_VIET_TIEP_KHO


def test_chi_dan_viet_tiep_duoc_dung_that():
    from application.poetry.sinh_theo_kho import _loi_nhac_khuon

    assert CHI_DAN_VIET_TIEP_KHO in _loi_nhac_khuon(["dòng một", "dòng hai"])
    # Chưa có khổ nào thì không nhắc gì — nhắc suông chỉ tốn token.
    assert _loi_nhac_khuon([]) == ""


# ── Hằng số, không nội suy ──────────────────────────────────────────────────


@pytest.mark.parametrize("chi_dan", TAT_CA)
def test_la_hang_so_khong_co_cho_noi_suy(chi_dan):
    """Nhét thứ đổi theo lượt vào tầng hằng số là phá prefix cache của mọi yêu cầu."""
    assert "{" not in chi_dan and "}" not in chi_dan


# ── Trợ giúp về thơ trong chat — loại việc KHÔNG có bộ kiểm đứng sau ────────


def test_bat_noi_ro_bai_viet_trong_chat_CHUA_qua_kiem():
    """⛔ Điều quan trọng nhất của chỉ dẫn này.

    Ba loại việc kia đều nằm trong vòng sinh–kiểm–sửa có bộ kiểm đứng cuối. Ở
    đường chat thì KHÔNG có bộ kiểm nào chạy — mô hình nói gì người dùng nhận nấy.

    Không nói rõ thì người dùng tưởng bài đã được hệ thống duyệt, vì họ đang dùng
    một sản phẩm mà điểm bán chính là "thơ đúng luật".
    """
    assert "CHƯA đi qua bộ kiểm luật" in CHI_DAN_TRO_GIUP_THO
    assert "chế độ làm thơ" in CHI_DAN_TRO_GIUP_THO


def test_bat_chi_ro_DONG_NAO_TIENG_THU_MAY():
    """"Bài này sai thanh luật" là câu vô dụng — người đọc không sửa được gì."""
    assert "DÒNG NÀO, TIẾNG THỨ MẤY" in CHI_DAN_TRO_GIUP_THO


def test_khong_tu_y_viet_lai_ca_bai_cua_nguoi_dung():
    assert "Đừng viết lại cả bài trừ khi người dùng nhờ" in CHI_DAN_TRO_GIUP_THO


def test_van_giu_ranh_gioi_phan_quyet():
    """Nhận xét thì tự do, phán quyết thì không — đúng như tầng 1."""
    assert "phỏng đoán" in CHI_DAN_TRO_GIUP_THO
    assert "bộ kiểm mới cho phán quyết" in CHI_DAN_TRO_GIUP_THO


def test_HAI_chi_dan_noi_NGUOC_nhau_ve_hinh_thuc_va_do_la_DUNG():
    """Hai đường đòi hai hình thức trả lời trái ngược, và cả hai đều đúng:

        đường thơ  cấm mọi lời dẫn — bộ đọc chỉ lấy bốn dòng đầu không rỗng,
                   một dòng lời dẫn lọt vào là hỏng cả ứng viên.
        đường chat lời dẫn là BẮT BUỘC — đó là chỗ nói cho người dùng biết bài
                   chưa qua kiểm.

    Vì vậy hai hằng số này KHÔNG được gộp, và không được dùng lẫn đường.
    """
    assert "Không lời dẫn" in CACH_LAM_VIEC
    assert "Không lời dẫn" not in CHI_DAN_TRO_GIUP_THO


def test_chi_dan_tro_giup_KHONG_di_vao_duong_tho():
    """Lọt sang đường thơ là hỏng mọi ứng viên: nó bảo mô hình viết lời dẫn."""
    from application.poetry.prompt import CHI_DAN_SINH_THO

    assert CHI_DAN_TRO_GIUP_THO not in CHI_DAN_SINH_THO
