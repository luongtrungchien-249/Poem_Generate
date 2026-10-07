"""Tầng 2 — chỉ dẫn CÁCH LÀM VIỆC, tách khỏi tầng LUẬT.

    LUẬT THƠ nói bài thơ phải NHƯ THẾ NÀO  → nguồn duy nhất `rule.LUAT`
    TẦNG 2 nói mô hình phải LÀM VIỆC RA SAO → file `prompting/system.py`

Hai thứ độc lập. Trộn chúng lại là tạo nguồn thứ hai cho luật, và đến ngày bảng
luật đổi thì mô hình được dạy hai luật khác nhau tuỳ đường nó đi qua.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from application.poetry.prompt import CHI_DAN_SINH_THO
from application.prompting.system import (
    CACH_LAM_VIEC,
    CHI_DAN_CHAT_LUONG,
    CHI_DAN_SUA,
    CHI_DAN_TRO_GIUP_THO,
    CHI_DAN_VIET_TIEP_KHO,
    THANG_LEO_THANG,
)
from application.rule import LUAT, MA_LUAT

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


# (đã gỡ test_chat_KHONG_duoc_tu_viet_tho_bang_tay — xem khối cuối file)

# (đã gỡ test_chat_phai_GOI_TOOL_chu_khong_dem_tay — xem khối cuối file)

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


# ── Giai đoạn 1: neo vần (A1) và giọng hai nhánh (A2), 22/09/2026 ───────────


def test_chi_dan_sinh_DAY_CACH_CHON_VAN_khong_chi_tuyen_bo():
    """⛔ Khối thanh luật dạy quy trình bốn bước, khối vần thì chỉ tuyên bố.

    Cùng một loại ràng buộc "chọn trước, lấp nghĩa sau" mà chỉ một bên được dạy
    cách làm. Test này ghim rằng vần cũng có quy trình, không chỉ có yêu cầu.
    """
    assert "CÁCH VIẾT ĐỂ KHÔNG HỤT VẦN" in CHI_DAN_SINH_THO
    assert "Chọn TRƯỚC tiếng cuối" in CHI_DAN_SINH_THO


def test_noi_ro_chon_van_truoc_KHONG_lam_lech_khuon():
    """Câu đáng giá nhất của khối, và là một sự thật kiểm lại được.

    `rule.khuon_cua_dong` chỉ đọc tiếng 2, 4, 6; tiếng gánh vần là tiếng cuối.
    Không nói ra thì mô hình phải tự đoán hai ràng buộc có tranh chỗ nhau không,
    và khi không chắc nó ưu tiên khuôn rồi bỏ vần.
    """
    assert "KHÔNG bao giờ làm lệch khuôn thanh" in CHI_DAN_SINH_THO


def test_neo_van_dung_dung_TANG_luat_khong_phai_tang_2():
    """Khối neo vần nói về luật nên phải ở `prompt.py` (sinh từ bảng luật),
    KHÔNG được rơi vào `instructions.py` — nơi cấm chép luật."""
    assert "CÁCH VIẾT ĐỂ KHÔNG HỤT VẦN" not in CHI_DAN_CHAT_LUONG
    assert "CÁCH VIẾT ĐỂ KHÔNG HỤT VẦN" not in CACH_LAM_VIEC


def test_chat_luong_CO_NHANH_cho_giong_doi_thuong():
    """⛔ Bảy mục đầu mã hoá cứng một mỹ học văn chương.

    Người dùng xin bài hài hước thì mục 3 ("đừng gọi tên cảm xúc") đang dạy ngược
    lại chính điều họ muốn. Phải có nhánh rẽ, và nhánh ấy phải nói rõ nới mục nào.
    """
    assert "giọng đời thường:" in CHI_DAN_CHAT_LUONG
    assert "giọng văn chương:" in CHI_DAN_CHAT_LUONG
    assert "mục 3 và mục 5 nới ra" in CHI_DAN_CHAT_LUONG


def test_nhanh_giong_VAN_day_bang_cap_doi_lap():
    """Cùng cách dạy với phần còn lại của khối: một cặp vẽ ra đường phân chia."""
    than = CHI_DAN_CHAT_LUONG.split("8.", 1)[1]
    assert "giọng văn chương:" in than and "giọng đời thường:" in than


def test_nhanh_giong_KHONG_noi_rong_ra_moi_muc():
    """Nới hai mục là có căn cứ; nới tất cả là bỏ luôn khối chất lượng.

    "Cụ thể hơn khái quát" đúng ở mọi giọng — chỉ "đừng gọi tên cảm xúc" mới là
    quy ước riêng của giọng văn chương.
    """
    assert "Các mục còn lại giữ nguyên" in CHI_DAN_CHAT_LUONG


# ══════════════════════════════════════════════════════════════════════════════
# 🩸 SỰ CỐ 22/09/2026 — GHÉP TAY PROMPT TỪ HAI FILE KHÔNG CÓ LUẬT
#
# Chủ dự án ghép `system.py` + `instructions.py` thành System Instruction, đưa cho
# Gemma sinh 200 bài. Đối chiếu qua `rule.py`: 1/200 đạt (0,50%).
#
# Nguyên nhân KHÔNG phải mô hình kém — hai file ấy cố ý KHÔNG chứa luật thơ, nên
# Gemma chưa bao giờ được cho biết bài thơ phải như thế nào. Nó vẫn viết đúng 7
# tiếng ở 98,9% số dòng, thuần bằng tiên nghiệm.
#
# Các test dưới ghim chính sự thật đó, để nó thành tài liệu sống thay vì một bài
# học bị quên. Chúng KHÔNG đòi sửa gì — chúng nói rõ phải lấy prompt ở đâu.
# ══════════════════════════════════════════════════════════════════════════════

_DAU_HIEU_LUAT = ("7 tiếng", "khuôn bằng", "khuôn trắc", "hiệp vần", "bội của 4")


# (đã gỡ test_hai_file_TANG_1_VA_2_GOP_LAI_VAN_KHONG_DU_lam_tho — xem khối cuối file)

def test_CHI_DAN_SINH_THO_moi_la_cho_co_du_luat():
    """Kiểm soát dương cho test trên: chỗ ĐÚNG thì phải có đủ."""
    for dau_hieu in _DAU_HIEU_LUAT:
        assert dau_hieu in CHI_DAN_SINH_THO, dau_hieu


def test_co_duong_LAY_PROMPT_THAT_khong_phai_ghep_tay():
    """Sự cố bắt nguồn từ việc dựng prompt bằng tay. Phải có đường khác.

    `datalake/scripts/xuat_prompt_sinh_tho.py` in ra đúng chuỗi hệ thống gửi đi,
    và nó gọi `dung_luot_yeu_cau` chứ KHÔNG dựng lại chuỗi — dựng lại là tạo
    nguồn thứ hai, đúng thứ vừa gây ra sự cố.
    """
    script = (
        Path(__file__).resolve().parents[3]
        / "datalake/scripts/xuat_prompt_sinh_tho.py"
    )
    assert script.exists(), "script xuất prompt đã biến mất"
    cay = ast.parse(script.read_text(encoding="utf-8"))
    assert "dung_luot_yeu_cau" in ast.dump(cay), "script không gọi hàm dựng prompt thật"

    # Bỏ docstring module ra trước khi soi: nó KỂ LẠI sự cố nên có nhắc "7 tiếng",
    # và đó là tài liệu, không phải luật chép tay. Thứ phải cấm là luật nằm trong
    # MÃ — một hằng số chuỗi dựng lại chỉ dẫn.
    than = ast.Module(body=cay.body[1:], type_ignores=[])
    ma = ast.unparse(than)
    for dau_hieu in _DAU_HIEU_LUAT:
        assert dau_hieu not in ma, f"script chép tay {dau_hieu!r} thay vì gọi hàm"


# ══════════════════════════════════════════════════════════════════════════════
# ĐƯỜNG THƠ KHÔNG GỬI SYSTEM MESSAGE — 23/09/2026
#
# Sự thật này là NỀN của cả kiến trúc hai tầng, nhưng trước hôm nay nó chỉ đúng
# DO CÁCH MÃ ĐƯỢC VIẾT, không ai cưỡng chế. Ai nối thêm một system message vào
# đường thơ sẽ không gặp cản trở nào — và mọi lập luận "vì sao không gộp tầng 1
# với tầng 2" im lặng mất hiệu lực.
#
# Hệ quả nếu quên: chuyển một khối của đường thơ sang `system.py` sẽ làm nó BIẾN
# MẤT khỏi đường thơ. Không lỗi, không cảnh báo — mô hình chỉ thôi không được dạy
# điều đó nữa. Đúng kiểu hỏng đã xảy ra với Gemma ngày 22/09.
# ══════════════════════════════════════════════════════════════════════════════


def _req_mau():
    from application.poetry.requirement import PoetryRequirement, Truong

    return PoetryRequirement(
        chu_de=Truong(gia_tri="mùa thu", nguon="nguoi_dung"),
        so_dong=Truong(gia_tri=4, nguon="nguoi_dung"),
    )


def test_chuoi_gui_DUONG_THO_khong_chua_SYSTEM_PROMPT():
    """🔴 Ghim sự thật nền: tầng 1 không tới được đường thơ."""
    from application.poetry.prompt import dung_luot_yeu_cau
    from application.prompting.system import SYSTEM_PROMPT_V1

    chuoi = dung_luot_yeu_cau(_req_mau())
    assert SYSTEM_PROMPT_V1.strip()[:60] not in chuoi


def test_hai_khoi_cua_duong_tho_PHAI_o_trong_CHI_DAN_SINH_THO():
    """Kiểm soát dương cho test trên.

    Nếu ai gỡ `CACH_LAM_VIEC` hay `CHI_DAN_CHAT_LUONG` sang tầng 1, test này đỏ
    ngay — thay vì đường thơ lặng lẽ mất chỉ dẫn và chỉ lộ ra ở tỉ lệ đạt.
    """
    assert CACH_LAM_VIEC.strip() in CHI_DAN_SINH_THO
    assert CHI_DAN_CHAT_LUONG.strip() in CHI_DAN_SINH_THO


def test_duong_sinh_tho_KHONG_dung_SystemMessage():
    """Soi MÃ NGUỒN, không soi chuỗi — bắt cả ca ai đó mới nối thêm.

    Cùng cách `test_reviewer_khong_noi_vao_cong_chan` ghim chiều import: ghim cấu
    trúc mã thì bắt được thay đổi ngay khi nó xuất hiện, không đợi tới lúc đo.
    """
    goc = Path(__file__).resolve().parents[3] / "src/application"
    for duong in ("poetry/sinh_theo_kho.py", "poetry/sinh_tho.py", "poetry/prompt.py"):
        cay = ast.parse((goc / duong).read_text(encoding="utf-8"))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Call) and isinstance(nut.func, ast.Name):
                assert nut.func.id != "SystemMessage", (
                    f"{duong} vừa dựng một SystemMessage. Đường thơ không gửi "
                    "system message — đọc `prompting/__init__.py` trước khi đổi."
                )


def test_file_prompt_CO_BIEN_BAO_o_dau():
    """Biển báo phải đọc được trong một cái liếc, không phải đọc hết docstring.

    Bản cũ VẪN nói "KHÔNG MỘT CHỮ LUẬT THƠ NÀO Ở ĐÂY" — nhưng ở dòng 97 của một
    docstring 104 dòng. Người ghép tay prompt ngày 22/09 không đọc tới đó.

    23/09: `instructions.py` đã gộp vào `system.py`, nên chỉ còn MỘT file để soi.
    """
    import application.prompting.system as mod_s

    # Đo bằng DÒNG, không bằng ký tự: khung viền ăn rất nhiều ký tự mà mắt đọc
    # lướt qua trong một nhịp. Hơn 20 dòng đầu là thứ người ta thật sự nhìn thấy.
    #
    # 🔴 ĐẢO NGƯỢC 23/09/2026. Biển báo cũ nói "ĐÂY KHÔNG PHẢI PROMPT LÀM THƠ";
    # nay hai file GỘP LẠI ĐÃ ĐỦ, nên biển báo phải nói điều ngược lại — và phải
    # cảnh báo đúng nguy cơ MỚI: gõ tay thêm luật vào, làm lệch khỏi `rule.LUAT`.
    for mod in (mod_s,):
        dau = "\n".join((mod.__doc__ or "").splitlines()[:22])
        assert "ĐỪNG GÕ TAY" in dau, mod.__name__
        assert "rule.LUAT" in dau, mod.__name__


# ══════════════════════════════════════════════════════════════════════════════
# BẢNG LUẬT ĐI CẢ HAI ĐƯỜNG — 23/09/2026
#
# 🩸 LỖ ĐƯỢC VÁ: `SYSTEM_PROMPT_V1` giao cho mô hình việc "giải thích luật thơ" và
# "chỉ ra chỗ bạn NGHI là lệch"; `CHI_DAN_TRO_GIUP_THO` còn bắt nó "nói rõ... đang
# mang thanh gì và CẦN THANH GÌ". Câu cuối BẤT KHẢ THI nếu không có bảng khuôn —
# và đường chat trước hôm nay chạy với đúng 0 chữ luật.
#
# Cách vá KHÔNG phải chép luật vào tầng 1/2 (vẫn cấm, các test trên vẫn ghim), mà
# là tách `BANG_LUAT_THO` — vẫn sinh từ `rule.LUAT` — rồi nối vào cả hai đường.
# ══════════════════════════════════════════════════════════════════════════════


def test_BANG_LUAT_THO_sinh_tu_rule_LUAT_khong_go_tay():
    """Mọi mã luật CỨNG phải có mặt. Gõ tay thì sót một mã là không ai biết."""
    from application.poetry.prompt import BANG_LUAT_THO
    from application.rule import LUAT

    ma_cung = [d.ma for d in LUAT if d.loai == "cung"]
    assert ma_cung
    for ma in ma_cung:
        assert ma in BANG_LUAT_THO, ma


def test_bang_luat_CHI_noi_LUAT_khong_noi_QUY_TRINH():
    """⛔ Ranh giới của khối này.

    Nó đi vào đường chat, nơi lời dẫn là BẮT BUỘC. Kéo `CACH_LAM_VIEC` sang là
    dạy mô hình "không lời dẫn" ngay chỗ nó phải giải thích cho người dùng.
    """
    from application.poetry.prompt import BANG_LUAT_THO

    assert CACH_LAM_VIEC.strip() not in BANG_LUAT_THO
    assert CHI_DAN_CHAT_LUONG.strip() not in BANG_LUAT_THO
    assert "CÁCH VIẾT ĐỂ KHÔNG PHÁ KHUÔN" not in BANG_LUAT_THO


def _nguon_chat() -> str:
    return (
        Path(__file__).resolve().parents[3]
        / "src/entrypoints/api/routers/chat.py"
    ).read_text(encoding="utf-8")


def test_chat_gui_DUNG_MOT_chuoi_khong_gui_lai_lan_hai():
    """Gộp 23/09/2026: `CHI_DAN_TRO_GIUP_THO` nay NẰM SẴN trong `SYSTEM_PROMPT_V1`.

    Gửi kèm một lần nữa là trả tiền hai lần cho cùng một khối chữ, và cho mô hình
    đọc hai bản có thể lệch nhau. Ghim bằng nguồn vì đây là chuyện ĐƯỜNG ĐI —
    không phép kiểm nào về nội dung prompt bắt được nó.
    """
    from application.prompting.system import CHI_DAN_TRO_GIUP_THO, SYSTEM_PROMPT_V1

    nguon = _nguon_chat()
    assert "chi_dan: list[str] = [SYSTEM_PROMPT_V1]" in nguon
    assert CHI_DAN_TRO_GIUP_THO.strip() in SYSTEM_PROMPT_V1


def test_chat_THAT_SU_truyen_tool_cho_mo_hinh():
    """🩸 Ghim chỗ hỏng gốc: `generate(...)` không truyền `tools`.

    Tool `kiem_tra_tho` đã đăng ký từ lâu mà đường chat chưa bao giờ với tới. Khai
    một tool mà router không đưa cho mô hình là đúng kiểu hỏng `prompting/__init__.py`
    liệt kê ba lần ở mục "BA LỖ HỔNG ĐÃ VÁ".
    """
    nguon = _nguon_chat()
    assert "app_container.tools.specs()" in nguon
    assert "tools=[" in nguon
    assert "call_many" in nguon


def test_vong_tool_cua_chat_CO_TRAN_va_CO_NGAN_SACH():
    """Một lượt chat nay kích hoạt được `sinh_tho` — tới ~36 lượt gọi model.

    Không có trần thì mô hình kẹt sẽ gọi mãi; không hỏi lại ngân sách mỗi vòng thì
    một lượt chat đốt hết hạn mức ngày.
    """
    from entrypoints.api.routers.chat import SO_VONG_TOOL_TOI_DA

    assert 1 <= SO_VONG_TOOL_TOI_DA <= 8
    nguon = _nguon_chat()
    assert "for _ in range(SO_VONG_TOOL_TOI_DA)" in nguon
    assert "within_daily_budget" in nguon.split("SO_VONG_TOOL_TOI_DA)")[1]


def test_duong_tho_VAN_dung_chung_MOT_bang_luat():
    """Hai đường mà hai bảng luật là tạo nguồn thứ hai — thứ cả kiến trúc này
    dựng lên để tránh."""
    from application.poetry.prompt import BANG_LUAT_THO

    assert BANG_LUAT_THO.strip() in CHI_DAN_SINH_THO


def test_chi_dan_chat_co_ca_NGOAI_PHAM_VI():
    """Chủ dự án chốt 23/09: hỏi ngoài thơ thì từ chối, kéo về làm thơ.

    Trả lời nửa vời làm người dùng tưởng đây là trợ lý chung, rồi lần sau họ hỏi
    tiếp thứ hệ thống không làm được.
    """
    from application.prompting.system import SYSTEM_PROMPT_V1

    assert "NGOÀI PHẠM VI THÌ NÓI THẲNG" in SYSTEM_PROMPT_V1
    assert "chỉ làm thơ" in SYSTEM_PROMPT_V1
    assert "Đừng trả lời nửa vời" in SYSTEM_PROMPT_V1


def test_ca_XIN_MOT_BAI_dung_DAU_danh_sach():
    """Dự án chỉ có một mục đích: sinh thơ. Ca quan trọng nhất phải đứng trước."""
    from application.prompting.system import SYSTEM_PROMPT_V1

    i_xin = SYSTEM_PROMPT_V1.index("KHI NGƯỜI DÙNG XIN MỘT BÀI THƠ")
    i_dua = SYSTEM_PROMPT_V1.index("KHI NGƯỜI DÙNG ĐƯA MỘT BÀI THƠ VÀO")
    i_ngoai = SYSTEM_PROMPT_V1.index("NGOÀI PHẠM VI THÌ NÓI THẲNG")
    assert i_xin < i_dua < i_ngoai


# ══════════════════════════════════════════════════════════════════════════════
# 🔴 ĐẢO NGƯỢC 23/09/2026 — LUẬT VÀO THẲNG HAI FILE, KHÔNG GỌI TOOL
#
# Chủ dự án chốt: *"dự án này chỉ có mục đích duy nhất là sinh thơ"* và *"không
# được gọi tool, hãy đưa luôn phần này vào system.py + instructions.py"*.
#
# Ba test bị gỡ ở trên ghim đúng quyết định NGƯỢC LẠI, nên chúng không còn đúng:
#
#   test_chat_KHONG_duoc_tu_viet_tho_bang_tay   -> nay chat PHẢI tự viết
#   test_chat_phai_GOI_TOOL_chu_khong_dem_tay   -> nay KHÔNG gọi tool
#   test_..._GOP_LAI_VAN_KHONG_DU_lam_tho       -> nay gộp lại ĐÃ ĐỦ, và đó là đích
#
# CÁI GIÁ, ghi ra chứ không giấu: bài viết thẳng ở đường chat KHÔNG qua cổng bảy
# tầng. Với p ≈ 0,56 mỗi dòng thì bài 20 dòng đạt cỡ 1 phần 100.000. Đường
# `/v1/poem` vẫn giữ nguyên cơ chế 32 ứng viên + cổng (~80 %) — hai đường nay đánh
# đổi khác nhau, và chỉ dẫn phải nói thật điều đó với người dùng.
# ══════════════════════════════════════════════════════════════════════════════


def test_hai_file_GOP_LAI_NAY_DA_DU_lam_tho():
    """Đích của lần đảo ngược: prompt tự đủ, mang sang nền tảng nào cũng chạy.

    Đây chính là thứ đã thiếu ngày 22/09 khi ghép tay hai file cho Gemma.
    """
    from application.prompting.system import SYSTEM_PROMPT_V1

    gop = SYSTEM_PROMPT_V1 + CACH_LAM_VIEC + CHI_DAN_CHAT_LUONG + CHI_DAN_TRO_GIUP_THO
    for dau_hieu in ("7 tiếng", "khuôn bằng", "khuôn trắc", "hiệp vần", "bội của 4"):
        assert dau_hieu in gop, dau_hieu


def test_chi_dan_chat_day_VIET_THANG_khong_goi_tool():
    """Không còn tool thì phép soát phải tự làm, và phải nói ra trong chỉ dẫn."""
    assert "tool" not in CHI_DAN_TRO_GIUP_THO.lower()
    assert "SOÁT LẠI từng dòng" in CHI_DAN_TRO_GIUP_THO
    assert "chọn khuôn, chọn tiếng 2/4/6" in CHI_DAN_TRO_GIUP_THO


def test_chat_VAN_phai_noi_bai_CHUA_qua_kiem():
    """⛔ Bất biến sống sót qua cả hai lần đảo chiều.

    Bài viết thẳng ở chat KHÔNG đi qua cổng. Không nói rõ thì người dùng tưởng nó
    đã được hệ thống duyệt — trong một sản phẩm mà điểm bán là thơ đúng luật.
    """
    assert "CHƯA đi qua bộ kiểm luật" in CHI_DAN_TRO_GIUP_THO
    assert "Đừng tự khẳng định nó đạt" in CHI_DAN_TRO_GIUP_THO


def test_bang_luat_SINH_tu_rule_LUAT_khong_go_tay():
    """Luật vào tầng 1/2 rồi thì nguy cơ mới là LỆCH NGUỒN. Ghim ngay chỗ đó."""
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import LUAT

    for d in LUAT:
        if d.loai == "cung":
            assert d.ma in BANG_LUAT_THO, d.ma


# ══════════════════════════════════════════════════════════════════════════════
# 🩸 CHÉP KHỔ, TÊN BÀI, VÀ NHỊP — 23/09/2026
#
# Chủ dự án đưa vào một bài hệ thống sinh ra: khổ đầu lặp NGUYÊN VĂN 3 lần, chiếm
# 12/16 dòng. Truy lại: bài ấy QUA CẢ HAI CỔNG — đạt luật và đạt chất lượng.
#
# `CL2 so_dong_lap` có ĐO nhưng `dat=True` luôn, vì S20 cho phép điệp dòng. Và
# việc chặn đã từng làm rồi gỡ, có đo: trên 6.000 bài người viết, 164 bài bị bắt
# và TOÀN BỘ là điệp có chủ ý. Nên KHÔNG siết lại cổng đó.
#
# Chỗ hổng thật: `CHI_DAN_VIET_TIEP_KHO` có câu "KHÔNG chép lại", nhưng nó chỉ đi
# vào `sinh_theo_kho` (đường /v1/poem). Đường chat viết thẳng cả bài và trước hôm
# nay KHÔNG có một chữ nào cấm chép khổ.
# ══════════════════════════════════════════════════════════════════════════════


def test_chi_dan_chat_CAM_CHEP_KHO():
    """Vá đúng chỗ hổng: đường chat trước đây không có lệnh này."""
    assert "MỖI KHỔ PHẢI NÓI MỘT ĐIỀU MỚI" in CHI_DAN_TRO_GIUP_THO
    assert "ĐỪNG chép thêm một khổ cũ" in CHI_DAN_TRO_GIUP_THO


def test_cam_chep_kho_PHAN_BIET_duoc_voi_diep_co_chu_y():
    """⛔ S20 CHO PHÉP điệp dòng, điệp khổ.

    Cấm suông sẽ dạy mô hình bỏ luôn một quyền hợp lệ. Phải vẽ được đường phân
    chia — và cách vẽ là cặp đối lập, đúng lối `CHI_DAN_CHAT_LUONG` vẫn dùng.
    """
    assert "điệp có chủ ý:" in CHI_DAN_TRO_GIUP_THO
    assert "chép cho đủ  :" in CHI_DAN_TRO_GIUP_THO


def test_chi_dan_chat_DOI_TEN_BAI_phan_anh_noi_dung():
    """Chủ dự án chốt: "tên sinh ra cần phản ánh nội dung của bài thơ"."""
    assert "ĐẶT TÊN CHO BÀI" in CHI_DAN_TRO_GIUP_THO
    assert "PHẢN ÁNH NỘI DUNG" in CHI_DAN_TRO_GIUP_THO
    assert "phản ánh bài:" in CHI_DAN_TRO_GIUP_THO
    assert "nhãn chung  :" in CHI_DAN_TRO_GIUP_THO


def test_CHI_DAN_DAT_TIEU_DE_KHONG_bi_dung_toi():
    """⛔ Đó là lượt gọi RIÊNG của /v1/poem, chạy SAU cổng.

    Đường đó sinh từng khổ 4 dòng và `_lay_bon_dong` lấy 4 dòng không rỗng đầu
    tiên — một dòng tên lọt vào là hỏng cả ứng viên.
    """
    from application.prompting.system import CHI_DAN_DAT_TIEU_DE

    assert "Chỉ trả về đúng tiêu đề, không gì khác" in CHI_DAN_DAT_TIEU_DE
    assert "ĐẶT TÊN CHO BÀI" not in CHI_DAN_DAT_TIEU_DE


def test_chi_dan_chat_doi_chon_NHIP_CHU_DAO():
    """Chủ dự án chốt: "thơ sinh ra phải đúng nhịp"."""
    assert "NHỊP CHỦ ĐẠO" in CHI_DAN_TRO_GIUP_THO
    assert "Đổi nhịp thì đổi ở chỗ chuyển ý" in CHI_DAN_TRO_GIUP_THO


# ── Bảng nhịp: đúng thứ tự tài liệu §6, và có đủ hiệu quả ───────────────────


def test_moi_nhip_trong_rule_deu_co_MO_TA_HIEU_QUA():
    """Thêm nhịp thứ tám vào bảng luật mà quên mô tả thì test này đỏ."""
    from application.prompting.luat_tho import HIEU_QUA_NHIP
    from application.rule import NHIP_TAI_LIEU

    for ten in NHIP_TAI_LIEU:
        assert ten in HIEU_QUA_NHIP, ten
        assert HIEU_QUA_NHIP[ten].strip()


def test_bang_nhip_giu_DUNG_THU_TU_tai_lieu():
    """🩸 Bản trước dùng `sorted()`, đẩy 4/3 từ vị trí 1 xuống 5.

    4/3 đứng đầu §6 vì nó là nhịp cân bằng, kế thừa Đường luật. Mô hình đọc danh
    sách theo thứ tự, nên đây không phải chuyện thẩm mỹ.
    """
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import NHIP_TAI_LIEU

    than = BANG_LUAT_THO[BANG_LUAT_THO.index("NHỊP"):]
    vi_tri = [than.index(ten) for ten in NHIP_TAI_LIEU]
    assert vi_tri == sorted(vi_tri), "bảng nhịp không còn theo thứ tự tài liệu"
    assert than.index("4/3") < than.index("1/6")


def test_bang_nhip_co_S13_va_S15_khong_chi_co_S14():
    """Bản trước chỉ có S14 ("nên có nhịp chủ đạo"). S13 và S15 mất hẳn."""
    from application.prompting.luat_tho import BANG_LUAT_THO

    # Lấy nguyên văn từ `rule.LUAT` — gõ tay ở đây là dựng nguồn thứ hai, và
    # bản trước ĐÃ gõ tay ("do NGHĨA của dòng") nên lệch thật khỏi bảng luật.
    for ma in ("S13", "S14", "S15"):
        assert MA_LUAT[ma].noi_dung in BANG_LUAT_THO, ma


def test_CHI_MOT_bang_luat_cho_ca_hai_duong():
    """🩸 ĐÃ TỪNG CÓ HAI, VÀ CHÚNG LỆCH NHAU THẬT — hợp nhất 23/09/2026.

    `poetry/prompt.py` và `prompting/luat_tho.py` mỗi bên từng giữ một
    `BANG_LUAT_THO` riêng: 1.436 vs 1.938 ký tự. Bản ở `prompting/` đã được bổ
    sung bảng hiệu quả bảy nhịp theo tài liệu §6, bản kia thì chưa — tức hai
    đường sinh thơ đang được dạy hai phần nhịp khác nhau.

    Đây đúng là kiểu hỏng cả kiến trúc dựng lên để tránh. `is` chứ không phải
    `==`: hai chuỗi bằng nhau hôm nay vẫn có thể tách ra ngày mai.
    """
    from application.poetry.prompt import BANG_LUAT_THO as o_duong_tho
    from application.prompting.luat_tho import BANG_LUAT_THO as nguon

    assert o_duong_tho is nguon


def test_ca_hai_duong_deu_nhan_bang_nhip_co_hieu_qua():
    """Kiểm soát dương cho test trên: hợp nhất rồi thì cả hai phải có phần mới."""
    from application.poetry.prompt import CHI_DAN_SINH_THO as duong_tho
    from application.prompting.system import SYSTEM_PROMPT_V1 as duong_chat

    for chuoi in (duong_tho, duong_chat):
        assert "Cân bằng, kế thừa âm hưởng Đường luật" in chuoi
        assert chuoi.index("4/3") < chuoi.index("1/6")


# ══════════════════════════════════════════════════════════════════════════════
# GỘP `instructions.py` VÀO `system.py` — 23/09/2026, chủ dự án chốt
# ══════════════════════════════════════════════════════════════════════════════


def test_instructions_py_DA_BI_XOA_khong_song_lai():
    """Hai file prompt là hai chỗ để lệch nhau. Nay chỉ còn một.

    Ghim bằng ĐƯỜNG DẪN chứ không bằng import: ai tạo lại file ấy sẽ không thấy
    lỗi nào cho tới khi hai bản chỉ dẫn đã trôi xa nhau.
    """
    goi = Path(__file__).resolve().parents[3] / "src" / "application" / "prompting"
    assert goi.is_dir(), goi
    assert not (goi / "instructions.py").exists()


def test_moi_hang_cua_DUONG_THO_van_o_system_va_KHONG_lot_vao_chuoi_chat():
    """⛔ BẪY CỦA VIỆC GỘP.

    `/v1/poem` KHÔNG gửi system message nào. Nhét chữ của đường thơ vào
    `SYSTEM_PROMPT_V1` là làm nó BIẾN MẤT khỏi đường thơ — không lỗi, không cảnh
    báo. Cùng một file KHÔNG có nghĩa là cùng một chuỗi.
    """
    from application.prompting.system import (
        CACH_LAM_VIEC,
        CHI_DAN_DAT_TIEU_DE,
        CHI_DAN_HUONG_DAN_DOC,
        CHI_DAN_TU_SOI,
        SYSTEM_PROMPT_V1,
    )

    for chi_dan in (CACH_LAM_VIEC, CHI_DAN_DAT_TIEU_DE, CHI_DAN_HUONG_DAN_DOC, CHI_DAN_TU_SOI):
        assert chi_dan.strip() not in SYSTEM_PROMPT_V1


# ══════════════════════════════════════════════════════════════════════════════
# BẢNG LUẬT DỰNG LẠI THEO BẢY TẦNG — 23/09/2026
#
# Chủ dự án: *"chi tiết từng Rule"*, *"phần Rule cần đầy đủ Rule của tôi"*.
# ══════════════════════════════════════════════════════════════════════════════


def test_bang_luat_co_DU_BAY_TANG_theo_dung_thu_tu_bo_kiem():
    """Mô hình đọc theo thứ tự, nên thứ tự phải là thứ tự nó sẽ bị chấm."""
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import TANG

    vi_tri = [BANG_LUAT_THO.index(f"\n{t.so}. ") for t in TANG]
    assert vi_tri == sorted(vi_tri)


def test_MOI_dieu_luat_cua_rule_deu_co_mat_khong_sot_dieu_nao():
    """🩸 Bản trước chỉ có 4 mã cứng. S11, S13, S15, S16–S21 mất hẳn.

    Sót một điều thì không ai biết — prompt vẫn đọc trôi chảy.
    """
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import LUAT

    for d in LUAT:
        assert d.ma in BANG_LUAT_THO, d.ma


def test_TANG_6_noi_ro_doi_MOT_nhip_phu_MOI_dong():
    """🩸 LỖ NẶNG NHẤT ĐƯỢC VÁ.

    Bản trước dạy *"nhịp không cố định cho toàn bài"* — đúng câu tài liệu §6,
    nhưng QĐ-4b ghi đè và cổng chặn theo QĐ-4b. Mô hình làm đúng theo prompt rồi
    trượt tầng 6, và không có cách nào đoán ra vì sao.
    """
    from application.prompting.luat_tho import BANG_LUAT_THO

    assert "phủ được MỌI dòng" in BANG_LUAT_THO or "ngắt được MỌI dòng" in BANG_LUAT_THO
    assert "không chỉ phần lớn các dòng" in BANG_LUAT_THO


def test_moi_dieu_bi_QUYET_DINH_ghi_de_deu_duoc_NOI_THANG():
    """Không nói ra thì prompt và cổng dạy hai điều khác nhau."""
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import GHI_DE_BOI_QUYET_DINH

    assert GHI_DE_BOI_QUYET_DINH
    for ma, ly_do in GHI_DE_BOI_QUYET_DINH.items():
        assert ly_do in BANG_LUAT_THO, ma


def test_QUYEN_va_DIEU_CHAN_KHONG_doc_ngang_hang():
    """N2: điều QUYỀN không bao giờ làm trượt bài, nên phải đọc ra là quyền.

    Danh sách phẳng khiến S20 ("được dùng điệp") đứng ngang một điều chặn — rồi
    mô hình hoặc sợ dùng quyền của mình, hoặc coi nhẹ điều thật sự chặn.
    """
    from application.prompting.luat_tho import BANG_LUAT_THO

    i_quyen = BANG_LUAT_THO.index("S20")
    than = BANG_LUAT_THO[:i_quyen]
    assert than.rindex("ĐƯỢC PHÉP") > than.rindex("BẮT BUỘC")


def test_N3_dieu_KHONG_KIEM_DUOC_phai_ghi_cong_khai():
    """N3: máy mù ở đâu thì nói ở đó. Giấu đi thì mô hình tưởng mọi thứ đều đo."""
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import TANG

    khong_do = {m for t in TANG for m in t.khong_kiem_duoc}
    assert khong_do
    assert "MÁY KHÔNG ĐO ĐƯỢC" in BANG_LUAT_THO
    for ma in khong_do:
        assert ma in BANG_LUAT_THO, ma


def test_bang_luat_VAN_sinh_tu_rule_khong_go_tay():
    """Kiểm soát: đổi một chữ trong `rule.LUAT` thì prompt phải đổi theo."""
    from application.prompting.luat_tho import BANG_LUAT_THO
    from application.rule import LUAT

    for d in LUAT:
        assert d.noi_dung in BANG_LUAT_THO, d.ma


# ══════════════════════════════════════════════════════════════════════════════
# BẢNG LUẬT CHUYỂN VÀO `system.py` — 23/09/2026, chủ dự án chốt
#
#     *"Thay vì import vào trong system.py, tôi cần bạn thêm trực tiếp
#       BANG_LUAT_THO + CACH_VIET_DUNG_LUAT vào trong system.py"*
#
# `luat_tho.py` giữ lại làm VỎ, vì `/v1/poem` và bảy test đọc qua đó.
# ══════════════════════════════════════════════════════════════════════════════


def test_bang_luat_DINH_NGHIA_o_system_khong_phai_o_luat_tho():
    """Ghim chỗ ĐỊNH NGHĨA, không chỉ ghim chỗ đọc được.

    Import lại được từ `luat_tho` thì một bản sao gõ tay ở đó cũng "đọc được" —
    test này phân biệt hai chuyện đó bằng cách soi nguồn.
    """
    import inspect

    from application.prompting import luat_tho, system

    assert 'BANG_LUAT_THO: str = f"""' in inspect.getsource(system)
    assert "BANG_LUAT_THO" not in inspect.getsource(luat_tho).split("__all__")[0].split(
        "import"
    )[-1].split("\n\n")[-1]


def test_luat_tho_CHI_LA_VO_khong_dinh_nghia_lai():
    """⛔ Lỗi đã xảy ra THẬT trong ngày: hai định nghĩa song song trôi thành
    1.436 vs 1.938 ký tự — hai đường sinh thơ học hai phần nhịp khác nhau."""
    import inspect

    from application.prompting import luat_tho

    nguon = inspect.getsource(luat_tho)
    assert '"""' in nguon
    for dau_hieu in ("def _bat_buoc", "def _bang_nhip", "HIEU_QUA_NHIP: dict"):
        assert dau_hieu not in nguon, dau_hieu


def test_BA_DUONG_cung_MOT_doi_tuong_khong_phai_ba_ban_sao():
    """`is` chứ không `==`: hai chuỗi bằng nhau hôm nay vẫn tách ra ngày mai.

    ⚠️ `is` CHỈ ĐÚNG GIỮA CÁC MODULE KHÔNG BỊ RELOAD. `test_KHONG_noi_suy_thu_doi
    _theo_LUOT` gọi `importlib.reload` lên `system`, sinh một đối tượng chuỗi mới
    — còn `luat_tho` và `poetry/prompt` vẫn giữ tham chiếu cũ. Nên chúng `is`
    nhau, mà không `is` bản vừa reload, và kết quả đổi theo THỨ TỰ CHẠY TEST.

    Vì vậy: `is` giữa hai đường tiêu thụ (thứ lỗi cũ thật sự làm hỏng), và `==`
    với nguồn — đủ bắt một bản sao gõ tay, mà không giả đỏ vì reload.
    """
    from application.poetry.prompt import BANG_LUAT_THO as o_duong_tho
    from application.prompting.luat_tho import BANG_LUAT_THO as qua_vo
    from application.prompting.system import BANG_LUAT_THO as o_nguon

    assert o_duong_tho is qua_vo, "hai đường tiêu thụ đã tách thành hai bản"
    assert o_duong_tho == o_nguon


def test_system_KHONG_import_nguoc_lai_luat_tho():
    """Vỏ trỏ về nguồn; nguồn trỏ về vỏ là một vòng lặp import."""
    import inspect

    from application.prompting import system

    assert "from application.prompting.luat_tho" not in inspect.getsource(system)
