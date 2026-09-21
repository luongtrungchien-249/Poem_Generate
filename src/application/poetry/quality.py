"""CHẤT LƯỢNG SÁNG TÁC — bảy chiều của §12.2 Tool 7, thi hành chỉ thị 3.

    *"cần kiểm tra đầy đủ chất lượng của LLM; nếu không đạt được thì cần
    Chain-of-thought trước khi trả ra kết quả."*  — chủ dự án, 21/09/2026

════ RANH GIỚI THẨM QUYỀN — đọc trước khi sửa file này ════

File này **KHÔNG BIẾT LUẬT THƠ** và không được phép biết. Nó nhận một `PoemVerdict`
đã tính sẵn từ `rule.py` và chỉ ĐỌC vài con số trong đó.

    `rule.py`    phán bài có THUỘC THỂ và có ĐÚNG LUẬT không
    file này     phán bài có ĐÁNG TRẢ RA không

Không chiều nào ở đây được đụng tới `thuoc_the`. Một bài trượt chất lượng vẫn là
thơ thất ngôn tự do hợp lệ — nó chỉ chưa đủ tốt để gửi đi. Trộn hai chuyện này là
cách chắc chắn để một ngày nào đó một bài bị loại vì "lặp từ" rồi được ghi lại như
thể nó sai luật thơ.

════ NĂM CHIỀU ĐO ĐƯỢC, HAI CHIỀU KHÔNG ════

§12.2 liệt kê bảy chiều. Năm chiều suy ra được từ hình thức; hai chiều còn lại
(`mach_lac`, `hinh_anh`) đòi hiểu nội dung. Theo nguyên tắc N3, hai chiều đó được
GHI CÔNG KHAI là không kiểm được, chứ không chấm điểm bừa rồi để người đọc tưởng
đã kiểm.

VÌ SAO KHÔNG GỌI LLM ĐỂ CHẤM HAI CHIỀU CUỐI NGAY Ở ĐÂY. Port `OutputVerifier` quy
định hiện thực phải ĐỒNG BỘ, THUẦN và TẤT ĐỊNH — *"cổng chặn không được phép trượt
vì mạng"*, và *"nếu không tất định, vòng sửa sẽ dao động"*. Một LLM-judge vi phạm
cả hai. Nó thuộc về node Reviewer (G7), nơi nó TƯ VẤN cho HITL chứ không chặn.

════ 🩸 HAI CHIỀU ĐÃ BỊ GỠ 21/09/2026 — VI PHẠM NGUYÊN TẮC N2 ════

Bản trước có hai chiều phạt sự LẶP, và cả hai đều sai theo đúng kiểu N2 cấm:
**đánh trượt một bài vì tác giả dùng đúng cái quyền tài liệu cho phép.**

    S20 (loại "quyen"): *"Có thể dùng điệp dòng, điệp khổ, điệp cấu trúc"*

  ❌ `lap_tieng ≥ 0,55` — ngưỡng tuỳ ý, và THIÊN VỊ THEO ĐỘ DÀI.
     Đo trên 6.000 bài người viết đã đạt luật: trung vị tụt từ 0,929 (bài 4–8
     dòng) xuống 0,638 (bài 56 dòng). Nguyên nhân là số học chứ không phải chất
     lượng — tiếng Việt có kho âm tiết hữu hạn và hư từ lặp lại tự nhiên, nên bài
     càng dài thì tỉ lệ *khác nhau / tổng* càng BUỘC phải giảm. Một ngưỡng cố định
     vì vậy nghiêm khắc hơn với bài dài mà không ai chủ ý như thế.

  ❌ `lap_dong = 0` — tôi từng biện minh là "suy ra từ nghĩa của trùng dòng", và
     không hề đối chiếu với S20. Đo lại: 164/6.000 bài bị bắt, và **toàn bộ là
     điệp có chủ ý** — "Em là con hát ở bên sông" lặp ở D1/D5/D9 (điệp khúc),
     "Nhấc chiếc phone lên bỗng lặng người" ở D1/D21 (kết cấu vòng tròn).

════ THAY BẰNG GÌ ════

Không có tiêu chí tự động nào phân biệt được *điệp có chủ ý* với *lặp suy biến* mà
không phạt nhầm cái thứ nhất. Thử nhiều cách đều rơi vào một trong hai: bỏ sót ca
suy biến, hoặc bắt nhầm điệp khúc.

Đó chính là tình huống nguyên tắc N3 nói tới — và câu trả lời của N3 là **ghi công
khai rằng không kiểm được**, chứ không phải bịa một ngưỡng nghe hợp lý.

Nên nay:
    `dong_phan_biet`  CHẶN, nhưng chỉ ở ca suy biến tuyệt đối: cả bài chỉ có
                      MỘT dòng duy nhất lặp lại. Đó không phải điệp, đó là không
                      có bài thơ. Tiêu chí là số nguyên, không phải ngưỡng dò được.
    `so_dong_lap`     KHÔNG chặn — đưa sang HITL (§22) làm tín hiệu cho người xem.

Ca `"Trời cao mây biếc xanh ngời X"` lặp bốn lần với mỗi dòng đổi một tiếng cuối:
luật cho qua, chiều nào cũng cho qua, và **đó là câu trả lời đúng** — nó là điệp
cấu trúc, thứ S20 cho phép. Nếu nó không đáng trả ra thì đó là phán đoán thẩm mỹ,
và phán đoán thẩm mỹ thuộc về người, không thuộc về một hằng số.

════ NGƯỠNG CÒN LẠI LẤY TỪ ĐÂU ════

Sau khi gỡ hai chiều trên, **KHÔNG CÒN NGƯỠNG TUỲ Ý NÀO** trong hệ thống:

    nhac_tinh = 1,0       SUY RA từ QĐ-2 (không cho phá khuôn)
    bam_chu_de ≥ 1 tiếng  ngưỡng nhỏ nhất có nghĩa, chỉ kiểm khi có chủ đề
    da_dang_van ≥ 1       suy ra từ nghĩa của "có gieo vần"
    dong_phan_biet ≥ 2    suy ra từ nghĩa của "một bài thơ"
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

# `rule.py` ĐÓNG BĂNG: chỉ đọc kiểu kết quả, không gọi hàm nào có thể đổi nó.
from application.rule import PoemVerdict

# Số dòng PHÂN BIỆT tối thiểu để một văn bản còn là bài thơ.
#
# KHÔNG phải ngưỡng dò được: đây là số nguyên nhỏ nhất có nghĩa. Một văn bản mà mọi
# dòng đều y hệt nhau không phải điệp — điệp cần có cái để điệp XEN GIỮA. Đặt ở 2
# là chỗ duy nhất phát biểu được mà không đụng vào quyền S20.
SO_DONG_PHAN_BIET_TOI_THIEU = 2


@dataclass(frozen=True, slots=True)
class ChieuChatLuong:
    """Một chiều chất lượng.

    `do_duoc=False` nghĩa là chiều này KHÔNG kiểm được bằng thuật toán — khi đó
    `dat` luôn True và không mang ý nghĩa gì. Ghi ra như vậy thay vì lặng lẽ cho
    qua, đúng nguyên tắc N3.
    """

    ma: str
    ten: str
    do_duoc: bool
    dat: bool
    so_do: float | None
    nguong: str
    bang_chung: str
    # Dòng bị chiều này quy trách nhiệm, đếm từ 1. Rỗng có HAI nghĩa khác nhau:
    # chiều đạt, hoặc chiều hỏng nhưng lỗi khuếch tán ra cả bài.
    # Vòng sửa dùng nó để biết dòng nào được phép ghim "giữ nguyên".
    dong_lien_quan: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True)
class KetQuaChatLuong:
    """Phán quyết chất lượng. KHÔNG bao giờ đụng `thuoc_the` của bài."""

    dat: bool
    chieu: tuple[ChieuChatLuong, ...]
    chi_tiet: Mapping[str, object] = field(default_factory=dict)

    @property
    def chieu_hong(self) -> tuple[ChieuChatLuong, ...]:
        return tuple(c for c in self.chieu if c.do_duoc and not c.dat)

    @property
    def chieu_khong_do_duoc(self) -> tuple[str, ...]:
        return tuple(c.ma for c in self.chieu if not c.do_duoc)

    @property
    def dong_bi_quy_trach_nhiem(self) -> frozenset[int]:
        """Hợp các dòng bị một chiều hỏng nào đó chỉ tên.

        Rỗng KHÔNG có nghĩa là mọi dòng đều ổn — nó có thể nghĩa là lỗi khuếch tán
        ra cả bài và không quy được cho dòng nào. Người gọi phải phân biệt hai ca
        đó; `dung_khung_suy_luan` làm đúng việc ấy.
        """
        return frozenset(d for c in self.chieu_hong for d in c.dong_lien_quan)

    @property
    def co_loi_khuech_tan(self) -> bool:
        """Có chiều hỏng nào không quy được cho dòng cụ thể không."""
        return any(not c.dong_lien_quan for c in self.chieu_hong)


def _bo_dau(s: str) -> str:
    """Bỏ dấu thanh và dấu nền để so khớp chủ đề rộng hơn một chút."""
    return "".join(
        k for k in unicodedata.normalize("NFD", s.lower()) if not unicodedata.combining(k)
    )


def _tu_khoa_chu_de(chu_de: str) -> frozenset[str]:
    """Tách chủ đề thành tiếng. Bỏ hư từ — chúng có mặt ở mọi bài nên vô dụng."""
    bo = {"ve", "cua", "va", "mot", "bai", "tho", "cho", "voi", "nhung", "cac"}
    return frozenset(
        t for t in _bo_dau(chu_de).replace(",", " ").split() if t and t not in bo
    )


def danh_gia_chat_luong(
    v: PoemVerdict,
    *,
    chu_de: str | None = None,
) -> KetQuaChatLuong:
    """Chấm bảy chiều. THUẦN, ĐỒNG BỘ, TẤT ĐỊNH — không I/O, không LLM.

    Nhận `PoemVerdict` đã tính sẵn thay vì tự phân tích văn bản: phân tích làm hai
    lần là mở đường cho hai nơi hiểu khác nhau về cùng một dòng thơ (nguyên tắc P1).
    """
    tat_ca_tieng: list[str] = [t for d in v.dong for t in d.tieng]
    chieu: list[ChieuChatLuong] = []

    # ── CL1 · dong_phan_biet — ca suy biến tuyệt đối ─────────────────────────
    #
    # Thay cho `lap_tieng ≥ 0,55` (ngưỡng tuỳ ý, thiên vị độ dài) và `lap_dong = 0`
    # (phạt đúng quyền S20). Xem docstring module.
    #
    # Tiêu chí là SỐ NGUYÊN nhỏ nhất có nghĩa, không phải ngưỡng dò được: một văn
    # bản mà mọi dòng y hệt nhau không phải điệp — điệp cần có cái để xen giữa.
    chuan = [" ".join(d.van_ban.split()).lower() for d in v.dong]
    so_phan_biet = len(set(chuan))
    chieu.append(
        ChieuChatLuong(
            ma="CL1", ten="dong_phan_biet", do_duoc=True,
            dat=not v.dong or so_phan_biet >= SO_DONG_PHAN_BIET_TOI_THIEU,
            so_do=float(so_phan_biet),
            nguong=f"≥ {SO_DONG_PHAN_BIET_TOI_THIEU} dòng phân biệt",
            bang_chung=f"{so_phan_biet}/{len(chuan)} dòng phân biệt",
        )
    )

    # ── CL2 · so_dong_lap — TÍN HIỆU, KHÔNG CHẶN ─────────────────────────────
    #
    # 🩸 Bản trước chặn khi có bất kỳ dòng nào lặp. Đo lại trên 6.000 bài người
    # viết: 164 bài bị bắt, và TOÀN BỘ là điệp có chủ ý (điệp khúc, kết cấu vòng
    # tròn). S20 cho phép điệp dòng, nên chặn vì nó là vi phạm N2.
    #
    # Nay chỉ ĐẾM và chuyển cho HITL (§22): người xem được, hằng số thì không.
    da_gap: set[str] = set()
    ban_sao: list[int] = []
    for d, c in zip(v.dong, chuan, strict=True):
        if c in da_gap:
            ban_sao.append(d.so)
        da_gap.add(c)
    chieu.append(
        ChieuChatLuong(
            ma="CL2", ten="so_dong_lap", do_duoc=True,
            # `dat` LUÔN True: chiều này quan sát, không phán.
            dat=True,
            so_do=float(len(ban_sao)),
            nguong="— (tín hiệu cho HITL, KHÔNG chặn: S20 cho phép điệp dòng)",
            bang_chung=(
                "không dòng nào lặp" if not ban_sao
                else f"{len(ban_sao)} dòng lặp lại (D{', D'.join(map(str, ban_sao[:5]))})"
                     " — điệp có chủ ý là quyền theo S20"
            ),
            dong_lien_quan=tuple(ban_sao),
        )
    )

    # ── CL3 · bam_chu_de (theme_alignment) ───────────────────────────────────
    # CHỈ kiểm khi người dùng có nêu chủ đề. Không có chủ đề mà vẫn chấm là chấm
    # một thứ không ai yêu cầu.
    if chu_de and _tu_khoa_chu_de(chu_de):
        khoa = _tu_khoa_chu_de(chu_de)
        trong_bai = {_bo_dau(t) for t in tat_ca_tieng}
        giao = khoa & trong_bai
        chieu.append(
            ChieuChatLuong(
                ma="CL3", ten="bam_chu_de", do_duoc=True,
                dat=bool(giao), so_do=float(len(giao)),
                nguong="≥ 1 tiếng của chủ đề xuất hiện trong bài",
                bang_chung=(
                    f"bài có {sorted(giao)} từ chủ đề {sorted(khoa)}" if giao
                    else f"không tiếng nào của chủ đề {sorted(khoa)} xuất hiện trong bài"
                ),
            )
        )
    else:
        chieu.append(
            ChieuChatLuong(
                ma="CL3", ten="bam_chu_de", do_duoc=False, dat=True, so_do=None,
                nguong="—",
                bang_chung="không kiểm: người dùng không nêu chủ đề",
            )
        )

    # ── CL4 · nhac_tinh (rhythm) ─────────────────────────────────────────────
    # Đọc thẳng số của rule.py. Ngưỡng 1,0 SUY RA từ QĐ-2: không cho phá khuôn,
    # nên mọi dòng phải theo khuôn, nên tỷ lệ phải bằng 1.
    chieu.append(
        ChieuChatLuong(
            ma="CL4", ten="nhac_tinh", do_duoc=True,
            dat=v.ty_le_theo_khuon >= 1.0, so_do=v.ty_le_theo_khuon,
            nguong="= 1,0 (suy ra từ QĐ-2, không phải ngưỡng tự chọn)",
            bang_chung=f"tỷ lệ dòng theo khuôn luân phiên = {v.ty_le_theo_khuon}",
        )
    )

    # ── CL5 · da_dang_van (rhythm) ───────────────────────────────────────────
    lop_van = {nhan for kho in v.so_do_van_theo_kho for nhan in kho if nhan != "x"}
    chieu.append(
        ChieuChatLuong(
            ma="CL5", ten="da_dang_van", do_duoc=True,
            dat=bool(lop_van), so_do=float(len(lop_van)),
            nguong="≥ 1 lớp vần",
            bang_chung=(
                f"{len(lop_van)} lớp vần: {sorted(lop_van)}" if lop_van
                else "không dòng nào tham gia gieo vần"
            ),
        )
    )

    # ── CL6, CL7 · KHÔNG KIỂM ĐƯỢC (N3) ──────────────────────────────────────
    chieu.append(
        ChieuChatLuong(
            ma="CL6", ten="mach_lac", do_duoc=False, dat=True, so_do=None, nguong="—",
            bang_chung="🔶 semantic_coherence đòi hiểu nội dung — thuộc node Reviewer (G7), "
                       "không chặn được ở cổng thuần",
        )
    )
    chieu.append(
        ChieuChatLuong(
            ma="CL7", ten="hinh_anh", do_duoc=False, dat=True, so_do=None, nguong="—",
            bang_chung="🔶 imagery đòi hiểu nội dung — thuộc node Reviewer (G7)",
        )
    )

    dat = all(c.dat for c in chieu if c.do_duoc)
    return KetQuaChatLuong(
        dat=dat,
        chieu=tuple(chieu),
        chi_tiet={
            "so_chieu_do_duoc": sum(1 for c in chieu if c.do_duoc),
            "so_chieu_khong_do_duoc": sum(1 for c in chieu if not c.do_duoc),
            "nguong_tuy_y": "không còn — xem docstring module",
            "canh_bao": "chất lượng KHÔNG loại bài khỏi thể — chỉ chặn việc trả ra",
        },
    )


def mo_ta_chat_luong(kq: KetQuaChatLuong) -> tuple[str, ...]:
    """Dòng tham khảo cho biên bản. Không dòng nào ở đây được dùng để chặn."""
    ra = [f"{c.ten}: {c.bang_chung}" for c in kq.chieu if c.do_duoc]
    ra.extend(f"{c.ten}: {c.bang_chung}" for c in kq.chieu if not c.do_duoc)
    return tuple(ra)


def cac_chieu_theo_ma(kq: KetQuaChatLuong, ma: Sequence[str]) -> tuple[ChieuChatLuong, ...]:
    can = set(ma)
    return tuple(c for c in kq.chieu if c.ma in can)
