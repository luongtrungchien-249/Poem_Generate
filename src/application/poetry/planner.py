"""§10 PLANNER — lập kế hoạch sáng tác trước khi viết.

════ KẾ HOẠCH LÀ TẤT ĐỊNH, KHÔNG GỌI MÔ HÌNH ════

Quyết định đáng bàn nhất của file này. §10 gợi ý một Planner do LLM chạy, nhưng
mọi thứ Planner phải quyết ở thể này đều **suy ra được từ luật**:

    số khổ, kích thước khổ   suy từ `so_dong` + H4 (bội của 4) + S17 (khổ 4 dòng)
    khuôn thanh từng khổ     suy từ QĐ-2 (chỉ hai khuôn hợp lệ)
    nhịp chủ đạo             suy từ bảy kiểu của §6

Giao mấy thứ đó cho mô hình chỉ thêm một chỗ hỏng: mô hình có thể đề xuất 3 khổ ×
3 dòng = 9 dòng, vi phạm H4, rồi bước B2 chặn — tốn một lượt gọi để nhận về một kế
hoạch mà một phép chia đã trả lời được.

Phần mô hình LÀM TỐT HƠN là `mach_cam_xuc` và `hinh_anh` — những thứ không suy ra
được từ luật. Hai trường đó vì vậy nhận từ ngoài vào, và để trống vẫn hợp lệ.

════ LUÂN PHIÊN KHUÔN GIỮA CÁC KHỔ ════

Không có điều luật nào bắt các khổ phải đổi khuôn. Nhưng S2 nói *"nên luân phiên
bằng – trắc để tạo nhạc tính"*, và đó là tinh thần của cả tầng 4. Vì vậy kế hoạch
GỢI Ý luân phiên `bang / trac / bang / ...` — gợi ý, không ép: `KhoPlan.khuon` chỉ
là khai báo dự định, còn phán quyết vẫn do `rule.py` đưa ra trên bài viết xong.
"""

from __future__ import annotations

from application.poetry.plan import KhoPlan, PoetryPlan, kiem_tra_ke_hoach
from application.poetry.requirement import PoetryRequirement

# S17: "Khổ phổ biến là 4 dòng". Chia đều 4 dòng mỗi khổ là lựa chọn an toàn nhất,
# và luôn khả thi vì H4 đã bảo đảm số dòng là bội của 4.
DONG_MOI_KHO = 4

# §6 — nhịp mặc định. 4/3 là nhịp phổ biến nhất của thất ngôn; đo trên corpus, mọi
# bài đạt đều tương thích với nó (xem tầng 6 của `rule.py`).
NHIP_MAC_DINH = "4/3"


def lap_ke_hoach(
    req: PoetryRequirement,
    *,
    mach_cam_xuc: tuple[str, ...] = (),
    hinh_anh: tuple[str, ...] = (),
) -> PoetryPlan:
    """Dựng kế hoạch từ yêu cầu. THUẦN và TẤT ĐỊNH — cùng vào, cùng ra.

    Gọi hàm này KHÔNG bảo đảm kế hoạch hợp lệ: nếu `so_dong` chưa có hoặc không
    phải bội của 4 thì kế hoạch sinh ra sẽ bị `kiem_tra_ke_hoach` bắt. Đó là đúng
    — cổng B1 đã phải chặn trước đó rồi, và hàm này không được lặng lẽ sửa yêu cầu
    cho vừa luật.
    """
    n = req.so_dong_int or 0
    so_kho, du = divmod(n, DONG_MOI_KHO)

    kho: list[KhoPlan] = []
    for i in range(so_kho):
        kho.append(
            KhoPlan(
                so_dong=DONG_MOI_KHO,
                y_chinh=mach_cam_xuc[i] if i < len(mach_cam_xuc) else "",
                # Luân phiên là GỢI Ý theo tinh thần S2, không phải ràng buộc.
                khuon="bang" if i % 2 == 0 else "trac",
                nhip=NHIP_MAC_DINH,
            )
        )
    if du:
        # Giữ lại phần dư thay vì làm tròn im lặng: kế hoạch phải phản ánh đúng yêu
        # cầu, kể cả khi yêu cầu sai. `kiem_tra_ke_hoach` sẽ báo lỗi K3.
        kho.append(KhoPlan(so_dong=du, nhip=NHIP_MAC_DINH))

    chu_de = req.chu_de.gia_tri if isinstance(req.chu_de.gia_tri, str) else ""
    return PoetryPlan(
        muc_tieu=f"Bài thất ngôn tự do {n} dòng về {chu_de}" if chu_de else "",
        mach_cam_xuc=mach_cam_xuc,
        kho=tuple(kho),
        chien_luoc_van="vần chân, mỗi cụm bốn dòng có ít nhất một cặp hiệp vần (QĐ-7b)",
        chien_luoc_thanh="mọi dòng khớp khuôn B T B hoặc T B T ở P2/P4/P6 (QĐ-2)",
        hinh_anh=hinh_anh,
    )


# QĐ-KH-1 phương án B, chủ dự án chốt 21/09/2026: hai trường nội dung lấy từ YÊU
# CẦU NGƯỜI DÙNG, không thêm một lượt gọi mô hình để nghĩ hộ.
#
# 🩸 VÌ SAO CẦN HÀM NÀY. `lap_ke_hoach` nhận `mach_cam_xuc` và `hinh_anh` từ ngoài
# vào, và docstring module nói rõ đó là "phần mô hình LÀM TỐT HƠN". Nhưng đường sinh
# thơ gọi `lap_ke_hoach_hop_le(yeu_cau)` — hàm chỉ nhận `req`, không có chỗ truyền
# hai trường kia. Nên `plan.hinh_anh` LUÔN rỗng và nhánh `if plan.hinh_anh:` trong
# `mo_ta_ke_hoach_cho_mo_hinh` CHƯA BAO GIỜ chạy. Một ô trống khai báo tử tế, có lý
# do viết rõ, và không đường nào dẫn tới.
#
# GIỚI HẠN CỦA PHƯƠNG ÁN B, ghi ra chứ không giấu: `PoetryRequirement` có trường cho
# cảm xúc nhưng KHÔNG có trường nào cho hình ảnh. Nên `hinh_anh` vẫn rỗng sau thay
# đổi này — B chỉ nối được phần có nguồn. Phần hình ảnh nay do khối `CHI_DAN_CHAT_LUONG`
# ở tầng 2 đảm nhiệm: dạy mô hình cách tự chọn hình ảnh, thay vì chọn hộ nó.
def _mach_cam_xuc_tu_yeu_cau(req: PoetryRequirement) -> tuple[str, ...]:
    """Mạch cảm xúc suy từ yêu cầu. Rỗng khi người dùng không nêu.

    CỐ Ý KHÔNG tách thành nhiều ý cho từng khổ: người dùng nêu một cảm xúc thì đó
    là một cảm xúc, không phải n cảm xúc chia đều. Bịa thêm ý cho các khổ sau là
    quyết định thay tác giả — cùng lý do cổng B1 không tự chọn hộ số dòng.
    """
    gt = req.cam_xuc.gia_tri
    return (gt.strip(),) if isinstance(gt, str) and gt.strip() else ()


def lap_ke_hoach_hop_le(req: PoetryRequirement) -> PoetryPlan | None:
    """Trả kế hoạch chỉ khi nó vượt được `kiem_tra_ke_hoach`, ngược lại None.

    Dùng ở đường sinh thơ: kế hoạch hỏng thì đi tiếp KHÔNG kèm kế hoạch, thay vì
    kéo theo một kế hoạch sai làm bước B3 chặn oan mọi bản nháp.
    """
    plan = lap_ke_hoach(req, mach_cam_xuc=_mach_cam_xuc_tu_yeu_cau(req))
    return plan if not kiem_tra_ke_hoach(plan, req.so_dong_int) else None


def mo_ta_ke_hoach_cho_mo_hinh(plan: PoetryPlan) -> str:
    """Kế hoạch viết thành lời cho Writer. Rỗng khi không có kế hoạch."""
    if not plan.kho:
        return ""
    dong = [f"Kế hoạch: {len(plan.kho)} khổ, tổng {plan.tong_so_dong} dòng."]
    for i, k in enumerate(plan.kho, start=1):
        phan = [f"  Khổ {i}: {k.so_dong} dòng"]
        if k.khuon:
            phan.append(f"nên nghiêng khuôn {k.khuon}")
        if k.nhip:
            phan.append(f"nhịp {k.nhip}")
        if k.y_chinh:
            phan.append(f"ý: {k.y_chinh}")
        dong.append(" · ".join(phan))
    if plan.hinh_anh:
        dong.append(f"  Hình ảnh gợi ý: {', '.join(plan.hinh_anh)}")
    return "\n".join(dong)
