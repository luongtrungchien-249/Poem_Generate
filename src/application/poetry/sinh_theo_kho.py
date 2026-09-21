"""SINH TỪNG KHỔ, CHỌN TRONG NHIỀU ỨNG VIÊN — phá phép toán `pⁿ`.

    *"thời gian suy nghĩ lấy nhiều thời gian nhưng thứ tôi cần chính là chất lượng
    của thơ cần đúng luật"*  — chủ dự án, 21/09/2026

════ PHÉP TOÁN PHẢI PHÁ ════

Đo thật (`docs/Do_That_21-09_R2.md`): mỗi DÒNG khớp khuôn thanh với xác suất
`p ≈ 0,56`. Một bài `n` dòng sinh một lần đạt với xác suất `pⁿ`:

    4 dòng   0,56⁴ ≈ 10%    <- khớp 2/20 đo được
    8 dòng   0,56⁸ ≈  1%    <- khớp 0/10
    12 dòng  0,56¹² ≈ 0,1%  <- khớp 0/10

`p` không sửa được: nó là giới hạn ngữ âm của mô hình, đã bác bỏ bằng bốn giả
thuyết (prompt, biên bản, tool, mô hình mạnh hơn).

Nhưng `n` thì cắt được. Sinh từng khổ 4 dòng và chọn trong `k` ứng viên:

    P(một khổ đạt)  = 1 − (1 − 0,10)^k
    P(cả bài đạt)   = P(một khổ)^(n/4)

    k = 16, bài 12 dòng:  (1 − 0,9¹⁶)³ ≈ 0,81³ ≈ **53%**
    k = 32, bài 12 dòng:  (1 − 0,9³²)³ ≈ 0,97³ ≈ **91%**

Đổi 0,1% lấy ~91%, trả bằng thời gian và tiền — đúng đánh đổi chủ dự án đã chọn.

════ ĐIỀU NÀY CÓ VI PHẠM P2 KHÔNG ════

    P2: *"Bộ kiểm PHÁN, mô hình SỬA. Không hàm nào được sửa văn bản thơ."*

Không. **Mô hình viết từng chữ của mọi ứng viên**, và viết khổ sau khi đã đọc các
khổ trước — nên mạch thơ là của nó, không phải của phép ghép. Hệ thống chỉ làm hai
việc: hỏi lại, và **chọn** ứng viên nào qua được luật.

Chọn không phải sửa. Đây đúng là thứ mà kiến trúc verification-first mở ra: khi có
bộ kiểm tất định, sinh nhiều rồi lọc là cách rẻ nhất để đổi tính toán lấy độ tin cậy.

════ HAI BẤT BIẾN KHÔNG ĐƯỢC PHÁ ════

1. **Khổ được nhận phải giữ CẢ BÀI hợp luật**, không chỉ riêng khổ đó. Kiểm trên
   toàn bộ phần đã tích luỹ, không kiểm rời từng khổ — nếu không thì ghép xong cả
   bài có thể hỏng ở chỗ vắt qua ranh giới khổ.

2. **Bài ghép xong VẪN đi qua cổng kiểm đầy đủ.** Hàm này chỉ là bộ SINH; quyền
   phán vẫn ở `PoemVerifierDayDu`. Không có đường tắt nào.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from application.poetry.prompt import dung_luot_yeu_cau
from application.poetry.requirement import PoetryRequirement
from application.ports.llm import CallContext, LlmPort, UserMessage
from application.ports.rate_limit import RateLimitPort
from application.prompting.builder import wrap_xml_tag
from application.prompting.instructions import CHI_DAN_VIET_TIEP_KHO
from application.rule import kiem_tra_bai_tho
from domain.common.errors import BotError, BudgetExceeded
from domain.common.result import Err, Ok, Result

DONG_MOI_KHO = 4

# Số ứng viên mỗi khổ. 16 cho ~81% mỗi khổ theo phép toán ở docstring.
#
# KHÔNG phải ngưỡng dò được: nó là một tham số ĐÁNH ĐỔI, và công thức để chọn nó
# nằm ngay trên. Muốn chắc hơn thì tăng, và biết trước mình trả bằng gì.
SO_UNG_VIEN_MAC_DINH = 16

# Số ứng viên gửi đi cùng lúc. Gửi cả 16 một lượt thì dễ chạm giới hạn tần suất
# của nhà cung cấp; gửi từng cái thì chậm gấp 16 lần.
SO_SONG_SONG = 8


@dataclass(frozen=True, slots=True)
class KetQuaSinhKho:
    """Kết quả sinh từng khổ. `van_ban` rỗng khi không khổ nào đạt."""

    van_ban: str
    so_kho_dat: int
    so_kho_can: int
    so_ung_vien_da_dung: int

    @property
    def du_kho(self) -> bool:
        return self.so_kho_dat == self.so_kho_can


def _loi_nhac_khuon(da_co: list[str]) -> str:
    """Nhắc lại phần đã viết để mô hình giữ mạch và giữ vần.

    Đưa vào lượt `user` chứ không phải `system`: đây là trạng thái động của một lần
    sinh cụ thể, và trạng thái động không được mang thẩm quyền hệ thống.
    """
    if not da_co:
        return ""
    return wrap_xml_tag(
        "phan_da_viet",
        "\n".join(da_co) + "\n\n" + CHI_DAN_VIET_TIEP_KHO,
    )


async def sinh_tung_kho(
    yeu_cau: PoetryRequirement,
    *,
    llm: LlmPort,
    ctx: CallContext,
    rate_limiter: RateLimitPort | None = None,
    khoi_vi_du: str = "",
    so_ung_vien: int = SO_UNG_VIEN_MAC_DINH,
    default_model: str = "gpt-4o-mini",
) -> Result[KetQuaSinhKho, BotError]:
    """Sinh bài theo từng khổ 4 dòng, mỗi khổ chọn trong `so_ung_vien` ứng viên.

    Trả `Ok` cả khi KHÔNG đủ khổ — `KetQuaSinhKho.du_kho` nói rõ. Không ném lỗi ở
    đây vì thiếu khổ chưa phải hỏng: tầng trên còn vòng sửa để chạy tiếp.
    """
    n = yeu_cau.so_dong_int or DONG_MOI_KHO
    so_kho_can = max(1, n // DONG_MOI_KHO)
    da_co: list[str] = []
    da_dung = 0

    for _ in range(so_kho_can):
        # Hỏi lại ngân sách ở MỖI khổ. Mỗi khổ là `so_ung_vien` lần gọi có tính
        # tiền, nên hỏi một lần ở đầu rồi tin mãi là bỏ ngỏ chốt chặn chi phí.
        if rate_limiter and not await rate_limiter.within_daily_budget(ctx.scope):
            return Err(BudgetExceeded(scope_name=ctx.scope.thread_id, limit=0, current=0))

        loi_nhac = dung_luot_yeu_cau(yeu_cau, khoi_vi_du) + "\n" + _loi_nhac_khuon(da_co)
        nhan = await _chon_mot_kho(
            loi_nhac, da_co, llm=llm, ctx=ctx,
            so_ung_vien=so_ung_vien, default_model=default_model,
        )
        da_dung += nhan[1]
        if nhan[0] is None:
            break
        da_co.extend(nhan[0])

    return Ok(
        KetQuaSinhKho(
            van_ban="\n".join(da_co),
            so_kho_dat=len(da_co) // DONG_MOI_KHO,
            so_kho_can=so_kho_can,
            so_ung_vien_da_dung=da_dung,
        )
    )


async def _chon_mot_kho(
    loi_nhac: str,
    da_co: list[str],
    *,
    llm: LlmPort,
    ctx: CallContext,
    so_ung_vien: int,
    default_model: str,
) -> tuple[list[str] | None, int]:
    """Sinh ứng viên theo đợt, nhận ứng viên ĐẦU TIÊN giữ được cả bài hợp luật.

    Dừng ngay khi có ứng viên đạt — không sinh nốt đợt còn lại. Với ~10% mỗi ứng
    viên thì phần lớn trường hợp chỉ tốn một đợt.
    """
    da_dung = 0
    for dau in range(0, so_ung_vien, SO_SONG_SONG):
        con = min(SO_SONG_SONG, so_ung_vien - dau)
        tra_loi = await asyncio.gather(
            *[
                llm.reply(
                    messages=(UserMessage(content=loi_nhac),),
                    tools=(),
                    ctx=ctx,
                    model=default_model,
                )
                for _ in range(con)
            ]
        )
        da_dung += con

        for r in tra_loi:
            if isinstance(r, Err):
                continue
            dong = _lay_bon_dong(r.value.text)
            if dong is None:
                continue
            # ⛔ Kiểm trên TOÀN BỘ phần đã tích luỹ, không kiểm riêng khổ này.
            # Kiểm rời thì lỗi vắt qua ranh giới khổ sẽ chỉ lộ ra khi đã ghép xong.
            if kiem_tra_bai_tho("\n".join(da_co + dong)).dat:
                return dong, da_dung
    return None, da_dung


def _lay_bon_dong(van_ban: str) -> list[str] | None:
    """Lấy đúng 4 dòng thơ từ câu trả lời.

    Mô hình hay kèm lời dẫn hoặc viết dư. Lấy 4 dòng KHÔNG RỖNG đầu tiên; ít hơn 4
    thì bỏ ứng viên — cắt ghép cho đủ là bắt đầu sửa văn bản thơ, điều P2 cấm.
    """
    dong = [d.strip() for d in van_ban.strip().splitlines() if d.strip()]
    return dong[:DONG_MOI_KHO] if len(dong) >= DONG_MOI_KHO else None
