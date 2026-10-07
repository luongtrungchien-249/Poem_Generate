"""IN RA ĐÚNG CHUỖI MÀ HỆ THỐNG GỬI CHO MÔ HÌNH KHI SINH THƠ.

════ VÌ SAO FILE NÀY TỒN TẠI ════

Ngày 22/09/2026, chủ dự án ghép `prompting/system.py` + `prompting/instructions.py`
thành System Instruction, đưa cho Gemma trên Google AI, sinh 200 bài.
Kết quả: **1/200 đạt (0,50 %)**.

Nguyên nhân KHÔNG phải mô hình kém. Hai file ấy **cố ý không chứa một chữ luật thơ
nào** — và đó là thiết kế, có test cưỡng chế:

    system.py       "KHÔNG MỘT CHỮ LUẬT THƠ NÀO Ở ĐÂY"
    instructions.py "File NÀY không chép một chữ luật nào"

Luật thơ có đúng MỘT nguồn: `rule.LUAT`. `poetry/prompt.py` sinh chỉ dẫn từ bảng
đó lúc import, nên prompt không bao giờ lệch khỏi bộ kiểm.

Hệ quả của việc ghép tay: Gemma chưa bao giờ được cho biết bài thơ phải như thế
nào — không ai nói mỗi dòng 7 tiếng, không ai đưa khuôn B T B / T B T, không ai
dạy tra thanh theo dấu.

Script này tồn tại để chuyện đó không lặp lại: cần prompt đem sang nền tảng khác
thì CHẠY NÓ, đừng ghép tay từ mấy file nguồn.

CHẠY
    python datalake/scripts/xuat_prompt_sinh_tho.py
    python datalake/scripts/xuat_prompt_sinh_tho.py --chu-de "mùa thu" --so-dong 20
    python datalake/scripts/xuat_prompt_sinh_tho.py --ra prompt.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from application.poetry.planner import lap_ke_hoach_hop_le  # noqa: E402
from application.poetry.prompt import dung_luot_yeu_cau  # noqa: E402
from application.poetry.requirement import PoetryRequirement, Truong  # noqa: E402


def _doc_tham_so() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="In chuỗi prompt sinh thơ THẬT SỰ mà hệ thống gửi cho mô hình."
    )
    p.add_argument("--chu-de", default="mùa thu trên phố cũ")
    p.add_argument("--so-dong", type=int, default=20, help="số dòng của bài")
    p.add_argument("--cam-xuc", default="")
    p.add_argument("--phong-cach", default="")
    p.add_argument("--ra", type=Path, default=None, help="ghi ra tệp thay vì in")
    return p.parse_args()


def main() -> int:
    a = _doc_tham_so()
    trong = PoetryRequirement()
    req = PoetryRequirement(
        chu_de=Truong(gia_tri=a.chu_de, nguon="nguoi_dung"),
        so_dong=Truong(gia_tri=a.so_dong, nguon="nguoi_dung"),
        cam_xuc=(
            Truong(gia_tri=a.cam_xuc, nguon="nguoi_dung") if a.cam_xuc else trong.cam_xuc
        ),
        phong_cach=(
            Truong(gia_tri=a.phong_cach, nguon="nguoi_dung")
            if a.phong_cach
            else trong.phong_cach
        ),
    )

    # KIỂM SỐ DÒNG BẰNG CHÍNH BỘ KIỂM, KHÔNG VIẾT LẠI ĐIỀU KIỆN.
    #
    # Bản đầu của script này tự viết `if a.so_dong % 4 != 0` kèm thông báo nhắc
    # tên điều luật — tức là chép luật lần nữa, đúng thứ nó sinh ra để chặn. Nay
    # nó HỎI kế hoạch: `lap_ke_hoach_hop_le` trả None khi yêu cầu không hợp luật,
    # và điều kiện ấy chỉ có một nguồn.
    if lap_ke_hoach_hop_le(req) is None:
        raise SystemExit(
            f"--so-dong {a.so_dong} không hợp luật. "
            f"Xem `application.rule.LUAT` để biết ràng buộc số dòng."
        )

    # Đúng hàm mà `sinh_theo_kho` gọi — không dựng lại chuỗi ở đây, vì dựng lại là
    # tạo nguồn thứ hai, đúng thứ sự cố 22/09 sinh ra từ đó.
    chuoi = dung_luot_yeu_cau(req)

    if a.ra:
        a.ra.write_text(chuoi, encoding="utf-8")
        print(f"-> {a.ra}  ({len(chuoi)} ký tự)")
    else:
        print(chuoi)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
