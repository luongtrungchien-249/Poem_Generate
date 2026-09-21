"""Kho thơ mẫu và bộ chọn few-shot — §9, §26–28.

BẤT BIẾN TRUNG TÂM, và là lý do cả cơ chế này đáng tin:

    MỌI ví dụ đi vào prompt đều ĐÚNG LUẬT.

Đưa một bài sai luật vào làm mẫu là dạy mô hình sai — và kiểu hỏng đó không để lại
dấu vết nào: bài sinh ra vẫn bị vòng ngoài chặn, chỉ là chặn nhiều hơn, và không
ai biết nguyên nhân nằm ở ví dụ.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from adapters.persistence.corpus import JsonlPoemCorpus, duong_dan_mac_dinh
from application.poetry.dataset import MauTho, tu_ban_ghi, tu_khoa_yeu_cau
from application.poetry.fewshot import (
    chon_che_do,
    chon_vi_du,
    dung_khoi_vi_du,
)
from application.poetry.plan import KhoPlan, PoetryPlan
from application.poetry.requirement import PoetryRequirement, mac_dinh, nguoi_dung
from application.rule import kiem_tra_bai_tho

pytestmark = pytest.mark.unit

GOC = Path(__file__).resolve().parents[3]
TAP_TUYEN = GOC / "datalake" / "corpus_tuyen" / "tho_mau.jsonl"

BAI_DUNG_4_DONG = (
    "Chiều rơi chậm xuống mái rêu xanh\n"
    "Gió cuốn heo may lạc cuối ghềnh\n"
    "Một bóng con đò trôi lặng lẽ\n"
    "Sông dài ôm trọn mảnh trời xanh"
)
BAI_SAI_LUAT = "\n".join(["Một dòng sáu tiếng thôi mà"] * 4)


# ── Lược đồ chuẩn: KHÔNG tin nhãn trong dữ liệu ──────────────────────────────


def test_bai_dat_luat_thi_dung_duoc_MauTho():
    m = tu_ban_ghi({"id": 1, "tieu_de": "Chiều sông", "tho": BAI_DUNG_4_DONG})
    assert m is not None
    assert m.so_dong == 4
    assert m.the_tho == "that_ngon_tu_do"
    assert "chieu" in m.tu_khoa


def test_bai_SAI_luat_KHONG_dung_duoc_MauTho_du_nhan_noi_la_dat():
    """⛔ Ca quan trọng nhất của file này.

    Bản ghi tự nhận `trang_thai="dat"`, `thuoc_the=True`. Nếu `tu_ban_ghi` đọc nhãn
    thay vì chạy lại `rule.py` thì bài sai luật sẽ lọt vào kho mẫu.
    """
    m = tu_ban_ghi(
        {"id": 9, "tieu_de": "Giả mạo", "tho": BAI_SAI_LUAT,
         "trang_thai": "dat", "thuoc_the": True}
    )
    assert m is None, "nhãn trong dữ liệu KHÔNG được ghi đè phán quyết của rule.py"


def test_ban_ghi_rong_hoac_thieu_tho_thi_bo_qua():
    assert tu_ban_ghi({"id": 1}) is None
    assert tu_ban_ghi({"id": 1, "tho": "   "}) is None


# ── Tập tuyển phải commit được VÀ phải đúng luật ─────────────────────────────


def test_tap_tuyen_ton_tai_tren_checkout_sach():
    """Rủi ro R4: kho lớn bị gitignore, nên few-shot sẽ im lặng tắt trên máy mới."""
    assert TAP_TUYEN.exists(), (
        f"Thiếu {TAP_TUYEN.relative_to(GOC)} — chạy "
        "`python datalake/scripts/tuyen_tho_mau.py` để sinh lại."
    )


def test_MOI_bai_trong_tap_tuyen_deu_dung_luat():
    """⛔ Bất biến trung tâm, kiểm trên toàn bộ tệp thật."""
    hong: list[str] = []
    for dong in TAP_TUYEN.read_text(encoding="utf-8").splitlines():
        if not dong.strip():
            continue
        r = json.loads(dong)
        if not kiem_tra_bai_tho(r["tho"]).dat:
            hong.append(str(r.get("id")))
    assert not hong, f"{len(hong)} bài trong tập tuyển KHÔNG đạt luật: {hong[:10]}"


def test_tap_tuyen_du_nho_de_commit():
    kb = TAP_TUYEN.stat().st_size / 1024
    assert kb < 1024, f"tập tuyển {kb:.0f} KB — quá lớn để commit, giảm hạn ngạch"


def test_tap_tuyen_phu_du_cac_co_bai():
    """Bộ chọn ưu tiên cùng số dòng, nên kho phải có mặt các cỡ thường gặp."""
    co = set()
    for dong in TAP_TUYEN.read_text(encoding="utf-8").splitlines():
        if dong.strip():
            co.add(len([d for d in json.loads(dong)["tho"].splitlines() if d.strip()]))
    assert {4, 8, 12, 16} <= co, f"thiếu cỡ bài: {sorted({4, 8, 12, 16} - co)}"


# ── Adapter đọc kho ──────────────────────────────────────────────────────────


def test_adapter_nap_duoc_va_moi_bai_deu_dung_luat():
    kho = JsonlPoemCorpus(duong_dan_mac_dinh(GOC), gioi_han=50).tat_ca()
    assert kho, "kho rỗng — kiểm lại đường dẫn"
    for m in kho:
        assert kiem_tra_bai_tho(m.tho).dat, f"bài {m.id} trong kho KHÔNG đạt luật"


def test_khong_co_tep_nao_thi_kho_RONG_chu_khong_no():
    """§32: Retrieval Failure -> zero-shot, không phải sập."""
    kho = JsonlPoemCorpus((GOC / "khong" / "ton" / "tai.jsonl",)).tat_ca()
    assert kho == ()


def test_dong_hong_khong_lam_hong_ca_kho(tmp_path: Path):
    tep = tmp_path / "kho.jsonl"
    tep.write_text(
        "{khong phai json}\n"
        + json.dumps({"id": 1, "tieu_de": "x", "tho": BAI_DUNG_4_DONG}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    assert len(JsonlPoemCorpus((tep,)).tat_ca()) == 1


# ── Chọn chế độ: §26 · §27 · §28 ─────────────────────────────────────────────


def _req(**kw: object) -> PoetryRequirement:
    goc: dict[str, object] = {
        "chu_de": nguoi_dung("quê hương"),
        "so_dong": nguoi_dung(8),
        "cam_xuc": mac_dinh(None),
        "phong_cach": mac_dinh(None),
        "rang_buoc_van": mac_dinh(None),
        "rang_buoc_thanh": mac_dinh(None),
    }
    goc.update(kw)
    return PoetryRequirement(**goc)  # type: ignore[arg-type]


def test_khong_rang_buoc_rieng_thi_zero_shot():
    assert chon_che_do(_req()) == "zero_shot"


def test_mot_rang_buoc_thi_one_shot():
    assert chon_che_do(_req(cam_xuc=nguoi_dung("hoài niệm"))) == "one_shot"


def test_nhieu_rang_buoc_thi_few_shot():
    assert (
        chon_che_do(
            _req(cam_xuc=nguoi_dung("buồn"), phong_cach=nguoi_dung("cổ điển"))
        )
        == "few_shot"
    )


def test_mac_dinh_cua_he_thong_KHONG_tinh_la_rang_buoc_nguoi_dung():
    """Nếu tính, thì mọi yêu cầu đều thành few_shot và chế độ mất ý nghĩa."""
    assert chon_che_do(_req(cam_xuc=mac_dinh("trung tính"))) == "zero_shot"


# ── Chọn ví dụ ───────────────────────────────────────────────────────────────


def _kho_gia() -> tuple[MauTho, ...]:
    tam = [
        tu_ban_ghi({"id": "a", "tieu_de": "Chiều sông quê", "tho": BAI_DUNG_4_DONG}),
        tu_ban_ghi(
            {"id": "b", "tieu_de": "Tám dòng", "tho": BAI_DUNG_4_DONG + "\n" + BAI_DUNG_4_DONG}
        ),
    ]
    return tuple(m for m in tam if m is not None)


def test_zero_shot_thi_KHONG_dua_vi_du_nao():
    assert chon_vi_du(_kho_gia(), _req()) == ()


def test_one_shot_dua_dung_MOT_vi_du():
    vd = chon_vi_du(_kho_gia(), _req(chu_de=nguoi_dung("sông"), cam_xuc=nguoi_dung("lặng")))
    assert len(vd) <= 1


def test_uu_tien_bai_CUNG_SO_DONG_voi_ke_hoach():
    """Đối sách cho rủi ro R2: cổng 4 chặn 55,29% corpus, nên cấu trúc quan trọng
    hơn chủ đề khi chọn mẫu."""
    plan = PoetryPlan(kho=(KhoPlan(so_dong=4), KhoPlan(so_dong=4)))  # 8 dòng
    vd = chon_vi_du(
        _kho_gia(),
        _req(cam_xuc=nguoi_dung("buồn"), phong_cach=nguoi_dung("cổ điển")),
        ke_hoach=plan,
    )
    assert vd, "phải chọn được ví dụ"
    assert vd[0].mau.so_dong == 8
    assert any("cùng 8 dòng" in lr for lr in vd[0].ly_do)


def test_moi_vi_du_duoc_chon_deu_co_LY_DO():
    vd = chon_vi_du(_kho_gia(), _req(cam_xuc=nguoi_dung("lặng")))
    for v in vd:
        assert v.ly_do, "chọn ví dụ mà không giải thích được là không kiểm lại được"


def test_kho_RONG_thi_tra_rong_chu_khong_no():
    assert chon_vi_du((), _req(cam_xuc=nguoi_dung("buồn"))) == ()


def test_vi_du_khong_giong_gi_yeu_cau_thi_bi_loai():
    """Ví dụ 0 điểm chỉ tốn token và có thể kéo mô hình lệch hướng."""
    vd = chon_vi_du(
        _kho_gia(),
        _req(chu_de=nguoi_dung("tàu vũ trụ sao Hoả"), so_dong=nguoi_dung(100),
             cam_xuc=nguoi_dung("x"), phong_cach=nguoi_dung("y")),
    )
    assert vd == ()


def test_chon_vi_du_TAT_DINH():
    """Hai lần chạy trên cùng dữ liệu phải cho cùng một bộ ví dụ — nếu không thì
    không ai tái lập được một lần sinh thơ."""
    req = _req(cam_xuc=nguoi_dung("lặng"), phong_cach=nguoi_dung("cổ điển"))
    a = chon_vi_du(_kho_gia(), req)
    b = chon_vi_du(_kho_gia(), req)
    assert [x.mau.id for x in a] == [x.mau.id for x in b]


# ── Khối ví dụ đưa vào prompt ────────────────────────────────────────────────


def test_khoi_vi_du_giu_NGUYEN_BAI_va_ghi_id():
    vd = chon_vi_du(_kho_gia(), _req(cam_xuc=nguoi_dung("lặng")))
    khoi = dung_khoi_vi_du(vd)
    for v in vd:
        # Nguyên bài: cắt đôi bài mẫu là dạy một khuôn không tồn tại.
        assert v.mau.tho in khoi
        assert f"id={v.mau.id}" in khoi
    assert "KHÔNG chép lại" in khoi


def test_khoi_vi_du_rong_khi_khong_co_vi_du():
    assert dung_khoi_vi_du(()) == ""


def test_MOI_bai_trong_khoi_vi_du_deu_dung_luat():
    """⛔ Bất biến trung tâm, kiểm ở đúng chỗ văn bản đi vào prompt."""
    vd = chon_vi_du(
        JsonlPoemCorpus(duong_dan_mac_dinh(GOC), gioi_han=200).tat_ca(),
        _req(cam_xuc=nguoi_dung("buồn"), phong_cach=nguoi_dung("cổ điển")),
    )
    for v in vd:
        assert kiem_tra_bai_tho(v.mau.tho).dat


def test_tu_khoa_hai_ben_tach_cung_mot_cach():
    """Nếu hai bên tách khác nhau thì phép giao không bao giờ khớp."""
    m = tu_ban_ghi({"id": 1, "tieu_de": "Chiều sông", "tho": BAI_DUNG_4_DONG})
    assert m is not None
    assert tu_khoa_yeu_cau("chiều sông") & m.tu_khoa
