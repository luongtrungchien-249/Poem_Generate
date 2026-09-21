"""Rào chắn luồng SSE — ghim lỗ hổng `stream=true` bỏ qua output rails.

Tính chất phải chứng minh: **không có mẩu nào đi ra mà chưa qua rào**, kể cả khi
mẫu nhạy cảm bị cắt đôi giữa hai chunk — đó chính là ca mà một bộ lọc ngây thơ
(lọc từng chunk độc lập) sẽ bỏ sót.
"""

from __future__ import annotations

import pytest

from domain.guardrails.output.streaming import (
    CUA_SO_GIU_LAI_MAC_DINH,
    Chan,
    PhatRa,
    StreamingOutputGuard,
)

pytestmark = pytest.mark.unit


def _chay(guard: StreamingOutputGuard, chunks: list[str]) -> tuple[str, Chan | None]:
    """Chạy hết luồng, trả (văn bản đã phát, lý do chặn nếu có)."""
    ra: list[str] = []
    for c in chunks:
        kq = guard.nap(c)
        if isinstance(kq, Chan):
            return "".join(ra), kq
        ra.append(kq.text)
    cuoi = guard.ket_thuc()
    if isinstance(cuoi, Chan):
        return "".join(ra), cuoi
    ra.append(cuoi.text)
    return "".join(ra), None


# ── Ca thuận ──────────────────────────────────────────────────────────────────


def test_van_ban_sach_di_ra_nguyen_ven():
    g = StreamingOutputGuard()
    goc = "Chiều rơi chậm xuống mái rêu xanh, gió cuốn heo may lạc cuối ghềnh."
    ra, chan = _chay(g, list(goc))
    assert chan is None
    assert ra == goc, "văn bản sạch không được bị sửa"


def test_khong_mat_chu_nao_du_chia_chunk_kieu_gi():
    goc = "Một dòng thơ bình thường không có gì nhạy cảm cả."
    for kich_thuoc in (1, 3, 7, 50, 1000):
        g = StreamingOutputGuard()
        chunks = [goc[i : i + kich_thuoc] for i in range(0, len(goc), kich_thuoc)]
        ra, chan = _chay(g, chunks)
        assert chan is None
        assert ra == goc, f"mất chữ khi chunk cỡ {kich_thuoc}"


# ── Tính chất cốt lõi: mẫu bị cắt đôi vẫn bị bắt ─────────────────────────────


def test_email_bi_cat_doi_giua_hai_chunk_VAN_bi_che():
    """🔴 Ca mà bộ lọc từng-chunk-độc-lập sẽ bỏ sót.

    Không mẩu nào chứa trọn email, nên lọc riêng từng mẩu thì không thấy gì cả.
    Cửa sổ giữ lại tồn tại đúng vì ca này.
    """
    g = StreamingOutputGuard()
    ra, chan = _chay(g, ["Liên hệ nguyen@vi", "du.com nhé bạn"])
    assert chan is None
    assert "nguyen@vidu.com" not in ra, "email lọt qua rào"
    assert "[REDACTED_EMAIL]" in ra


def test_so_dien_thoai_bi_cat_doi_VAN_bi_che():
    g = StreamingOutputGuard()
    ra, chan = _chay(g, ["Gọi số 0912", "345678 nhé"])
    assert chan is None
    assert "0912345678" not in ra
    assert "[REDACTED_PHONE]" in ra


def test_the_tin_dung_bi_cat_thanh_bon_manh_VAN_bi_che():
    g = StreamingOutputGuard()
    ra, chan = _chay(g, ["Thẻ ", "4111 ", "1111 ", "1111 ", "1111 hết"])
    assert chan is None
    assert "4111 1111 1111 1111" not in ra
    assert "[REDACTED_CARD]" in ra


def test_doc_to_bi_chan_va_KHONG_phat_them_gi_nua():
    """Fail closed giữa luồng: chặn rồi thì mọi lần nạp sau đều bị từ chối."""
    g = StreamingOutputGuard()
    kq = g.nap("Câu trả lời là đồ ngu")
    assert isinstance(kq, Chan), "độc tố phải chặn ngay khi phát hiện"
    assert g.da_chan
    assert isinstance(g.nap("thêm chữ"), Chan), "chặn rồi thì không nạp thêm được"
    assert isinstance(g.ket_thuc(), Chan), "chặn rồi thì không xả nốt được"


def test_doc_to_bi_cat_doi_giua_hai_chunk_VAN_bi_chan():
    """Cùng lý do với PII: độc tố kiểm trên toàn bộ văn bản tích luỹ, không kiểm
    từng mẩu rời."""
    g = StreamingOutputGuard()
    a = g.nap("Câu trả lời là đồ ")
    assert isinstance(a, PhatRa)
    b = g.nap("ngu thật")
    assert isinstance(b, Chan)


def test_doc_to_chan_TRUOC_khi_chu_kip_di_ra():
    """Cửa sổ giữ lại có tác dụng phụ quan trọng: lúc độc tố lộ ra thì phần chứa
    nó vẫn còn đang bị giữ, nên chưa có byte nào đi tới người dùng."""
    g = StreamingOutputGuard()
    da_phat: list[str] = []
    for mau in ["Xin chào bạn. ", "Câu trả lời là ", "đồ ngu"]:
        kq = g.nap(mau)
        if isinstance(kq, Chan):
            break
        da_phat.append(kq.text)
    assert g.da_chan
    assert "đồ ngu" not in "".join(da_phat)


# ── Cửa sổ giữ lại: hành vi và giới hạn ──────────────────────────────────────


def test_giu_lai_du_cua_so_truoc_khi_phat():
    """Chữ đầu tiên chỉ ra sau khi đã tích đủ quá cửa sổ — đó là cái giá đã biết."""
    g = StreamingOutputGuard(cua_so_giu_lai=10)
    assert g.nap("12345").text == ""
    assert g.nap("67890").text == ""
    assert g.nap("A").text == "1"


def test_cua_so_bang_0_thi_phat_ngay_nhung_mat_kha_nang_bat_mau_cat_doi():
    """Ghim ĐÁNH ĐỔI, không ghim một con số 'đúng'.

    Cửa sổ 0 = độ trễ 0 = mẫu vắt qua ranh giới không bắt được nữa. Ai chỉnh
    `cua_so_giu_lai` xuống phải thấy test này và biết mình đang đánh đổi cái gì.
    """
    g = StreamingOutputGuard(cua_so_giu_lai=0)
    ra, chan = _chay(g, ["Liên hệ nguyen@vi", "du.com nhé"])
    # Nửa đầu đã đi ra trước khi mẫu hoàn tất -> guard chặn phần còn lại.
    assert chan is not None or "nguyen@vidu.com" not in ra


def test_cua_so_mac_dinh_dai_hon_moi_mau_PII_hien_co():
    """Nếu ai thêm một mẫu PII dài hơn cửa sổ, test này là chỗ nhắc tăng cửa sổ."""
    mau_dai_nhat = len("4111 1111 1111 1111")  # thẻ có dấu cách
    assert mau_dai_nhat * 2 < CUA_SO_GIU_LAI_MAC_DINH


def test_toan_van_giu_ca_phan_chua_phat():
    g = StreamingOutputGuard(cua_so_giu_lai=100)
    g.nap("một hai ba")
    assert g.toan_van == "một hai ba"


def test_trich_dan_bia_ra_duoc_bao_cao_nhung_KHONG_chan():
    """Trích dẫn sai là lỗi chất lượng, không phải lỗi an toàn — và ở luồng thì
    chặn ở cuối cũng đã muộn."""
    g = StreamingOutputGuard(valid_chunk_ids=["doc_1"])
    ra, chan = _chay(g, ["Theo tài liệu [doc_999] thì như vậy."])
    assert chan is None, "trích dẫn bịa KHÔNG được chặn luồng"
    assert "doc_999" in g.kiem_trich_dan()
