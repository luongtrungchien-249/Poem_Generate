"""Tool `sinh_tho` — nối đường CHAT vào máy sinh thơ ĐÃ KIỂM.

════ VÌ SAO TOOL NÀY RA ĐỜI, 23/09/2026 ════

Chủ dự án chỉnh lại định hướng: *"dự án này không phải là giải thích luật thơ mà
là sinh thơ"*. Khảo sát cho thấy đường chat đang đi ngược đúng điều đó:

    sổ đăng ký có   `kiem_tra_tho`, `danh_gia_chat_luong_tho`   -> vai NGƯỜI KIỂM
    không có        một tool nào SINH thơ

Nên khi người dùng xin một bài thơ trong chat, mô hình **tự viết tay** ở chất
lượng `pⁿ` — với `p ≈ 0,56` thì bài 20 dòng đạt cỡ 1 phần 100.000 — rồi dán nhãn
"chưa qua bộ kiểm" và chỉ người ta sang chỗ khác.

Trong khi đó máy sinh thơ đã kiểm **có sẵn và chạy tốt**: đo được **80 %** cho bài
20 dòng. Nó chỉ chưa được nối vào bề mặt trò chuyện. Tool này là cái nối đó.

Không dựng lại đường sinh nào: gọi thẳng `sinh_bai_tho`, vốn đã có 32 ứng viên mỗi
khổ, cổng bảy tầng, vòng sửa, bước cứu ReAct và đặt tiêu đề.

════ GIÁ, VÀ VÌ SAO CHỦ DỰ ÁN CHẤP NHẬN ════

Một lượt gọi tool này tốn tới ~36 lượt gọi model cho bài 20 dòng. Con số ấy KHÔNG
phải lãng phí — nó là giá để đi từ `0,56²⁰` lên 80 %:

    P(một khổ 4 dòng đạt) = 0,56⁴ ≈ 10 %   -> 90 % số khổ viết ra là hỏng
    xin 4 phương án mỗi lượt              -> ~2,9 lượt/khổ nếu độc lập
    đo thật                               -> 7,3 lượt/khổ (khổ sau còn phải giữ vần)

Chủ dự án chốt 23/09/2026: **không giới hạn số dòng trong chat**, vì đó đúng là
sản phẩm. Chốt chặn chi phí duy nhất là `rate_limiter` — `sinh_bai_tho` hỏi lại
ngân sách ở MỖI khổ, nên nó phải được truyền xuống thật.
"""

from typing import Any

from application.agent.tools.registry import tool_registry
from application.poetry.requirement import PoetryRequirement, Truong
from application.poetry.sinh_tho import CanLamRo, sinh_bai_tho
from application.ports.llm import CallContext, LlmPort
from application.ports.rate_limit import RateLimitPort
from application.ports.tools import ToolPort, ToolSpec
from domain.common.result import Ok
from domain.conversation.thread import ThreadScope

TEN_TOOL = "sinh_tho"


class _ToolTruBoChinhNo:
    """Bộ tool đã lọc bỏ `sinh_tho`, để đưa xuống đường sinh thơ.

    ⛔ CHẶN ĐỆ QUY. `sinh_bai_tho` truyền `tools` xuống đường lùi của nó, và vòng
    ReAct ở đó có quyền gọi bất cứ tool nào nó thấy. Nếu `sinh_tho` nằm trong bộ
    ấy thì mô hình đang sửa một bài thơ có thể gọi lại chính máy sinh thơ — mỗi
    tầng đệ quy nhân thêm ~36 lượt gọi.

    Lọc ở đây chứ không ở sổ đăng ký: sổ đăng ký dùng chung cho mọi đường, và
    `sinh_tho` VẪN phải có mặt ở đường chat. Chỉ đường bên trong mới cần trừ nó.
    """

    def __init__(self, goc: ToolPort) -> None:
        self._goc = goc

    def specs(self) -> tuple[ToolSpec, ...]:
        return tuple(s for s in self._goc.specs() if s.name != TEN_TOOL)

    async def call_many(self, calls: Any, ctx: CallContext) -> Any:
        return await self._goc.call_many(calls, ctx)


def register_poem_generate_tool(
    llm: LlmPort | None = None,
    tools: ToolPort | None = None,
    rate_limiter: RateLimitPort | None = None,
    default_model: str = "gpt-4o-mini",
) -> None:
    """Đăng ký tool sinh thơ. Phụ thuộc vào closure, không đọc trạng thái toàn cục.

    Theo đúng khuôn `search_kb.py`: sổ đăng ký dùng chung cho mọi request, nên
    trạng thái toàn cục ở đây là đường dẫn thẳng tới rò dữ liệu giữa các tenant.

    Thiếu phụ thuộc (ca test, ca dựng container dở dang) thì tool vẫn đăng ký
    được nhưng báo lỗi rõ khi gọi — im lặng trả rỗng sẽ khiến chat tưởng máy sinh
    thơ đã chạy và không có bài nào đạt.
    """

    @tool_registry.register(
        name=TEN_TOOL,
        description=(
            "Sinh một bài thơ thất ngôn tự do ĐÃ QUA BỘ KIỂM LUẬT. "
            "Dùng tool này mỗi khi người dùng xin một bài thơ — đừng tự viết tay, "
            "vì bài tự viết gần như chắc chắn sai luật và sẽ không qua được cổng. "
            "Tool chạy lâu (có thể cả phút) vì nó sinh nhiều bản rồi chọn bản đạt."
        ),
        parameters_schema={
            "type": "object",
            "properties": {
                "chu_de": {
                    "type": "string",
                    "description": "Chủ đề bài thơ, ví dụ 'mùa thu Hà Nội'",
                },
                "so_dong": {
                    "type": "integer",
                    "description": "Số dòng của bài. Phải là bội của 4.",
                },
                "cam_xuc": {"type": "string", "description": "Cảm xúc chủ đạo, tuỳ chọn"},
                "phong_cach": {
                    "type": "string",
                    "description": "Phong cách, ví dụ 'đời thường' hay 'văn chương'. Tuỳ chọn.",
                },
            },
            "required": ["chu_de", "so_dong"],
        },
    )
    async def _sinh_tho(
        chu_de: str,
        so_dong: int,
        cam_xuc: str = "",
        phong_cach: str = "",
        tenant_id: str = "default",
    ) -> dict[str, Any]:
        if llm is None or tools is None or rate_limiter is None:
            return {
                "loi": "Máy sinh thơ chưa được nối. Báo cho người dùng biết và "
                       "ĐỪNG tự viết một bài thay thế."
            }

        trong = PoetryRequirement()
        yeu_cau = PoetryRequirement(
            chu_de=Truong(gia_tri=chu_de, nguon="nguoi_dung"),
            so_dong=Truong(gia_tri=so_dong, nguon="nguoi_dung"),
            cam_xuc=Truong(gia_tri=cam_xuc, nguon="nguoi_dung") if cam_xuc else trong.cam_xuc,
            phong_cach=(
                Truong(gia_tri=phong_cach, nguon="nguoi_dung") if phong_cach else trong.phong_cach
            ),
        )

        ctx = CallContext(
            scope=ThreadScope(platform="web", thread_id=tenant_id),
            sender_id=tenant_id,
            trace_id=f"chat-sinh-tho-{tenant_id}",
        )

        kq = await sinh_bai_tho(
            yeu_cau,
            llm=llm,
            # Bộ tool TRỪ chính nó — xem `_ToolTruBoChinhNo`.
            tools=_ToolTruBoChinhNo(tools),
            rate_limiter=rate_limiter,
            ctx=ctx,
            default_model=default_model,
        )

        if not isinstance(kq, Ok):
            # Cổng fail-closed: hết lượt sửa mà chưa đạt thì KHÔNG có bài nào đi ra.
            # Trả chẩn đoán để chat nói thật, thay vì im lặng rồi để mô hình tự bịa.
            return {
                "dat": False,
                "loi": str(getattr(kq, "error", "không sinh được bài đạt luật")),
                "nhac": "KHÔNG tự viết một bài thay thế. Nói thật là chưa sinh được.",
            }

        ra = kq.value

        if isinstance(ra, CanLamRo):
            # Chưa đủ thông tin -> `sinh_bai_tho` KHÔNG gọi model lượt nào, không
            # tốn tiền. Chuyển nguyên câu hỏi về cho chat hỏi lại người dùng.
            return {
                "can_hoi_lai": True,
                "cau_hoi": ra.cau_hoi.cau_hoi,
                "truong_thieu": list(ra.cau_hoi.truong_thieu),
            }

        v = ra.bien_ban.verdict
        return {
            "dat": True,
            "tieu_de": ra.tieu_de,
            "bai_tho": ra.text,
            "so_dong": v.so_dong,
            "so_kho": v.so_kho,
            "so_do_van": ["".join(k) for k in v.so_do_van_theo_kho],
            "so_luot_sua": ra.so_luot,
            # Bằng chứng để chat thuật lại, thay vì tự phán "bài này đúng luật".
            "bang_chung_tung_tang": [
                {"tang": t.so, "ten": t.ten, "dat": t.dat, "bang_chung": t.bang_chung}
                for t in v.tang
                if t.da_chay
            ],
        }
