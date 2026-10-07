"""ĐO `p` — Plan_PoeTone GĐ0.4. Đầu vào của công thức chọn `k` ở `sinh_theo_kho.py`.

    python datalake/scripts/do_p.py [--so-ung-vien 16] [--moi-luot 1 4]

Sinh ứng viên KHỔ ĐẦU (4 dòng) với đúng lời nhắc của đường sinh thật, rồi đếm:

    du_7_tieng   tỉ lệ dòng đúng 7 tiếng                      (tầng 2)
    p            tỉ lệ dòng đúng 7 tiếng VÀ khớp khuôn bằng/trắc  (tầng 4)
    kho_dat      số ứng viên khổ qua cả bảy tầng của `rule.py`

`p` là xác suất một DÒNG qua được cả tầng 2 lẫn tầng 4. Công thức đầu file
`sinh_theo_kho.py` dùng đúng con số này: P(khổ) ≈ p⁴.

`--vi-du` so sánh zero-shot với one-shot / few-shot (QĐ-P4). Ứng viên chép nguyên
dòng của bài mẫu bị đếm riêng và KHÔNG tính là khổ đạt.

`--moi-luot` so sánh số phương án xin trong một lượt gọi (`SO_UNG_VIEN_MOI_LUOT`).
Cùng chủ đề, cùng số ứng viên — chỉ khác cách xin.

⚠️ Khuôn đọc bằng `rule.khuon_cua_dong`, trả "bang" / "trac" / "pha" /
"khong_xac_dinh" — KHÔNG trả None. Kiểm `is not None` sẽ đếm mọi dòng là khớp.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(GOC / "src"))
sys.path.insert(0, str(GOC))

from evals.do_that import _ctx, _DemLuotGoi, _yeu_cau  # noqa: E402

from adapters.llm.chat_port import ChatLlmAdapter  # noqa: E402
from adapters.persistence.corpus import JsonlPoemCorpus, duong_dan_mac_dinh  # noqa: E402
from application.poetry.fewshot import chon_vi_du, dung_khoi_vi_du  # noqa: E402
from application.poetry.prompt import dung_luot_yeu_cau  # noqa: E402
from application.poetry.sinh_theo_kho import _lay_cac_phuong_an  # noqa: E402
from application.ports.llm import UserMessage  # noqa: E402
from application.prompting.system import CHI_DAN_NHIEU_UNG_VIEN  # noqa: E402
from application.rule import dem_tieng, khuon_cua_dong, kiem_tra_bai_tho, tach_tieng  # noqa: E402
from bootstrap.container import _build_llm  # noqa: E402
from bootstrap.settings import get_settings  # noqa: E402
from domain.common.result import Err  # noqa: E402

CHU_DE = (
    "người thợ may", "mùa gặt", "căn bếp mẹ", "chợ phiên vùng cao", "ga tàu cuối năm",
    "đêm trăng", "quê hương", "người mẹ", "dòng sông tuổi thơ", "cơn mưa đầu hạ",
    "tiễn bạn lên đường", "hoa cải ven sông",
)


def _khoi_vi_du(kho: tuple, req: object, so_vi_du: int) -> tuple[str, set[str]]:
    """Khối ví dụ đúng như sản phẩm dựng, kèm tập dòng mẫu để đếm chép."""
    if so_vi_du <= 0:
        return "", set()
    che_do = "one_shot" if so_vi_du == 1 else "few_shot"
    vi_du = chon_vi_du(kho, req, che_do=che_do, toi_da=so_vi_du)  # type: ignore[arg-type]
    dong_mau = {
        " ".join(tach_tieng(d)).lower() for v in vi_du for d in v.mau.tho.splitlines() if d.strip()
    }
    return dung_khoi_vi_du(vi_du), dong_mau


async def _mot_nhanh(
    llm: _DemLuotGoi, model: str, moi_luot: int, so_uv: int, so_vi_du: int = 0, kho: tuple = ()
) -> dict:
    dong = du7 = khop = kho_dat = n = chep = 0
    for i, c in enumerate(CHU_DE):
        req = _yeu_cau(c, 4)
        khoi, dong_mau = _khoi_vi_du(kho, req, so_vi_du)
        nhac = dung_luot_yeu_cau(req, khoi)
        if moi_luot > 1:
            nhac += "\n" + CHI_DAN_NHIEU_UNG_VIEN.format(so=moi_luot)
        tra_loi = await asyncio.gather(*[
            llm.reply(messages=(UserMessage(content=nhac),), tools=(), ctx=_ctx(i), model=model)
            for _ in range(-(-so_uv // moi_luot))
        ])
        for r in tra_loi:
            if isinstance(r, Err):
                continue
            for pa in _lay_cac_phuong_an(r.value.text):
                n += 1
                dong += len(pa)
                for d in pa:
                    if dem_tieng(d) == 7:
                        du7 += 1
                        khop += khuon_cua_dong(tach_tieng(d)) in ("bang", "trac")
                kho_dat += kiem_tra_bai_tho("\n".join(pa)).dat
    return {
        "moi_luot": moi_luot, "so_vi_du": so_vi_du, "ung_vien": n, "chep": chep, "dong": dong,
        "du_7_tieng": round(du7 / max(dong, 1), 4), "p": round(khop / max(dong, 1), 4),
        "kho_dat": kho_dat, "luot_goi": llm.luot_reply, "token_vao": llm.token_vao,
        "token_ra": llm.token_ra,
    }


async def main() -> int:
    ap = argparse.ArgumentParser(description="Đo p (dòng khớp khuôn) cho mô hình hiện tại.")
    ap.add_argument("--so-ung-vien", type=int, default=16, help="ứng viên mỗi chủ đề")
    ap.add_argument("--moi-luot", type=int, nargs="+", default=[1, 4])
    ap.add_argument("--vi-du", type=int, nargs="+", default=[0],
                    help="số bài mẫu trong lời nhắc (0 = zero-shot, như sản phẩm từ 22/09)")
    ap.add_argument("--ra", type=Path, default=None)
    a = ap.parse_args()

    st = get_settings()
    if st.llm.default_provider == "mock":
        print("⛔ provider là mock — số đo trên mock vô nghĩa.")
        return 1
    llm = _DemLuotGoi(ChatLlmAdapter(_build_llm(st), default_model=st.llm.default_model))
    kho = JsonlPoemCorpus(duong_dan_mac_dinh(GOC)).tat_ca()
    kq = []
    for m in a.moi_luot:
        for v in a.vi_du:
            llm.dat_lai()
            kq.append(await _mot_nhanh(llm, st.llm.default_model, m, a.so_ung_vien, v, kho))
            print(json.dumps(kq[-1], ensure_ascii=False), flush=True)
    if a.ra:
        a.ra.write_text(json.dumps(
            {"model": st.llm.default_model, "chu_de": list(CHU_DE), "ket_qua": kq},
            ensure_ascii=False, indent=2,
        ), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
