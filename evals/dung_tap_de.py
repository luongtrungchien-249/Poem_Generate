"""DỰNG TẬP ĐỀ CỐ ĐỊNH — Plan_PoeTone GĐ0.1.

    python evals/dung_tap_de.py

Ghi `evals/datasets/de_danh_gia.jsonl`: 200 đề, mỗi đề một `chu_de` và một
`so_dong ∈ {4, 8, 12, 16, 20}`, đúng 40 đề mỗi độ dài.

════ BẤT BIẾN ════

1. **Tất định.** Cùng nguồn, cùng `HAT_GIONG` thì cùng tập đề. Tập đề là mẫu số của
   mọi phép so sánh A/B về sau; đổi nó là đổi thước đo giữa chừng.
2. **Không bao giờ** dùng 200 đề này để chọn ví dụ mẫu, dựng thi liệu hay huấn
   luyện. `tests/unit/application/test_tap_de.py` ghim điều đó.

════ NGUỒN CHỦ ĐỀ ════

    generate_poem.jsonl   105 chủ đề không trùng (trường `topic`)
    do_that.py            12 chủ đề
    CHU_DE_BO_SUNG        phần còn thiếu, viết tay để phủ nhóm mà hai nguồn trên
                          ít có: lao động, thành thị, lịch sử, gia đình, tuổi trẻ

`generate_poem.jsonl` có một bản ghi hỏng JSON (dòng 19, `analysis_generate.md` §0),
nên chủ đề được rút bằng biểu thức chính quy, không bằng `json.loads`.
"""

from __future__ import annotations

import json
import random
import re
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC))

from evals.do_that import DE_BAI  # noqa: E402

HAT_GIONG = 20260926
SO_DE = 200
DO_DAI = (4, 8, 12, 16, 20)
RA = GOC / "evals" / "datasets" / "de_danh_gia.jsonl"
NGUON_SINH = GOC / "datalake" / "generate" / "generate_poem.jsonl"

CHU_DE_BO_SUNG: tuple[str, ...] = (
    "người công nhân tan ca đêm", "bác nông dân ra đồng sớm", "tiếng búa lò rèn",
    "chợ phiên vùng cao", "người lái đò trên sông vắng", "cô giáo vùng xa",
    "người lính gác biển đảo", "phố cổ Hội An", "ga tàu cuối năm", "chuyến xe khách đêm",
    "khu tập thể cũ", "góc phố mùa đông", "quán cà phê vỉa hè", "ánh đèn đô thị",
    "căn phòng trọ sinh viên", "bến Nhà Rồng", "thành cổ Quảng Trị", "cột cờ Lũng Cú",
    "sông Bạch Đằng", "Điện Biên năm ấy", "Trường Sơn đông nắng tây mưa",
    "nghĩa trang liệt sĩ", "bữa cơm gia đình", "ông nội bên hiên", "bàn tay cha",
    "mái tóc bà", "đứa em nhỏ", "ngày cưới", "đứa con đầu lòng", "căn bếp mẹ",
    "tuổi mười tám", "mùa thi", "sân trường ngày chia tay", "chiếc xe đạp cũ",
    "tình bạn học trò", "lần đầu xa nhà", "Tết Nguyên Đán", "đêm giao thừa",
    "Trung thu phố cổ", "rằm tháng bảy", "hội làng mùa xuân", "hoa đào Nhật Tân",
    "hoa sữa cuối thu", "hoa phượng tháng năm", "cánh đồng lúa chín", "rừng thông Đà Lạt",
    "biển Nha Trang", "ruộng bậc thang", "thác nước đầu nguồn", "đỉnh Fansipan",
    "vịnh Hạ Long", "cơn bão miền Trung", "hạn mặn đồng bằng", "đàn cò trắng",
    "tiếng gà trưa", "cánh diều tuổi thơ", "giếng làng", "cây đa đầu làng",
    "con trâu và bờ tre", "gánh hàng rong", "ly biệt sân ga", "thư tay ngày cũ",
    "lời hẹn không thành", "mối tình đầu", "ngày trở về", "người đi xa không về",
    "tuổi già cô đơn", "bệnh viện đêm khuya", "thời gian trôi", "ý nghĩa của sự chờ đợi",
    "lẽ vô thường", "cái thiện và cái ác", "bình yên trong tâm", "con đường phía trước",
    "hạt mưa và biển", "ngọn nến trong đêm", "chiếc lá cuối cùng", "tiếng chuông chùa",
    "sương sớm trên đồi", "ánh trăng quê", "ngôi sao xa", "mùa đông không lạnh",
    "đồng hồ quả lắc", "cánh cửa khép hờ", "người thợ may", "người bán vé số",
    "đứa trẻ bán báo", "mùa nước nổi", "cầu tre lắt lẻo", "dòng Mekong",
)


def _chu_de_nguon() -> list[str]:
    tu_sinh = re.findall(r'"topic":\s*"([^"]+)"', NGUON_SINH.read_text(encoding="utf-8"))
    tat_ca = [*tu_sinh, *(c for c, _ in DE_BAI), *CHU_DE_BO_SUNG]
    thay: set[str] = set()
    duy_nhat: list[str] = []
    for c in tat_ca:
        khoa = c.strip().lower()
        if khoa and khoa not in thay:
            thay.add(khoa)
            duy_nhat.append(c.strip())
    return duy_nhat


def dung_tap_de() -> list[dict[str, object]]:
    chu_de = _chu_de_nguon()
    if len(chu_de) < SO_DE:
        raise SystemExit(f"chỉ có {len(chu_de)} chủ đề không trùng, cần {SO_DE}")
    rng = random.Random(HAT_GIONG)
    rng.shuffle(chu_de)
    return [
        {"id": f"de-{i:03d}", "chu_de": c, "so_dong": DO_DAI[i % len(DO_DAI)]}
        for i, c in enumerate(chu_de[:SO_DE])
    ]


def main() -> int:
    de = dung_tap_de()
    RA.write_text(
        "".join(json.dumps(d, ensure_ascii=False) + "\n" for d in de), encoding="utf-8"
    )
    print(f"{len(de)} đề -> {RA.relative_to(GOC)}  (hạt giống {HAT_GIONG})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
