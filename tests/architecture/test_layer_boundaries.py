"""Ranh giới tầng phải do máy cưỡng chế, không dựa vào review.

Kiểm chứng trực tiếp bằng AST nên chạy được cả khi chưa cài import-linter;
CI vẫn chạy `lint-imports` cho bộ hợp đồng đầy đủ trong .importlinter.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src"

# Mỗi tầng chỉ được import chính nó và các tầng bên trong.
ALLOWED: dict[str, set[str]] = {
    "domain": {"domain", "contracts"},
    "application": {"application", "domain", "contracts"},
    "adapters": {"adapters", "application", "domain", "contracts"},
    "bootstrap": {"bootstrap", "adapters", "application", "domain", "contracts"},
    "entrypoints": {"entrypoints", "bootstrap", "adapters", "application", "domain", "contracts"},
    "contracts": {"contracts"},
}

# Thư viện hạ tầng bị cấm ở hai vòng trong cùng.
FORBIDDEN_EXTERNAL: dict[str, set[str]] = {
    "domain": {"httpx", "fastapi", "starlette", "prometheus_client", "redis", "sqlalchemy", "yaml"},
    "application": {"httpx", "fastapi", "starlette", "prometheus_client", "redis", "sqlalchemy"},
}


def _iter_modules() -> list[tuple[str, Path]]:
    out = []
    for path in SRC.rglob("*.py"):
        rel = path.relative_to(SRC)
        layer = rel.parts[0]
        if layer == "__pycache__" or layer not in ALLOWED:
            continue  # tệp ở gốc gói (vd: __init__.py) không thuộc tầng nào
        out.append((layer, path))
    return out


def _imported_roots(path: Path) -> set[tuple[str, str]]:
    """Trả về tập (gói gốc, tên module đầy đủ) mà file này import."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                found.add((alias.name.split(".")[0], alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # import tương đối: luôn trong cùng tầng
                continue
            if node.module:
                found.add((node.module.split(".")[0], node.module))
    return found


@pytest.mark.architecture
@pytest.mark.parametrize("layer,path", _iter_modules(), ids=lambda v: getattr(v, "name", str(v)))
def test_tang_chi_import_vao_trong(layer: str, path: Path) -> None:
    allowed = ALLOWED[layer]
    for root, _full in _imported_roots(path):
        if root not in ALLOWED:
            continue  # thư viện ngoài, không phải tầng của hệ thống
        target_layer = root
        assert target_layer in allowed, (
            f"{path.relative_to(SRC)} (tầng '{layer}') import sang tầng '{target_layer}' — "
            f"vi phạm chiều phụ thuộc. Cho phép: {sorted(allowed)}"
        )


@pytest.mark.architecture
@pytest.mark.parametrize("layer,path", _iter_modules(), ids=lambda v: getattr(v, "name", str(v)))
def test_long_khong_biet_cong_nghe(layer: str, path: Path) -> None:
    forbidden = FORBIDDEN_EXTERNAL.get(layer)
    if not forbidden:
        return
    for root, _full in _imported_roots(path):
        assert root not in forbidden, (
            f"{path.relative_to(SRC)} (tầng '{layer}') import '{root}' — "
            f"lõi không được biết đến thư viện hạ tầng."
        )
