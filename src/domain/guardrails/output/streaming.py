"""Rào chắn đầu ra cho luồng SSE — vá lỗ hổng `stream=true` bỏ qua output rails.

════ LỖ HỔNG ĐÃ CÓ, VÀ VÌ SAO NÓ NGUY HIỂM ════

`routers/chat.py` chạy `enforce_output_guardrails` ở nhánh non-streaming, nhưng
nhánh `req.stream` thì yield thẳng `chunk.delta` ra SSE. Nghĩa là **bật stream là
tắt rào chắn đầu ra** — và stream thường là chế độ mặc định của client.

Đây không phải tính năng thiếu. Đây là một rào chắn có thật bị đi vòng bằng một cờ.

════ RÀNG BUỘC VẬT LÝ: BYTE ĐÃ GỬI KHÔNG THU VỀ ĐƯỢC ════

Vì vậy "kiểm ở cuối luồng" KHÔNG phải là cách vá. Khi kiểm xong thì người dùng đã
đọc hết rồi. Mọi thiết kế ở đây phải xuất phát từ ràng buộc ấy.

Cách vá: **CỬA SỔ GIỮ LẠI**. Guard luôn giữ lại `cua_so_giu_lai` ký tự cuối chưa
phát, và chỉ phát phần đã nằm trọn trong vùng đã soi. Nhờ vậy một mẫu bị cắt đôi
giữa hai chunk vẫn bị bắt TRƯỚC khi nửa đầu kịp đi ra.

    chunk 1: "Liên hệ nguyen@vi"      -> giữ lại, chưa phát
    chunk 2: "du.com nhé"             -> ghép lại, thấy email, che, rồi mới phát

Giá phải trả là độ trễ: người dùng thấy chữ chậm hơn `cua_so_giu_lai` ký tự. Đó là
đánh đổi có chủ ý — chậm vài chục ký tự đổi lấy việc không rò dữ liệu.

⚠️ HẠN CHẾ PHẢI BIẾT, ghi ra chứ không giấu: mẫu DÀI HƠN cửa sổ giữ lại vẫn có thể
lọt. Với cửa sổ mặc định 128 ký tự, mọi mẫu PII hiện có (email, điện thoại, thẻ,
CCCD) đều ngắn hơn nhiều. Nhưng một mẫu tương lai dài hơn thì phải tăng cửa sổ —
không có cách nào vừa phát sớm vừa bắt được mẫu dài vô hạn.

Độc tố thì kiểm trên TOÀN BỘ văn bản tích luỹ ở mỗi lần nạp, vì nó là phán quyết
cấp văn bản chứ không cấp ký tự: chặn được lúc nào thì chặn ngay lúc đó.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias

from domain.guardrails.input.pii import mask_pii

from .citation import validate_citations
from .toxicity import check_toxicity

# Dài hơn mọi mẫu PII hiện có (email dài nhất trong thực tế ~64, thẻ có dấu cách 19).
CUA_SO_GIU_LAI_MAC_DINH = 128


@dataclass(frozen=True, slots=True)
class PhatRa:
    """Phần văn bản đã qua rào, được phép gửi đi. `text` rỗng = chưa có gì để gửi."""

    text: str


@dataclass(frozen=True, slots=True)
class Chan:
    """Rào chắn chặn. Từ đây trở đi KHÔNG được gửi thêm gì ngoài thông báo lỗi."""

    ly_do: str


KetQuaNap: TypeAlias = PhatRa | Chan


class StreamingOutputGuard:
    """Rào chắn tăng dần cho một luồng đầu ra.

    Có TRẠNG THÁI và dùng cho đúng MỘT luồng — không chia sẻ giữa các request.

    Vòng đời:
        g = StreamingOutputGuard(valid_chunk_ids=[...])
        for chunk in luong:  kq = g.nap(chunk.delta)   -> PhatRa | Chan
        kq = g.ket_thuc()                              -> PhatRa | Chan
    """

    def __init__(
        self,
        valid_chunk_ids: list[str] | None = None,
        *,
        cua_so_giu_lai: int = CUA_SO_GIU_LAI_MAC_DINH,
    ) -> None:
        self._valid_chunk_ids = valid_chunk_ids or []
        self._cua_so = max(0, cua_so_giu_lai)
        self._tich_luy = ""
        self._da_phat = ""
        self._da_chan = False

    @property
    def toan_van(self) -> str:
        """Toàn bộ văn bản mô hình đã sinh, KỂ CẢ phần chưa phát."""
        return self._tich_luy

    @property
    def da_chan(self) -> bool:
        return self._da_chan

    def nap(self, delta: str) -> KetQuaNap:
        """Nạp một mẩu từ mô hình, nhận về phần được phép gửi đi."""
        if self._da_chan:
            return Chan(ly_do="luồng đã bị chặn trước đó")

        self._tich_luy += delta

        # 1. Độc tố: phán quyết cấp văn bản, kiểm trên toàn bộ phần đã tích luỹ.
        tox = check_toxicity(self._tich_luy)
        if tox.is_toxic:
            self._da_chan = True
            return Chan(ly_do="Violated toxicity safety policy")

        # 2. Chỉ xét phần đã ra khỏi cửa sổ giữ lại.
        gioi_han = len(self._tich_luy) - self._cua_so
        if gioi_han <= 0:
            return PhatRa(text="")

        an_toan = mask_pii(self._tich_luy[:gioi_han]).masked_text

        # 3. Che PII làm đổi độ dài, nên không thể cắt theo chỉ số của văn bản gốc.
        #    So bằng TIỀN TỐ: phần đã phát phải vẫn là tiền tố của phần đã che.
        if not an_toan.startswith(self._da_phat):
            # Một mẫu hoàn tất VẮT QUA ranh giới đã phát -> không thu byte về được.
            # Chặn là lựa chọn đúng duy nhất còn lại. Xảy ra khi mẫu dài hơn cửa sổ.
            self._da_chan = True
            return Chan(
                ly_do=(
                    "Phát hiện dữ liệu nhạy cảm vắt qua phần đã gửi — "
                    "mẫu dài hơn cửa sổ giữ lại"
                )
            )

        moi = an_toan[len(self._da_phat):]
        self._da_phat = an_toan
        return PhatRa(text=moi)

    def ket_thuc(self) -> KetQuaNap:
        """Xả nốt phần còn giữ lại, sau khi soi lần cuối trên toàn văn."""
        if self._da_chan:
            return Chan(ly_do="luồng đã bị chặn trước đó")

        tox = check_toxicity(self._tich_luy)
        if tox.is_toxic:
            self._da_chan = True
            return Chan(ly_do="Violated toxicity safety policy")

        an_toan = mask_pii(self._tich_luy).masked_text
        if not an_toan.startswith(self._da_phat):
            self._da_chan = True
            return Chan(ly_do="Phát hiện dữ liệu nhạy cảm vắt qua phần đã gửi")

        moi = an_toan[len(self._da_phat):]
        self._da_phat = an_toan
        return PhatRa(text=moi)

    def kiem_trich_dan(self) -> list[str]:
        """Trích dẫn bịa ra trong toàn văn. Chỉ để BÁO CÁO, không chặn.

        Không chặn là có chủ ý: trích dẫn sai là lỗi chất lượng, không phải lỗi an
        toàn, và ở luồng stream thì chặn ở cuối cũng đã muộn. Nơi chặn được thật là
        nhánh non-streaming.
        """
        return list(validate_citations(self._tich_luy, self._valid_chunk_ids).invalid_ids)
