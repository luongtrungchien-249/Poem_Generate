"""ĐO THẬT với provider thật — §33.1 · §33.2 · §33.4 và ba chỉ số vận hành.

    DEFAULT_PROVIDER=openai python evals/do_that.py [số_yêu_cầu]

════ VÌ SAO PHẢI CÓ TỆP NÀY ════

Toàn bộ 788 test của repo chạy trên provider `mock`. Chúng chứng minh **cổng kiểm
không rò** — không có đường nào để bài sai luật đi ra. Chúng KHÔNG chứng minh được
mô hình có làm nổi bài thơ đúng luật hay không.

Rủi ro **R2** ghi từ đầu `Plan_Thi_Cong_DeepAgent.md`: tầng 4 (thanh luật) loại
**55,29% thơ NGƯỜI VIẾT** trong corpus 67.150 bài. Chưa có cơ sở nào để tin mô hình
làm tốt hơn người ở đúng ràng buộc đó.

Ba chỉ số dưới đây là thứ duy nhất trả lời được câu hỏi ấy:

    tỉ lệ đạt lượt đầu    mô hình viết đúng ngay lần đầu bao nhiêu phần trăm
    số lượt sửa trung bình  chi phí thật mỗi bài
    tỉ lệ kiệt lượt        bao nhiêu yêu cầu kết thúc bằng 422

⚠️ TỆP NÀY TỐN TIỀN THẬT. Mỗi yêu cầu tốn tối đa `max_repair_rounds + 1` lượt gọi
model. Mặc định 12 yêu cầu × tối đa 4 lượt = tối đa 48 lượt gọi.

⚠️ KHÔNG MOCK GÌ CẢ. Nếu provider không phải mô hình thật, tệp này DỪNG ngay — một
con số đo trên mock còn tệ hơn không có con số nào, vì nó trông như bằng chứng.
"""

from __future__ import annotations

import asyncio
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path

GOC = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(GOC / "src"))
sys.path.insert(0, str(GOC))

from adapters.llm.chat_port import ChatLlmAdapter  # noqa: E402
from adapters.persistence.corpus import JsonlPoemCorpus, duong_dan_mac_dinh  # noqa: E402
from adapters.rate_limit.memory import InMemoryRateLimiter  # noqa: E402
from adapters.tools import register_default_tools  # noqa: E402
from adapters.tools.executor import RegistryToolExecutor  # noqa: E402
from application.poetry.requirement import (  # noqa: E402
    PoetryRequirement,
    mac_dinh,
    nguoi_dung,
)
from application.poetry.sinh_tho import CanLamRo, DaSinhTho, sinh_bai_tho  # noqa: E402
from application.ports.llm import CallContext  # noqa: E402
from application.rule import kiem_tra_bai_tho  # noqa: E402
from bootstrap.container import _build_llm  # noqa: E402
from bootstrap.settings import get_settings  # noqa: E402
from domain.common.errors import OutputKhongDat  # noqa: E402
from domain.common.result import Err  # noqa: E402
from domain.conversation.thread import ThreadScope  # noqa: E402

# 12 chủ đề khác nhau, 3 cỡ bài. Đa dạng chủ ý: đo trên một chủ đề duy nhất thì
# con số nói về chủ đề ấy, không nói về hệ thống.
DE_BAI: list[tuple[str, int]] = [
    ("quê hương", 4),
    ("mùa thu Hà Nội", 8),
    ("người mẹ", 4),
    ("dòng sông tuổi thơ", 8),
    ("cơn mưa đầu hạ", 4),
    ("nỗi nhớ xa quê", 8),
    ("con đường làng", 4),
    ("đêm trăng", 8),
    ("mùa gặt", 4),
    ("tiễn bạn lên đường", 8),
    ("chiều biên giới", 12),
    ("hoa cải ven sông", 12),
]


@dataclass
class KetQuaMotBai:
    chu_de: str
    so_dong_yc: int
    thanh_cong: bool
    so_luot: int
    ly_do_that_bai: str = ""
    tang_dung_lai: int | None = None
    bai_tho: str = ""
    giay: float = 0.0


def _yeu_cau(chu_de: str, so_dong: int) -> PoetryRequirement:
    return PoetryRequirement(
        chu_de=nguoi_dung(chu_de),
        so_dong=nguoi_dung(so_dong),
        cam_xuc=nguoi_dung("hoài niệm"),
        phong_cach=mac_dinh(None),
        rang_buoc_van=mac_dinh(None),
        rang_buoc_thanh=mac_dinh(None),
        van_ban_goc=f"Viết bài thất ngôn tự do {so_dong} dòng về {chu_de}",
    )


def _ctx(i: int) -> CallContext:
    return CallContext(
        scope=ThreadScope(platform="web", thread_id=f"do-that-{i}"),
        sender_id="do-that",
        trace_id=f"trace-do-that-{i}",
    )


async def _chay_mot(i: int, chu_de: str, so_dong: int, deps: dict) -> KetQuaMotBai:
    t0 = time.monotonic()
    kq = await sinh_bai_tho(
        _yeu_cau(chu_de, so_dong),
        llm=deps["llm"],
        tools=deps["tools"],
        rate_limiter=deps["rate_limiter"],
        ctx=_ctx(i),
        corpus=deps["corpus"],
        max_repair_rounds=3,
        timeout_sec=180.0,
        default_model=deps["model"],
    )
    giay = time.monotonic() - t0

    if isinstance(kq, Err):
        e = kq.error
        if isinstance(e, OutputKhongDat):
            return KetQuaMotBai(
                chu_de, so_dong, False, e.so_luot_da_sua,
                ly_do_that_bai=e.chan_doan[:200], giay=giay,
            )
        return KetQuaMotBai(
            chu_de, so_dong, False, 0, ly_do_that_bai=type(e).__name__, giay=giay
        )

    ra = kq.value
    if isinstance(ra, CanLamRo):
        return KetQuaMotBai(
            chu_de, so_dong, False, 0, ly_do_that_bai=f"hỏi lại: {ra.cau_hoi.ly_do}", giay=giay
        )

    assert isinstance(ra, DaSinhTho)
    return KetQuaMotBai(chu_de, so_dong, True, ra.so_luot, bai_tho=ra.text, giay=giay)


async def main() -> int:
    so_yeu_cau = int(sys.argv[1]) if len(sys.argv) > 1 else len(DE_BAI)
    de = DE_BAI[:so_yeu_cau]

    s = get_settings()
    if s.llm.default_provider == "mock":
        print("⛔ DỪNG: provider đang là `mock`.")
        print("   Một con số đo trên mock còn tệ hơn không có con số nào — nó trông")
        print("   như bằng chứng. Chạy lại với DEFAULT_PROVIDER=openai.")
        return 1

    client = _build_llm(s)
    if type(client).__name__ == "MockLLMClient":
        print("⛔ DỪNG: lùi về MockLLMClient (thiếu khoá?). Xem bootstrap/container.py.")
        return 1

    register_default_tools()
    deps = {
        "llm": ChatLlmAdapter(client, default_model=s.llm.default_model),
        "tools": RegistryToolExecutor(),
        "rate_limiter": InMemoryRateLimiter(
            so_yeu_cau_moi_phut=10_000, so_lan_goi_model_moi_ngay=10_000
        ),
        "corpus": JsonlPoemCorpus(duong_dan_mac_dinh(GOC)),
        "model": s.llm.default_model,
    }

    print("=" * 74)
    print(f"ĐO THẬT — provider={s.llm.default_provider} model={s.llm.default_model}")
    print(f"{len(de)} yêu cầu · tối đa 3 lượt sửa mỗi bài · KHÔNG mock gì cả")
    print("=" * 74)

    kq: list[KetQuaMotBai] = []
    for i, (chu_de, n) in enumerate(de):
        print(f"[{i + 1:>2}/{len(de)}] {chu_de} ({n} dòng) ... ", end="", flush=True)
        r = await _chay_mot(i, chu_de, n, deps)
        kq.append(r)
        if r.thanh_cong:
            print(f"ĐẠT sau {r.so_luot} lượt sửa ({r.giay:.1f}s)")
        else:
            print(f"KHÔNG ĐẠT ({r.giay:.1f}s) — {r.ly_do_that_bai[:70]}")

    # ── Ba chỉ số vận hành ──────────────────────────────────────────────────
    n = len(kq)
    dat = [r for r in kq if r.thanh_cong]
    dat_luot_dau = [r for r in dat if r.so_luot == 0]
    kiet_luot = [r for r in kq if not r.thanh_cong]

    print()
    print("=" * 74)
    print("BA CHỈ SỐ VẬN HÀNH — trả lời rủi ro R2")
    print("=" * 74)
    print(f"  tỉ lệ đạt lượt đầu   : {len(dat_luot_dau)}/{n} = {len(dat_luot_dau) / n:.1%}")
    print(f"  tỉ lệ đạt (mọi lượt) : {len(dat)}/{n} = {len(dat) / n:.1%}")
    print(f"  tỉ lệ KIỆT LƯỢT      : {len(kiet_luot)}/{n} = {len(kiet_luot) / n:.1%}")
    if dat:
        print(f"  số lượt sửa TB (bài đạt): {statistics.mean(r.so_luot for r in dat):.2f}")
    print(f"  thời gian TB mỗi bài : {statistics.mean(r.giay for r in kq):.1f}s")

    # ── Vì sao trượt ────────────────────────────────────────────────────────
    if kiet_luot:
        print()
        print("VÌ SAO KHÔNG ĐẠT — đếm theo mã lỗi trong chẩn đoán")
        dem: dict[str, int] = {}
        for r in kiet_luot:
            for ma in ("H1", "H2", "H3", "H4", "S11", "S14", "CL", "B1", "B2", "B3", "B6"):
                if f" {ma}" in r.ly_do_that_bai or f"{ma}:" in r.ly_do_that_bai:
                    dem[ma] = dem.get(ma, 0) + 1
        for ma, c in sorted(dem.items(), key=lambda x: -x[1]):
            print(f"    {ma:>4}: {c} bài")

    # ── §33.3 trên thơ MÔ HÌNH SINH, không phải thơ người viết ──────────────
    if dat:
        print()
        print("§33.3 — LUẬT THƠ trên bài mô hình sinh ra")
        from evals.metrics.poetry import do_luong_tho

        m = do_luong_tho([r.bai_tho for r in dat], chu_de=None)
        print(f"  {m.so_bai} bài đạt: đúng số tiếng {m.ty_le_dung_so_tieng:.0%} · "
              f"đúng khuôn {m.ty_le_dung_khuon:.0%} · có vần {m.ty_le_co_van_chan:.0%}")

        print()
        print("MỘT BÀI LÀM VÍ DỤ")
        mau = dat[0]
        print(f"  [{mau.chu_de}, {mau.so_dong_yc} dòng, {mau.so_luot} lượt sửa]")
        for d in mau.bai_tho.splitlines():
            print(f"    {d}")
        v = kiem_tra_bai_tho(mau.bai_tho)
        print(f"  kiểm lại: dat={v.dat} · {v.so_dong} dòng · "
              f"sơ đồ vần {['' .join(k) for k in v.so_do_van_theo_kho]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
