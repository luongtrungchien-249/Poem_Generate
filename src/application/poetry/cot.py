"""CHAIN-OF-THOUGHT CÓ CẤU TRÚC — bật khi chất lượng chưa đạt.

    *"nếu không đạt được thì cần Chain-of-thought trước khi trả ra kết quả."*
    — chủ dự án, 21/09/2026

════ ĐÂY LÀ LOẠI CoT NÀO ════

Structured Reasoning theo §29 của tài liệu đích, KHÔNG phải private chain-of-thought.
§29 nói rõ: *"Không yêu cầu Agent xuất Chain-of-Thought"*, và các artifact có cấu
trúc là *"operational state, không phải private chain-of-thought"*.

Hai điều đó không chọi với chỉ thị 3: chỉ thị đòi mô hình PHẢI SUY LUẬN CÓ KỶ LUẬT
trước khi viết lại, chứ không đòi phơi dòng suy nghĩ nội tại ra cho người dùng.

════ BẬT KHI NÀO — và vì sao không bật lúc nào ════

    luật trượt          -> KHÔNG bật. Biên bản đã chỉ thẳng "D3 thừa 1 tiếng".
                           Bắt suy luận thêm về một lỗi đã có địa chỉ là tốn tiền.

    chất lượng trượt    -> BẬT. Lỗi khuếch tán, không có dòng nào "sai" cả; mô hình
                           phải tự tìm ra chỗ hỏng mới sửa được.

    cả hai trượt        -> biên bản luật trước, CoT sau. Sửa cái có địa chỉ trước.

    lặp / không tiến bộ -> BẬT bất kể loại lỗi. `verify_output` đã phát hiện được
                           hai trạng thái này (chặn G5 và G6); chúng nghĩa là cách
                           sửa hiện tại không ăn, nên phải đổi cách nghĩ chứ không
                           phải xin lại y hệt.
"""

from __future__ import annotations

from application.poetry.quality import KetQuaChatLuong

THE_CoT = "khung_suy_luan"


def can_bat_cot(
    *,
    dat_luat: bool,
    dat_chat_luong: bool,
    lap_lai: bool = False,
    khong_tien_bo: bool = False,
) -> bool:
    """Bốn nhánh của bảng trên, viết thành một vị từ."""
    if lap_lai or khong_tien_bo:
        return True
    if not dat_chat_luong:
        return True
    # Luật trượt mà chất lượng đạt: biên bản luật đã đủ cụ thể.
    _ = dat_luat
    return False


def dung_khung_suy_luan(
    kq: KetQuaChatLuong,
    *,
    dong_dat: tuple[int, ...] = (),
    ly_do_khac: str = "",
) -> str:
    """Bốn ô mô hình phải điền TRƯỚC khi được viết lại.

    Ô 3 cấm viết thơ là có chủ đích: tách *quyết định sửa gì* khỏi *viết câu chữ*.
    Trộn hai việc lại thì mô hình nhảy thẳng vào viết và bỏ qua phần chẩn đoán.

    Ô 4 chống đúng kiểu hỏng đã biết — mô hình viết lại cả bài rồi làm hỏng dòng
    đang đúng, khiến vòng sửa quay vòng mà không hội tụ.

    🩸 LỖI ĐÃ SỬA — ghi lại để không lặp. Bản đầu nhận `dong_dat` là MỌI dòng của
    bài rồi in thẳng vào ô 4. Với lỗi trùng dòng, khung hoá ra bảo mô hình *"giữ
    nguyên cả 8 dòng"* trong khi lỗi chính là có dòng phải đổi — một chỉ dẫn tự
    mâu thuẫn, và mô hình không có cách nào tuân theo.

    Nay ô 4 trừ đi các dòng bị chiều hỏng quy trách nhiệm, và khi lỗi khuếch tán
    ra cả bài (`lap_tieng`) thì nói thẳng là không ghim được dòng nào — thà nói
    "không biết" còn hơn đưa một danh sách sai.
    """
    hong = kq.chieu_hong
    if hong:
        mo_ta = "; ".join(f"{c.ten} = {c.so_do} (cần {c.nguong})" for c in hong)
    else:
        mo_ta = ly_do_khac or "vòng sửa không tiến bộ hoặc đang lặp lại bản nháp cũ"

    bi_quy = kq.dong_bi_quy_trach_nhiem
    con_giu = tuple(d for d in dong_dat if d not in bi_quy)

    if kq.co_loi_khuech_tan and hong:
        ds_dat = (
            "(lỗi khuếch tán ra cả bài — không ghim được dòng nào; "
            "tự chọn dòng cần đổi, và đổi ít nhất có thể)"
        )
    elif con_giu:
        ds_dat = " ".join(f"D{i}" for i in con_giu) + (
            f"  ·  PHẢI ĐỔI: {' '.join(f'D{i}' for i in sorted(bi_quy))}" if bi_quy else ""
        )
    else:
        ds_dat = "(chưa có dòng nào đạt)"

    khung = [
        "Bài đúng luật nhưng CHƯA ĐẠT CHẤT LƯỢNG." if kq.chieu_hong else "Vòng sửa đang bế tắc.",
        "",
        "Trước khi viết lại, hãy điền đủ bốn ô sau. KHÔNG viết thơ ở ô 1–3.",
        "",
        f"<{THE_CoT}>",
        f"1. CHIỀU CHƯA ĐẠT      : {mo_ta}",
        "2. NGUYÊN NHÂN         : <vì sao bài hiện tại không đạt chiều đó>",
        "3. HƯỚNG SỬA           : <sửa thế nào — mô tả cách làm, KHÔNG viết câu thơ>",
        f"4. DÒNG PHẢI GIỮ NGUYÊN: {ds_dat}",
        f"</{THE_CoT}>",
        "",
        "Điền xong bốn ô rồi mới viết bài hoàn chỉnh bên dưới khung.",
    ]
    if kq.chieu_khong_do_duoc:
        khung.insert(
            3,
            "Lưu ý: "
            + ", ".join(kq.chieu_khong_do_duoc)
            + " không kiểm được bằng thuật toán — đừng cố tối ưu riêng chúng.",
        )
    return "\n".join(khung)


def da_dien_khung(van_ban: str) -> bool:
    """Mô hình đã thực sự điền khung hay chỉ viết lại bài?

    Dùng để biết vòng sửa có tuân thủ chỉ thị 3 hay không. KHÔNG dùng để chặn đầu
    ra: bài cuối cùng phải là thơ, không phải khung suy luận — nên khung được gỡ
    khỏi văn bản trước khi kiểm luật, xem `tach_tho_khoi_khung`.
    """
    return f"<{THE_CoT}>" in van_ban and f"</{THE_CoT}>" in van_ban


def tach_tho_khoi_khung(van_ban: str) -> str:
    """Gỡ khối `<khung_suy_luan>…</khung_suy_luan>` ra, giữ lại phần thơ.

    Cần thiết vì bộ kiểm luật đếm TIẾNG trên từng dòng: để nguyên khung thì mấy
    dòng chẩn đoán sẽ bị đem đi đếm âm tiết và bài nào cũng trượt H1.
    """
    mo, dong = f"<{THE_CoT}>", f"</{THE_CoT}>"
    while mo in van_ban and dong in van_ban:
        i, j = van_ban.index(mo), van_ban.index(dong) + len(dong)
        if j <= i:
            break
        van_ban = van_ban[:i] + van_ban[j:]
    return van_ban.strip()
