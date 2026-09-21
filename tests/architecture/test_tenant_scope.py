"""CƯỠNG CHẾ ADR-0003 — `TenantScope` ở tham số ĐẦU TIÊN của mọi port chạm dữ liệu.

    *"mọi phương thức port chạm dữ liệu phải nhận `TenantScope` ở tham số đầu tiên,
    để việc cô lập tenant được bảo đảm bằng chữ ký hàm chứ không bằng review."*

VÌ SAO PHẢI CÓ TEST NÀY, chứ không chỉ sửa một lần rồi thôi.

Lỗi cũ không phải do ai đó cẩu thả. Nó là hệ quả tự nhiên của việc truyền tenant qua
một `dict`: gõ `{"tenant_id": x}` rồi lọc trên `chunk.metadata` trông hoàn toàn hợp
lý khi đọc, và trình kiểm kiểu không có gì để nói. Sửa một lần thì lần sau vẫn tái
diễn ở một port mới.

Test này chặn cả LOẠI lỗi đó: thêm một phương thức mới quên `scope` là test đỏ ngay,
trước khi nó kịp có người gọi.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
PORT_LUU_TRU = SRC / "application" / "ports" / "repositories.py"

# Protocol nào phải mang TenantScope. `BlobRepository` và `CacheRepository` KHÔNG
# có mặt ở đây có chủ ý: blob dùng khoá đầy đủ do người gọi dựng, cache dùng khoá
# đã băm gồm cả nội dung — cả hai không có khái niệm "danh sách của một tenant" để
# mà rò. Thêm bừa `scope` vào chúng là nghi thức, không phải bảo vệ.
PROTOCOL_CAN_SCOPE = frozenset({"RelationalRepository", "VectorRepository"})


def _cac_phuong_thuc(cay: ast.Module, ten_lop: str) -> list[ast.AsyncFunctionDef]:
    for nut in ast.walk(cay):
        if isinstance(nut, ast.ClassDef) and nut.name == ten_lop:
            return [
                m for m in nut.body if isinstance(m, ast.AsyncFunctionDef)
            ]
    return []


@pytest.mark.architecture
def test_moi_phuong_thuc_port_luu_tru_nhan_TenantScope_o_dau():
    cay = ast.parse(PORT_LUU_TRU.read_text(encoding="utf-8"))
    vi_pham: list[str] = []

    for ten_lop in PROTOCOL_CAN_SCOPE:
        pt = _cac_phuong_thuc(cay, ten_lop)
        assert pt, f"không tìm thấy phương thức nào của {ten_lop}"
        for m in pt:
            tham_so = [a.arg for a in m.args.args]
            # [0] là `self`, nên `scope` phải ở [1].
            if len(tham_so) < 2 or tham_so[1] != "scope":
                vi_pham.append(
                    f"{ten_lop}.{m.name}: tham số đầu (sau self) là "
                    f"{tham_so[1] if len(tham_so) > 1 else '(không có)'!r}, phải là 'scope'"
                )

    assert not vi_pham, (
        "ADR-0003: cô lập tenant phải nằm trong CHỮ KÝ HÀM.\n"
        + "\n".join(f"  - {v}" for v in vi_pham)
    )


@pytest.mark.architecture
def test_scope_phai_dung_kieu_TenantScope():
    cay = ast.parse(PORT_LUU_TRU.read_text(encoding="utf-8"))
    vi_pham: list[str] = []
    for ten_lop in PROTOCOL_CAN_SCOPE:
        for m in _cac_phuong_thuc(cay, ten_lop):
            if len(m.args.args) < 2:
                continue
            chu_thich = m.args.args[1].annotation
            ten = getattr(chu_thich, "id", None)
            if ten != "TenantScope":
                vi_pham.append(f"{ten_lop}.{m.name}: scope khai kiểu {ten!r}")
    assert not vi_pham, (
        "`scope` phải là `TenantScope`, không phải chuỗi — một chuỗi thì gõ sai là "
        "lọt, còn một kiểu riêng thì không.\n" + "\n".join(f"  - {v}" for v in vi_pham)
    )


@pytest.mark.architecture
def test_KHONG_con_noi_nao_loc_tenant_qua_dict_filters():
    """🩸 Ghim đúng lỗi cũ: truyền tenant qua `filters` dạng dict.

    Đó là cách viết đã khiến RAG luôn trả rỗng suốt một thời gian mà không ai biết.

    Soi bằng AST chứ không bằng tìm chuỗi: nhiều docstring trong repo **cố ý nhắc
    lại** cách viết cũ để ghi nhớ nó đã hỏng thế nào. Tìm chuỗi thô sẽ bắt chính
    những lời cảnh báo ấy — và cách sửa duy nhất khi đó là xoá lời cảnh báo đi,
    tức là test buộc người ta phá thứ nó định bảo vệ.
    """
    vi_pham: list[str] = []
    for tep in SRC.rglob("*.py"):
        cay = ast.parse(tep.read_text(encoding="utf-8"), filename=str(tep))
        for nut in ast.walk(cay):
            if not isinstance(nut, ast.Call):
                continue
            for kw in nut.keywords:
                if kw.arg != "filters" or not isinstance(kw.value, ast.Dict):
                    continue
                for khoa in kw.value.keys:
                    if isinstance(khoa, ast.Constant) and khoa.value == "tenant_id":
                        vi_pham.append(
                            f"{tep.relative_to(SRC)}:{nut.lineno}: "
                            "truyền tenant_id qua dict filters"
                        )
    assert not vi_pham, (
        "Tenant phải đi qua `TenantScope`, KHÔNG qua dict filters:\n"
        + "\n".join(f"  - {v}" for v in vi_pham)
    )
