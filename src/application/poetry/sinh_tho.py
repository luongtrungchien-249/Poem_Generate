"""USE CASE SINH THƠ — nơi năm chỉ thị gặp nhau trên một đường đi.

    người dùng
        │
        ▼
    B1 CỔNG THÔNG TIN ĐẦY ĐỦ  (chỉ thị 5)  ──chưa đủ──► HỎI LẠI, dừng tại đây
        │ đủ
        ▼
    dựng chỉ dẫn + yêu cầu    (prompt.py)
        │
        ▼
    generate_with_verification (vòng ngoài đã có, 7 chặn cứng G1–G7)
        │  mỗi lượt gọi PoemVerifierDayDu:
        │     B2..B6  sáu bước suy luận   (chỉ thị 2)
        │     luật    rule.py ĐÓNG BĂNG   (chỉ thị 1)
        │     chất lượng + CoT            (chỉ thị 3)
        ▼
    Ok(DaSinhTho)  hoặc  Err(OutputKhongDat) — KHÔNG BAO GIỜ trả bài sai

VÌ SAO CỔNG B1 CHẠY Ở ĐÂY CHỨ KHÔNG CHỈ Ở TRONG VERIFIER. Verifier chạy SAU khi
đã gọi mô hình. Nếu chỉ dựa vào nó thì mỗi lần thiếu chủ đề, hệ thống vẫn tốn một
lượt gọi model rồi mới phát hiện là lẽ ra phải hỏi. Hỏi trước thì không tốn gì.

Verifier VẪN giữ bước B1 — hai nơi cùng kiểm là có chủ ý: đường này chặn sớm cho
rẻ, verifier chặn chắc cho đúng. Cùng một hàm `danh_gia_du_thong_tin`, nên không
có nguy cơ hai nơi hiểu khác nhau.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeAlias

from application.pipeline.stages.verify_output import generate_with_verification
from application.poetry.fewshot import chon_che_do, chon_vi_du, dung_khoi_vi_du
from application.poetry.plan import PoetryPlan
from application.poetry.planner import lap_ke_hoach_hop_le, mo_ta_ke_hoach_cho_mo_hinh
from application.poetry.prompt import dung_luot_yeu_cau
from application.poetry.requirement import (
    CanHoi,
    PoetryRequirement,
    danh_gia_du_thong_tin,
)
from application.poetry.sinh_theo_kho import SO_UNG_VIEN_MAC_DINH, sinh_tung_kho
from application.poetry.state import DauVetTrangThai
from application.poetry.verifier import BienBanDayDu, PoemVerifierDayDu
from application.ports.llm import CallContext, LlmPort, UserMessage
from application.ports.poem_corpus import PoemCorpusPort
from application.ports.rate_limit import RateLimitPort
from application.ports.tools import ToolPort
from application.ports.verifier import OutputSpec
from application.prompting.context import ContextEnvelope
from domain.common.errors import BotError
from domain.common.result import Err, Ok, Result

MA_THE = "that_ngon_tu_do"


@dataclass(frozen=True, slots=True)
class CanLamRo:
    """Chưa đủ thông tin. KHÔNG phải lỗi — là một bước hợp lệ của hội thoại."""

    cau_hoi: CanHoi
    duong_di: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DaSinhTho:
    """Bài đã qua cổng. Tồn tại object này nghĩa là `bien_ban.dat` đúng."""

    text: str
    bien_ban: BienBanDayDu
    so_luot: int
    chien_luoc_cuoi: str | None
    # Ghi lại mô hình đã NHÌN THẤY ví dụ nào. Khi chất lượng tụt, câu hỏi đầu tiên
    # là "nó học khuôn từ đâu" — không ghi thì không trả lời được.
    che_do_vi_du: str = "zero_shot"
    id_vi_du: tuple[str, ...] = ()
    # Bộ sinh nào cho ra bài này. Đo thật cho thấy hai đường có năng suất khác
    # nhau hàng chục lần, nên không ghi lại thì mọi số liệu về sau đều vô nghĩa.
    bo_sinh: str = "mot_lan"
    so_ung_vien_da_dung: int = 0
    ke_hoach: PoetryPlan | None = None
    # §31 — đường đi thật của yêu cầu này qua máy trạng thái. §23 đòi reviewer thấy
    # được lịch sử; không ghi thì sau sự cố không ai biết hệ thống đã đi qua đâu.
    duong_di: tuple[str, ...] = ()


KetQuaSinhTho: TypeAlias = CanLamRo | DaSinhTho


async def sinh_bai_tho(
    yeu_cau: PoetryRequirement,
    *,
    llm: LlmPort,
    tools: ToolPort,
    rate_limiter: RateLimitPort,
    ctx: CallContext,
    verifier: PoemVerifierDayDu | None = None,
    corpus: PoemCorpusPort | None = None,
    max_repair_rounds: int = 3,
    so_ung_vien_moi_kho: int = SO_UNG_VIEN_MAC_DINH,
    timeout_sec: float = 60.0,
    should_stop_hook: Callable[[], bool] | None = None,
    default_model: str = "gpt-4o-mini",
) -> Result[KetQuaSinhTho, BotError]:
    """Sinh một bài thơ đã qua luật, chất lượng và sáu bước suy luận."""
    vet = DauVetTrangThai()
    vet.chuyen("VALIDATED", "qua rào đầu vào")
    vet.chuyen("ANALYZING", "đọc yêu cầu đã chuẩn hoá")

    cong = danh_gia_du_thong_tin(yeu_cau)
    if isinstance(cong, CanHoi):
        # Chỉ thị 5: chưa đủ thông tin thì KHÔNG gọi mô hình. Không tốn một đồng.
        vet.chuyen("NEED_CLARIFICATION", f"ca {cong.ca}: {cong.ly_do}")
        vet.chuyen("WAIT_USER", "chờ người dùng trả lời")
        return Ok(CanLamRo(cau_hoi=cong, duong_di=vet.duong_di()))

    bo_kiem = verifier or PoemVerifierDayDu()
    spec = OutputSpec(
        ma_the=MA_THE,
        tham_so={
            "yeu_cau": yeu_cau,
            "chu_de": yeu_cau.chu_de.gia_tri if yeu_cau.chu_de.co_gia_tri else None,
            "so_dong": yeu_cau.so_dong_int,
        },
    )

    # §26–28. Kho vắng, hoặc không có ví dụ nào giống yêu cầu -> lùi về zero-shot,
    # đúng §32 *Retrieval Failure -> Zero-shot generation -> Verification*. Thiếu
    # ví dụ làm bài KHÓ HƠN, không làm hệ thống hỏng: vòng ngoài vẫn bảo đảm.
    che_do = chon_che_do(yeu_cau)
    if corpus:
        vet.chuyen("RESEARCHING", f"tra kho thơ mẫu, chế độ {che_do}")
    vi_du = chon_vi_du(corpus.tat_ca(), yeu_cau, che_do=che_do) if corpus else ()
    if not vi_du:
        # §32 Retrieval Failure -> zero-shot.
        che_do = "zero_shot"

    vet.chuyen("PLANNING", "lập kế hoạch tất định từ yêu cầu")
    ke_hoach = lap_ke_hoach_hop_le(yeu_cau)
    if ke_hoach is not None:
        # Kế hoạch vào `tham_so` để bước B3 đối chiếu bản nháp với nó.
        spec = OutputSpec(ma_the=spec.ma_the, tham_so={**spec.tham_so, "ke_hoach": ke_hoach})

    envelope = ContextEnvelope(
        messages=(
            UserMessage(
                content=dung_luot_yeu_cau(
                    yeu_cau,
                    dung_khoi_vi_du(vi_du),
                    mo_ta_ke_hoach_cho_mo_hinh(ke_hoach) if ke_hoach else "",
                )
            ),
        ),
        tokens_used=0,
        has_knowledge=bool(vi_du),
    )

    # ════ SINH TỪNG KHỔ TRƯỚC — xem `sinh_theo_kho.py` ════
    #
    # Đo thật: sinh cả bài một lần đạt ~10% (4 dòng) và ~0% (8–12 dòng), vì lỗi
    # thanh luật nhân lên theo số dòng (`pⁿ`). Sinh từng khổ 4 dòng rồi chọn trong
    # nhiều ứng viên cắt `n` xuống 4 ở mọi bài, đưa tỉ lệ lên hàng chục phần trăm.
    #
    # Chủ dự án đã chọn đánh đổi này: *"thời gian lấy nhiều nhưng thứ tôi cần là
    # thơ đúng luật"*.
    #
    # Thất bại ở đây KHÔNG phải lỗi: rơi xuống vòng sinh–kiểm–sửa cũ bên dưới.
    vet.chuyen("GENERATING", "sinh từng khổ, chọn trong nhiều ứng viên")
    bo_sinh = "mot_lan"
    da_dung = 0
    if so_ung_vien_moi_kho > 1:
        theo_kho = await sinh_tung_kho(
            yeu_cau,
            llm=llm,
            ctx=ctx,
            rate_limiter=rate_limiter,
            khoi_vi_du=dung_khoi_vi_du(vi_du),
            so_ung_vien=so_ung_vien_moi_kho,
            default_model=default_model,
        )
        if isinstance(theo_kho, Ok) and theo_kho.value.du_kho:
            da_dung = theo_kho.value.so_ung_vien_da_dung
            # Bài ghép xong VẪN đi qua cổng kiểm đầy đủ. Bộ sinh không có quyền
            # phán — nó chỉ đề nghị.
            bien_ban_kho = bo_kiem.lap_bien_ban(theo_kho.value.van_ban, spec)
            if bien_ban_kho.dat:
                vet.chuyen("VERIFYING", "kiểm bài ghép từ các khổ đã chọn")
                vet.chuyen("VERIFIED", "qua toàn bộ sáu bước suy luận")
                vet.chuyen("SAFETY_CHECK", "rào chắn đầu ra")
                return Ok(
                    DaSinhTho(
                        text=bien_ban_kho.van_ban_tho,
                        bien_ban=bien_ban_kho,
                        so_luot=0,
                        chien_luoc_cuoi=None,
                        che_do_vi_du=che_do,
                        id_vi_du=tuple(v.mau.id for v in vi_du),
                        ke_hoach=ke_hoach,
                        duong_di=(*vet.duong_di(), "FINAL_RESPONSE"),
                        bo_sinh="tung_kho",
                        so_ung_vien_da_dung=da_dung,
                    )
                )
        elif isinstance(theo_kho, Err):
            return Err(theo_kho.error)

    # ════ ĐƯỜNG LÙI: sinh cả bài rồi sửa ════
    kq = await generate_with_verification(
        envelope=envelope,
        spec=spec,
        verifier=bo_kiem,
        llm=llm,
        tools=tools,
        rate_limiter=rate_limiter,
        ctx=ctx,
        max_repair_rounds=max_repair_rounds,
        timeout_sec=timeout_sec,
        should_stop_hook=should_stop_hook,
        default_model=default_model,
    )
    if isinstance(kq, Err):
        return Err(kq.error)
    vet.chuyen("VERIFYING", "bài đã sinh, chạy bảy tầng + chất lượng")
    if kq.value.so_luot:
        vet.chuyen("REVISING", f"{kq.value.so_luot} lượt sửa")
        vet.chuyen("VERIFYING", "kiểm lại sau sửa")
    vet.chuyen("VERIFIED", "qua toàn bộ sáu bước suy luận")
    vet.chuyen("SAFETY_CHECK", "rào chắn đầu ra")

    ra = kq.value
    # Lập lại biên bản trên bản văn ĐÃ ĐẠT để lấy dấu vết đầy đủ cho response.
    # Rẻ (thuần, mili-giây) và tránh phải nhét dữ liệu riêng của thơ vào
    # `VerifiedOutput` — kiểu đó thuộc về đường ống chung, không thuộc về thể loại.
    bien_ban = bo_kiem.lap_bien_ban(ra.text, spec)
    return Ok(
        DaSinhTho(
            text=bien_ban.van_ban_tho,
            bien_ban=bien_ban,
            so_luot=ra.so_luot,
            chien_luoc_cuoi=ra.chien_luoc_cuoi,
            che_do_vi_du=che_do,
            id_vi_du=tuple(v.mau.id for v in vi_du),
            ke_hoach=ke_hoach,
            duong_di=(*vet.duong_di(), "FINAL_RESPONSE"),
            bo_sinh=bo_sinh,
            so_ung_vien_da_dung=da_dung,
        )
    )
