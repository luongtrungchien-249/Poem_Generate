"""CƯỠNG CHẾ CHỈ THỊ 1 — *"Rule của tôi phải là không được thay đổi."*

Ba lớp bảo vệ, mỗi lớp bắt một kiểu vi phạm khác nhau:

    lớp 1  SHA-256 của rule.py bị ghim         -> bắt việc SỬA trực tiếp
    lớp 2  không ai cài lại phép đếm tiếng     -> bắt việc VÒNG QUA bằng bản sao
    lớp 3  không ai ghi vào biến module của rule -> bắt việc GHI ĐÈ lúc chạy

Lớp 1 cố ý khó chịu. Nó KHÔNG cấm sửa `rule.py` — nó buộc người sửa phải nhìn thấy
cái giá trước khi sửa: đổi luật thì phải đo lại corpus 67.150 bản ghi và cập nhật
ba báo cáo đã đối soát.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"
RULE = SRC / "application" / "rule.py"

# Băm của bản đã được chủ dự án chốt ngày 18/09/2026, đo lại 21/09/2026.
#
# ĐỔI CON SỐ NÀY LÀ MỘT QUYẾT ĐỊNH, KHÔNG PHẢI MỘT THAO TÁC SỬA TEST.
# Trước khi đổi, phải làm đủ ba việc:
#   1. chạy `python datalake/scripts/kiem_tra_toan_bo.py` để đo lại corpus
#   2. chạy `python datalake/scripts/doi_soat_tai_lieu.py` cho tới khi xanh
#   3. ghi lý do sửa vào docs/Plan_Rule_Phan_Tang.md
BAM_DA_CHOT = "9f808d59f43d98012f0d3a01f3ea3c4734004fe82a269aee12cde6739b4f2571"

# Tên phép đếm chỉ được định nghĩa MỘT lần, ở rule.py. Cài lại ở chỗ khác là tạo
# nguồn luật thứ hai — vi phạm nguyên tắc P1 của plan thi công.
TEN_DOC_QUYEN = frozenset(
    {"tach_tieng", "dem_tieng", "thanh_cua", "van_cua", "kiem_tra_bai_tho", "hiep_van"}
)


@pytest.mark.architecture
def test_rule_py_khong_bi_sua():
    """Lớp 1 — SHA-256 bị ghim."""
    bam = hashlib.sha256(RULE.read_bytes()).hexdigest()
    assert bam == BAM_DA_CHOT, (
        "\n\n"
        "  ⛔ `src/application/rule.py` ĐÃ BỊ SỬA.\n\n"
        "  Chỉ thị chủ dự án 21/09/2026: *\"Rule của tôi phải là không được thay đổi.\"*\n\n"
        f"  băm đã chốt : {BAM_DA_CHOT}\n"
        f"  băm hiện tại: {bam}\n\n"
        "  Nếu việc sửa là CÓ CHỦ Ý và đã được chủ dự án duyệt, làm đủ ba việc trước\n"
        "  khi cập nhật hằng số trên:\n"
        "    1. python datalake/scripts/kiem_tra_toan_bo.py   (đo lại 67.150 bản ghi)\n"
        "    2. python datalake/scripts/doi_soat_tai_lieu.py  (phải xanh)\n"
        "    3. ghi lý do vào docs/Plan_Rule_Phan_Tang.md\n\n"
        "  Nếu KHÔNG chủ ý: `git checkout -- src/application/rule.py`\n"
    )


@pytest.mark.architecture
def test_khong_ai_cai_lai_phep_dem_tieng():
    """Lớp 2 — không tệp nào ngoài rule.py định nghĩa lại phép đếm."""
    vi_pham: list[str] = []
    for tep in SRC.rglob("*.py"):
        if tep == RULE:
            continue
        cay = ast.parse(tep.read_text(encoding="utf-8"), filename=str(tep))
        for nut in ast.walk(cay):
            if isinstance(nut, ast.FunctionDef | ast.AsyncFunctionDef) and (
                nut.name in TEN_DOC_QUYEN
            ):
                vi_pham.append(f"{tep.relative_to(SRC)}:{nut.lineno} định nghĩa {nut.name}()")

    assert not vi_pham, (
        "Phép kiểm thơ chỉ được định nghĩa ở application/rule.py (nguyên tắc P1).\n"
        "Hai bộ luật song song là cách chắc chắn nhất để hai nơi nói hai điều khác nhau.\n"
        + "\n".join(f"  - {v}" for v in vi_pham)
    )


@pytest.mark.architecture
def test_khong_ai_ghi_de_bien_module_cua_rule():
    """Lớp 3 — không ai gán vào `rule.<gì đó>` lúc chạy."""
    vi_pham: list[str] = []
    for tep in SRC.rglob("*.py"):
        if tep == RULE:
            continue
        cay = ast.parse(tep.read_text(encoding="utf-8"), filename=str(tep))
        for nut in ast.walk(cay):
            if not isinstance(nut, ast.Assign):
                continue
            for dich in nut.targets:
                if (
                    isinstance(dich, ast.Attribute)
                    and isinstance(dich.value, ast.Name)
                    and dich.value.id in ("rule", "luat")
                ):
                    vi_pham.append(
                        f"{tep.relative_to(SRC)}:{nut.lineno} gán vào {dich.value.id}.{dich.attr}"
                    )

    assert not vi_pham, (
        "Không module nào được ghi vào biến của rule.py lúc chạy — đóng băng nghĩa là\n"
        "đóng băng cả lúc chạy, không chỉ lúc đọc mã.\n"
        + "\n".join(f"  - {v}" for v in vi_pham)
    )
