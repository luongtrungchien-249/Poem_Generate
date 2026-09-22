"""VÒNG NGOÀI — sinh, kiểm, và BẮT BUỘC soạn lại khi chưa đạt.

Vì sao có file này: prompt không phải là bảo đảm. Không mô hình nào đếm âm tiết
tiếng Việt đủ tin cậy để bảo đảm ràng buộc ở mọi dòng. Bảo đảm đến từ bộ kiểm tất
định đặt SAU bộ sinh, không đến từ câu chữ trong prompt.

HAI VÒNG, HAI THẨM QUYỀN
    Vòng trong (`generate_react_loop`)  mô hình tự chủ; nó CÓ THỂ gọi tool tự soi,
                                        cũng có thể không gọi, hoặc gọi rồi phớt lờ.
    Vòng ngoài (file này)               đường ống luôn chạy; mô hình KHÔNG bỏ qua được.

    Cùng một bộ kiểm, hai chỗ gọi. Vòng trong giúp sửa sớm cho rẻ; vòng ngoài là
    thứ bảo đảm không có bài sai lọt ra.

LUẬT BẤT DI BẤT DỊCH
    Bộ kiểm PHÁN, mô hình SỬA. Không dòng nào trong file này được sửa văn bản.
    Sửa bằng code là âm thầm thay đổi tác phẩm rồi ghi lại như thể mô hình viết ra
    như thế — cùng loại sai lầm với việc cắt bớt lời gọi tool rồi ghi lại như thể
    mô hình chỉ xin bấy nhiêu.

    Hết lượt thì KHÔNG trả bài sai. Không có "gần đúng".
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass

from application.pipeline.stages.generate import generate_react_loop
from application.ports.llm import (
    AssistantMessage,
    CallContext,
    LlmMessage,
    LlmPort,
    UserMessage,
)
from application.ports.rate_limit import RateLimitPort
from application.ports.tools import ToolPort
from application.ports.verifier import KetQuaKiemDinh, OutputSpec, OutputVerifier
from application.prompting.builder import wrap_xml_tag
from application.prompting.context import ContextEnvelope
from application.prompting.instructions import (
    CHI_DAN_SUA,
    THANG_LEO_THANG,
    ChienLuoc,
)
from domain.common.errors import BotError, BudgetExceeded, OutputKhongDat, UpstreamTimeout
from domain.common.result import Err, Ok, Result

# Thang leo thang. Không lặp lại cùng một cách sửa ba lần: nếu cách nhẹ không ăn,
# phải đổi cách chứ không phải xin lại y hệt.
#
# 🩸 LỖI ĐÃ SỬA 21/09/2026 — LEO THANG THEO SỐ LƯỢT, KHÔNG THEO BẰNG CHỨNG.
#
# Bản trước tính `_chien_luoc_cho_luot(luot + leo_them)`, nên SỐ LƯỢT tự nó đẩy
# thang lên. Với `max_repair_rounds=3` thì:
#
#     lượt 0 -> sua_dong        (sửa đúng dòng hỏng)
#     lượt 1 -> sinh_lai_kho
#     lượt 2 -> sinh_lai_ca_bai  <- "viết lại toàn bài từ đầu"
#
# Nghĩa là ngay ở lượt sửa THỨ HAI, hệ thống đã bảo mô hình vứt cả bài — kể cả
# những dòng đã đạt. Và đó thường là lúc bài chỉ còn 1–2 lỗi.
#
# Đo thật, gpt-4o-mini: vòng sửa CHỈ dùng `sua_dong` hội tụ 4/4 trong 0–2 lượt
# (số lỗi đi [1,0] · [1,1,0] · [2,0]). Cùng đường ống nhưng có leo thang theo
# lượt: 0–3/12. Leo thang đang phá đúng thứ nó định cứu.
#
# Nay thang CHỈ nhích khi có BẰNG CHỨNG là cách nhẹ không ăn — số lỗi không giảm
# hai lượt liên tiếp, hoặc mô hình trả lại đúng bài đã thấy. Số lượt không còn tự
# nó đẩy thang.
# `ChienLuoc`, `THANG_LEO_THANG` và chỉ dẫn từng bước nay ở `prompting/instructions.py`.
#
# Chúng từng nằm ngay đây, và `_CHI_DAN` còn là biến PRIVATE — nghĩa là chỉ dẫn
# quan trọng nhất của vòng sửa không nằm trong bất kỳ bản kiểm kê prompt nào, và
# không test nào về nội dung prompt chạm tới được.


@dataclass(frozen=True, slots=True)
class VerifiedOutput:
    """Đầu ra đã qua cổng. Tồn tại object này nghĩa là `ket_qua.dat` đúng."""

    text: str
    ket_qua: KetQuaKiemDinh
    so_luot: int
    chien_luoc_cuoi: ChienLuoc | None


def _bam(van_ban: str) -> str:
    """Băm văn bản đã chuẩn hoá, dùng cho chặn lặp G6."""
    chuan = " ".join(van_ban.split()).lower()
    return hashlib.sha256(chuan.encode("utf-8")).hexdigest()


def _chien_luoc_cho_luot(luot: int) -> ChienLuoc:
    return THANG_LEO_THANG[min(luot, len(THANG_LEO_THANG) - 1)]


def _dung_luot_sua(
    ban_nhap: str, ket_qua: KetQuaKiemDinh, chien_luoc: ChienLuoc
) -> tuple[LlmMessage, LlmMessage]:
    """Dựng cặp lượt hội thoại cho vòng sửa.

    Hai quy tắc kỹ thuật:
      - Bản nháp vào lượt `assistant`, biên bản vào lượt `user`. TUYỆT ĐỐI không
        đưa biên bản vào lượt `system`: trạng thái động không được mang thẩm quyền
        hệ thống.
      - Biên bản bọc thẻ XML để mô hình phân biệt được đâu là dữ liệu kiểm định,
        đâu là nội dung nó tự viết.
    """
    noi_dung = f"{ket_qua.bien_ban}\n\n{CHI_DAN_SUA[chien_luoc]}"
    return (
        AssistantMessage(content=ban_nhap),
        UserMessage(content=wrap_xml_tag("bien_ban_kiem_dinh", noi_dung)),
    )


def _chan_doan(ket_qua: KetQuaKiemDinh, so_luot: int) -> str:
    dong_loi = "; ".join(f"{e.dia_chi} {e.ma}: cần {e.ky_vong}, đang {e.thuc_te}" for e in ket_qua.loi)
    return f"Sau {so_luot} lượt sửa vẫn còn {len(ket_qua.loi)} lỗi cứng — {dong_loi}"


async def generate_with_verification(
    envelope: ContextEnvelope,
    spec: OutputSpec,
    verifier: OutputVerifier,
    llm: LlmPort,
    tools: ToolPort,
    rate_limiter: RateLimitPort,
    ctx: CallContext,
    *,
    max_repair_rounds: int = 3,
    timeout_sec: float = 60.0,
    should_stop_hook: Callable[[], bool] | None = None,
    default_model: str = "gpt-4o-mini",
) -> Result[VerifiedOutput, BotError]:
    """Sinh → kiểm → bắt buộc soạn lại. Bảy chặn cứng G1–G7, đánh số tại chỗ."""
    bat_dau = time.monotonic()
    messages: list[LlmMessage] = list(envelope.messages)

    ket_qua_cuoi: KetQuaKiemDinh | None = None
    ban_nhap_cuoi = ""
    chien_luoc_cuoi: ChienLuoc | None = None
    so_loi_truoc: int | None = None
    lan_khong_tien_bo = 0
    da_thay: set[str] = set()
    leo_them = 0

    # CHẶN G1: trần số lượt. Lượt 0 là lần sinh đầu, các lượt sau là lượt sửa.
    for luot in range(max_repair_rounds + 1):
        # CHẶN G2: deadline, kiểm ĐẦU mỗi lượt chứ không giữa chừng
        if time.monotonic() - bat_dau > timeout_sec:
            return Err(UpstreamTimeout(upstream="verify_output", timeout_sec=timeout_sec))

        # CHẶN G3: ngân sách ngày. Mỗi lượt sửa là một lần gọi model có tính tiền,
        # nên phải hỏi lại port mỗi lượt, không hỏi một lần rồi tin mãi.
        if not await rate_limiter.within_daily_budget(ctx.scope):
            return Err(BudgetExceeded(scope_name=ctx.scope.thread_id, limit=0, current=0))

        # CHẶN G4: cờ dừng của người dùng
        if should_stop_hook and should_stop_hook():
            return Err(
                OutputKhongDat(
                    ma_the=spec.ma_the,
                    so_luot_da_sua=luot,
                    chan_doan="Người dùng đã huỷ yêu cầu trước khi bài kịp đạt.",
                )
            )

        sinh = await generate_react_loop(
            envelope=ContextEnvelope(
                messages=tuple(messages),
                tokens_used=envelope.tokens_used,
                has_knowledge=envelope.has_knowledge,
            ),
            llm=llm,
            tools=tools,
            rate_limiter=rate_limiter,
            ctx=ctx,
            should_stop_hook=should_stop_hook,
            default_model=default_model,
        )
        # So khớp tagged union bằng `isinstance`, đúng quy ước của dự án: nó thu
        # hẹp kiểu ở CẢ HAI nhánh, còn TypeGuard (`is_ok`/`is_err`) chỉ thu hẹp ở
        # nhánh đúng nên dòng lấy `.value` phía sau vẫn không được kiểm kiểu.
        if isinstance(sinh, Err):
            return Err(sinh.error)

        ban_nhap = sinh.value
        ban_nhap_cuoi = ban_nhap
        ket_qua = verifier.kiem(ban_nhap, spec)
        ket_qua_cuoi = ket_qua

        if ket_qua.dat:
            return Ok(
                VerifiedOutput(
                    text=ban_nhap,
                    ket_qua=ket_qua,
                    so_luot=luot,
                    chien_luoc_cuoi=chien_luoc_cuoi,
                )
            )

        # CHẶN G5: không tiến bộ. Số lỗi phải GIẢM; đứng yên hai lượt liên tiếp
        # nghĩa là cách sửa hiện tại không ăn, phải leo thang chứ không xin lại.
        so_loi = len(ket_qua.loi)
        if so_loi_truoc is not None and so_loi >= so_loi_truoc:
            lan_khong_tien_bo += 1
            if lan_khong_tien_bo >= 2:
                leo_them += 1
                lan_khong_tien_bo = 0
        else:
            lan_khong_tien_bo = 0
        so_loi_truoc = so_loi

        # CHẶN G6: lặp. Mô hình trả lại đúng bài đã thấy nghĩa là nó đang kẹt;
        # xin lại lần nữa chỉ tốn tiền. Leo thang ngay.
        dau_van = _bam(ban_nhap)
        if dau_van in da_thay:
            leo_them += 1
        da_thay.add(dau_van)

        # CHỈ `leo_them` điều khiển thang. `luot` không còn góp vào — xem chú
        # thích ở `THANG_LEO_THANG`.
        chien_luoc_cuoi = _chien_luoc_cho_luot(leo_them)
        messages.extend(_dung_luot_sua(ban_nhap, ket_qua, chien_luoc_cuoi))

    # CHẶN G7: fail closed. Hết lượt thì KHÔNG trả bài sai — kể cả khi đã có văn
    # bản trông ổn. Trả lỗi có chẩn đoán để tầng trên nói thật với người dùng.
    assert ket_qua_cuoi is not None  # vòng chạy ít nhất một lượt
    _ = ban_nhap_cuoi  # giữ lại cho chẩn đoán; KHÔNG đưa vào đường trả về
    return Err(
        OutputKhongDat(
            ma_the=spec.ma_the,
            so_luot_da_sua=max_repair_rounds,
            chan_doan=_chan_doan(ket_qua_cuoi, max_repair_rounds),
        )
    )
