"""Hiện thực `ChiMucDongThoPort` — chỉ mục dòng thơ 7 tiếng.

════ HAI CÁCH NẠP ════

    1. TỆP DỰNG SẴN  `datalake/hf/chi_muc_dong.{bin,json}` (gitignored)
       Dựng bằng `python datalake/scripts/dung_chi_muc_dong.py`. Nạp < 1 giây.
    2. LÙI VỀ        `datalake/corpus_tuyen/tho_mau.jsonl` (commit được, nhỏ)
       Khi thiếu tệp dựng sẵn — checkout sạch, CI. Vẫn bắt được việc chép BÀI MẪU,
       kiểu chép dễ xảy ra nhất khi one-shot bật.

Vì sao không dựng từ JSONL lúc chạy: đo 26/09/2026, dựng từ đủ nguồn (547.181 dòng,
266 MB `bai_dat.jsonl` + kho HF) mất ~190 giây. Người dùng đầu tiên sau mỗi lần khởi
động không được phải chờ ba phút.

Nạp LƯỜI tới lần tra đầu tiên, như `JsonlPoemCorpus`.

Bộ nhớ: khoá băm về 8 byte, mỗi dòng giữ một số nguyên trỏ vào bảng nguồn — không
giữ nguyên chuỗi dòng thơ. Đo: ~52 MB cho 547 nghìn dòng.
"""

from __future__ import annotations

import hashlib
import json
from array import array
from collections.abc import Iterable
from pathlib import Path

from application.poetry.doi_chieu_chep import khoa_dong
from application.ports.chi_muc_tho import NguonDong


def bam_khoa(khoa: str) -> int:
    return int.from_bytes(hashlib.blake2b(khoa.encode("utf-8"), digest_size=8).digest(), "big")


def nguon_jsonl_mac_dinh(goc_du_an: Path) -> tuple[tuple[Path, str, str], ...]:
    """(tệp, tên kho, trường thơ). Thứ tự quyết định nguồn nào được ghi khi trùng."""
    hf = goc_du_an / "datalake" / "hf"
    return (
        (goc_du_an / "datalake" / "corpus_tuyen" / "tho_mau.jsonl", "tho_mau", "tho"),
        (goc_du_an / "datalake" / "analysis" / "bai_dat.jsonl", "bai_dat", "tho"),
        *(
            (hf / f"{k}_{kq}.jsonl", "hf", "poem")
            for k in ("bay_chu", "duong_luat")
            for kq in ("dat", "truot")
        ),
    )


def tep_dung_san_mac_dinh(goc_du_an: Path) -> Path:
    return goc_du_an / "datalake" / "hf" / "chi_muc_dong.bin"


def _doc_jsonl(nguon: Iterable[tuple[Path, str, str]]) -> tuple[dict[int, int], list[NguonDong]]:
    chi_muc: dict[int, int] = {}
    bang: list[NguonDong] = []
    for tep, ten_kho, truong in nguon:
        if not tep.exists():
            continue
        with tep.open(encoding="utf-8") as f:
            for dong_json in f:
                try:
                    rec = json.loads(dong_json)
                except json.JSONDecodeError:
                    continue
                tho = rec.get(truong)
                if not isinstance(tho, str):
                    continue
                i_nguon: int | None = None
                for dong in tho.splitlines():
                    khoa = khoa_dong(dong)
                    if khoa is None:
                        continue
                    h = bam_khoa(khoa)
                    if h in chi_muc:
                        continue
                    if i_nguon is None:
                        bang.append(NguonDong(
                            kho=ten_kho,
                            tieu_de=str(rec.get("title") or rec.get("tieu_de") or ""),
                            tac_gia=str(rec.get("author") or ""),
                            url=str(rec.get("url") or ""),
                        ))
                        i_nguon = len(bang) - 1
                    chi_muc[h] = i_nguon
    return chi_muc, bang


class ChiMucDongTho:
    """`ChiMucDongThoPort`. Dựng bằng một trong hai hàm tạo bên dưới."""

    def __init__(self, nap: object) -> None:
        # `nap`: hàm không đối số trả (chỉ mục, bảng nguồn). Gọi đúng MỘT lần.
        self._nap_fn = nap
        self._chi_muc: dict[int, int] | None = None
        self._bang: list[NguonDong] = []

    # ---- hàm tạo ------------------------------------------------------------

    @classmethod
    def tu_jsonl(cls, nguon: tuple[tuple[Path, str, str], ...]) -> ChiMucDongTho:
        return cls(lambda: _doc_jsonl(nguon))

    @classmethod
    def tu_tep_hoac_lui(cls, tep_bin: Path, lui: tuple[tuple[Path, str, str], ...]) -> ChiMucDongTho:
        """Tệp dựng sẵn nếu có; không có thì lùi về `lui` (nên là nguồn NHỎ)."""
        def nap() -> tuple[dict[int, int], list[NguonDong]]:
            if tep_bin.exists() and tep_bin.with_suffix(".json").exists():
                return _doc_tep(tep_bin)
            return _doc_jsonl(lui)
        return cls(nap)

    # ---- cổng -------------------------------------------------------------

    def tim(self, khoa: str) -> NguonDong | None:
        i = self._dam_bao().get(bam_khoa(khoa))
        return self._bang[i] if i is not None else None

    @property
    def so_dong(self) -> int:
        return len(self._dam_bao())

    def luu(self, tep_bin: Path) -> None:
        """Ghi tệp dựng sẵn: `.bin` (băm + chỉ số nguồn) và `.json` (bảng nguồn)."""
        chi_muc = self._dam_bao()
        khoa = array("Q", chi_muc.keys())
        gia_tri = array("I", chi_muc.values())
        tep_bin.parent.mkdir(parents=True, exist_ok=True)
        with tep_bin.open("wb") as f:
            array("Q", [len(khoa)]).tofile(f)
            khoa.tofile(f)
            gia_tri.tofile(f)
        tep_bin.with_suffix(".json").write_text(
            json.dumps([[n.kho, n.tieu_de, n.tac_gia, n.url] for n in self._bang], ensure_ascii=False),
            encoding="utf-8",
        )

    def _dam_bao(self) -> dict[int, int]:
        if self._chi_muc is None:
            self._chi_muc, self._bang = self._nap_fn()  # type: ignore[operator]
        return self._chi_muc


def _doc_tep(tep_bin: Path) -> tuple[dict[int, int], list[NguonDong]]:
    with tep_bin.open("rb") as f:
        n = array("Q")
        n.fromfile(f, 1)
        khoa = array("Q")
        khoa.fromfile(f, n[0])
        gia_tri = array("I")
        gia_tri.fromfile(f, n[0])
    bang = [
        NguonDong(kho=k, tieu_de=t, tac_gia=a, url=u)
        for k, t, a, u in json.loads(tep_bin.with_suffix(".json").read_text(encoding="utf-8"))
    ]
    return dict(zip(khoa, gia_tri, strict=True)), bang
