"""Kho thơ mẫu đọc từ JSONL.

HAI NGUỒN, ƯU TIÊN THEO THỨ TỰ:

    1. datalake/corpus_tuyen/tho_mau.jsonl   tập TUYỂN, nhỏ, COMMIT ĐƯỢC
    2. datalake/analysis/bai_dat.jsonl       toàn bộ 24.366 bài, 266 MB, gitignored

Vì sao cần nguồn 1: rủi ro R4 của plan. Nguồn 2 không có trên checkout sạch, nên
nếu chỉ dựa vào nó thì few-shot im lặng tắt trên mọi máy mới — và không ai biết,
vì hệ thống vẫn chạy (lùi về zero-shot đúng theo §32).

Tệp tuyển được sinh bằng `datalake/scripts/tuyen_tho_mau.py`, có phương pháp lấy
mẫu ghi rõ trong đó.

⛔ KHÔNG BAO GIỜ TIN NHÃN TRONG TỆP. `tu_ban_ghi()` chạy lại `kiem_tra_bai_tho`
cho từng bài; bài nào không đạt thì bị loại lặng lẽ khỏi kho. Tệp có thể cũ hơn
`rule.py`, và dạy mô hình bằng ví dụ sai là kiểu hỏng không để lại dấu vết.
"""

from __future__ import annotations

import json
from pathlib import Path

from application.poetry.dataset import MauTho, tu_ban_ghi


def duong_dan_mac_dinh(goc_du_an: Path) -> tuple[Path, ...]:
    return (
        goc_du_an / "datalake" / "corpus_tuyen" / "tho_mau.jsonl",
        goc_du_an / "datalake" / "analysis" / "bai_dat.jsonl",
    )


class JsonlPoemCorpus:
    """Nạp MỘT LẦN rồi giữ trong bộ nhớ; nạp lười tới lần gọi đầu tiên.

    Nạp lười vì container được dựng ở mọi tiến trình, kể cả worker không bao giờ
    làm thơ — đọc 266 MB lúc khởi động là bắt mọi tiến trình trả giá cho một tính
    năng mà phần lớn trong số chúng không dùng.
    """

    def __init__(self, duong_dan: tuple[Path, ...], *, gioi_han: int = 2000) -> None:
        self._duong_dan = duong_dan
        # Trần số bài nạp. Bộ chọn chấm điểm toàn kho, nên kho càng lớn mỗi lần
        # chọn càng chậm — mà giá trị tăng thêm thì tắt dần. 2000 bài đã phủ đủ
        # các cỡ 4/8/12/16 dòng.
        self._gioi_han = gioi_han
        self._kho: tuple[MauTho, ...] | None = None

    def tat_ca(self) -> tuple[MauTho, ...]:
        if self._kho is None:
            self._kho = self._nap()
        return self._kho

    def _nap(self) -> tuple[MauTho, ...]:
        for tep in self._duong_dan:
            if tep.exists():
                return self._doc(tep)
        # Không có nguồn nào: kho rỗng, few-shot tự lùi về zero-shot (§32).
        return ()

    def _doc(self, tep: Path) -> tuple[MauTho, ...]:
        ra: list[MauTho] = []
        with tep.open(encoding="utf-8") as f:
            for dong in f:
                dong = dong.strip()
                if not dong:
                    continue
                try:
                    ban_ghi = json.loads(dong)
                except json.JSONDecodeError:
                    # Một dòng hỏng không được làm hỏng cả kho.
                    continue
                mau = tu_ban_ghi(ban_ghi)
                if mau is not None:
                    ra.append(mau)
                if len(ra) >= self._gioi_han:
                    break
        return tuple(ra)
