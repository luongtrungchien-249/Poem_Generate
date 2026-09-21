"""KIỂM SÁU BƯỚC SUY LUẬN CỦA AGENT — thi hành chỉ thị 2.

    *"chi tiết từng bước tạo thơ cần có kiểm tra từng bước suy luận của Agent và
    kiểm tra Output trước khi trả cho người dùng."*  — chủ dự án, 21/09/2026

Kiểm kết quả cuối là chưa đủ: một bài đúng luật vẫn có thể là bài mà Planner hoạch
định 8 dòng còn Writer viết 12 dòng — cả hai "đạt" phần của mình, kế hoạch bị bỏ
qua, và không ai biết. Vì vậy mỗi bước suy luận phải nộp bằng chứng riêng.

SÁU BƯỚC, TẤT CẢ ĐỀU CHẶN

    B1  YÊU CẦU            đủ thông tin chưa (chỉ thị 5)
    B2  KẾ HOẠCH           kế hoạch có hợp luật không
    B3  BẢN NHÁP ↔ KẾ HOẠCH bài viết ra có đúng bài đã hoạch định không
    B4  LUẬT               rule.py — ĐÓNG BĂNG, chỉ đọc phán quyết
    B5  CHẤT LƯỢNG         năm chiều đo được
    B6  TUYÊN BỐ           §19.4 — không khẳng định suông

BỐN QUY ƯỚC, sao chép đúng kỷ luật bảy tầng của `rule.py` — đọc một lần thì đọc
được cả sáu hàm:

    1. DỪNG Ở BƯỚC TRƯỢT ĐẦU TIÊN. Bước sau mang `da_chay=False`, nghĩa là CHƯA
       KIỂM — khác hẳn "đã kiểm và đạt".
    2. LUÔN NỘP BẰNG CHỨNG, kể cả khi đạt.
    3. GHI CÔNG KHAI ĐIỀU KHÔNG KIỂM ĐƯỢC, không lặng lẽ cho qua (N3).
    4. KHÔNG BƯỚC NÀO GỌI BƯỚC KHÁC. Thứ tự do `kiem_tra_chuoi_suy_luan` điều khiển.

B3 KHÔNG CÓ TRONG TÀI LIỆU ĐÍCH. Nó được thêm vào vì thiếu nó thì kế hoạch trở
thành trang trí — không gì buộc bản nháp phải theo.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from application.poetry.plan import PoetryPlan, kiem_tra_ke_hoach, mo_ta_ke_hoach
from application.poetry.quality import KetQuaChatLuong
from application.poetry.requirement import (
    CanHoi,
    PoetryRequirement,
    danh_gia_du_thong_tin,
)

# `rule.py` ĐÓNG BĂNG: chỉ đọc kiểu kết quả.
from application.rule import PoemVerdict
from domain.guardrails.output.verification_claim import check_verification_claim


@dataclass(frozen=True, slots=True)
class KetQuaBuoc:
    """Kết quả một bước, kèm bằng chứng người đọc kiểm lại được.

    `da_chay=False` nghĩa là bước này bị bỏ qua vì một bước trước đã chặn. Khi đó
    `dat` KHÔNG mang ý nghĩa gì.
    """

    ma: str
    ten: str
    da_chay: bool
    dat: bool
    bang_chung: str
    loi: tuple[str, ...] = ()
    chi_tiet: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class KetQuaSuyLuan:
    """Dấu vết sáu bước. `cau_hoi` khác None nghĩa là phải hỏi người dùng, không sinh thơ."""

    dat: bool
    buoc: tuple[KetQuaBuoc, ...]
    buoc_dung_lai: str | None
    cau_hoi: str | None = None


_TEN_BUOC: tuple[tuple[str, str], ...] = (
    ("B1", "Yêu cầu đầy đủ"),
    ("B2", "Kế hoạch hợp luật"),
    ("B3", "Bản nháp khớp kế hoạch"),
    ("B4", "Luật thơ"),
    ("B5", "Chất lượng"),
    ("B6", "Tuyên bố có bằng chứng"),
)


def _bo_qua(ma: str, ten: str, buoc_chan: str) -> KetQuaBuoc:
    return KetQuaBuoc(
        ma=ma, ten=ten, da_chay=False, dat=False,
        bang_chung=f"bỏ qua vì bước {buoc_chan} đã chặn",
    )


def _b1_yeu_cau(req: PoetryRequirement | None) -> KetQuaBuoc:
    """B1 — chỉ thị 5. Không có yêu cầu thì KHÔNG coi là đạt."""
    if req is None:
        return KetQuaBuoc(
            ma="B1", ten="Yêu cầu đầy đủ", da_chay=True, dat=False,
            bang_chung="không có PoetryRequirement — không thể xác nhận đã đủ thông tin",
            loi=("thiếu yêu cầu đã chuẩn hoá",),
        )
    kq = danh_gia_du_thong_tin(req)
    if isinstance(kq, CanHoi):
        return KetQuaBuoc(
            ma="B1", ten="Yêu cầu đầy đủ", da_chay=True, dat=False,
            bang_chung=f"chưa đủ thông tin (ca {kq.ca}): {kq.ly_do}",
            loi=(kq.cau_hoi,),
            chi_tiet={"ca": kq.ca, "cau_hoi": kq.cau_hoi, "truong_thieu": list(kq.truong_thieu)},
        )
    return KetQuaBuoc(
        ma="B1", ten="Yêu cầu đầy đủ", da_chay=True, dat=True,
        bang_chung=kq.bang_chung,
        chi_tiet={"nguon_tung_truong": {t: v.nguon for t, v in req.cac_truong()}},
    )


def _b2_ke_hoach(plan: PoetryPlan | None, so_dong_yeu_cau: int | None) -> KetQuaBuoc:
    """B2 — kế hoạch phải hợp luật TRƯỚC khi tốn một lượt gọi mô hình."""
    if plan is None:
        return KetQuaBuoc(
            ma="B2", ten="Kế hoạch hợp luật", da_chay=True, dat=True,
            bang_chung="không có kế hoạch — bỏ qua, đường sinh trực tiếp không bắt buộc lập kế hoạch",
            chi_tiet={"B2_khong_ap_dung": "chỉ kiểm khi Planner có chạy"},
        )
    loi = kiem_tra_ke_hoach(plan, so_dong_yeu_cau)
    return KetQuaBuoc(
        ma="B2", ten="Kế hoạch hợp luật", da_chay=True, dat=not loi,
        bang_chung=(
            mo_ta_ke_hoach(plan) if not loi
            else f"{len(loi)} lỗi kế hoạch: "
                 + "; ".join(f"{e.ma} {e.cho}: cần {e.ky_vong}, đang {e.thuc_te}" for e in loi)
        ),
        loi=tuple(f"{e.ma} {e.cho}: cần {e.ky_vong}, đang {e.thuc_te}" for e in loi),
        chi_tiet={"tong_so_dong": plan.tong_so_dong, "so_kho": len(plan.kho)},
    )


def _b3_nhap_khop_ke_hoach(plan: PoetryPlan | None, v: PoemVerdict) -> KetQuaBuoc:
    """B3 — bước tài liệu đích không có. Thiếu nó thì kế hoạch chỉ là trang trí."""
    if plan is None or not plan.kho:
        return KetQuaBuoc(
            ma="B3", ten="Bản nháp khớp kế hoạch", da_chay=True, dat=True,
            bang_chung="không có kế hoạch để đối chiếu",
            chi_tiet={"B3_khong_ap_dung": "chỉ kiểm khi Planner có chạy"},
        )
    # 🩸 LỖI ĐÃ SỬA 21/09/2026 — B3 từng chặn cả khi SỐ KHỔ lệch kế hoạch.
    #
    # Sai, và sai theo đúng kiểu mà nguyên tắc N2 cấm. S18 nói *"Có thể viết liên
    # hoàn, không chia khổ"* — chia khổ là một QUYỀN của tác giả, không phải nghĩa
    # vụ. Một bài 8 dòng liền mạch và một bài 8 dòng chia hai khổ đều hợp lệ như
    # nhau, nên đánh trượt bài liền mạch là trượt vì tác giả dùng đúng cái quyền
    # tài liệu cho phép.
    #
    # Test hợp đồng `test_bai_dat_thi_200_kem_du_bang_chung_bay_tang` bắt được:
    # kế hoạch đề 2 khổ, mô hình viết 8 dòng liền, API trả 422 cho một bài hoàn
    # toàn đúng luật.
    #
    # B3 vì vậy CHỈ kiểm TỔNG SỐ DÒNG — con số đó do H4 và người dùng quyết, không
    # phải phong cách. Cách chia khổ chỉ được GHI NHẬN vào bằng chứng.
    loi: list[str] = []
    if v.so_dong != plan.tong_so_dong:
        loi.append(f"kế hoạch {plan.tong_so_dong} dòng, bản nháp {v.so_dong} dòng")

    ghi_chu_kho = (
        ""
        if v.so_kho == len(plan.kho)
        else f"; chia {v.so_kho} khổ thay vì {len(plan.kho)} — được phép theo S18"
    )
    return KetQuaBuoc(
        ma="B3", ten="Bản nháp khớp kế hoạch", da_chay=True, dat=not loi,
        bang_chung=(
            f"bản nháp {v.so_dong} dòng — khớp kế hoạch{ghi_chu_kho}" if not loi
            else "; ".join(loi)
        ),
        loi=tuple(loi),
        chi_tiet={
            "so_kho_ke_hoach": len(plan.kho),
            "so_kho_ban_nhap": v.so_kho,
            "S18_chia_kho_la_quyen": "không dùng số khổ làm tiêu chí chặn (N2)",
        },
    )


def _b4_luat(v: PoemVerdict) -> KetQuaBuoc:
    """B4 — ĐỌC phán quyết của `rule.py`. Không diễn giải lại, không ghi đè."""
    tang_chay = [t for t in v.tang if t.da_chay]
    return KetQuaBuoc(
        ma="B4", ten="Luật thơ", da_chay=True, dat=v.dat,
        bang_chung=(
            f"qua {len(tang_chay)}/7 tầng" + (
                "" if v.dat else f", dừng ở tầng {v.tang_dung_lai}"
            )
            + " — " + "; ".join(f"T{t.so}: {t.bang_chung}" for t in tang_chay[-2:])
        ),
        loi=tuple(
            f"{vp.ma} {'D' + str(vp.dong) if vp.dong else 'toàn bài'}: "
            f"cần {vp.ky_vong}, đang {vp.thuc_te}"
            for vp in v.vi_pham
        ),
        chi_tiet={
            "thuoc_the": v.thuoc_the,
            "tang_dung_lai": v.tang_dung_lai,
            "bang_chung_tung_tang": [
                {"tang": t.so, "ten": t.ten, "da_chay": t.da_chay, "dat": t.dat,
                 "bang_chung": t.bang_chung}
                for t in v.tang
            ],
            "nguon": "application/rule.py — ĐÓNG BĂNG, chỉ đọc",
        },
    )


def _b5_chat_luong(kq: KetQuaChatLuong) -> KetQuaBuoc:
    """B5 — chuẩn DỰ ÁN. Không bao giờ đụng `thuoc_the`."""
    hong = kq.chieu_hong
    return KetQuaBuoc(
        ma="B5", ten="Chất lượng", da_chay=True, dat=kq.dat,
        bang_chung=(
            f"{sum(1 for c in kq.chieu if c.do_duoc)} chiều đo được, tất cả đạt" if kq.dat
            else f"{len(hong)} chiều chưa đạt: "
                 + "; ".join(f"{c.ten} = {c.so_do} (cần {c.nguong})" for c in hong)
        ),
        loi=tuple(f"CL {c.ten}: cần {c.nguong}, đang {c.so_do}" for c in hong),
        chi_tiet={
            "chieu_khong_do_duoc": list(kq.chieu_khong_do_duoc),
            "canh_bao": "chất lượng KHÔNG loại bài khỏi thể",
        },
    )


def _b6_tuyen_bo(van_ban: str, v: PoemVerdict) -> KetQuaBuoc:
    """B6 — §19.4. Bằng chứng luôn có ở đây vì B4 đã chạy."""
    kq = check_verification_claim(van_ban, has_evidence=True, verdict_passed=v.dat)
    return KetQuaBuoc(
        ma="B6", ten="Tuyên bố có bằng chứng", da_chay=True, dat=kq.allowed,
        bang_chung=kq.reason,
        loi=() if kq.allowed else tuple(f'tuyên bố không có căn cứ: "{c}"' for c in kq.claims_found),
        chi_tiet={"tuyen_bo_tim_thay": list(kq.claims_found)},
    )


def kiem_tra_chuoi_suy_luan(
    *,
    van_ban: str,
    verdict: PoemVerdict,
    chat_luong: KetQuaChatLuong,
    yeu_cau: PoetryRequirement | None = None,
    ke_hoach: PoetryPlan | None = None,
) -> KetQuaSuyLuan:
    """Chạy TUẦN TỰ sáu bước, dừng ở bước trượt đầu tiên.

    Dừng sớm không phải để nhanh mà để đúng: chấm chất lượng một bài chưa đủ 7 tiếng
    mỗi dòng là chấm một thứ chưa tồn tại.
    """
    so_dong_yc = yeu_cau.so_dong_int if yeu_cau else None

    ket_qua: list[KetQuaBuoc] = []
    dung_lai: str | None = None

    thu_tu = (
        lambda: _b1_yeu_cau(yeu_cau),
        lambda: _b2_ke_hoach(ke_hoach, so_dong_yc),
        lambda: _b3_nhap_khop_ke_hoach(ke_hoach, verdict),
        lambda: _b4_luat(verdict),
        lambda: _b5_chat_luong(chat_luong),
        lambda: _b6_tuyen_bo(van_ban, verdict),
    )
    for lam in thu_tu:
        kq = lam()
        ket_qua.append(kq)
        if not kq.dat:
            dung_lai = kq.ma
            break

    for ma, ten in _TEN_BUOC[len(ket_qua):]:
        ket_qua.append(_bo_qua(ma, ten, dung_lai or "?"))

    cau_hoi: str | None = None
    if dung_lai == "B1":
        chi_tiet = ket_qua[0].chi_tiet
        hoi = chi_tiet.get("cau_hoi")
        cau_hoi = hoi if isinstance(hoi, str) else None

    return KetQuaSuyLuan(
        dat=all(b.dat for b in ket_qua),
        buoc=tuple(ket_qua),
        buoc_dung_lai=dung_lai,
        cau_hoi=cau_hoi,
    )
