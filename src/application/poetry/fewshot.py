"""Chọn ví dụ mẫu — §26 zero-shot · §27 one-shot · §28 few-shot.

════ CHỌN THEO GÌ ════

§28 nói chọn theo `poetry_form · topic · style · mood · structure`. Plan này thêm
một tiêu chí mà tài liệu đích không có, và nó quan trọng nhất trong bốn:

    **cùng SỐ DÒNG và cùng PHỐI KHUÔN với kế hoạch**

Lý do đo được: tầng 4 (thanh luật) chặn 55,29% corpus — đó là nút cổ chai thật của
hệ thống. Mô hình học khuôn `B T B` / `T B T` từ một bài mẫu CÙNG phối khuôn thì
dễ hơn nhiều so với học từ một câu mô tả trong prompt. Đây là đối sách trực tiếp
cho rủi ro R2 của plan.

════ BA CHẾ ĐỘ, CHỌN THEO ĐỘ PHỨC TẠP YÊU CẦU ════

    zero-shot  §26  yêu cầu đơn giản, ràng buộc rõ, không đòi phong cách riêng
    one-shot   §27  cần ghim MỘT khuôn mẫu cụ thể
    few-shot   §28  yêu cầu phức tạp — nhiều ràng buộc cùng lúc

Không chọn few-shot cố định (§28 dặn thẳng). Và không phải cứ nhiều ví dụ là tốt:
mỗi ví dụ tốn token, và ví dụ lệch chủ đề còn kéo mô hình đi sai hướng.

⛔ BẤT BIẾN KHÔNG ĐƯỢC PHÁ: mọi ví dụ đi vào prompt đều phải ĐÚNG LUẬT. `MauTho`
chỉ dựng được từ bài đã qua `kiem_tra_bai_tho`, nên bất biến này được giữ bởi
KIỂU DỮ LIỆU chứ không bởi kỷ luật của người viết code.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal, TypeAlias

from application.poetry.dataset import MauTho, tu_khoa_yeu_cau
from application.poetry.plan import PoetryPlan
from application.poetry.requirement import PoetryRequirement

CheDo: TypeAlias = Literal["zero_shot", "one_shot", "few_shot"]

SO_VI_DU_TOI_DA = 3


@dataclass(frozen=True, slots=True)
class ViDuDuocChon:
    """Một ví dụ, kèm LÝ DO nó được chọn.

    Lý do không phải trang trí: khi chất lượng đầu ra tụt, câu hỏi đầu tiên là
    "mô hình đã nhìn thấy ví dụ nào". Không ghi lý do thì không trả lời được.
    """

    mau: MauTho
    diem: int
    ly_do: tuple[str, ...]


def _cham_diem(
    mau: MauTho, *, tu_khoa: frozenset[str], so_dong_muon: int | None
) -> ViDuDuocChon:
    """Thang điểm cộng dồn, cố ý đơn giản và giải thích được.

    Trọng số KHÔNG được chọn bằng cách thử cho tới khi số liệu đẹp — đó là sai lầm
    §1.1 của plan luật. Thứ tự ưu tiên ở đây suy từ một sự thật đo được: cổng 4
    chặn 55,29% corpus, còn chủ đề thì không chặn bài nào. Nên cấu trúc đứng trước
    chủ đề.
    """
    diem = 0
    ly_do: list[str] = []

    if so_dong_muon is not None and mau.so_dong == so_dong_muon:
        diem += 4
        ly_do.append(f"cùng {so_dong_muon} dòng")

    giao = tu_khoa & mau.tu_khoa
    if giao:
        diem += min(3, len(giao))
        ly_do.append(f"chung chủ đề: {', '.join(sorted(giao)[:3])}")

    # Bài chia khổ đều 4 dòng là khuôn dễ học nhất, và cũng là khổ phổ biến nhất
    # theo S17 của tài liệu luật.
    if mau.so_kho > 1 and mau.so_dong % 4 == 0:
        diem += 1
        ly_do.append(f"chia {mau.so_kho} khổ")

    return ViDuDuocChon(mau=mau, diem=diem, ly_do=tuple(ly_do))


def chon_che_do(req: PoetryRequirement) -> CheDo:
    """§26–28. Độ phức tạp đo bằng SỐ RÀNG BUỘC người dùng thực sự nêu ra.

    Đếm ràng buộc thay vì đọc độ dài câu chữ: một yêu cầu dài dòng nhưng chỉ có
    chủ đề vẫn là yêu cầu đơn giản.
    """
    rang_buoc = sum(
        1
        for t in (req.cam_xuc, req.phong_cach, req.rang_buoc_van, req.rang_buoc_thanh)
        if t.nguon == "nguoi_dung" and t.co_gia_tri
    )
    if rang_buoc == 0:
        return "zero_shot"
    if rang_buoc == 1:
        return "one_shot"
    return "few_shot"


def chon_vi_du(
    kho: Sequence[MauTho],
    req: PoetryRequirement,
    *,
    ke_hoach: PoetryPlan | None = None,
    che_do: CheDo | None = None,
    toi_da: int = SO_VI_DU_TOI_DA,
) -> tuple[ViDuDuocChon, ...]:
    """Chọn ví dụ cho một yêu cầu. Kho rỗng -> trả rỗng, KHÔNG ném lỗi.

    Không ném lỗi là có chủ ý: §32 quy định *"Retrieval Failure -> Zero-shot
    generation -> Verification"*. Thiếu ví dụ làm bài khó hơn, không làm hệ thống
    hỏng — vòng ngoài vẫn bảo đảm không có bài sai luật đi ra.
    """
    cd = che_do or chon_che_do(req)
    if cd == "zero_shot" or not kho or toi_da <= 0:
        return ()

    so_can = 1 if cd == "one_shot" else toi_da
    so_dong_muon = ke_hoach.tong_so_dong if ke_hoach and ke_hoach.kho else req.so_dong_int
    tu_khoa = tu_khoa_yeu_cau(
        req.chu_de.gia_tri if isinstance(req.chu_de.gia_tri, str) else None,
        req.cam_xuc.gia_tri if isinstance(req.cam_xuc.gia_tri, str) else None,
    )

    cham = [_cham_diem(m, tu_khoa=tu_khoa, so_dong_muon=so_dong_muon) for m in kho]
    # Sắp xếp TẤT ĐỊNH: điểm giảm dần, rồi id tăng dần. Thiếu khoá phụ thì hai lần
    # chạy trên cùng dữ liệu có thể cho ra hai bộ ví dụ khác nhau, và khi đó không
    # ai tái lập được một kết quả sinh thơ.
    cham.sort(key=lambda x: (-x.diem, x.mau.id))

    # Bỏ ví dụ không có điểm nào: nó không giống yêu cầu ở bất kỳ chiều nào, đưa
    # vào chỉ tốn token và có thể kéo mô hình lệch hướng.
    co_ich = [c for c in cham if c.diem > 0]
    return tuple(co_ich[:so_can])


def dung_khoi_vi_du(cac_vi_du: Sequence[ViDuDuocChon]) -> str:
    """Dựng khối văn bản đưa vào prompt.

    §9.4 dặn *"Không copy nguyên bài thơ nếu không cần thiết"*. Với few-shot thì
    NGUYÊN BÀI chính là thứ cần thiết — mô hình phải thấy đủ 7 tiếng mỗi dòng và
    khuôn thanh trải suốt bài. Cắt đôi bài mẫu là dạy một khuôn không tồn tại.

    Đổi lại, số lượng bị giới hạn ở `SO_VI_DU_TOI_DA` và mỗi bài đều được ghi
    nguồn bằng id, để truy lại được bài nào đã vào prompt nào.
    """
    if not cac_vi_du:
        return ""
    khuc = ["Dưới đây là các bài ĐÚNG LUẬT để bạn nhìn khuôn. KHÔNG chép lại chữ nào."]
    for i, vd in enumerate(cac_vi_du, start=1):
        m = vd.mau
        khuc.append("")
        khuc.append(f"--- Mẫu {i} (id={m.id}; {m.so_dong} dòng / {m.so_kho} khổ) ---")
        khuc.append(m.tho)
    return "\n".join(khuc)
