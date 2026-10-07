"""PHÁT HIỆN CHÉP — Plan_PoeTone GĐ1.3, QĐ-P2 (chủ dự án chốt 26/09/2026).

    Bài có ÍT NHẤT MỘT DÒNG trùng nguyên văn một dòng thơ đã có -> CHẶN.

════ VÌ SAO LÀ "MỘT DÒNG" CHỨ KHÔNG PHẢI MỘT TỈ LỆ ════

Với thể 7 tiếng, "7-gram trùng" gần như đồng nghĩa với "trùng nguyên một dòng". Một
dòng là đơn vị nhỏ nhất có nghĩa của việc chép — "chép một câu thơ" — nên đây là số
nguyên có nghĩa, không phải ngưỡng dò được (G11). Mọi tỉ lệ kiểu "trùng quá 30%"
đều phải có người chốt con số, và chưa ai chốt.

════ CHUẨN HOÁ ════

Khoá là dãy tiếng của `rule.tach_tieng`, hạ chữ thường, nối bằng một dấu cách: bỏ
qua dấu câu và hoa thường, GIỮ dấu thanh. Đổi thanh là đổi chữ ("mà" ≠ "má"), nên
đổi thanh không còn là chép nguyên văn.

Chỉ dòng ĐÚNG 7 TIẾNG mới vào chỉ mục và mới được tra: dòng khác độ dài không thể
là một dòng của bài đạt luật, nên tra nó chỉ tốn bộ nhớ.

⛔ File này KHÔNG sửa văn bản thơ. Nó chỉ chỉ ra dòng nào trùng, và trùng với đâu.
"""

from __future__ import annotations

from application.ports.chi_muc_tho import ChiMucDongThoPort, NguonDong
from application.rule import tach_tieng

SO_TIENG = 7
MA_LOI = "CHEP"


def khoa_dong(dong: str) -> str | None:
    """Khoá tra của một dòng; None nếu dòng không đúng 7 tiếng."""
    tieng = tach_tieng(dong)
    if len(tieng) != SO_TIENG:
        return None
    return " ".join(t.lower() for t in tieng)


def tim_dong_chep(
    van_ban: str, chi_muc: ChiMucDongThoPort | None
) -> tuple[tuple[int, str, NguonDong], ...]:
    """Mọi dòng trùng nguyên văn, dạng (số dòng tính từ 1, dòng, nguồn).

    Không có chỉ mục -> trả rỗng. Đó là "không kiểm được", không phải "không chép":
    người gọi muốn phân biệt thì kiểm `chi_muc is None` trước.
    """
    if chi_muc is None:
        return ()
    ra: list[tuple[int, str, NguonDong]] = []
    so = 0
    for dong in van_ban.splitlines():
        if not dong.strip():
            continue
        so += 1
        khoa = khoa_dong(dong)
        if khoa is None:
            continue
        nguon = chi_muc.tim(khoa)
        if nguon is not None:
            ra.append((so, dong.strip(), nguon))
    return tuple(ra)
