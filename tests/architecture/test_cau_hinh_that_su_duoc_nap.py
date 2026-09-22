"""Cấu hình trong `configs/` phải THẬT SỰ được nạp lúc chạy.

Vì sao cần một test riêng cho việc này: `load_settings` và `ModelRouter._load_config`
đều LẶNG LẼ bỏ qua khi đường dẫn không tồn tại, rồi rơi về mặc định viết trong mã.
Một `PROJECT_ROOT` lệch một cấp không làm hỏng test nào — mọi test cùng chạy trên
cùng bộ mặc định đó — nhưng làm hệ thống chạy với danh mục model RỖNG.

Đúng như vậy đã xảy ra: `PROJECT_ROOT` từng là `parents[3]`, trỏ ra thư mục CHA của
dự án, và chỉ lộ ra khi `GET /v1/models` trả về danh sách rỗng.
"""

from pathlib import Path

from adapters.llm.router import ModelRouter
from bootstrap.settings import CONFIGS_DIR, PROJECT_ROOT, load_settings

GOC_THAT = Path(__file__).resolve().parents[2]


def test_PROJECT_ROOT_dung_la_goc_du_an():
    assert PROJECT_ROOT == GOC_THAT, (
        f"PROJECT_ROOT={PROJECT_ROOT} không phải gốc dự án {GOC_THAT} — "
        "mọi đường dẫn cấu hình suy ra từ nó đều lệch."
    )


def test_cac_file_cau_hinh_dang_duoc_tro_toi_deu_ton_tai():
    """Trỏ tới một file không tồn tại thì mã rơi về mặc định mà không báo gì."""
    s = load_settings()
    assert CONFIGS_DIR.is_dir(), f"{CONFIGS_DIR} không tồn tại"
    assert s.models_catalog_path.is_file(), f"{s.models_catalog_path} không tồn tại"
    assert s.guardrails.policy_file.is_file(), f"{s.guardrails.policy_file} không tồn tại"


def test_danh_muc_model_khong_rong():
    """Danh mục rỗng nghĩa là mọi định tuyến model đều chạy trên nhánh dự phòng."""
    r = ModelRouter(config_path=str(load_settings().models_catalog_path))
    assert r.models, "ModelRouter nạp được 0 model — cấu hình không tới nơi"
    assert r.tiers, "ModelRouter nạp được 0 tier"
