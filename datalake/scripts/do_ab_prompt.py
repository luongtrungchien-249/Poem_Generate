"""BỘ ĐO A/B CHO THAY ĐỔI PROMPT — hạ tầng chung, không gắn vào một thay đổi nào.

════ VÌ SAO FILE NÀY PHẢI CÓ TRƯỚC MỌI THAY ĐỔI PROMPT ════

Repo này đã trả giá hai lần cho việc sửa prompt theo một giả thuyết nghe hợp lý:

    instructions.py §VIỆC 4   nới `CHI_DAN_VIET_TIEP_KHO` -> ứng viên dùng được
                              TỤT 8,00% -> 2,67% (p = 0,036), và mô hình chép
                              nguyên văn khổ trước TĂNG 0,67% -> 14,00%
    sinh_tho.py §few-shot     tắt few-shot -> dòng đủ 7 tiếng TỤT 62,69% -> 55,62%

Cả hai lần, số liệu chỉ có được vì ai đó chịu đo. Nhưng script đo của lượt 22/09
KHÔNG được commit, nên hai con số ấy nay không tái lập được — chúng chỉ còn là chữ
trong chú thích. Đó là lý do file này tồn tại, và là lý do nó nằm trong repo chứ
không nằm trong một thư mục tạm.

════ 🔴 CHỈ SỐ: "ỨNG VIÊN DÙNG ĐƯỢC THẬT", KHÔNG PHẢI "ĐẠT LUẬT" ════

Đây là chỗ dễ sai nhất và đã sai một lần. `instructions.py` ghi rõ:

    "KHÔNG được lấy 'đạt luật' làm chỉ số — bản chép luôn đạt luật vì khổ nó chép
     vốn đã đạt."

Một khối prompt đẩy mô hình về phía chép lại phần đã viết sẽ làm "đạt luật" tăng
vọt trong khi sản phẩm tệ đi. Vì vậy chỉ số chính ở đây là hợp của BA điều kiện:

    1. `rule.kiem_tra_bai_tho(...).dat`      đúng luật
    2. không dòng nào lặp lại dòng nào       không chép
    3. `quality.danh_gia_chat_luong(...).dat` qua cổng chất lượng

Các chỉ số phụ (dòng đủ tiếng, dòng khớp khuôn, tỉ lệ chép) vẫn được ghi ra, vì
khi chỉ số chính tụt thì phải biết nó tụt ở đâu.

════ ĐỐI CHỨNG ════

Hai nhánh chạy trên CÙNG danh sách chủ đề, CÙNG số ứng viên, CÙNG mô hình. Thứ
duy nhất khác nhau là hàm dựng lời nhắc. Khi đo việc VIẾT TIẾP, khổ đầu phải lấy
từ corpus đã đạt và giữ CỐ ĐỊNH cho cả hai nhánh — nếu để mỗi nhánh tự sinh khổ
đầu thì chênh lệch đo được lẫn cả sai khác của khổ đầu.

CHẠY
    export OPENAI_API_KEY=...
    python datalake/scripts/do_ab_prompt.py --help
"""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))

from adapters.llm.chat_port import ChatLlmAdapter  # noqa: E402
from adapters.llm.openai import OpenAIClient  # noqa: E402
from application.poetry.quality import danh_gia_chat_luong  # noqa: E402
from application.poetry.requirement import PoetryRequirement, Truong  # noqa: E402
from application.ports.llm import CallContext, UserMessage  # noqa: E402
from application.rule import kiem_tra_bai_tho  # noqa: E402
from domain.conversation.thread import ThreadScope  # noqa: E402

RA_MAC_DINH = GOC / "datalake/analysis/do_ab"


# ══════════════════════════════════════════════════════════════════════════════
# §1. CHỦ ĐỀ ĐỐI CHỨNG
#
# Hai nhóm tách riêng vì A2 (phong cách hai nhánh) chỉ có nghĩa khi đo trên cả hai
# giọng. Đo một giọng rồi kết luận cho cả hai là đúng kiểu sai mà A2 định sửa.
# ══════════════════════════════════════════════════════════════════════════════

CHU_DE_VAN_CHUONG: tuple[str, ...] = (
    "mùa thu", "người về nhà cũ", "bến sông chiều", "mưa đêm",
    "cây bàng sân trường", "tiếng chuông xa", "con ngõ nhỏ", "bóng mẹ",
    "chuyến tàu muộn", "giếng nước đầu làng", "áo cũ", "trăng trên đồng",
    "lá rụng", "quán nước ven đường", "cánh đồng sau gặt",
)

CHU_DE_DOI_THUONG: tuple[str, ...] = (
    "kẹt xe giờ tan tầm", "cà phê sáng thứ hai", "deadline cuối tháng",
    "mèo nhà hàng xóm", "bữa cơm sinh viên", "điện thoại hết pin",
    "chợ Tết", "đi làm ngày mưa", "lương về", "hàng xóm hát karaoke",
)


# ══════════════════════════════════════════════════════════════════════════════
# §2. CHẤM MỘT ỨNG VIÊN
#
# THUẦN và TẤT ĐỊNH — không gọi mạng. Tách khỏi phần sinh để test lại được, và để
# chấm lại một lượt đo cũ mà không phải sinh lại.
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class DiemUngVien:
    """Chấm một ứng viên trên mọi chiều. `dung_duoc` là chỉ số CHÍNH."""

    dung_duoc: bool
    dat_luat: bool
    dat_chat_luong: bool
    co_lap_dong: bool
    chep_phan_da_viet: bool
    so_dong: int
    so_dong_du_tieng: int
    so_dong_khop_khuon: int


def _dong_sach(van_ban: str) -> list[str]:
    return [d.strip() for d in van_ban.strip().splitlines() if d.strip()]


def cham_ung_vien(
    van_ban: str, *, chu_de: str | None = None, phan_da_viet: str = ""
) -> DiemUngVien:
    """Chấm một ứng viên. Không I/O, cùng vào cùng ra.

    `phan_da_viet` chỉ dùng khi đo việc VIẾT TIẾP: nó cho phép phát hiện mô hình
    chép lại khổ trước — kiểu hỏng đã đo được ở lượt 22/09 (0,67% -> 14,00%) và là
    lý do "đạt luật" một mình không dùng làm chỉ số được.
    """
    dong = _dong_sach(van_ban)
    v = kiem_tra_bai_tho(van_ban)
    cl = danh_gia_chat_luong(v, chu_de=chu_de)

    co_lap = len({d.lower() for d in dong}) < len(dong)

    da_co = {d.strip().lower() for d in _dong_sach(phan_da_viet)}
    chep = bool(da_co) and any(d.lower() in da_co for d in dong)

    return DiemUngVien(
        # Ba điều kiện, KHÔNG phải một. Xem docstring module.
        dung_duoc=v.dat and cl.dat and not co_lap and not chep,
        dat_luat=v.dat,
        dat_chat_luong=cl.dat,
        co_lap_dong=co_lap,
        chep_phan_da_viet=chep,
        so_dong=len(dong),
        so_dong_du_tieng=sum(1 for bc in v.dong if bc.so_tieng == 7),
        so_dong_khop_khuon=sum(1 for bc in v.dong if bc.khuon in ("bang", "trac")),
    )


# ══════════════════════════════════════════════════════════════════════════════
# §3. THỐNG KÊ
#
# Two-proportion z-test. Cố ý KHÔNG kéo scipy về: một hàm mười dòng đọc được và
# kiểm lại bằng tay, so với một phụ thuộc nữa cho đúng một phép tính.
# ══════════════════════════════════════════════════════════════════════════════


def _pnorm(z: float) -> float:
    """Hàm phân phối tích luỹ chuẩn tắc, qua erf của thư viện chuẩn."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def p_value_hai_ti_le(x1: int, n1: int, x2: int, n2: int) -> float:
    """p hai phía cho H0: hai tỉ lệ bằng nhau. Trả 1.0 khi không tính được.

    ════ ĐÃ KIỂM CHỨNG NGƯỢC BẰNG SỐ LIỆU CŨ ════

    Hàm này được đối chiếu với ba con số đã ghi trong mã nguồn từ lượt 22/09:

        nới CHI_DAN_VIET_TIEP_KHO v2   23/300 vs 4/150   -> 0,0353  (mã ghi 0,036) ✓
        tắt few-shot, dòng đủ tiếng    445/800 vs 501/800 -> 0,0044  (mã ghi 0,0044) ✓
        chép nguyên văn khổ trước      1/150 vs 21/150    -> 9,4e-06 (mã ghi 5,5e-06) ✗

    Hai ca đầu khớp tới chữ số đã ghi. Ca thứ ba LỆCH ba lần về độ lớn — gần như
    chắc chắn vì lượt đo cũ dùng một phép kiểm khác (Fisher chính xác, hoặc
    chi-square có hiệu chỉnh liên tục) chứ không phải z-test hai tỉ lệ. Kết luận
    không đổi ở cả hai phép (p ≪ 0,001), nhưng ghi ra đây để người sau đọc số
    trong `instructions.py` biết chúng KHÔNG sinh ra từ hàm này, và đừng so hai
    con số của hai phép kiểm khác nhau rồi tưởng có gì sai.
    """
    if n1 <= 0 or n2 <= 0:
        return 1.0
    p1, p2 = x1 / n1, x2 / n2
    p_gop = (x1 + x2) / (n1 + n2)
    if p_gop in (0.0, 1.0):
        return 1.0
    se = math.sqrt(p_gop * (1.0 - p_gop) * (1.0 / n1 + 1.0 / n2))
    if se == 0.0:
        return 1.0
    return 2.0 * (1.0 - _pnorm(abs((p1 - p2) / se)))


# ══════════════════════════════════════════════════════════════════════════════
# §4. CHẠY MỘT NHÁNH
# ══════════════════════════════════════════════════════════════════════════════

# Hàm dựng lời nhắc của một nhánh: (chủ đề, số dòng) -> chuỗi gửi mô hình.
DungLoiNhac = Callable[[str, int], str]


@dataclass
class KetQuaNhanh:
    ten: str
    diem: list[DiemUngVien] = field(default_factory=list)
    so_loi_goi_hong: int = 0

    @property
    def n(self) -> int:
        return len(self.diem)

    @property
    def so_dung_duoc(self) -> int:
        return sum(1 for d in self.diem if d.dung_duoc)

    def ti_le(self, lay: Callable[[DiemUngVien], bool]) -> float:
        return round(sum(1 for d in self.diem if lay(d)) / self.n, 4) if self.n else 0.0

    def tom_tat(self) -> dict:
        tong_dong = sum(d.so_dong for d in self.diem) or 1
        return {
            "ten": self.ten,
            "so_ung_vien": self.n,
            "so_loi_goi_hong": self.so_loi_goi_hong,
            # Chỉ số CHÍNH.
            "ti_le_dung_duoc": self.ti_le(lambda d: d.dung_duoc),
            "so_dung_duoc": self.so_dung_duoc,
            # Chỉ số phụ — để biết chỉ số chính tụt ở đâu.
            "ti_le_dat_luat": self.ti_le(lambda d: d.dat_luat),
            "ti_le_dat_chat_luong": self.ti_le(lambda d: d.dat_chat_luong),
            "ti_le_co_lap_dong": self.ti_le(lambda d: d.co_lap_dong),
            "ti_le_chep_phan_da_viet": self.ti_le(lambda d: d.chep_phan_da_viet),
            "ti_le_dong_du_tieng": round(
                sum(d.so_dong_du_tieng for d in self.diem) / tong_dong, 4
            ),
            "ti_le_dong_khop_khuon": round(
                sum(d.so_dong_khop_khuon for d in self.diem) / tong_dong, 4
            ),
        }


async def chay_mot_nhanh(
    ten: str,
    dung_loi_nhac: DungLoiNhac,
    *,
    chu_de: Sequence[str],
    so_dong: int,
    so_ung_vien: int,
    llm: ChatLlmAdapter,
    ctx: CallContext,
    model: str,
    song_song: int = 8,
) -> KetQuaNhanh:
    """Sinh `so_ung_vien` ứng viên cho mỗi chủ đề, chấm từng cái.

    KHÔNG dừng sớm khi gặp ứng viên đạt — khác hẳn `sinh_theo_kho._chon_mot_kho`.
    Ở đó dừng sớm là đúng vì mục tiêu là lấy MỘT khổ dùng được; ở đây mục tiêu là
    ĐO TỈ LỆ, nên dừng sớm sẽ cắt cụt mẫu đúng ở những chủ đề dễ.
    """
    kq = KetQuaNhanh(ten=ten)

    for de in chu_de:
        loi_nhac = dung_loi_nhac(de, so_dong)
        for dau in range(0, so_ung_vien, song_song):
            con = min(song_song, so_ung_vien - dau)
            tra_loi = await asyncio.gather(
                *[
                    llm.reply(
                        messages=(UserMessage(content=loi_nhac),),
                        tools=(),
                        ctx=ctx,
                        model=model,
                    )
                    for _ in range(con)
                ]
            )
            for r in tra_loi:
                text = getattr(getattr(r, "value", None), "text", None)
                if not text:
                    kq.so_loi_goi_hong += 1
                    continue
                kq.diem.append(cham_ung_vien(text, chu_de=de))
    return kq


def doi_chieu(nen: KetQuaNhanh, moi: KetQuaNhanh) -> dict:
    """So hai nhánh trên chỉ số chính, kèm p."""
    p = p_value_hai_ti_le(nen.so_dung_duoc, nen.n, moi.so_dung_duoc, moi.n)
    chenh = (moi.so_dung_duoc / moi.n if moi.n else 0.0) - (
        nen.so_dung_duoc / nen.n if nen.n else 0.0
    )
    return {
        "chi_so": "ti_le_dung_duoc",
        "nen": nen.tom_tat(),
        "moi": moi.tom_tat(),
        "chenh_lech_diem_phan_tram": round(chenh * 100, 2),
        "p_value": round(p, 6),
        # Ngưỡng 0,05 là quy ước, KHÔNG phải luật của dự án. Kết luận ghi ra để
        # người đọc thấy ngay, nhưng quyết định giữ hay bỏ vẫn là của chủ dự án.
        "co_y_nghia_thong_ke": p < 0.05,
        "ket_luan": (
            "GIỮ ĐƯỢC — không giảm có ý nghĩa"
            if chenh >= 0 or p >= 0.05
            else "⛔ HOÀN NGUYÊN — giảm có ý nghĩa thống kê"
        ),
    }


# ══════════════════════════════════════════════════════════════════════════════
# §5. LỜI NHẮC CỦA HAI NHÁNH
#
# Nhánh NỀN luôn là chuỗi prompt đang chạy thật trong `src/`. Nhánh MỚI nạp từ một
# file Python do người đo chỉ định, phải có hàm `dung_loi_nhac(chu_de, so_dong)`.
#
# Cách này cố ý: nhánh mới KHÔNG được sửa thẳng vào `src/` rồi đo, vì khi đó không
# còn nhánh nền để so, và một lần quên hoàn nguyên là hệ thống chạy bản chưa đo.
# ══════════════════════════════════════════════════════════════════════════════


def _req(chu_de: str, so_dong: int, phong_cach: str = "") -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=Truong(gia_tri=chu_de, nguon="nguoi_dung"),
        so_dong=Truong(gia_tri=so_dong, nguon="nguoi_dung"),
        phong_cach=(
            Truong(gia_tri=phong_cach, nguon="nguoi_dung")
            if phong_cach
            else PoetryRequirement().phong_cach
        ),
    )


def loi_nhac_nen(phong_cach: str = "") -> DungLoiNhac:
    """Nhánh nền — đúng chuỗi đang gửi cho mô hình trong hệ thống sống.

    Import ở TRONG hàm, không ở đầu file: nhánh mới có thể vá `prompt.py` bằng
    monkeypatch trước khi gọi, và import sớm sẽ khoá mất bản cũ.
    """
    from application.poetry.prompt import dung_luot_yeu_cau

    def dung(chu_de: str, so_dong: int) -> str:
        return dung_luot_yeu_cau(_req(chu_de, so_dong, phong_cach))

    return dung


def nap_nhanh_moi(duong_dan: Path) -> DungLoiNhac:
    """Nạp hàm `dung_loi_nhac` từ một file Python rời."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("nhanh_moi", duong_dan)
    if spec is None or spec.loader is None:
        raise SystemExit(f"không nạp được {duong_dan}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    ham = getattr(mod, "dung_loi_nhac", None)
    if not callable(ham):
        raise SystemExit(f"{duong_dan} phải có hàm dung_loi_nhac(chu_de, so_dong)")
    return ham


# ══════════════════════════════════════════════════════════════════════════════
# §6. CHẠY
# ══════════════════════════════════════════════════════════════════════════════


def _doc_tham_so() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Đo A/B một thay đổi prompt trên chỉ số 'ứng viên dùng được thật'."
    )
    p.add_argument("--nhanh-moi", type=Path, help="file .py có hàm dung_loi_nhac()")
    p.add_argument("--giong", choices=("van_chuong", "doi_thuong", "ca_hai"),
                   default="van_chuong", help="nhóm chủ đề đối chứng")
    p.add_argument("--so-dong", type=int, default=4, help="số dòng mỗi bài (bội của 4)")
    p.add_argument("--so-ung-vien", type=int, default=6, help="ứng viên mỗi chủ đề mỗi nhánh")
    p.add_argument("--so-chu-de", type=int, default=0, help="0 = dùng hết")
    p.add_argument("--model", default="gpt-4o-mini")
    p.add_argument("--phong-cach", default="", help="giá trị trường phong_cach")
    p.add_argument("--ra", type=Path, default=None, help="file JSON kết quả")
    return p.parse_args()


def _chu_de_cua(giong: str, so: int) -> tuple[str, ...]:
    bang = {
        "van_chuong": CHU_DE_VAN_CHUONG,
        "doi_thuong": CHU_DE_DOI_THUONG,
        "ca_hai": CHU_DE_VAN_CHUONG + CHU_DE_DOI_THUONG,
    }[giong]
    return bang[:so] if so > 0 else bang


async def _chay(a: argparse.Namespace) -> int:
    if a.so_dong % 4 != 0:
        raise SystemExit(f"--so-dong phải là bội của 4 (H4), nhận {a.so_dong}")

    chu_de = _chu_de_cua(a.giong, a.so_chu_de)

    khoa = os.environ.get("OPENAI_API_KEY", "")
    if not khoa:
        raise SystemExit("thiếu OPENAI_API_KEY — bộ đo phải gọi mô hình thật")
    llm = ChatLlmAdapter(OpenAIClient(api_key=khoa), default_model=a.model)
    ctx = CallContext(
        scope=ThreadScope(platform="cli", thread_id="do_ab_prompt"),
        sender_id="do_ab_prompt",
        trace_id=datetime.now(UTC).strftime("ab-%Y%m%d-%H%M%S"),
    )
    chung = dict(
        chu_de=chu_de, so_dong=a.so_dong, so_ung_vien=a.so_ung_vien,
        llm=llm, ctx=ctx, model=a.model,
    )

    print(f"nhánh NỀN  · {len(chu_de)} chủ đề × {a.so_ung_vien} ứng viên …", flush=True)
    nen = await chay_mot_nhanh("nen", loi_nhac_nen(a.phong_cach), **chung)

    if a.nhanh_moi is None:
        # Không có nhánh mới thì đây là một lượt ĐO NỀN — vẫn có ích: nó cho biết
        # nền đang ở đâu, và lặp lại hai lần cho biết nền dao động bao nhiêu.
        bao_cao = {"chi_do_nen": True, "nen": nen.tom_tat()}
    else:
        print(f"nhánh MỚI  · {a.nhanh_moi} …", flush=True)
        moi = await chay_mot_nhanh("moi", nap_nhanh_moi(a.nhanh_moi), **chung)
        bao_cao = doi_chieu(nen, moi)

    bao_cao["tham_so"] = {
        "giong": a.giong, "so_dong": a.so_dong, "so_chu_de": len(chu_de),
        "so_ung_vien_moi_chu_de": a.so_ung_vien, "model": a.model,
        "phong_cach": a.phong_cach, "nhanh_moi": str(a.nhanh_moi or ""),
        "luc": ctx.trace_id,
    }

    ra = a.ra or (RA_MAC_DINH / f"{ctx.trace_id}.json")
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps(bao_cao, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(bao_cao, ensure_ascii=False, indent=2))
    print(f"\n-> {ra}")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_chay(_doc_tham_so())))
