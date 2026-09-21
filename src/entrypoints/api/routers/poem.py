"""`POST /v1/poem` — sinh thơ thất ngôn tự do có kiểm định.

Router MỎNG: nó đổi DTO sang kiểu nghiệp vụ, gọi use case, rồi đổi kết quả về DTO.
Không có luật thơ, không có ngưỡng, không có quyết định nào ở đây. Toàn bộ phán
quyết nằm ở `application/poetry/`.

BA MÃ TRẠNG THÁI, ba nghĩa khác nhau:

    200 + PoemResponse   bài đã qua luật + chất lượng, kèm bằng chứng bảy tầng
    200 + CanLamRo       chưa đủ thông tin -> hệ thống HỎI LẠI (chỉ thị 5)
    422 + PoemKhongDat   hết lượt sửa mà chưa đạt -> KHÔNG trả bài sai

`CanLamRo` trả 200 chứ không phải 4xx là có chủ ý: người dùng không làm gì sai cả.
Hỏi lại là một bước hợp lệ của hội thoại, không phải một lỗi của yêu cầu.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from adapters.observability.tracing import get_current_trace_id
from application.poetry.phan_tich_yeu_cau import TRUONG_TRICH, phan_tich_yeu_cau
from application.poetry.requirement import (
    PoetryRequirement,
    Truong,
    nguoi_dung,
)
from application.poetry.sinh_tho import CanLamRo, DaSinhTho, sinh_bai_tho
from application.ports.llm import CallContext
from contracts.poem import (
    BangChungChieu,
    BangChungTang,
    PoemRequest,
    PoemResponse,
)
from contracts.poem import CanLamRo as CanLamRoDTO
from contracts.poem import PoemKhongDat as PoemKhongDatDTO
from domain.common.errors import OutputKhongDat
from domain.common.result import Err
from domain.conversation.thread import ThreadScope
from domain.guardrails.input import (
    check_forbidden_topics,
    check_input_length,
    detect_injection,
)
from domain.policy.hitl import TinHieuHitl, quyet_dinh_hitl
from entrypoints.api.deps import AppContainer, get_container

router = APIRouter(prefix="/v1", tags=["Poem"])


def _truong(gia_tri: object | None) -> Truong:
    """Người dùng nói thì ghi nguồn `nguoi_dung`; không nói thì để trống.

    KHÔNG BAO GIỜ tự điền giá trị thay người dùng — cổng B1 sẽ hỏi lại. Đây là
    chỗ dễ phạm nhất: điền một mặc định "hợp lý" ở đây là vô hiệu hoá chỉ thị 5.
    """
    return nguoi_dung(gia_tri) if gia_tri not in (None, "") else Truong(None, "mac_dinh")


async def _dung_yeu_cau(
    req: PoemRequest, app_container: AppContainer, ctx: CallContext
) -> PoetryRequirement:
    """Trường HTTP tường minh THẮNG phần trích từ câu nói tự nhiên.

    Người dùng điền `chu_de="biển"` rồi viết `yeu_cau="thơ về núi"` thì trường
    tường minh là ý định rõ ràng hơn. Chỉ những trường BỎ TRỐNG mới nhờ tới §7.2.
    """
    tuong_minh = _dung_yeu_cau_tuong_minh(req)
    thieu = [t for t, v in tuong_minh.cac_truong() if not v.co_gia_tri]

    # Chỉ gọi mô hình khi nó THẬT SỰ giúp được. `so_dong` do regex tất định lo
    # (H4 là luật cứng, không giao cho mô hình), nên nếu thứ duy nhất còn thiếu là
    # số dòng thì một lượt gọi ở đây là tiền vứt đi: cổng B1 sẽ hỏi lại y hệt.
    thieu_mo_hinh_lo_duoc = [t for t in thieu if t in TRUONG_TRICH]
    if not thieu_mo_hinh_lo_duoc:
        return tuong_minh

    kq = await phan_tich_yeu_cau(req.yeu_cau, llm=app_container.chat_llm, ctx=ctx)
    if isinstance(kq, Err):
        return tuong_minh
    trich = kq.value.yeu_cau

    # Ghép: giữ trường tường minh, lấy trường trích cho chỗ còn trống.
    bu = {
        ten: gt
        for ten, gt in trich.cac_truong()
        if ten in thieu and (gt.co_gia_tri or gt.nguon == "suy_doan")
    }
    return replace(tuong_minh, **bu)  # type: ignore[arg-type]


def _dung_yeu_cau_tuong_minh(req: PoemRequest) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=_truong(req.chu_de),
        so_dong=_truong(req.so_dong),
        cam_xuc=_truong(req.cam_xuc),
        phong_cach=_truong(req.phong_cach),
        rang_buoc_van=_truong(req.rang_buoc_van),
        rang_buoc_thanh=_truong(req.rang_buoc_thanh),
        # Ba trường dưới KHÔNG chặn bài đúng luật, nên có mặc định là hợp lệ.
        # Chủ đề và số dòng thì không — chúng quyết định bài thơ ra sao.
        van_ban_goc=req.yeu_cau,
    )


@router.post("/poem", response_model=None)
async def sinh_tho_endpoint(
    req: PoemRequest,
    raw_request: Request,
    app_container: AppContainer = Depends(get_container),
) -> Any:
    trace_id = getattr(raw_request.state, "trace_id", None) or get_current_trace_id()

    # INPUT RAILS (§17). Đường thơ trước đây KHÔNG có rào chắn đầu vào nào — nó chỉ
    # có rào đầu ra. Thiếu vế này thì một yêu cầu tiêm lệnh đi thẳng vào prompt.
    #
    # Thứ tự có ý nghĩa: độ dài trước (rẻ nhất), rồi tiêm lệnh, rồi chủ đề.
    do_dai = check_input_length(req.yeu_cau)
    if not do_dai.is_valid:
        raise HTTPException(status_code=400, detail=do_dai.reason)

    tiem = detect_injection(req.yeu_cau)
    if tiem.is_injection:
        raise HTTPException(
            status_code=400,
            detail=f"Phát hiện tiêm lệnh: {', '.join(tiem.matched_patterns)}",
        )

    chu_de_res = check_forbidden_topics(req.yeu_cau)
    if chu_de_res.muc == "BLOCK":
        raise HTTPException(
            status_code=400,
            detail=f"Chủ đề không được hỗ trợ ({chu_de_res.category}): {chu_de_res.ly_do}",
        )

    # `platform` là Literal đóng của domain; "web" là vai của người gọi qua HTTP.
    # Thêm giá trị mới vào Literal đó là một quyết định của domain, không phải của
    # một router — nên ở đây dùng đúng giá trị đã có.
    scope = ThreadScope(platform="web", thread_id=req.session_id or trace_id)
    ctx = CallContext(scope=scope, sender_id="api", trace_id=trace_id)

    kq = await sinh_bai_tho(
        await _dung_yeu_cau(req, app_container, ctx),
        llm=app_container.chat_llm,
        tools=app_container.tools,
        rate_limiter=app_container.rate_limiter,
        ctx=ctx,
        verifier=app_container.poem_verifier,
        corpus=app_container.poem_corpus,
        max_repair_rounds=req.max_repair_rounds,
        default_model=app_container.default_model,
    )

    if isinstance(kq, Err):
        e = kq.error
        if isinstance(e, OutputKhongDat):
            # FAIL CLOSED. Không trường nào của response này chứa văn bản thơ —
            # kể cả khi bản nháp cuối trông có vẻ ổn.
            return JSONResponse(
                status_code=422,
                content=PoemKhongDatDTO(
                    ma_the=e.ma_the,
                    so_luot_da_sua=e.so_luot_da_sua,
                    chan_doan=e.chan_doan,
                    trace_id=trace_id,
                ).model_dump(),
            )
        # Lỗi hạ tầng: để middleware xử lý theo cách chung của hệ thống.
        raise RuntimeError(f"Sinh thơ thất bại: {type(e).__name__}")

    ra = kq.value

    if isinstance(ra, CanLamRo):
        h = ra.cau_hoi
        return CanLamRoDTO(
            ca=h.ca,
            cau_hoi=h.cau_hoi,
            ly_do=h.ly_do,
            truong_thieu=list(h.truong_thieu),
            duong_di=list(ra.duong_di),
            trace_id=trace_id,
        )

    assert isinstance(ra, DaSinhTho)
    bb = ra.bien_ban
    v = bb.verdict

    # §22 — quyết định HITL. Tồn tại `DaSinhTho` nghĩa là bài đã qua toàn bộ sáu
    # bước, nên nhánh REJECT ở đây gần như không với tới được; vẫn gọi đủ để một
    # thay đổi ở tầng dưới không lặng lẽ bỏ qua cổng này.
    hitl = quyet_dinh_hitl(
        TinHieuHitl(
            yeu_cau_day_du=True,
            an_toan_dat=True,
            dat_luat=bb.dat_luat,
            dat_chat_luong=bb.dat_chat_luong,
            so_luot_sua=ra.so_luot,
            chu_de_can_xem_lai=chu_de_res.muc == "REVIEW",
            tran_luot_sua=req.max_repair_rounds,
        )
    )
    return PoemResponse(
        poem=ra.text,
        dat=bb.dat,
        thuoc_the=v.thuoc_the,
        dat_luat=bb.dat_luat,
        dat_chat_luong=bb.dat_chat_luong,
        so_dong=v.so_dong,
        so_kho=v.so_kho,
        so_luot_sua=ra.so_luot,
        chien_luoc_cuoi=ra.chien_luoc_cuoi,
        bang_chung_bay_tang=[
            BangChungTang(
                tang=t.so, ten=t.ten, ma_luat=list(t.ma_luat), muc=t.muc,
                da_chay=t.da_chay, dat=t.dat, trich_luat=t.trich_luat,
                bang_chung=t.bang_chung, chi_tiet=dict(t.chi_tiet),
            )
            for t in v.tang
        ],
        chat_luong=[
            BangChungChieu(
                ma=c.ma, ten=c.ten, do_duoc=c.do_duoc, dat=c.dat,
                so_do=c.so_do, nguong=c.nguong, bang_chung=c.bang_chung,
            )
            for c in bb.chat_luong.chieu
        ],
        so_do_van=["".join(k) for k in v.so_do_van_theo_kho],
        ghi_chu=list(v.ghi_chu),
        quyet_dinh_hitl=hitl.quyet_dinh,
        ly_do_hitl=hitl.ly_do,
        duong_di=list(ra.duong_di),
        che_do_vi_du=ra.che_do_vi_du,
        id_vi_du=list(ra.id_vi_du),
        trace_id=trace_id,
    )
