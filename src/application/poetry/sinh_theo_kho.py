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
import re
from dataclasses import dataclass

from application.pipeline.stages.generate import generate_react_loop
from application.pipeline.stages.verify_output import co_dang_bai_tho
from application.poem_verifier import dung_bien_ban
from application.poetry.diem_tuan_thu import do_diem_tuan_thu
from application.poetry.doi_chieu_chep import tim_dong_chep
from application.poetry.prompt import dung_luot_yeu_cau
from application.poetry.requirement import PoetryRequirement
from application.ports.chi_muc_tho import ChiMucDongThoPort
from application.ports.llm import CallContext, LlmPort, UserMessage
from application.ports.rate_limit import Pass, RateLimitOutcome, RateLimitPort
from application.ports.tools import ToolPort
from application.prompting.builder import wrap_xml_tag
from application.prompting.context import ContextEnvelope
from application.prompting.system import (
    CHI_DAN_NHIEU_UNG_VIEN,
    CHI_DAN_TU_SOI,
    CHI_DAN_VIET_TIEP_KHO,
)
from application.rule import kiem_tra_bai_tho
from domain.common.errors import BotError, BudgetExceeded
from domain.common.result import Err, Ok, Result
from domain.conversation.thread import ThreadScope

DONG_MOI_KHO = 4

# Số ứng viên mỗi khổ.
#
# KHÔNG phải ngưỡng dò được: nó là một tham số ĐÁNH ĐỔI, và công thức để chọn nó
# nằm ngay trên. Muốn chắc hơn thì tăng, và biết trước mình trả bằng gì.
#
# ════ 16 -> 32, chủ dự án chốt 22/09/2026 ════
#
# Theo đúng phép toán ở docstring đầu file, với p = 0,56 đo được:
#
#     k = 16   mỗi khổ ~81%   bài 20 dòng  0,81^5 = 35%
#     k = 32   mỗi khổ ~97%   bài 20 dòng  0,97^5 = 86%
#
# Trả bằng gấp đôi số lượt gọi. Đây là đánh đổi chủ dự án đã chọn từ 21/09:
# *"thời gian lấy nhiều cũng được, thứ tôi cần là thơ đúng luật"*.
#
# ⚠️ CON SỐ TRÊN MƯỢN `p` CỦA MỘT MÔ HÌNH KHÁC. p = 0,56 đo trên `gpt-4o-mini`.
# Với Gemma hay bất kỳ model nào khác, PHẢI ĐO LẠI `p` trước khi tin hai dòng
# trên — và nếu `p` thấp hơn hẳn thì kết luận đúng là đổi model, không phải tăng
# tiếp 32 -> 64. Bộ đo: `datalake/scripts/do_ab_prompt.py`.
SO_UNG_VIEN_MAC_DINH = 32

# Số ứng viên gửi đi cùng lúc. Gửi cả một đợt lớn thì dễ chạm giới hạn tần suất
# của nhà cung cấp; gửi từng cái thì chậm gấp `SO_UNG_VIEN_MAC_DINH` lần.
#
# ⚠️ CHẠM TRẦN TẦN SUẤT THÌ HẠ HẰNG SỐ NÀY, ĐỪNG HẠ SỐ ỨNG VIÊN. Số ứng viên mới
# là thứ quyết định tỉ lệ đạt; số song song chỉ quyết định nhanh hay chậm. Hạ nhầm
# cái là đổi chất lượng lấy tốc độ mà tưởng mình đang né lỗi 429.
#
# Hạn mức miễn phí của Google AI thường chỉ vài chục lượt/phút, mà một bài 20 dòng
# nay có thể tốn tới 5 khổ × 32 ứng viên. Đo hạn mức thật trước khi chạy lô lớn.
# Nay đọc được từ cấu hình: `SO_SONG_SONG` trong `.env` (bootstrap/settings.py), và
# tham số `so_song_song` của `sinh_tung_kho` / `sinh_bai_tho`. Hằng số này là mặc định.
SO_SONG_SONG = 8

# Số phương án xin trong MỘT lượt gọi (22/09/2026, nhập từ `compare_prompt.py`).
#
# Vì sao là một số NHỎ chứ không gộp cả đợt: `_chon_mot_kho` dừng sớm ngay khi có
# ứng viên đạt. Gộp cả 16 vào một lượt thì mất dừng sớm — luôn trả tiền cho đủ 16.
# Số nhỏ giữ được dừng sớm ở mức đợt, mà vẫn ép các phương án trong cùng một lượt
# phải khác nhau (mô hình thấy được bản nó vừa viết).
#
# 1 = tắt hẳn, quay về đúng hành vi trước 22/09. Giữ lối tắt đó để đối chiếu A/B
# mà không phải gỡ mã.
SO_UNG_VIEN_MOI_LUOT = 4


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
    tools: ToolPort | None = None,
    chi_muc_chep: ChiMucDongThoPort | None = None,
    so_song_song: int = SO_SONG_SONG,
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
            tools=tools, rate_limiter=rate_limiter, chi_muc_chep=chi_muc_chep,
            so_song_song=so_song_song,
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
    tools: ToolPort | None = None,
    rate_limiter: RateLimitPort | None = None,
    chi_muc_chep: ChiMucDongThoPort | None = None,
    so_song_song: int = SO_SONG_SONG,
) -> tuple[list[str] | None, int]:
    """Sinh ứng viên theo đợt, nhận ứng viên ĐẦU TIÊN giữ được cả bài hợp luật.

    Dừng ngay khi có ứng viên đạt — không sinh nốt đợt còn lại. Với ~10% mỗi ứng
    viên thì phần lớn trường hợp chỉ tốn một đợt.

    Hết ứng viên mà chưa cái nào đạt thì KHÔNG bỏ cuộc ngay: chạy một vòng ReAct
    trên ứng viên hụt ít nhất, để mô hình tự soi bằng tool rồi sửa. Xem
    `_cuu_kho_bang_react`.
    """
    da_dung = 0
    # Ứng viên hụt ít nhất từ trước tới giờ, kèm khoá xếp hạng. Dùng cho bước cứu.
    gan_nhat: tuple[list[str], tuple[int, int, int]] | None = None
    moi_luot = max(1, SO_UNG_VIEN_MOI_LUOT)
    # Mỗi lượt gọi nay xin `moi_luot` phương án, nên cần ít lượt hơn cho cùng một
    # số ứng viên. Làm tròn LÊN: thiếu còn hơn thừa thì ngược lại — hụt ứng viên
    # làm tụt tỉ lệ đạt của cả khổ.
    so_luot_can = -(-so_ung_vien // moi_luot)
    nhac = loi_nhac if moi_luot == 1 else f"{loi_nhac}\n{CHI_DAN_NHIEU_UNG_VIEN.format(so=moi_luot)}"

    buoc = max(1, so_song_song)
    for dau in range(0, so_luot_can, buoc):
        con = min(buoc, so_luot_can - dau)
        tra_loi = await asyncio.gather(
            *[
                llm.reply(
                    messages=(UserMessage(content=nhac),),
                    tools=(),
                    ctx=ctx,
                    model=default_model,
                )
                for _ in range(con)
            ]
        )
        # Đếm theo LƯỢT GỌI, không theo số phương án xin được: đây là con số đi
        # vào `so_ung_vien_da_dung` để truy chi phí, và chi phí tính theo lượt gọi.
        da_dung += con

        for r in tra_loi:
            if isinstance(r, Err):
                continue
            for dong in _lay_cac_phuong_an(r.value.text):
                # QĐ-P2: khổ có dòng chép nguyên văn thơ đã có thì bỏ luôn, kể cả
                # khi nó đạt luật — cổng cuối cũng sẽ chặn, nhận nó ở đây chỉ là
                # tốn tiền mang một bài chắc chắn trượt đi tới tận cổng.
                if tim_dong_chep("\n".join(dong), chi_muc_chep):
                    continue
                # ⛔ Kiểm trên TOÀN BỘ phần đã tích luỹ, không kiểm riêng khổ này.
                # Kiểm rời thì lỗi vắt qua ranh giới khổ sẽ chỉ lộ ra khi đã ghép xong.
                v = kiem_tra_bai_tho("\n".join(da_co + dong))
                if v.dat:
                    return dong, da_dung
                # Giữ lại ứng viên HỤT ÍT NHẤT để cứu ở dưới: ứng viên sai 1 dòng
                # gần đích hơn hẳn cái sai 4 dòng, và vòng ReAct chỉ đáng chạy trên
                # cái gần đích.
                #
                # Xếp theo `diem_tuan_thu`, KHÔNG theo `len(v.vi_pham)` (Plan_PoeTone
                # GĐ3.2): bộ kiểm dừng ở tầng chặn đầu tiên nên `vi_pham` chỉ đếm lỗi
                # của MỘT tầng — ứng viên chết ở tầng 2 chưa hề được kiểm thanh.
                khoa = do_diem_tuan_thu("\n".join(da_co + dong)).khoa_xep_hang()
                if gan_nhat is None or khoa < gan_nhat[1]:
                    gan_nhat = (dong, khoa)

    # ════ CHƯA ĐẠT THÌ SUY NGHĨ, ĐỪNG BỎ CUỘC NGAY ════
    if gan_nhat is not None and tools is not None:
        cuu = await _cuu_kho_bang_react(
            gan_nhat[0], da_co, loi_nhac,
            llm=llm, ctx=ctx, tools=tools, rate_limiter=rate_limiter,
            default_model=default_model,
        )
        da_dung += 1
        if cuu is not None:
            return cuu, da_dung

    return None, da_dung


async def _cuu_kho_bang_react(
    gan_nhat: list[str],
    da_co: list[str],
    loi_nhac_goc: str,
    *,
    llm: LlmPort,
    ctx: CallContext,
    tools: ToolPort,
    rate_limiter: RateLimitPort | None,
    default_model: str,
) -> list[str] | None:
    """Một vòng ReAct trên ứng viên gần đích nhất. Trả None nếu vẫn chưa đạt.

    ════ VÌ SAO BƯỚC NÀY TỒN TẠI ════

    Trước 22/09/2026, đường sinh CHÍNH gọi thẳng `llm.reply` với `tools=()`. Nghĩa
    là mô hình viết MÙ: nó không đếm được tiếng, không tra được dấu, và không có
    cách nào tự biết mình vừa viết một dòng 8 tiếng. Nó chỉ việc đoán, rồi cổng
    chặn. Hết `so_ung_vien` ứng viên mà không cái nào đạt thì khổ ấy bị bỏ, bài
    thành thiếu khổ, và người dùng nhận về một lỗi.

    Tool `kiem_tra_tho` đã có sẵn từ lâu (`adapters/tools/poem_check.py`) và đã
    đăng ký — chỉ là đường sinh chính chưa bao giờ đưa nó cho mô hình. Bước này
    nối chỗ đó lại: ĐẾM TRƯỚC, NGHĨ, RỒI MỚI TRẢ.

    ════ VÌ SAO CHỈ CỨU MỘT ỨNG VIÊN, VÀ CHỈ MỘT LẦN ════

    Vòng ReAct đắt hơn hẳn một lượt `reply`: mỗi lần mô hình gọi tool là thêm một
    lượt gọi nữa. Chạy nó cho cả 16 ứng viên sẽ phá đúng phép tính kinh tế mà
    docstring đầu file dựng lên — sinh nhiều bản RẺ rồi lọc.

    Nên giữ nguyên phần sinh rẻ, và chỉ bỏ tiền suy nghĩ vào ứng viên HỤT ÍT NHẤT,
    đúng một lần. Ứng viên sai một dòng thì một vòng tự soi thường đủ; ứng viên sai
    bốn dòng thì có nghĩ thêm cũng không cứu được, và sinh lại rẻ hơn.

    ════ KHÔNG NỚI CỔNG MỘT LY NÀO ════

    Kết quả vòng ReAct vẫn phải qua `kiem_tra_bai_tho` trên TOÀN BỘ phần đã tích
    luỹ, y hệt mọi ứng viên khác. Chưa đạt thì trả None — bước này làm bài DỄ ĐẠT
    HƠN, nó không làm chuẩn đạt THẤP ĐI. Chủ dự án chốt 22/09/2026: hết lượt mà
    vẫn hỏng thì vẫn chặn, không trả bài sai kèm biên bản.
    """
    if rate_limiter is not None and not await rate_limiter.within_daily_budget(ctx.scope):
        return None

    v = kiem_tra_bai_tho("\n".join(da_co + gan_nhat))
    loi_nhac = "\n".join(
        [
            loi_nhac_goc,
            wrap_xml_tag("ban_nhap_chua_dat", "\n".join(gan_nhat)),
            wrap_xml_tag("bien_ban_kiem_dinh", dung_bien_ban(v)),
            CHI_DAN_TU_SOI,
        ]
    )

    kq = await generate_react_loop(
        envelope=ContextEnvelope(
            messages=(UserMessage(content=loi_nhac),),
            tokens_used=0,
            has_knowledge=False,
        ),
        llm=llm,
        tools=tools,
        rate_limiter=rate_limiter or _NganSachLuonMo(),
        ctx=ctx,
        default_model=default_model,
        la_ban_nhap=co_dang_bai_tho,
    )
    if isinstance(kq, Err):
        return None

    for dong in _lay_cac_phuong_an(kq.value):
        if kiem_tra_bai_tho("\n".join(da_co + dong)).dat:
            return dong
    return None


class _NganSachLuonMo:
    """Cổng ngân sách rỗng, dùng khi người gọi không đưa `rate_limiter` vào.

    `generate_react_loop` đòi một `RateLimitPort` thật. Truyền None vào sẽ nổ ở
    dòng đầu tiên của nó. Ca này chỉ xảy ra trong test và trong lời gọi trực tiếp
    — đường chạy thật luôn có rate limiter, và nó đã được hỏi ở đầu hàm này.
    """

    async def check(self, scope: ThreadScope, sender_id: str) -> RateLimitOutcome:  # noqa: ARG002
        return Pass()

    async def should_warn(self, scope: ThreadScope, sender_id: str) -> bool:  # noqa: ARG002
        return False

    async def within_daily_budget(self, scope: ThreadScope) -> bool:  # noqa: ARG002
        return True


_THE_PHUONG_AN = re.compile(
    r"<phuong_an>(.*?)</phuong_an>", re.IGNORECASE | re.DOTALL
)


def _lay_cac_phuong_an(van_ban: str) -> list[list[str]]:
    """Rút MỌI phương án dùng được từ một câu trả lời. Rỗng nghĩa là không có cái nào.

    Hai chế độ, và chế độ hai là LỐI LÙI BẮT BUỘC:

      - Có thẻ `<phuong_an>` -> đọc từng thẻ một, bỏ thẻ nào không đủ bốn dòng.
      - Không có thẻ nào     -> coi cả câu trả lời là MỘT phương án, đúng hành vi
        trước 22/09.

    Lối lùi không phải để cho đẹp: mô hình không phải lúc nào cũng nghe lời về
    định dạng, và một câu trả lời đúng luật mà thiếu thẻ thì vẫn dùng được. Bỏ nó
    đi là tự nguyện vứt các ứng viên hợp lệ chỉ vì cái vỏ.
    """
    khoi = _THE_PHUONG_AN.findall(van_ban)
    if not khoi:
        mot = _lay_bon_dong(van_ban)
        return [mot] if mot is not None else []
    ra = [_lay_bon_dong(k) for k in khoi]
    return [x for x in ra if x is not None]


def _lay_bon_dong(van_ban: str) -> list[str] | None:
    """Lấy đúng 4 dòng thơ từ câu trả lời.

    Mô hình hay kèm lời dẫn hoặc viết dư. Lấy 4 dòng KHÔNG RỖNG đầu tiên; ít hơn 4
    thì bỏ ứng viên — cắt ghép cho đủ là bắt đầu sửa văn bản thơ, điều P2 cấm.
    """
    dong = [d.strip() for d in van_ban.strip().splitlines() if d.strip()]
    return dong[:DONG_MOI_KHO] if len(dong) >= DONG_MOI_KHO else None
