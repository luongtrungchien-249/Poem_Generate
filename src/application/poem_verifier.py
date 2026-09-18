"""Nối `rule.py` vào cổng kiểm định tổng quát, và dựng biên bản gửi lại mô hình.

Phân vai:
    `rule.py`        biết LUẬT THƠ, không biết có mô hình nào trên đời
    file này         dịch phán quyết của luật sang ngôn ngữ của vòng sửa
    `verify_output`  điều khiển vòng sửa, không biết thơ là gì

Nhờ tách ba vai này, thay thể loại khác chỉ cần viết một file tương đương file này.
"""

from __future__ import annotations

from collections.abc import Mapping

from application.ports.verifier import (
    KetQuaKiemDinh,
    LoiKiemDinh,
    OutputSpec,
)
from application.rule import PoemVerdict, kiem_tra_bai_tho, mo_ta_luat

MA_THE = "that_ngon_tu_do"


def _dia_chi(dong: int | None) -> str:
    return f"D{dong}" if dong is not None else "toàn bài"


def dung_bien_ban(v: PoemVerdict) -> str:
    """Dựng biên bản kiểm định để gửi lại mô hình.

    Ba tính chất bắt buộc, rút ra từ các kiểu hỏng đã biết của vòng tự sửa:

    1. CÓ ĐỊA CHỈ. "Sai rồi, viết lại đi" gần như vô dụng; "D3 thừa 1 tiếng" thì
       mô hình sửa được ngay.
    2. GHIM DÒNG ĐÃ ĐẠT. Không ghim thì mô hình hay viết lại cả bài và làm hỏng
       dòng đang đúng — vòng sửa quay vòng mà không hội tụ.
    3. KHÔNG GỢI Ý CÂU CHỮ. Bộ kiểm phán, mô hình sửa. Đưa sẵn câu thay thế là
       bộ kiểm đang viết thơ hộ.
    """
    if v.dat:
        return ""

    khuc: list[str] = [f"Bài chưa đạt. {len(v.vi_pham)} lỗi cứng."]

    for vp in v.vi_pham:
        bc = next((d for d in v.dong if d.so == vp.dong), None)
        khuc.append("")
        if bc is not None:
            khuc.append(f'{_dia_chi(vp.dong)} | "{bc.van_ban}"')
        else:
            khuc.append(f"{_dia_chi(vp.dong)} |")
        khuc.append(f"   | {mo_ta_luat(vp.ma)}")
        khuc.append(f"   | cần {vp.ky_vong}, đang có {vp.thuc_te}")
        khuc.append(f"   | {vp.goi_y}")

    dong_hong = {vp.dong for vp in v.vi_pham if vp.dong is not None}
    dong_dat = [d.so for d in v.dong if d.so not in dong_hong]
    if dong_dat and dong_hong:
        ds_dat = " ".join(f"D{i}" for i in dong_dat)
        ds_hong = " ".join(f"D{i}" for i in sorted(dong_hong))
        khuc.append("")
        khuc.append(f"Các dòng {ds_dat} đã đạt — GIỮ NGUYÊN, không sửa.")
        khuc.append(f"Chỉ viết lại {ds_hong}.")

    return "\n".join(khuc)


def _mo_ta_mem(v: PoemVerdict) -> tuple[str, ...]:
    """Số liệu tham khảo. Không mục nào trong đây được phép chặn đầu ra (§9 Bước 4)."""
    ra = [
        f"{v.so_dong} dòng / {v.so_kho} khổ",
        f"sơ đồ vần: {' | '.join(''.join(k) for k in v.so_do_van_theo_kho)}",
        f"phối khuôn từng khổ (§4.3): {' | '.join(v.phoi_khuon_theo_kho)}",
        f"tỷ lệ dòng theo khuôn luân phiên: {v.ty_le_theo_khuon}",
    ]
    if v.van_lung:
        vi_tri = ", ".join(f"D{d}/P{p}" for d, p in v.van_lung)
        ra.append(f"vần lưng (S7): {vi_tri}")
    ra.extend(v.ghi_chu)
    return tuple(ra)


class PoemVerifier:
    """Hiện thực `OutputVerifier` cho thể thất ngôn tự do.

    Đồng bộ và thuần: chỉ gọi `rule.kiem_tra_bai_tho`, không I/O. Vì vậy vòng sửa
    gọi nó bao nhiêu lần cũng được, và test chạy trong mili-giây.
    """

    ma_the = MA_THE

    def kiem(self, van_ban: str, spec: OutputSpec) -> KetQuaKiemDinh:
        v = kiem_tra_bai_tho(van_ban)

        loi = tuple(
            LoiKiemDinh(
                ma=vp.ma,
                dia_chi=_dia_chi(vp.dong),
                ky_vong=vp.ky_vong,
                thuc_te=vp.thuc_te,
                goi_y=vp.goi_y,
            )
            for vp in v.vi_pham
        )

        loi = loi + _kiem_so_dong_mong_muon(v, spec.tham_so)

        return KetQuaKiemDinh(
            dat=not loi,
            loi=loi,
            bien_ban=dung_bien_ban(v) if not v.dat else _bien_ban_so_dong(loi),
            mo_ta_mem=_mo_ta_mem(v),
        )


def _kiem_so_dong_mong_muon(
    v: PoemVerdict, tham_so: Mapping[str, object]
) -> tuple[LoiKiemDinh, ...]:
    """Số dòng do NGƯỜI DÙNG yêu cầu, không phải do thể loại quy định.

    F5 nói rõ thể này không giới hạn số dòng, nên đây không phải luật thơ. Nhưng
    nếu người dùng xin 8 dòng mà nhận 4 thì yêu cầu vẫn chưa được đáp ứng, nên nó
    vẫn là ràng buộc cứng — chỉ khác nguồn gốc. Mã lỗi đặt riêng là "YC1" để không
    lẫn với các mã H của tài liệu luật.
    """
    mong_muon = tham_so.get("so_dong")
    if not isinstance(mong_muon, int) or mong_muon <= 0 or v.so_dong == mong_muon:
        return ()
    return (
        LoiKiemDinh(
            ma="YC1",
            dia_chi="toàn bài",
            ky_vong=f"{mong_muon} dòng (người dùng yêu cầu)",
            thuc_te=f"{v.so_dong} dòng",
            goi_y=(
                f"thêm {mong_muon - v.so_dong} dòng"
                if mong_muon > v.so_dong
                else f"bớt {v.so_dong - mong_muon} dòng"
            ),
        ),
    )


def _bien_ban_so_dong(loi: tuple[LoiKiemDinh, ...]) -> str:
    """Biên bản cho trường hợp thơ đúng luật nhưng chưa đúng yêu cầu người dùng."""
    if not loi:
        return ""
    khuc = ["Bài đúng luật thất ngôn tự do nhưng chưa đúng yêu cầu."]
    for e in loi:
        khuc.append("")
        khuc.append(f"{e.dia_chi} | cần {e.ky_vong}, đang có {e.thuc_te}")
        khuc.append(f"   | {e.goi_y}")
        khuc.append("   | Các dòng hiện có đều đúng 7 tiếng — GIỮ NGUYÊN.")
    return "\n".join(khuc)
