"""G12.2 — bộ đếm dùng chung giữa tiến trình · G13 — vòng đời khoá API.

Hai tính chất phải chứng minh, và cả hai đều từng SAI:

    1. Hai tiến trình cùng thấy MỘT bộ đếm — trước đây mỗi tiến trình một bản, nên
       chạy N worker thì hạn mức thực tế bị nhân N
    2. Thu hồi khoá có hiệu lực NGAY — trước đây phải restart, tức là khoá bị lộ
       vẫn dùng được tới lần deploy sau
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from adapters.persistence.sql import (
    SqlApiKeyStore,
    SqlRateLimiter,
    dung_dsn_sqlite,
    tao_bang,
    tao_engine,
)
from application.ports.rate_limit import Pass, Silent, Warn
from domain.conversation.thread import ThreadScope
from domain.policy.api_key import (
    BanGhiKhoa,
    KhoaHopLe,
    KhoaKhongHopLe,
    bam_khoa,
    kiem_khoa,
    sinh_khoa,
)

pytestmark = pytest.mark.unit

SCOPE = ThreadScope(platform="web", thread_id="t1")


async def _engine(duong_dan: Path):
    """Engine mới trên CÙNG một tệp — cách mô phỏng một tiến trình khác."""
    e = tao_engine(dung_dsn_sqlite(duong_dan))
    await tao_bang(e)
    return e


# ── G12.2 — bộ đếm dùng chung ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_HAI_TIEN_TRINH_cung_thay_MOT_bo_dem(tmp_path: Path):
    """⛔ Tính chất trung tâm của G12.2.

    Hai `SqlRateLimiter` khác nhau, hai engine khác nhau, cùng một tệp — đúng như
    hai uvicorn worker. Bộ đếm phải là MỘT.
    """
    tep = tmp_path / "rl.sqlite3"
    tien_trinh_1 = SqlRateLimiter(await _engine(tep), so_yeu_cau_moi_phut=3, nguong_canh_bao=99)
    tien_trinh_2 = SqlRateLimiter(await _engine(tep), so_yeu_cau_moi_phut=3, nguong_canh_bao=99)

    assert isinstance(await tien_trinh_1.check(SCOPE, "u1"), Pass)
    assert isinstance(await tien_trinh_2.check(SCOPE, "u1"), Pass)
    assert isinstance(await tien_trinh_1.check(SCOPE, "u1"), Pass)
    # Lượt thứ tư: nếu mỗi tiến trình đếm riêng thì lượt này vẫn qua.
    assert isinstance(await tien_trinh_2.check(SCOPE, "u1"), Silent), (
        "hai tiến trình đang đếm riêng — hạn mức bị nhân lên theo số worker"
    )


@pytest.mark.asyncio
async def test_ngan_sach_ngay_cung_dung_chung(tmp_path: Path):
    """`within_daily_budget` là chốt chặn CHI TIỀN — phải đếm trên một nguồn."""
    tep = tmp_path / "ns.sqlite3"
    a = SqlRateLimiter(await _engine(tep), so_lan_goi_model_moi_ngay=2)
    b = SqlRateLimiter(await _engine(tep), so_lan_goi_model_moi_ngay=2)

    assert await a.within_daily_budget(SCOPE) is True
    assert await b.within_daily_budget(SCOPE) is True
    assert await a.within_daily_budget(SCOPE) is False, "trần ngân sách bị nới ra"


@pytest.mark.asyncio
async def test_bo_dem_SONG_QUA_restart(tmp_path: Path):
    tep = tmp_path / "rs.sqlite3"
    truoc = SqlRateLimiter(await _engine(tep), so_lan_goi_model_moi_ngay=1)
    assert await truoc.within_daily_budget(SCOPE) is True
    del truoc

    sau = SqlRateLimiter(await _engine(tep), so_lan_goi_model_moi_ngay=1)
    assert await sau.within_daily_budget(SCOPE) is False, "restart làm reset hạn mức"


@pytest.mark.asyncio
async def test_hai_nguoi_dung_khac_nhau_dem_rieng(tmp_path: Path):
    rl = SqlRateLimiter(await _engine(tmp_path / "u.sqlite3"), so_yeu_cau_moi_phut=1)
    assert isinstance(await rl.check(SCOPE, "u1"), Pass)
    assert isinstance(await rl.check(SCOPE, "u2"), Pass), "hai người dùng bị gộp bộ đếm"


@pytest.mark.asyncio
async def test_canh_bao_truoc_khi_chan(tmp_path: Path):
    rl = SqlRateLimiter(
        await _engine(tmp_path / "w.sqlite3"), so_yeu_cau_moi_phut=3, nguong_canh_bao=2
    )
    assert isinstance(await rl.check(SCOPE, "u1"), Pass)
    assert isinstance(await rl.check(SCOPE, "u1"), Warn)


# ── G13 — luật thuần về vòng đời khoá ───────────────────────────────────────


def test_khoa_moi_sinh_ra_la_ngau_nhien_va_co_tien_to():
    a, b = sinh_khoa(), sinh_khoa()
    assert a != b
    assert a.startswith("sk_")
    assert len(a) > 20


def test_khoa_con_hieu_luc_thi_qua():
    br = BanGhiKhoa(bam="x", tenant_id="t1", ten="ứng dụng A")
    kq = kiem_khoa(br, bay_gio=time.time())
    assert isinstance(kq, KhoaHopLe)
    assert kq.tenant_id == "t1"


def test_khoa_khong_ton_tai():
    kq = kiem_khoa(None, bay_gio=time.time())
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "khong_ton_tai"


def test_khoa_da_het_han():
    br = BanGhiKhoa(bam="x", tenant_id="t1", het_han_luc=100.0)
    kq = kiem_khoa(br, bay_gio=200.0)
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "da_het_han"


def test_khoa_chua_het_han_thi_van_dung_duoc():
    br = BanGhiKhoa(bam="x", tenant_id="t1", het_han_luc=300.0)
    assert isinstance(kiem_khoa(br, bay_gio=200.0), KhoaHopLe)


def test_thu_hoi_UU_TIEN_hon_het_han():
    """Khoá vừa thu hồi vừa hết hạn phải báo là ĐÃ THU HỒI.

    Hai lý do dẫn tới hai hành động khác nhau khi truy vết.
    """
    br = BanGhiKhoa(bam="x", tenant_id="t1", het_han_luc=100.0, thu_hoi_luc=50.0)
    kq = kiem_khoa(br, bay_gio=200.0)
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "da_thu_hoi"


def test_het_han_None_nghia_la_KHONG_het_han():
    br = BanGhiKhoa(bam="x", tenant_id="t1", het_han_luc=None)
    assert isinstance(kiem_khoa(br, bay_gio=1e12), KhoaHopLe)


# ── G13 — kho khoá bền vững ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_phat_hanh_roi_tra_duoc(tmp_path: Path):
    kho = SqlApiKeyStore(await _engine(tmp_path / "k.sqlite3"))
    khoa = await kho.phat_hanh("cong_ty_a", ten="ứng dụng A")
    br = await kho.tra(bam_khoa(khoa))
    assert br is not None and br.tenant_id == "cong_ty_a"


@pytest.mark.asyncio
async def test_KHOA_NGUYEN_VAN_KHONG_duoc_luu(tmp_path: Path):
    """⛔ G13.4 — một bản sao lưu rò rỉ không được kéo theo mọi khoá.

    Đọc TOÀN BỘ byte trên đĩa mà vẫn không thấy khoá nguyên văn.

    🩸 BÀI HỌC TỪ CHÍNH TEST NÀY. Bản đầu chỉ đọc tệp `.sqlite3`, và khẳng định
    "không có khoá nguyên văn" ĐÚNG MỘT CÁCH RỖNG: ở chế độ WAL, dữ liệu vừa ghi
    nằm trong tệp `-wal` chứ chưa checkpoint sang tệp chính. Test xanh trong khi
    không kiểm gì cả.

    Phát hiện được là nhờ khẳng định ĐỐI CHỨNG (`phải lưu băm`) — nó đỏ, và đó là
    lý do một test phủ định luôn cần một đối chứng dương đi kèm. Không có nó thì
    test này sẽ xanh vĩnh viễn kể cả khi có ai đó chuyển sang lưu khoá nguyên văn.
    """
    tep = tmp_path / "bam.sqlite3"
    kho = SqlApiKeyStore(await _engine(tep))
    khoa = await kho.phat_hanh("cong_ty_a")

    # Gom mọi tệp SQLite sinh ra: .sqlite3, -wal, -shm. Sao lưu thì chép tất.
    noi_dung = b"".join(
        p.read_bytes() for p in tmp_path.iterdir() if p.is_file()
    )
    assert bam_khoa(khoa).encode() in noi_dung, "đối chứng: băm phải có mặt trên đĩa"
    assert khoa.encode() not in noi_dung, "khoá nguyên văn nằm trên đĩa"


@pytest.mark.asyncio
async def test_THU_HOI_co_hieu_luc_NGAY(tmp_path: Path):
    """⛔ Tính chất trung tâm của G13: không cần restart."""
    kho = SqlApiKeyStore(await _engine(tmp_path / "th.sqlite3"))
    khoa = await kho.phat_hanh("cong_ty_a")
    bam = bam_khoa(khoa)

    assert isinstance(kiem_khoa(await kho.tra(bam), bay_gio=time.time()), KhoaHopLe)
    assert await kho.thu_hoi(bam) is True
    kq = kiem_khoa(await kho.tra(bam), bay_gio=time.time())
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "da_thu_hoi"


@pytest.mark.asyncio
async def test_thu_hoi_hai_lan_khong_doi_dau_vet(tmp_path: Path):
    kho = SqlApiKeyStore(await _engine(tmp_path / "th2.sqlite3"))
    bam = bam_khoa(await kho.phat_hanh("t1"))
    assert await kho.thu_hoi(bam) is True
    assert await kho.thu_hoi(bam) is False, "lần hai không được ghi đè mốc thu hồi"


@pytest.mark.asyncio
async def test_khoa_song_qua_restart(tmp_path: Path):
    tep = tmp_path / "ks.sqlite3"
    khoa = await SqlApiKeyStore(await _engine(tep)).phat_hanh("cong_ty_a")
    br = await SqlApiKeyStore(await _engine(tep)).tra(bam_khoa(khoa))
    assert br is not None and br.tenant_id == "cong_ty_a"


@pytest.mark.asyncio
async def test_khoa_co_han_su_dung(tmp_path: Path):
    kho = SqlApiKeyStore(await _engine(tmp_path / "hh.sqlite3"))
    khoa = await kho.phat_hanh("t1", song_giay=-1)  # hết hạn ngay
    kq = kiem_khoa(await kho.tra(bam_khoa(khoa)), bay_gio=time.time())
    assert isinstance(kq, KhoaKhongHopLe) and kq.ly_do == "da_het_han"


@pytest.mark.asyncio
async def test_nap_tu_cau_hinh_khong_trung_lap(tmp_path: Path):
    kho = SqlApiKeyStore(await _engine(tmp_path / "nc.sqlite3"))
    assert await kho.nap_tu_cau_hinh({"k1": "t1", "k2": "t2"}) == 2
    assert await kho.nap_tu_cau_hinh({"k1": "t1", "k2": "t2"}) == 0, "nạp lại tạo bản trùng"
    br = await kho.tra(bam_khoa("k1"))
    assert br is not None and br.tenant_id == "t1"
