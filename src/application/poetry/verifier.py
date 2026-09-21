"""CỔNG CHẶN ĐẦU RA ĐẦY ĐỦ — luật + chất lượng + Chain-of-thought.

Hiện thực `OutputVerifier`, cắm thẳng vào `verify_output.generate_with_verification`
đã có. Nhờ đó toàn bộ bảy chặn cứng G1–G7 của vòng ngoài (trần lượt, deadline, ngân
sách, cờ huỷ, phát hiện không tiến bộ, phát hiện lặp, fail-closed) áp dụng luôn cho
cả phần chất lượng mà không phải viết lại vòng lặp nào.

════ HAI CỜ, CỐ Ý KHÔNG GỘP ════

    dat_luat        rule.py phán — ĐÓNG BĂNG, không ai được ghi đè
    dat_chat_luong  chuẩn dự án phán
    dat             cả hai — cờ duy nhất được phép chặn việc TRẢ RA

Một bài `dat_luat=True, dat_chat_luong=False` vẫn là thơ thất ngôn tự do hợp lệ.
Nó chỉ chưa đủ tốt để gửi đi. Báo cáo phải nói đúng như vậy, không được nói nó sai luật.

════ THỨ TỰ BIÊN BẢN ════

Luật trượt  -> biên bản có địa chỉ dòng, KHÔNG kèm CoT (lỗi đã có địa chỉ).
Chất lượng  -> khung CoT bốn ô (lỗi khuếch tán, phải suy luận mới sửa được).
Cả hai      -> biên bản luật TRƯỚC. Sửa cái có địa chỉ trước, đó là cái rẻ.

LUẬT BẤT DI BẤT DỊCH: không dòng nào trong file này được sửa văn bản thơ.
"""

from __future__ import annotations

from dataclasses import dataclass

from application.poem_verifier import MA_THE, dung_bien_ban
from application.poetry.cot import can_bat_cot, dung_khung_suy_luan, tach_tho_khoi_khung
from application.poetry.plan import PoetryPlan
from application.poetry.quality import (
    KetQuaChatLuong,
    danh_gia_chat_luong,
    mo_ta_chat_luong,
)
from application.poetry.reasoning import KetQuaSuyLuan, kiem_tra_chuoi_suy_luan
from application.poetry.requirement import PoetryRequirement
from application.ports.verifier import KetQuaKiemDinh, LoiKiemDinh, OutputSpec
from application.rule import PoemVerdict, kiem_tra_bai_tho


@dataclass(frozen=True, slots=True)
class BienBanDayDu:
    """Dấu vết đầy đủ một lần kiểm — thứ đi vào response cho người dùng."""

    dat: bool
    dat_luat: bool
    dat_chat_luong: bool
    verdict: PoemVerdict
    chat_luong: KetQuaChatLuong
    suy_luan: KetQuaSuyLuan
    van_ban_tho: str


class PoemVerifierDayDu:
    """`OutputVerifier` gộp luật và chất lượng, bật CoT khi cần.

    Đồng bộ và thuần — chỉ gọi `rule.kiem_tra_bai_tho` và các hàm chấm thuần, không
    I/O. Vì vậy vòng sửa gọi bao nhiêu lần cũng được, và test chạy trong mili-giây.

    `spec.tham_so` nhận thêm ba khoá so với `PoemVerifier` gốc:
        `chu_de`     str          — để chấm CL3
        `yeu_cau`    PoetryRequirement
        `ke_hoach`   PoetryPlan
    Tham số lạ bị bỏ qua, đúng hợp đồng của `OutputSpec`.
    """

    ma_the = MA_THE

    def __init__(self, *, bat_cot: bool = True) -> None:
        # `bat_cot=False` dùng cho ca đối chiếu: đo xem CoT có thực sự giúp hội tụ
        # nhanh hơn không. Không phải cờ tắt chất lượng.
        self.bat_cot = bat_cot

    # ---- phần dùng chung cho cả cổng chặn lẫn báo cáo -----------------------

    def lap_bien_ban(self, van_ban: str, spec: OutputSpec) -> BienBanDayDu:
        """Chạy đủ luật + chất lượng + sáu bước suy luận, trả dấu vết đầy đủ."""
        tham = spec.tham_so
        # Mô hình có thể trả kèm khung CoT. Gỡ ra trước khi đếm tiếng: để nguyên thì
        # mấy dòng chẩn đoán bị đem đi kiểm H1 và bài nào cũng trượt.
        tho = tach_tho_khoi_khung(van_ban)

        v = kiem_tra_bai_tho(tho)

        chu_de = tham.get("chu_de")
        yeu_cau = tham.get("yeu_cau")
        ke_hoach = tham.get("ke_hoach")

        cl = danh_gia_chat_luong(v, chu_de=chu_de if isinstance(chu_de, str) else None)
        sl = kiem_tra_chuoi_suy_luan(
            van_ban=tho,
            verdict=v,
            chat_luong=cl,
            yeu_cau=yeu_cau if isinstance(yeu_cau, PoetryRequirement) else None,
            ke_hoach=ke_hoach if isinstance(ke_hoach, PoetryPlan) else None,
        )
        return BienBanDayDu(
            dat=sl.dat,
            dat_luat=v.dat,
            dat_chat_luong=cl.dat,
            verdict=v,
            chat_luong=cl,
            suy_luan=sl,
            van_ban_tho=tho,
        )

    # ---- hợp đồng OutputVerifier -------------------------------------------

    def kiem(self, van_ban: str, spec: OutputSpec) -> KetQuaKiemDinh:
        bb = self.lap_bien_ban(van_ban, spec)
        v, cl, sl = bb.verdict, bb.chat_luong, bb.suy_luan

        loi: list[LoiKiemDinh] = []

        # Lỗi LUẬT giữ nguyên mã H/S của tài liệu luật.
        for vp in v.vi_pham:
            loi.append(
                LoiKiemDinh(
                    ma=vp.ma,
                    dia_chi=f"D{vp.dong}" if vp.dong is not None else "toàn bài",
                    ky_vong=vp.ky_vong, thuc_te=vp.thuc_te, goi_y=vp.goi_y,
                )
            )

        # Lỗi CHẤT LƯỢNG mang mã CL* để KHÔNG lẫn với mã luật. Người đọc biên bản
        # phải phân biệt được ngay "sai luật" với "chưa đủ tốt".
        for c in cl.chieu_hong:
            loi.append(
                LoiKiemDinh(
                    ma=c.ma, dia_chi="toàn bài",
                    ky_vong=f"{c.ten} {c.nguong}", thuc_te=f"{c.so_do}",
                    goi_y="Đây là chuẩn chất lượng của dự án, KHÔNG phải luật thơ — "
                          "bài vẫn thuộc thể thất ngôn tự do.",
                )
            )

        # Lỗi SUY LUẬN (B1, B2, B3, B6) — những bước không sinh ra lỗi luật hay
        # chất lượng nhưng vẫn chặn.
        for b in sl.buoc:
            if b.da_chay and not b.dat and b.ma in ("B1", "B2", "B3", "B6"):
                for m in b.loi:
                    loi.append(
                        LoiKiemDinh(
                            ma=b.ma, dia_chi="quy trình",
                            ky_vong=b.ten, thuc_te=m,
                            goi_y="Bước suy luận này chặn; sửa ở đúng bước đó, không sửa bài.",
                        )
                    )

        return KetQuaKiemDinh(
            dat=sl.dat,
            loi=tuple(loi),
            bien_ban=self._dung_bien_ban(bb),
            mo_ta_mem=self._mo_ta_mem(bb),
        )

    # ---- biên bản ------------------------------------------------------------

    def _dung_bien_ban(self, bb: BienBanDayDu) -> str:
        if bb.dat:
            return ""

        khuc: list[str] = []

        # 1. Bước quy trình chặn TRƯỚC cả luật — không có gì để sửa trong bài cả.
        if bb.suy_luan.buoc_dung_lai in ("B1", "B2"):
            b = next(x for x in bb.suy_luan.buoc if x.ma == bb.suy_luan.buoc_dung_lai)
            khuc.append(f"Chưa thể sinh thơ — dừng ở bước {b.ma} ({b.ten}).")
            khuc.append(f"   | {b.bang_chung}")
            for m in b.loi:
                khuc.append(f"   | {m}")
            return "\n".join(khuc)

        # 2. Luật trượt -> biên bản có địa chỉ dòng. KHÔNG kèm CoT.
        if not bb.dat_luat:
            khuc.append(dung_bien_ban(bb.verdict))

        # 3. Bản nháp lệch kế hoạch.
        if bb.suy_luan.buoc_dung_lai == "B3":
            b = next(x for x in bb.suy_luan.buoc if x.ma == "B3")
            khuc.append("")
            khuc.append(f"Bản nháp không khớp kế hoạch: {b.bang_chung}")

        # 4. Tuyên bố suông.
        if bb.suy_luan.buoc_dung_lai == "B6":
            b = next(x for x in bb.suy_luan.buoc if x.ma == "B6")
            khuc.append("")
            khuc.append(f"Bỏ lời khẳng định về tính đúng luật: {b.bang_chung}")
            khuc.append("   | Chỉ trả bài thơ. Hệ thống tự đính kèm bằng chứng kiểm định.")

        # 5. Chất lượng trượt -> BẬT CoT (chỉ thị 3).
        if bb.dat_luat and not bb.dat_chat_luong and self.bat_cot:
            hong = {c.ma for c in bb.chat_luong.chieu_hong}
            if can_bat_cot(dat_luat=bb.dat_luat, dat_chat_luong=bb.dat_chat_luong):
                khuc.append("")
                khuc.append(
                    dung_khung_suy_luan(
                        bb.chat_luong,
                        dong_dat=tuple(d.so for d in bb.verdict.dong),
                    )
                )
                khuc.append(f"(chiều chưa đạt: {', '.join(sorted(hong))})")
        elif not bb.dat_chat_luong:
            khuc.append("")
            khuc.append(
                "Chất lượng chưa đạt: "
                + "; ".join(f"{c.ten} = {c.so_do} (cần {c.nguong})" for c in bb.chat_luong.chieu_hong)
            )

        return "\n".join(k for k in khuc if k is not None).strip()

    def _mo_ta_mem(self, bb: BienBanDayDu) -> tuple[str, ...]:
        """Số liệu tham khảo. Không mục nào ở đây được phép chặn đầu ra."""
        v = bb.verdict
        ra = [
            f"{v.so_dong} dòng / {v.so_kho} khổ",
            f"thuộc thể (H1–H4): {v.thuoc_the}",
            f"đúng luật (bảy tầng): {v.dat}",
            f"đạt chất lượng (chuẩn dự án): {bb.dat_chat_luong}",
            f"sơ đồ vần: {' | '.join(''.join(k) for k in v.so_do_van_theo_kho)}",
        ]
        ra.extend(mo_ta_chat_luong(bb.chat_luong))
        ra.extend(v.ghi_chu)
        return tuple(ra)
