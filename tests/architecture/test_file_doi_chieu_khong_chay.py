"""Các file `compare_*.py` ở gốc repo là HỒ SƠ ĐỐI CHIẾU, không phải mã chạy.

Chủ dự án chốt 21/09/2026: *"Không cần xóa đâu, chỉ cần không chạy qua đó là được."*

════ VÌ SAO CẦN TEST CHỨ KHÔNG CHỈ CẦN MỘT LỜI DẶN ════

`compare_prompt.py` là bản prompt của một thế hệ trước (lục bát · 7 chữ · 8 chữ, tự
gõ luật vào chuỗi, tự chấm điểm bằng LLM). Nó có giá trị làm tài liệu: phần lớn
những gì hệ thống sống vừa nhập — cách dạy bằng cặp đối lập, mỏ neo hiệu chuẩn,
lối thoát khi bế tắc — đều đối chiếu từ đó ra.

Nhưng một file prompt nằm trong repo mà không ai gọi là một cái bẫy, và
`instructions.py` đã đặt tên cho nó:

    "Ai sửa quy tắc ở bản chép sẽ tin mình vừa đổi hành vi hệ thống, trong khi
     không có gì đổi."

Giữ file thì phải chặn đúng cái bẫy đó. Hai lớp:

    lớp 1  không module nào trong `src/` import nó   -> bắt việc NỐI VÀO
    lớp 2  đầu file có nhãn nói rõ nó không chạy     -> bắt việc HIỂU NHẦM

Lớp 2 không thay được lớp 1: nhãn thì người đọc mới thấy, còn test thì máy thấy.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

GOC = Path(__file__).resolve().parents[2]
SRC = GOC / "src"

# Bắt theo TIỀN TỐ, không liệt kê từng tên: thêm `compare_rule.py` hay bất kỳ bản
# đối chiếu nào sau này cũng tự động được bảo vệ, không phải nhớ cập nhật danh sách.
TIEN_TO = "compare_"


def _cac_file_doi_chieu() -> list[Path]:
    return sorted(p for p in GOC.glob(f"{TIEN_TO}*.py") if p.is_file())


@pytest.mark.architecture
def test_khong_module_nao_trong_src_import_file_doi_chieu():
    """Lớp 1 — quét cây cú pháp, không quét bằng mắt.

    Một `import compare_prompt` lọt vào `src/` nghĩa là bản prompt cũ vừa thành mã
    sống: hai nguồn luật cùng lúc, và mô hình được dạy hai luật khác nhau tuỳ
    đường nó đi qua.
    """
    ten_module = {p.stem for p in _cac_file_doi_chieu()}
    if not ten_module:
        pytest.skip("không có file đối chiếu nào ở gốc repo")

    vi_pham: list[str] = []
    for tep in SRC.rglob("*.py"):
        cay = ast.parse(tep.read_text(encoding="utf-8"), filename=str(tep))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.Import):
                for a in nut.names:
                    if a.name.split(".")[0] in ten_module:
                        vi_pham.append(f"{tep.relative_to(GOC)} -> import {a.name}")
            elif isinstance(nut, ast.ImportFrom):
                goc_mod = (nut.module or "").split(".")[0]
                if goc_mod in ten_module:
                    vi_pham.append(f"{tep.relative_to(GOC)} -> from {nut.module}")

    assert not vi_pham, (
        "File đối chiếu đã bị nối vào mã sống:\n  " + "\n  ".join(vi_pham) + "\n"
        "Chúng là hồ sơ, không phải mã chạy. Cần nội dung nào thì CHÉP nó vào đúng "
        "tầng có mã đọc tới, đừng import."
    )


@pytest.mark.architecture
def test_khong_nam_trong_goi_ma_nguon():
    """Nằm trong `src/` là tự động vào đường import — dù chưa ai import."""
    for p in SRC.rglob(f"{TIEN_TO}*.py"):
        raise AssertionError(f"{p.relative_to(GOC)} nằm trong src/, phải để ở gốc repo")


@pytest.mark.architecture
def test_dau_file_co_nhan_noi_ro_khong_chay():
    """Lớp 2 — người mở file ra phải thấy ngay, trước khi kịp sửa gì.

    Không có nhãn thì người sửa nó tin mình vừa đổi hành vi hệ thống.
    """
    for p in _cac_file_doi_chieu():
        dau = p.read_text(encoding="utf-8")[:1200].upper()
        assert "KHÔNG CHẠY" in dau or "KHONG CHAY" in dau, (
            f"{p.name} thiếu nhãn ở đầu file. Thêm một khối nói rõ đây là hồ sơ "
            "đối chiếu, không phải mã sống."
        )
