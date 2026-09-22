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

# `rule.py` ĐÓNG BĂNG: chỉ GỌI, không bao giờ viết lại phép phân tích thanh ở
# đây. Chú thích khuôn đưa vào prompt phải do CHÍNH bộ luật chấm bài sinh ra —
# nếu không, mô hình được dạy một khuôn khác với khuôn dùng để đánh trượt nó.
from application.rule import khuon_cua_dong, tach_tieng, thanh_cua

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
    khuc = [
        "Dưới đây là các bài ĐÚNG LUẬT để bạn nhìn khuôn. KHÔNG chép lại chữ nào.",
        "Sau mỗi bài có bảng chỉ ra tiếng 2·4·6 của từng dòng và khuôn của dòng đó.",
        "Bảng đó chỉ để bạn thấy khuôn nằm ở đâu. BÀI CỦA BẠN CHỈ GỒM CÁC DÒNG THƠ:",
        "không kèm bảng, không kèm chú thích, không đánh dấu B/T.",
    ]
    for i, vd in enumerate(cac_vi_du, start=1):
        m = vd.mau
        khuc.append("")
        khuc.append(f"--- Mẫu {i} (id={m.id}; {m.so_dong} dòng / {m.so_kho} khổ) ---")
        khuc.append(m.tho)
        bang = _bang_khuon(m.tho)
        if bang:
            khuc.append("khuôn của từng dòng:")
            khuc.append(bang)
    return "\n".join(khuc)


# Tên khuôn hiện cho mô hình. `khuon_cua_dong` còn trả "pha" và "khong_xac_dinh";
# hai mã đó không bao giờ xuất hiện ở đây vì mọi mẫu đều đã qua `kiem_tra_bai_tho`
# — vẫn xử lý để một mẫu hỏng không làm sập việc dựng prompt.
_TEN_KHUON = {"bang": "khuôn bằng (B T B)", "trac": "khuôn trắc (T B T)"}


def _bang_khuon(tho: str) -> str:
    """Chú thích tiếng 2·4·6 của từng dòng, tính bằng chính `rule.py`.

    VÌ SAO CHÚ THÍCH THAY VÌ ĐƯA THƠ TRẦN:

    Bài mẫu trần buộc mô hình tự suy ra khuôn `B T B` từ văn bản — đúng việc nó làm
    dở nhất, và là nguyên nhân số một khiến bài bị đánh trượt (tầng thanh luật chặn
    55,29% corpus). Chỉ thẳng ra tiếng nào mang thanh gì thì ví dụ dạy được điều nó
    cần học, thay vì chỉ cho thấy một bài thơ hay.

    Bảng để RIÊNG dưới bài, không gắn vào từng dòng thơ: gắn vào dòng thì mô hình
    bắt chước và viết chú thích vào bài của nó, mà bộ đọc kết quả chỉ lấy bốn dòng
    đầu không rỗng — một dòng chú thích lọt vào đó là hỏng cả ứng viên.
    """
    hang: list[str] = []
    for so, dong in enumerate((d for d in tho.splitlines() if d.strip()), start=1):
        tieng = tach_tieng(dong)
        ten = _TEN_KHUON.get(khuon_cua_dong(tieng))
        if ten is None:
            # Dòng không đủ 7 tiếng thì P2/P4/P6 không còn là P2/P4/P6 của thể.
            continue
        bo_ba = "  ".join(f"{tieng[i]}={thanh_cua(tieng[i])}" for i in (1, 3, 5))
        hang.append(f"  dòng {so}: {bo_ba}  -> {ten}")
    return "\n".join(hang)
