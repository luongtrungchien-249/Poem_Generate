"""ĐIỂM TUÂN THỦ LIÊN TỤC — Plan_PoeTone GĐ1.1, QĐ-P1 (ba số rời, không trọng số).

════ VÌ SAO CẦN ════

`kiem_tra_bai_tho` DỪNG ở tầng chặn đầu tiên. Nên `len(v.vi_pham)` chỉ đếm lỗi của
MỘT tầng: một ứng viên chết ở tầng 2 vì 1 dòng 8 tiếng có "1 vi phạm", còn một ứng
viên qua tầng 2 nhưng sai thanh ở 2 dòng có "2 vi phạm" — xếp theo số đó thì cái
thứ nhất trông gần đích hơn, dù nó chưa từng được kiểm thanh.

File này đo MỌI chiều độc lập với nhau, để so được hai ứng viên chết ở hai tầng
khác nhau.

════ RANH GIỚI THẨM QUYỀN ════

    `rule.py`    phán ĐẠT / TRƯỢT. Không gì ở đây thay được phán quyết đó.
    file này     chỉ MÔ TẢ khoảng cách tới đích, dùng để CHỌN giữa các ứng viên.

`rule.py` ĐÓNG BĂNG: chỉ gọi hàm công khai của nó, không viết lại phép đếm tiếng,
phép tách thanh hay phép suy vần. Test đối chiếu ghim: bài đạt luật thì mọi chiều
ở đây đều trọn vẹn.

════ BA SỐ RỜI, KHÔNG GỘP (QĐ-P1) ════

Trọng số 0,4 / 0,3 / 0,3 của PoeTone đo trên Songci Trung Quốc, không có nguồn cho
thể này. Gộp đòi trọng số, trọng số đòi người chốt. Để XẾP HẠNG thì không cần gộp:
`khoa_xep_hang` so theo thứ tự tầng, bằng SỐ NGUYÊN — số dòng phải viết lại.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.rule import cua_so_co_van_chan, dem_tieng, khuon_cua_dong, tach_tieng

SO_TIENG = 7
DONG_MOI_CUM = 4


@dataclass(frozen=True, slots=True)
class DiemTuanThu:
    """Khoảng cách tới đích, đo trên từng chiều riêng rẽ.

    `hinh_thuc`   H3 + H4: ≥ 4 dòng và số dòng là bội của 4
    `cau_truc`    tỉ lệ dòng đúng 7 tiếng                         (H1, H2)
    `thanh`       tỉ lệ dòng đúng 7 tiếng VÀ khớp khuôn bằng/trắc  (S2)
    `van`         1,0 nếu có ít nhất một cụm 4 dòng có vần chân, ngược lại 0,0 (S11)

    `van` là 0/1 chứ không phải tỉ lệ: tầng 5 đạt khi CÓ MỘT cụm như thế. Tỉ lệ cụm
    có vần sẽ cho bài đạt luật một điểm dưới 1 — tức là mô tả một luật không có.
    """

    so_dong: int
    hinh_thuc: bool
    cau_truc: float
    thanh: float
    van: float
    so_dong_can_sua: int

    @property
    def tron_ven(self) -> bool:
        return self.hinh_thuc and self.so_dong_can_sua == 0 and self.van == 1.0

    def khoa_xep_hang(self) -> tuple[int, int, int]:
        """Nhỏ hơn = gần đích hơn. Theo thứ tự tầng, không trọng số.

        Số dòng phải viết lại là thước đo chung của tầng 2 và tầng 4: dòng thiếu
        tiếng hay dòng sai thanh đều tốn đúng một lần viết lại dòng đó.
        """
        return (0 if self.hinh_thuc else 1, self.so_dong_can_sua, 0 if self.van else 1)


def _dong_khong_rong(van_ban: str) -> list[str]:
    return [d.strip() for d in van_ban.splitlines() if d.strip()]


def do_diem_tuan_thu(van_ban: str) -> DiemTuanThu:
    """THUẦN, TẤT ĐỊNH, không gọi mô hình. Bài rỗng được 0 ở mọi chiều."""
    dong = _dong_khong_rong(van_ban)
    n = len(dong)
    if n == 0:
        return DiemTuanThu(0, False, 0.0, 0.0, 0.0, 0)

    tieng = [tach_tieng(d) for d in dong]
    du_tieng = [dem_tieng(d) == SO_TIENG for d in dong]
    # `khuon_cua_dong` trả "bang" / "trac" / "pha" / "khong_xac_dinh" — KHÔNG trả None.
    khop = [khuon_cua_dong(t) in ("bang", "trac") for t in tieng]
    dong_tot = sum(d and k for d, k in zip(du_tieng, khop, strict=True))

    tieng_cuoi = tuple(t[-1] if t else "" for t in tieng)
    co_van = bool(cua_so_co_van_chan(tieng_cuoi))

    return DiemTuanThu(
        so_dong=n,
        hinh_thuc=n >= DONG_MOI_CUM and n % DONG_MOI_CUM == 0,
        cau_truc=sum(du_tieng) / n,
        thanh=dong_tot / n,
        van=1.0 if co_van else 0.0,
        so_dong_can_sua=n - dong_tot,
    )
