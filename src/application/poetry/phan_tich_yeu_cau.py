"""§7.2 REQUIREMENT ANALYZER — trích yêu cầu từ câu nói tự nhiên.

════ VẤN ĐỀ CỐT LÕI: LÀM SAO BIẾT MÔ HÌNH ĐANG ĐỌC HAY ĐANG ĐOÁN ════

Chỉ thị 5 đòi *"thoả mãn đầy đủ mọi thông tin trước khi cho thơ"*, và §3.2 cấm tự
suy đoán. `PoetryRequirement` đã có trường `nguon` để phân biệt — nhưng nếu mô
hình tự khai `nguon="nguoi_dung"` thì cái nhãn ấy vô giá trị: mô hình đoán chủ đề
rồi tự nhận là người dùng nói, và cổng B1 cho qua.

CÁCH GIẢI: **BẮT TRÍCH DẪN, RỒI KIỂM TRÍCH DẪN ĐÓ CÓ THẬT KHÔNG.**

Mô hình phải trả về, cho mỗi trường, một đoạn NGUYÊN VĂN của người dùng chống
lưng cho giá trị đó. Hệ thống kiểm đoạn ấy có thật sự nằm trong câu người dùng:

    trích có thật  -> nguon = "nguoi_dung"
    trích rỗng/bịa -> nguon = "suy_doan"  -> cổng B1 CHẶN, hỏi lại

Nhờ vậy `nguon` là thứ **kiểm được bằng máy**, không phải lời tự khai. Mô hình
không có cách nào tuyên bố người dùng đã nói điều họ chưa nói.

════ SỐ DÒNG KHÔNG GIAO CHO MÔ HÌNH ════

`so_dong` quyết định H4 (bội của 4) — luật cứng. Trích bằng regex TẤT ĐỊNH trước,
và kết quả regex luôn thắng kết quả mô hình. Một con số đọc sai làm hỏng cả bài,
mà regex thì không bao giờ "sáng tạo".
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace

from application.poetry.requirement import (
    PoetryRequirement,
    Truong,
    mac_dinh,
    nguoi_dung,
    suy_doan,
)
from application.ports.llm import CallContext, LlmPort, UserMessage
from domain.common.errors import BotError
from domain.common.result import Err, Ok, Result

# Trường mô hình được phép đề xuất. `so_dong` KHÔNG có trong này — xem docstring.
TRUONG_TRICH = ("chu_de", "cam_xuc", "phong_cach", "rang_buoc_van", "rang_buoc_thanh")

CHI_DAN_TRICH = """Bạn là bộ trích yêu cầu làm thơ. KHÔNG làm thơ.

Đọc yêu cầu của người dùng và trả về DUY NHẤT một object JSON:

{
  "chu_de":          {"gia_tri": "...", "trich": "..."},
  "cam_xuc":         {"gia_tri": "...", "trich": "..."},
  "phong_cach":      {"gia_tri": "...", "trich": "..."},
  "rang_buoc_van":   {"gia_tri": "...", "trich": "..."},
  "rang_buoc_thanh": {"gia_tri": "...", "trich": "..."}
}

LUẬT BẮT BUỘC:
1. "trich" phải là đoạn NGUYÊN VĂN, sao chép y hệt từ câu của người dùng, chống
   lưng cho "gia_tri". Không được diễn đạt lại, không được thêm chữ.
2. Người dùng KHÔNG nói về trường nào thì để cả hai khoá là chuỗi rỗng "".
   TUYỆT ĐỐI không đoán. Để trống là câu trả lời đúng và được mong đợi.
3. Không thêm khoá nào khác. Không viết gì ngoài JSON.
"""

# "8 dòng", "8 câu", "bài 12 dòng"
_SO_DONG_SO = re.compile(r"\b(\d{1,3})\s*(?:dòng|dong|câu|cau)\b", re.IGNORECASE)
# Số viết bằng chữ, giới hạn ở các giá trị thực tế của thể.
_CHU_SO = {
    "bốn": 4, "bon": 4, "tám": 8, "tam": 8, "mười hai": 12, "muoi hai": 12,
    "mười sáu": 16, "muoi sau": 16, "hai mươi": 20, "hai muoi": 20,
}
_SO_DONG_CHU = re.compile(
    r"\b(" + "|".join(sorted(_CHU_SO, key=len, reverse=True)) + r")\s*(?:dòng|dong|câu|cau)\b",
    re.IGNORECASE,
)


def trich_so_dong(van_ban: str) -> int | None:
    """Trích số dòng bằng regex TẤT ĐỊNH. Không có thì trả None để cổng B1 hỏi.

    Chữ số trước, rồi tới số viết bằng chữ. Không suy diễn từ "ngắn"/"dài" — hai
    từ đó không có nghĩa đo được, và đoán ở đây là đoán đúng chỗ H4 không tha.
    """
    m = _SO_DONG_SO.search(van_ban)
    if m:
        return int(m.group(1))
    m = _SO_DONG_CHU.search(van_ban)
    if m:
        return _CHU_SO[m.group(1).lower()]
    return None


def _chuan(s: str) -> str:
    return " ".join(s.split()).lower()


def _trich_co_that(trich: str, van_ban_goc: str) -> bool:
    """Đoạn trích có thật sự nằm trong câu người dùng không.

    So khớp sau khi chuẩn hoá khoảng trắng và hoa/thường — mô hình hay đổi mấy thứ
    đó mà không đổi nội dung. Nhưng KHÔNG so khớp mờ hơn nữa: cả điểm của cơ chế
    này là trích dẫn phải nguyên văn.
    """
    t = _chuan(trich)
    return len(t) >= 2 and t in _chuan(van_ban_goc)


# 🩸 Giá trị GIẢ — chỗ giữ chỗ của chính khung JSON trong chỉ dẫn.
#
# Lỗi đã bắt được: mô hình (hoặc một provider lặp lại đầu vào) trả về nguyên khung
# mẫu trong `CHI_DAN_TRICH`, và bộ đọc JSON coi "..." là một giá trị thật. Kết quả:
# mọi trường thành `suy_doan`, và cổng B1 hỏi sai câu — hỏi "tôi chưa chắc về chủ
# đề" trong khi vấn đề là mô hình chưa trả lời gì cả.
#
# Nhận diện theo HÌNH DẠNG chứ không theo danh sách: chuỗi chỉ gồm dấu chấm/ba
# chấm, hoặc trùng đúng tên trường, đều là chỗ giữ chỗ.
_GIA_TRI_GIA = frozenset({"...", "…", "..", ".", "string", "n/a", "null", "none"})


def _la_gia_tri_gia(s: str, ten_truong: str = "") -> bool:
    t = s.strip().lower()
    return (not t) or t in _GIA_TRI_GIA or t == ten_truong or set(t) <= {".", "…", " "}


def _truong_tu_trich(
    gia_tri: object, trich: object, van_ban_goc: str, ten_truong: str = ""
) -> Truong:
    """Quy đổi một mục JSON thành `Truong`, với `nguon` KIỂM ĐƯỢC."""
    if not isinstance(gia_tri, str) or _la_gia_tri_gia(gia_tri, ten_truong):
        return mac_dinh(None)
    if (
        isinstance(trich, str)
        and not _la_gia_tri_gia(trich, ten_truong)
        and _trich_co_that(trich, van_ban_goc)
    ):
        return nguoi_dung(gia_tri.strip())
    # Có giá trị nhưng không chứng minh được người dùng đã nói -> SUY ĐOÁN.
    # Cổng B1 sẽ chặn và hỏi lại. Đây là hành vi đúng, không phải thất bại.
    return suy_doan(gia_tri.strip())


def _doc_json(van_ban: str) -> dict[str, object]:
    """Đọc JSON từ câu trả lời của mô hình, chịu được lời dẫn thừa và rào ```."""
    t = van_ban.strip()
    if "```" in t:
        khoi = [p for p in t.split("```") if "{" in p]
        t = khoi[0] if khoi else t
        t = t.removeprefix("json").strip()
    i, j = t.find("{"), t.rfind("}")
    if i == -1 or j <= i:
        return {}
    try:
        ra = json.loads(t[i : j + 1])
    except json.JSONDecodeError:
        return {}
    return ra if isinstance(ra, dict) else {}


@dataclass(frozen=True, slots=True)
class KetQuaPhanTich:
    yeu_cau: PoetryRequirement
    # Trường nào mô hình đưa ra mà KHÔNG chứng minh được bằng trích dẫn.
    truong_suy_doan: tuple[str, ...]
    # True khi không gọi được mô hình: yêu cầu chỉ có phần trích bằng regex.
    chi_co_regex: bool


def phan_tich_tho(van_ban: str) -> PoetryRequirement:
    """Phần TẤT ĐỊNH, không cần mô hình. Luôn chạy, và luôn thắng mô hình.

    Tách riêng để dùng được cả khi provider hỏng — §32 *LLM Failure*.
    """
    n = trich_so_dong(van_ban)
    return PoetryRequirement(
        so_dong=nguoi_dung(n) if n is not None else mac_dinh(None),
        van_ban_goc=van_ban,
    )


async def phan_tich_yeu_cau(
    van_ban: str,
    *,
    llm: LlmPort,
    ctx: CallContext,
) -> Result[KetQuaPhanTich, BotError]:
    """Trích `PoetryRequirement` từ câu nói tự nhiên.

    Mô hình hỏng hoặc trả rác thì KHÔNG phải lỗi chí mạng: rơi về phần regex, và
    cổng B1 sẽ hỏi lại những gì còn thiếu. Đúng §32 *LLM Failure -> Repair /
    Retry -> Fallback*.
    """
    goc = phan_tich_tho(van_ban)

    kq = await llm.cheap(
        messages=(UserMessage(content=f"{CHI_DAN_TRICH}\n\nYêu cầu:\n{van_ban}"),),
        route="extract",
        ctx=ctx,
    )
    if isinstance(kq, Err):
        return Ok(KetQuaPhanTich(yeu_cau=goc, truong_suy_doan=(), chi_co_regex=True))

    data = _doc_json(kq.value)
    if not data:
        return Ok(KetQuaPhanTich(yeu_cau=goc, truong_suy_doan=(), chi_co_regex=True))

    thay_doi: dict[str, Truong] = {}
    doan: list[str] = []
    for ten in TRUONG_TRICH:
        muc = data.get(ten)
        if not isinstance(muc, dict):
            continue
        t = _truong_tu_trich(muc.get("gia_tri"), muc.get("trich"), van_ban, ten)
        if t.nguon == "suy_doan":
            doan.append(ten)
        if t.co_gia_tri:
            thay_doi[ten] = t

    # `so_dong` KHÔNG nhận từ mô hình — regex đã quyết ở `goc`.
    return Ok(
        KetQuaPhanTich(
            yeu_cau=replace(goc, **thay_doi),  # type: ignore[arg-type]
            truong_suy_doan=tuple(doan),
            chi_co_regex=False,
        )
    )
