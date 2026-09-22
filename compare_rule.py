"""⛔ HỒ SƠ ĐỐI CHIẾU — FILE NÀY KHÔNG CHẠY TRONG HỆ THỐNG SỐNG.

Bộ kiểm luật **LỤC BÁT** của một hệ khác. Hệ thống sống làm thất ngôn tự do, và bộ
kiểm của nó là `src/application/rule.py` — file ĐÓNG BĂNG, có băm SHA-256 ghim
trong `tests/architecture/test_rule_dong_bang.py`.

⚠️ **Đừng nhập luật từ đây.** Luật lục bát — niêm, vần lưng, câu Lục/câu Bát —
không thuộc thể mà hệ thống này làm. Một điều luật sai thể lọt vào `rule.LUAT` hay
vào prompt sẽ được mô hình đọc như luật thật.

Có test ghim: `tests/architecture/test_file_doi_chieu_khong_chay.py` — không module
nào trong `src/` được import file này.

════════════════════════════════════════════════════════════════════════════
BỔ SUNG PHẦN LÕI — 22/09/2026

Bản trước không import nổi: `import __main__` thừa, và hai import tương đối
`from .constants` / `from .rhyme` trỏ tới một gói KHÔNG TỒN TẠI trong repo.

Lượt sửa này CHỈ BÙ PHẦN LÕI CÒN THIẾU. §0 dưới đây cung cấp đúng sáu cái mà thân
bài cần và chưa bao giờ có:

    CRITICAL_ERROR_KEYWORDS     (vốn ở .constants)
    clean_and_tokenize          ┐
    get_tone                    │
    get_bang_type               ├ (vốn ở .rhyme)
    is_rhyme_match              │
    get_suggested_endings       ┘

⛔ **LOGIC LUẬT CHỈ ĐỔI ĐÚNG HAI KHỐI** — xem §1.1 ngay dưới đây. Ngoài hai khối ấy,
toàn bộ phần từ `evaluate_errors` trở xuống vẫn được chép NGUYÊN VĂN từ
`git show HEAD:compare_rule.py`. Mọi khiếm khuyết thiết kế đã ghi ở
`docs/Report_Phan_Tich_Ma_Kiem_Luat.md` — bắt buộc câu 1 gieo vần, `elif` nuốt lỗi,
hai nhánh cùng điều kiện ở thơ tám chữ, lệch pha lục/bát sau khổ lẻ — VẪN CÒN
NGUYÊN. Đó là chủ ý: hồ sơ đối chiếu phải phản ánh đúng bộ luật thế hệ trước,
không phải bản đã được sửa hộ.

Ai muốn biết các khiếm khuyết ấy làm lệch kết quả bao nhiêu thì đọc
`docs/Report_analisys_rule2.md` — lưu ý số liệu trong đó sinh ra TRƯỚC bản sửa 22/09
dưới đây, nên không còn khớp với hành vi hiện tại của hai hàm thất ngôn.

════════════════════════════════════════════════════════════════════════════
§1.1. BẢN SỬA 22/09/2026 — NỚI LUẬT BẰNG/TRẮC THẤT NGÔN

Theo yêu cầu chủ dự án: **chỉ câu đầu** phải tuân thủ nhịp "nhị tứ lục phân minh"
(B-T-B hoặc T-B-T ở tiếng 2/4/6). Các câu còn lại KHÔNG còn bị chấm Bằng/Trắc —
không error, không success, im lặng hoàn toàn.

    bay_chu_rule_check          bỏ bảng `expected_patterns` 4 dòng + vòng lặp;
                                guard đổi từ `all(...)` sang `len(line1) >= 6`
    bay_chu_bat_cu_rule_check   bỏ bảng `base/opposite` 8 dòng + vòng lặp

Hai khối GIEO VẦN của cả hai hàm không đụng tới. `luc_bat_rule_check` và
`tam_chu_rule_check` không đụng tới.

Vì sao nới: bảng cũ suy luật từ tiếng 2 câu 1 rồi ép cả khổ theo, quá nghiêm với
thất ngôn hiện đại — một bài chỉ giữ nhịp ở câu mở sẽ trượt hàng loạt lỗi CRITICAL.

⚠️ Lệnh đối chiếu nguyên văn ở §1 KHÔNG còn cho kết quả trùng khít vì bản sửa này.

KHÔNG SỬA: `rule.py`. File ấy đóng băng và lượt bổ sung này không chạm vào nó.
"""

import re
import unicodedata
from typing import List, Set, Tuple

# ══════════════════════════════════════════════════════════════════════════════
# §0. PHẦN LÕI CÒN THIẾU
#
# Sáu cái tên mà thân bài import từ `.constants` và `.rhyme` — hai module chưa bao
# giờ tồn tại trong repo. Viết ở đây để file tự chứa và chạy được.
#
# CỐ Ý KHÔNG import từ `src/application/rule.py`: một hồ sơ đối chiếu mà dùng lại
# ngữ âm của bộ kiểm đang sống thì không còn là ý kiến thứ hai, nó chỉ là
# `rule.py` soi gương. Mức đồng thuận giữa hai tầng ngữ âm được ĐO chứ không giả
# định — xem `datalake/scripts/chay_doi_chieu_rule2.py` §3.
# ══════════════════════════════════════════════════════════════════════════════

#: Từ khoá phân loại lỗi nặng. Thân bài gắn nhãn "[CRITICAL!]" vào chính câu
#: thông điệp, nên bảng này tra đúng chuỗi ấy.
CRITICAL_ERROR_KEYWORDS = {
    "luc_bat": ["CRITICAL!"],
    "bay_chu": ["CRITICAL!"],
    "tam_chu": ["CRITICAL!"],
}

_GACH_NOI = "-"


def _la_dau_cau(ky_tu: str) -> bool:
    """Nhận diện dấu câu theo PHÂN LOẠI UNICODE, không theo danh sách liệt kê tay.

    Danh sách liệt kê luôn thiếu — gạch ngang dài "—", gạch ngang ngắn "–", nháy
    kép "«»", ba chấm "…". Gạch nối "-" là ngoại lệ duy nhất vì nó mang thông tin
    tách âm tiết ("ra-đi-ô" = 3 tiếng).
    """
    if ky_tu == _GACH_NOI:
        return False
    return unicodedata.category(ky_tu).startswith(("P", "S"))


_CHU_SO = re.compile(r"^\d+$")
_SO_THAP_PHAN = re.compile(r"^(\d+)[.,](\d+)$")
_DON_VI = ("không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín")
_HANG = ("", "nghìn", "triệu", "tỷ")


def _doc_nhom_ba(n: int, day_du: bool) -> List[str]:
    tram, chuc, dv = n // 100, (n // 10) % 10, n % 10
    ra: List[str] = []
    if tram > 0 or day_du:
        ra += [_DON_VI[tram], "trăm"]
    if chuc == 0:
        if dv > 0:
            ra += (["linh", _DON_VI[dv]] if (tram > 0 or day_du) else [_DON_VI[dv]])
    elif chuc == 1:
        ra += ["mười"]
        if dv == 5:
            ra += ["lăm"]
        elif dv > 0:
            ra += [_DON_VI[dv]]
    else:
        ra += [_DON_VI[chuc], "mươi"]
        if dv == 1:
            ra += ["mốt"]
        elif dv == 4:
            ra += ["tư"]
        elif dv == 5:
            ra += ["lăm"]
        elif dv > 0:
            ra += [_DON_VI[dv]]
    return ra


def doc_so(n: int) -> List[str]:
    """Quy một số nguyên về danh sách âm tiết (chuẩn đọc văn viết miền Bắc).

    Số vượt quá "tỷ" thì đọc rời từng chữ số — tránh phải bịa quy ước "nghìn tỷ
    tỷ", và đó cũng là cách người Việt thật sự đọc khi số quá dài.
    """
    if n == 0:
        return ["không"]
    goc = str(n)
    nhom: List[int] = []
    m = n
    while m > 0:
        nhom.append(m % 1000)
        m //= 1000
    if len(nhom) > len(_HANG):
        return [_DON_VI[int(c)] for c in goc]
    nhom.reverse()
    ra: List[str] = []
    for i, gia_tri in enumerate(nhom):
        if gia_tri == 0:
            continue
        ra += _doc_nhom_ba(gia_tri, day_du=(i != 0))
        bac = len(nhom) - i - 1
        if bac > 0:
            ra.append(_HANG[bac])
    return ra


def _doc_token_so(token: str) -> List[str]:
    m = _SO_THAP_PHAN.match(token)
    if m:
        return _doc_token_so(m.group(1)) + ["phẩy"] + [_DON_VI[int(c)] for c in m.group(2)]
    if len(token) > 1 and token[0] == "0":
        return [_DON_VI[int(c)] for c in token]
    return doc_so(int(token))


def _got_hai_dau(tu: str) -> str:
    i, j = 0, len(tu)
    while i < j and _la_dau_cau(tu[i]):
        i += 1
    while j > i and _la_dau_cau(tu[j - 1]):
        j -= 1
    return tu[i:j]


def clean_and_tokenize(dong: str) -> List[str]:
    """Tách một dòng thành danh sách TIẾNG (âm tiết).

    Không phải tách theo dấu cách: dấu câu bị loại trước khi đếm, gạch nối tách
    tiếp, chữ số quy về cách đọc rồi mới đếm ("năm 1975" = 8 tiếng).
    """
    ra: List[str] = []
    for tho in dong.split():
        tu = _got_hai_dau(tho)
        if not tu:
            continue
        if _SO_THAP_PHAN.match(tu):
            ra.extend(_doc_token_so(tu))
            continue
        sach = "".join(" " if _la_dau_cau(c) else c for c in tu)
        for cum in sach.split():
            for phan in cum.split(_GACH_NOI):
                if not phan:
                    continue
                ra.extend(_doc_token_so(phan) if _CHU_SO.match(phan) else [phan])
    return ra


_DAU_SAC, _DAU_HUYEN = "́", "̀"
_DAU_HOI, _DAU_NGA, _DAU_NANG = "̉", "̃", "̣"
_DAU_THANH = frozenset({_DAU_SAC, _DAU_HUYEN, _DAU_HOI, _DAU_NGA, _DAU_NANG})


def _dau_thanh_cua(tieng: str) -> str:
    for c in unicodedata.normalize("NFD", tieng):
        if c in _DAU_THANH:
            return c
    return ""


def get_tone(tieng: str) -> str:
    """Bằng = ngang, huyền.  Trắc = sắc, hỏi, ngã, nặng."""
    d = _dau_thanh_cua(tieng)
    return "Bằng" if (not d or d == _DAU_HUYEN) else "Trắc"


def get_bang_type(tieng: str) -> str:
    """Phân biệt hai thanh bằng — phục vụ luật điệp thanh của câu Bát."""
    return "huyền" if _dau_thanh_cua(tieng) == _DAU_HUYEN else "ngang"


def _bo_dau_thanh(tieng: str) -> str:
    """Bỏ dấu thanh, GIỮ dấu nền: "về" -> "vê", không thành "ve"."""
    ra = "".join(c for c in unicodedata.normalize("NFD", tieng) if c not in _DAU_THANH)
    return unicodedata.normalize("NFC", ra)


# ── Cấu trúc âm tiết: [Âm đầu] + [Âm đệm] + Âm chính + [Âm cuối] ──────────────
_AM_DAU = (
    "ngh", "ng", "nh", "ch", "gh", "gi", "kh", "ph", "th", "tr", "qu",
    "b", "c", "d", "đ", "g", "h", "k", "l", "m", "n", "p", "r", "s", "t", "v", "x",
)
_AM_CUOI = ("ng", "nh", "ch", "c", "m", "n", "p", "t", "i", "y", "o", "u")
_CHUAN_HOA = {"ia": "iê", "ya": "iê", "yê": "iê", "ua": "uô", "ưa": "ươ", "y": "i"}
_SAU_AM_DEM_U = ("y", "ê", "â", "ơ")
_NGUYEN_AM = set("aăâeêioôơuưy")


def _am_dau_kha_di(s: str) -> str:
    """Khớp dài nhất MÀ phần dư còn nguyên âm; không có thì lùi về khớp dài nhất.

    Nếu chỉ khớp dài nhất thì "gìn" bị đọc thành "gi" + "n" (phần vần "n", vô
    nghĩa) thay vì "g" + "ìn", và "gìn" hoá ra không vần với "nhìn".
    """
    dai_nhat = ""
    for pa in _AM_DAU:
        if s.startswith(pa) and len(s) > len(pa):
            if not dai_nhat:
                dai_nhat = pa
            if _NGUYEN_AM & set(s[len(pa):]):
                return pa
    return dai_nhat


def van_cua(tieng: str) -> str:
    """Phần dùng để so vần: ÂM CHÍNH + ÂM CUỐI, bỏ âm đệm.

    Âm đệm không cản trở hiệp vần trong thơ Việt: `hoa` gieo được với `nhà`, `ta`.
    """
    s = _bo_dau_thanh(tieng).lower()
    am_dau = _am_dau_kha_di(s)
    if am_dau:
        s = s[len(am_dau):]
    if am_dau == "qu":
        pass  # chữ "u" đã nằm trong âm đầu, phần còn lại là vần
    elif s.startswith("o") and len(s) > 1 and s[1] in "aăe":
        s = s[1:]
    elif s.startswith("u") and len(s) > 1 and s[1] in _SAU_AM_DEM_U:
        s = s[1:]
    am_cuoi = ""
    for ac in _AM_CUOI:
        if s.endswith(ac) and len(s) > len(ac):
            am_cuoi, s = ac, s[: -len(ac)]
            break
    return _CHUAN_HOA.get(s, s) + am_cuoi


# ── Bảng vần thông — Trần Trọng Kim, "Việt thi" I-6 ───────────────────────────
# ĐÂY LÀ ĐỒ THỊ, KHÔNG PHẢI PHÂN HOẠCH. Chính tác giả viết "ang thông với ương
# (không thông được với uông)" rồi vài dòng sau "uông thông với ương" — nên quan
# hệ này ĐỐI XỨNG nhưng KHÔNG BẮC CẦU. Ép thành lớp tương đương sẽ bịa thêm
# những cặp hiệp vần mà nguồn không cho.
_NHOM_VAN = (
    ("e", "ê", "i"),
    ("o", "ô", "u"),
    ("ai", "oi", "ôi", "ơi", "ươi", "ui"),
    ("ao", "eo", "êu", "iêu", "iu", "ưu"),
    ("en", "in", "iên"),
    ("on", "ôn", "uôn"),
    ("ăng", "âng", "ưng"),
    ("ong", "ông", "ung"),
    ("anh", "ênh", "inh"),
)
_CAP_VAN = (
    ("a", "ơ"), ("ơ", "ư"),
    ("ai", "ay"), ("ao", "au"),
    ("am", "ơm"), ("ăm", "âm"), ("êm", "im"),
    ("an", "ơn"), ("ăn", "ân"),
    ("on", "un"),
    ("ang", "ương"), ("uông", "ương"),
    ("o", "uô"), ("iê", "ê"), ("ac", "ươc"), ("ât", "ưt"),
)


def _dung_bang_van() -> frozenset:
    canh = set()
    for nhom in _NHOM_VAN:
        for i, a in enumerate(nhom):
            for b in nhom[i + 1:]:
                canh.add(frozenset((a, b)))
    for a, b in _CAP_VAN:
        canh.add(frozenset((a, b)))
    return frozenset(canh)


CAP_VAN_THONG = _dung_bang_van()


def is_rhyme_match(a: str, b: str, poem_type: str = "luc_bat") -> bool:
    """Hai tiếng có hiệp vần không. Vần chính hoặc vần thông đều tính.

    `poem_type` giữ nguyên trong chữ ký vì thân bài truyền nó vào, nhưng phép so
    không đổi theo thể: quan hệ hiệp vần là chuyện của âm tiết, không của thể thơ.
    """
    if not a or not b:
        return False
    va, vb = van_cua(a), van_cua(b)
    return va == vb or frozenset((va, vb)) in CAP_VAN_THONG


def get_suggested_endings(tieng: str, poem_type: str = "luc_bat") -> str:
    """Các phần vần gieo được với `tieng`, lấy từ bảng vần thông ở trên."""
    v = van_cua(tieng)
    goi = sorted({x for c in CAP_VAN_THONG if v in c for x in c if x != v})
    return ", ".join("-" + x for x in [v] + goi[:7])


# ══════════════════════════════════════════════════════════════════════════════
# §1. THÂN BÀI — NGUYÊN VĂN, TRỪ HAI KHỐI ĐÃ NÊU Ở §1.1
#
# Chép từ `git show HEAD:compare_rule.py`, sau đó nới luật Bằng/Trắc ở đúng hai chỗ:
# khối chấm tiếng 2/4/6 trong `bay_chu_rule_check` và trong `bay_chu_bat_cu_rule_check`
# (chi tiết ở §1.1 đầu file). Đối chiếu phần còn lại bằng:
#     git show HEAD:compare_rule.py | sed -n '/^def evaluate_errors/,$p'
# — lệnh này sẽ báo khác ở hai khối trên; mọi khác biệt NGOÀI hai khối đó là lỗi.
# ══════════════════════════════════════════════════════════════════════════════

def evaluate_errors(errors: List[str], poem_type: str = "luc_bat") -> Tuple[int, int]:
    """Return (critical_count, minor_count)."""
    kw_list = CRITICAL_ERROR_KEYWORDS.get(poem_type, [])
    critical = sum(1 for e in errors if any(kw in e for kw in kw_list))
    return critical, len(errors) - critical
 
 
def annotate_poem_words(poem: str) -> str:
    lines = [line.strip() for line in poem.splitlines() if line.strip()]
    annotated = []
    for line in lines:
        words = clean_and_tokenize(line)
        parts = [f"{w} ({i}, {get_tone(w)})" for i, w in enumerate(words, start=1)]
        annotated.append(" ".join(parts))
    return "\n".join(annotated)
 
 
def luc_bat_rule_check(poem: str) -> Tuple[bool, List[str], List[str]]:
    """
    Checks lục bát prosody for a poem of any length.
 
    Stanza handling:
    - Stanzas are delimited by one or more blank lines (\\n\\n).
    - All per-line rules (Bằng/Trắc, syllable count) apply regardless of stanza.
    - Niêm check applies within each lục-bát pair UNLESS the pair straddles a stanza break.
    - Lục T6 ↔ Bát T6/T4 rhyme check applies within each pair (same rule).
    - Bát T8 ↔ next Lục T6 rhyme check is SKIPPED when the two lines belong to different stanzas.
 
    Returns: (is_ok, list_of_errors, list_of_successes)
    """
    errors: List[str] = []
    successes: List[str] = []
 
    # --- Parse stanzas ---
    raw_stanzas = re.split(r"\n{2,}", poem)
    stanzas_lines: List[List[str]] = []
    for raw in raw_stanzas:
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if lines:
            stanzas_lines.append(lines)
 
    if not stanzas_lines:
        errors.append("Bài thơ trống.")
        return False, errors, successes
 
    # Build flat line list; record which global indices open a new stanza
    all_lines: List[str] = []
    new_stanza_starts: Set[int] = set()
    for stanza in stanzas_lines:
        if all_lines:
            new_stanza_starts.add(len(all_lines))
        all_lines.extend(stanza)
 
    n = len(all_lines)
 
    # --- 0. Structural checks ---
    if n % 2 != 0:
        errors.append(
            f"Sai số dòng [CRITICAL!]: {n} dòng "
            f"(lục bát cần số dòng chẵn để tạo cặp lục-bát hoàn chỉnh)."
        )
    else:
        successes.append(f"Cấu trúc: {n} dòng ({n // 2} cặp lục-bát).")
 
    for s_idx, stanza in enumerate(stanzas_lines):
        if len(stanza) % 2 != 0:
            errors.append(
                f"[Khổ {s_idx + 1}] Có {len(stanza)} dòng lẻ "
                f"— khổ lục bát cần số dòng chẵn."
            )
 
    words_by_line = [clean_and_tokenize(line) for line in all_lines]
    lengths = [len(w) for w in words_by_line]
 
    # Syllable-count check
    length_errors = []
    for i, length in enumerate(lengths):
        expected = 6 if (i % 2 == 0) else 8
        if length != expected:
            length_errors.append(f"Dòng {i + 1} ('{all_lines[i]}'): {length} tiếng (cần {expected})")
    if length_errors:
        errors.append(f"Sai số tiếng theo dòng [CRITICAL!]: {'; '.join(length_errors)}")
    else:
        successes.append(f"Số tiếng: Đúng chuẩn ({'-'.join(str(l) for l in lengths)}).")
 
    # --- 1. Bằng/Trắc & Nhạc điệu ---
    for idx, words in enumerate(words_by_line):
        if not words:
            continue
        is_luc = (idx % 2 == 0)
        line_name = f"Dòng {idx + 1}"
 
        if is_luc and len(words) >= 6:
            t2, t3, t4, t6 = (
                get_tone(words[1]), get_tone(words[2]),
                get_tone(words[3]), get_tone(words[5]),
            )
            if t2 == "Trắc":
                if t3 != "Trắc" or t6 != "Bằng":
                    errors.append(
                        f"[{line_name}] Vi phạm luật Tiểu Đối: Từ 2 mang thanh Trắc ('{words[1]}'). Yêu cầu bắt buộc từ 3 ('{words[2]}') phải là thanh Trắc và từ 6 ('{words[5]}') phải là thanh Bằng."
                    )
                else:
                    successes.append(f"[{line_name}] Đạt chuẩn Tiểu Đối (Từ 2, 3 Trắc - Từ 6 Bằng).")
            else:
                if t4 != "Trắc" or t6 != "Bằng":
                    wrong_words = []
                    if t4 != "Trắc": wrong_words.append(f"Từ 4 '{words[3]}' ({t4}) sai luật, bắt buộc phải là thanh Trắc")
                    if t6 != "Bằng": wrong_words.append(f"Từ 6 '{words[5]}' ({t6}) sai luật, bắt buộc phải là thanh Bằng")
                    errors.append(
                        f"[{line_name}] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(wrong_words)}. Hãy thay thế bằng các từ có thanh điệu đúng."
                    )
                else:
                    successes.append(f"[{line_name}] Đạt chuẩn Bằng/Trắc (2 Bằng, 4 Trắc, 6 Bằng).")
 
        elif not is_luc and len(words) >= 8:
            t2, t4, t6, t8 = (
                get_tone(words[1]), get_tone(words[3]),
                get_tone(words[5]), get_tone(words[7]),
            )
            if t6 == "Bằng" and t8 == "Bằng":
                b6, b8 = get_bang_type(words[5]), get_bang_type(words[7])
                if b6 == b8:
                    errors.append(
                        f"[{line_name}] Mất tính nhạc: Từ 6 ('{words[5]}') và từ 8"
                        f" ('{words[7]}') điệp thanh {b6}."
                        f" Yêu cầu một thanh ngang, một thanh huyền."
                    )
                else:
                    successes.append(f"[{line_name}] Nhạc điệu chuẩn (Từ 6 và 8 phối hợp Ngang/Huyền tốt).")
            if t2 != "Bằng" or t8 != "Bằng":
                wrong_words = []
                if t2 != "Bằng": wrong_words.append(f"Từ 2 '{words[1]}' ({t2})")
                if t8 != "Bằng": wrong_words.append(f"Từ 8 '{words[7]}' ({t8})")
                errors.append(
                    f"[{line_name}] Vi phạm Bằng/Trắc [CRITICAL!]: {' và '.join(wrong_words)} sai luật, bắt buộc phải là thanh Bằng."
                )
            elif not (t4 == "Trắc" and t6 == "Bằng"):
                wrong_words = []
                if t4 != "Trắc": wrong_words.append(f"Từ 4 '{words[3]}' ({t4}) sai luật, bắt buộc phải là thanh Trắc")
                if t6 != "Bằng": wrong_words.append(f"Từ 6 '{words[5]}' ({t6}) sai luật, bắt buộc phải là thanh Bằng")
                errors.append(
                    f"[{line_name}] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(wrong_words)}. Hãy thay thế bằng các từ có thanh điệu đúng."
                )
            else:
                successes.append(f"[{line_name}] Đạt chuẩn Bằng/Trắc (2 Bằng, 4 Trắc, 6 Bằng, 8 Bằng).")
 
    # --- 2. Niêm ---
    for i in range(0, n - 1, 2):
        j = i + 1
        if j >= n or j in new_stanza_starts:
            continue
        luc_w, bat_w = words_by_line[i], words_by_line[j]
        if len(luc_w) >= 4 and len(bat_w) >= 4:
            niem_loi = False
            if get_tone(luc_w[1]) != get_tone(bat_w[1]):
                errors.append(
                    f"[Lỗi Niêm] Dòng {i + 1} từ 2 ('{luc_w[1]}' - {get_tone(luc_w[1])})"
                    f" không niêm với Dòng {j + 1} từ 2 ('{bat_w[1]}' - {get_tone(bat_w[1])}). Bắt buộc hai từ này phải cùng nhóm thanh Bằng hoặc cùng nhóm thanh Trắc."
                )
                niem_loi = True
            if get_tone(luc_w[3]) != get_tone(bat_w[3]):
                errors.append(
                    f"[Lỗi Niêm] Dòng {i + 1} từ 4 ('{luc_w[3]}' - {get_tone(luc_w[3])})"
                    f" không niêm với Dòng {j + 1} từ 4 ('{bat_w[3]}' - {get_tone(bat_w[3])}). Bắt buộc hai từ này phải cùng nhóm thanh Bằng hoặc cùng nhóm thanh Trắc."
                )
                niem_loi = True
            if not niem_loi:
                successes.append(f"[Luật Niêm] Dòng {i + 1} niêm chuẩn xác với Dòng {j + 1}.")
 
    # --- 3. Vần ---
    for i in range(0, n - 1, 2):
        j = i + 1
        if j >= n or j in new_stanza_starts:
            continue
 
        luc_w = words_by_line[i]
        bat_w = words_by_line[j]
        luc_name = f"Dòng {i + 1}"
        bat_name = f"Dòng {j + 1}"
 
        # Rule A: Lục T6 ↔ Bát T6/T4
        if len(luc_w) >= 6 and len(bat_w) >= 6:
            w_l6 = luc_w[5]
            w_b6 = bat_w[5]
            w_b4 = bat_w[3] if len(bat_w) >= 4 else ""
            rhyme_6_6 = is_rhyme_match(w_l6, w_b6)
            rhyme_6_4 = is_rhyme_match(w_l6, w_b4) if w_b4 else False
 
            if not rhyme_6_6 and not rhyme_6_4:
                sugg = get_suggested_endings(w_l6)
                errors.append(
                    f"[Sai Vần] [CRITICAL!] {luc_name} ('{w_l6}') chưa vần với"
                    f" từ thứ 6 ('{w_b6}') hay từ thứ 4 ('{w_b4}') ở {bat_name}."
                    f" Gợi ý: {sugg}"
                )
            elif rhyme_6_4 and not rhyme_6_6:
                if get_tone(w_b4) == "Bằng" and get_tone(w_b6) != "Trắc":
                    errors.append(
                        f"[Luật Gieo Vần {bat_name}] Vì gieo vần lưng vào từ thứ 4"
                        f" ('{w_b4}') là thanh Bằng, từ thứ 6 ('{w_b6}')"
                        f" bắt buộc phải là thanh Trắc."
                    )
                else:
                    successes.append(
                        f"[Gieo Vần] {luc_name} ('{w_l6}') gieo vần lưng chuẩn xác"
                        f" với từ 4 {bat_name} ('{w_b4}') và đổi thanh đúng luật."
                    )
            elif not rhyme_6_4 and rhyme_6_6:
                if get_tone(w_b4) != "Trắc" or get_tone(w_b6) != "Bằng":
                    errors.append(
                        f"[Luật Bằng/Trắc {bat_name}][CRITICAL!]"
                        f" Mô hình chuẩn: từ 4 phải Trắc, từ 6 phải Bằng."
                    )
                else:
                    successes.append(
                        f"[Gieo Vần] {luc_name} ('{w_l6}') gieo vần chuẩn"
                        f" với từ 6 {bat_name} ('{w_b6}')."
                    )
 
        # Rule B: Bát T8 ↔ next Lục T6 (only within same stanza)
        next_i = j + 1
        if next_i < n and next_i not in new_stanza_starts:
            next_luc_w = words_by_line[next_i]
            if len(bat_w) >= 8 and len(next_luc_w) >= 6:
                w_b8 = bat_w[7]
                w_nl6 = next_luc_w[5]
                if not is_rhyme_match(w_b8, w_nl6):
                    sugg = get_suggested_endings(w_b8)
                    errors.append(
                        f"[Sai Vần] {bat_name} ('{w_b8}') chưa vần chân"
                        f" với Dòng {next_i + 1} ('{w_nl6}'). Gợi ý: {sugg}"
                    )
                else:
                    successes.append(
                        f"[Gieo Vần] {bat_name} ('{w_b8}') vần chân chuẩn xác"
                        f" với Dòng {next_i + 1} ('{w_nl6}')."
                    )
 
    return len(errors) == 0, errors, successes
 
def bay_chu_rule_check(poem: str) -> Tuple[bool, List[str], List[str]]:
    """
    Checks prosody for 7-word poetry (Thơ 7 chữ / Thất ngôn) based on the user's provided rules.
    Processes the poem in 4-line chunks (tứ tuyệt).
    
    Returns: (is_ok, list_of_errors, list_of_successes)
    """
    errors: List[str] = []
    successes: List[str] = []
 
    # --- Parse lines ---
    raw_stanzas = re.split(r"\n{2,}", poem)
    all_lines: List[str] = []
    for raw in raw_stanzas:
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        all_lines.extend(lines)
 
    if not all_lines:
        errors.append("Bài thơ trống.")
        return False, errors, successes
 
    n = len(all_lines)
 
    # --- 0. Structural checks ---
    if n % 4 != 0:
        errors.append(
            f"Sai số dòng: Bài thơ hiện có {n} dòng. "
            f"Thơ 7 chữ (theo luật tứ tuyệt) cần có số dòng chia hết cho 4 để khớp luật Bằng/Trắc và gieo vần."
        )
    else:
        successes.append(f"Cấu trúc: {n} dòng (chia thành {n // 4} khổ 4 câu).")
 
    words_by_line = [clean_and_tokenize(line) for line in all_lines]
    lengths = [len(w) for w in words_by_line]
 
    # Syllable-count check
    length_errors = []
    for i, length in enumerate(lengths):
        if length != 7:
            length_errors.append(f"Dòng {i + 1} ('{all_lines[i]}'): {length} tiếng (cần 7)")
            
    if length_errors:
        errors.append(f"Sai số tiếng theo dòng [CRITICAL!]: {'; '.join(length_errors)}")
    else:
        successes.append("Số tiếng: Tất cả các dòng đều đạt chuẩn 7 tiếng.")
 
    # --- 1. Luật Bằng/Trắc & Vần (theo từng khổ 4 câu) ---
    for i in range(0, n, 4):
        chunk = words_by_line[i:i+4]
        chunk_idx = (i // 4) + 1
        
        if len(chunk) < 4:
            break
 
        line1, line2, line3, line4 = chunk
        
        # Check Bằng/Trắc cho các chữ 2, 4, 6 — CHỈ CÂU ĐẦU KHỔ (bản sửa 22/09, xem §1.1)
        # Guard chỉ nhìn câu 1: bản cũ đòi `all(len(line) >= 6 for line in chunk)`, nên một
        # câu 3 thiếu tiếng làm câu 1 thoát kiểm hoàn toàn.
        if len(line1) >= 6:
            t1_2 = get_tone(line1[1])
            is_bang_rule = (t1_2 == "Bằng")
            rule_name = "Luật Bằng" if is_bang_rule else "Luật Trắc"
            successes.append(f"[Khổ {chunk_idx}] Xác định được {rule_name} (do từ 2 câu 1 là thanh {t1_2}).")

            exp_2, exp_4, exp_6 = (
                ("Bằng", "Trắc", "Bằng") if is_bang_rule else ("Trắc", "Bằng", "Trắc")
            )
            t2, t4, t6 = get_tone(line1[1]), get_tone(line1[3]), get_tone(line1[5])

            # `t2` chính là cái xác định luật nên không bao giờ lệch `exp_2`; chỉ tiếng 4 và
            # tiếng 6 mới có thể sai. Không kiểm lại `t2` để khỏi để một nhánh chết trong mã.
            line_errs = []
            if t4 != exp_4: line_errs.append(f"Từ 4 '{line1[3]}' ({t4} -> cần {exp_4})")
            if t6 != exp_6: line_errs.append(f"Từ 6 '{line1[5]}' ({t6} -> cần {exp_6})")

            if line_errs:
                errors.append(
                    f"[Dòng {i + 1}] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(line_errs)}. "
                    f"Câu đầu khổ theo {rule_name} yêu cầu (Từ 2 {exp_2}, Từ 4 {exp_4}, Từ 6 {exp_6})."
                )
            else:
                successes.append(
                    f"[Dòng {i + 1}] Luật Bằng/Trắc chuẩn xác (2 {t2} - 4 {t4} - 6 {t6})."
                )
 
        # --- Check Gieo Vần (Dòng 1, 2, 4) ---
        if len(line1) >= 7 and len(line2) >= 7 and len(line4) >= 7:
            w1_7, w2_7, w4_7 = line1[6], line2[6], line4[6]
            
            # Kiểm tra thanh Bằng cho cả 3 dòng
            wrong_tones = []
            if get_tone(w1_7) != "Bằng": wrong_tones.append(f"Dòng {i+1} ('{w1_7}' - {get_tone(w1_7)})")
            if get_tone(w2_7) != "Bằng": wrong_tones.append(f"Dòng {i+2} ('{w2_7}' - {get_tone(w2_7)})")
            if get_tone(w4_7) != "Bằng": wrong_tones.append(f"Dòng {i+4} ('{w4_7}' - {get_tone(w4_7)})")
            
            if wrong_tones:
                errors.append(
                    f"[Lỗi Gieo Vần Khổ {chunk_idx}] {', '.join(wrong_tones)} sai thanh điệu. "
                    f"Từ cuối các câu 1, 2 và 4 bắt buộc phải là vần Bằng."
                )
            
            # Kiểm tra hiệp vần giữa các dòng 1, 2 và 4
            rhyme_errs = []
            if not is_rhyme_match(w1_7, w2_7, poem_type="bay_chu"):
                sugg_1 = get_suggested_endings(w2_7, poem_type="bay_chu")
                rhyme_errs.append(f"Từ cuối Dòng {i+1} ('{w1_7}') chưa vần với Dòng {i+2} ('{w2_7}'). Gợi ý: {sugg_1}")
                
            if not is_rhyme_match(w2_7, w4_7, poem_type="bay_chu"):
                sugg_2 = get_suggested_endings(w2_7, poem_type="bay_chu")
                rhyme_errs.append(f"Từ cuối Dòng {i+4} ('{w4_7}') chưa vần với Dòng {i+2} ('{w2_7}'). Gợi ý: {sugg_2}")
                
            if rhyme_errs:
                errors.append(f"[Sai Vần] [CRITICAL!] Khổ {chunk_idx}: " + " | ".join(rhyme_errs))
            else:
                successes.append(
                    f"[Gieo Vần] Khổ {chunk_idx}: Từ cuối các dòng {i+1}, {i+2}, {i+4} "
                    f"hiệp vần chuẩn xác ('{w1_7}' - '{w2_7}' - '{w4_7}')."
                )
 
    return len(errors) == 0, errors, successes
 
 
def bay_chu_modern_rule_check(
    poem: str, expected_lines: int | None = None
) -> Tuple[bool, List[str], List[str]]:
    """Validate modern seven-syllable verse without imposing Đường-law tones."""
    errors: List[str] = []
    successes: List[str] = []
    lines = [line.strip() for line in poem.splitlines() if line.strip()]
 
    if not lines:
        return False, ["Bài thơ trống."], successes
 
    if expected_lines is not None and len(lines) != expected_lines:
        errors.append(
            f"Sai số dòng [CRITICAL!]: {len(lines)} dòng (cần {expected_lines} dòng theo yêu cầu)."
        )
    else:
        successes.append(f"Cấu trúc: {len(lines)} dòng thơ 7 chữ hiện đại.")
 
    length_errors = []
    for index, line in enumerate(lines, start=1):
        count = len(clean_and_tokenize(line))
        if count != 7:
            length_errors.append(f"Dòng {index} ('{line}'): {count} tiếng (cần 7)")
    if length_errors:
        errors.append(f"Sai số tiếng theo dòng [CRITICAL!]: {'; '.join(length_errors)}")
    else:
        successes.append("Số tiếng: Tất cả các dòng đều đạt chuẩn 7 tiếng.")
 
    return len(errors) == 0, errors, successes
 
 
def bay_chu_bat_cu_rule_check(poem: str) -> Tuple[bool, List[str], List[str]]:
    """Validate the strict eight-line, seven-syllable Đường-law variant."""
    errors: List[str] = []
    successes: List[str] = []
    lines = [line.strip() for line in poem.splitlines() if line.strip()]
 
    if not lines:
        return False, ["Bài thơ trống."], successes
    if len(lines) != 8:
        errors.append(f"Sai số dòng [CRITICAL!]: {len(lines)} dòng (thất ngôn bát cú cần đúng 8 dòng).")
    else:
        successes.append("Cấu trúc: Đúng 8 dòng thất ngôn bát cú.")
 
    words_by_line = [clean_and_tokenize(line) for line in lines]
    length_errors = [
        f"Dòng {index} ('{line}'): {len(words)} tiếng (cần 7)"
        for index, (line, words) in enumerate(zip(lines, words_by_line), start=1)
        if len(words) != 7
    ]
    if length_errors:
        errors.append(f"Sai số tiếng theo dòng [CRITICAL!]: {'; '.join(length_errors)}")
    else:
        successes.append("Số tiếng: Tất cả các dòng đều đạt chuẩn 7 tiếng.")
 
    if len(words_by_line) >= 8 and all(len(words) >= 7 for words in words_by_line[:8]):
        # CHỈ CÂU ĐẦU chịu luật Bằng/Trắc (bản sửa 22/09, xem §1.1). Bảng 8 dòng
        # base/opposite của Đường luật đã bỏ: bảy câu sau không còn bị chấm tiếng 2/4/6.
        is_bang_rule = get_tone(words_by_line[0][1]) == "Bằng"
        base = ("Bằng", "Trắc", "Bằng") if is_bang_rule else ("Trắc", "Bằng", "Trắc")
        cau_dau = words_by_line[0]
        actual = (get_tone(cau_dau[1]), get_tone(cau_dau[3]), get_tone(cau_dau[5]))
        mismatches = [
            f"từ {position} '{cau_dau[position - 1]}' ({got} -> cần {want})"
            for position, got, want in zip((2, 4, 6), actual, base)
            if got != want
        ]
        if mismatches:
            errors.append(
                f"[Dòng 1] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(mismatches)}."
            )
        else:
            successes.append(
                f"[Dòng 1] Luật Bằng/Trắc chuẩn xác "
                f"({'Luật Bằng' if is_bang_rule else 'Luật Trắc'}: 2-4-6 = {' - '.join(base)})."
            )
 
        rhyme_lines = (1, 2, 4, 6, 8)
        rhyme_words = [words_by_line[index - 1][6] for index in rhyme_lines]
        anchor = rhyme_words[1]
        rhyme_errors = []
        for line_number, word in zip(rhyme_lines, rhyme_words):
            if get_tone(word) != "Bằng":
                rhyme_errors.append(f"Dòng {line_number} kết bằng '{word}' không mang thanh Bằng")
            if not is_rhyme_match(anchor, word, poem_type="bay_chu"):
                rhyme_errors.append(f"Dòng {line_number} ('{word}') không hiệp vần với '{anchor}'")
        if rhyme_errors:
            errors.append(f"[Sai Vần] [CRITICAL!] {'; '.join(rhyme_errors)}")
        else:
            successes.append("Gieo vần: Các dòng 1, 2, 4, 6, 8 hiệp vần Bằng.")
 
    return len(errors) == 0, errors, successes
 
def tam_chu_rule_check(poem: str) -> Tuple[bool, List[str], List[str]]:
    """
    Checks prosody for 8-word poetry (Thơ tám chữ).
    - Ensures exactly 8 words per line.
    - Evaluates rhyming schemes (AABB, ABAB, ABBA) for 4-line stanzas.
    - Provides soft warnings for Tone (Bằng/Trắc) musicality rules.
    
    Returns: (is_ok, list_of_errors, list_of_successes)
    """
    errors: List[str] = []
    successes: List[str] = []
 
    # --- Parse lines ---
    raw_stanzas = re.split(r"\n{2,}", poem)
    all_lines: List[str] = []
    for raw in raw_stanzas:
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        all_lines.extend(lines)
 
    if not all_lines:
        errors.append("Bài thơ trống.")
        return False, errors, successes
 
    n = len(all_lines)
    successes.append(f"Cấu trúc: {n} dòng.")
 
    words_by_line = [clean_and_tokenize(line) for line in all_lines]
    
    # --- 1. Kiểm tra số tiếng (Bắt buộc) ---
    length_errors = []
    for i, words in enumerate(words_by_line):
        if len(words) != 8:
            length_errors.append(f"Dòng {i + 1} ('{all_lines[i]}'): {len(words)} tiếng (cần 8)")
            
    if length_errors:
        errors.append(f"Sai số tiếng [CRITICAL!]: {'; '.join(length_errors)}")
    else:
        successes.append("Số tiếng: Tất cả các dòng đều đạt chuẩn 8 tiếng.")
 
    # --- 2. Kiểm tra Bằng/Trắc (Khuyến nghị, không bắt lỗi Critical) ---
    for i, words in enumerate(words_by_line):
        if len(words) == 8:
            t3 = get_tone(words[2])
            t5 = get_tone(words[4])
            t6 = get_tone(words[5])
            t8 = get_tone(words[7])
            
            line_name = f"Dòng {i+1}"
            
            if t8 == "Trắc":
                if t3 != "Trắc":
                    errors.append(f"[Nhạc điệu {line_name}] [CRITICAL!] Sai luật Bằng/Trắc: Từ cuối là Trắc ('{words[7]}'), bắt buộc từ thứ 3 phải là thanh Trắc (hiện tại '{words[2]}' là {t3}).")
                if t5 != "Bằng" and t6 != "Bằng":
                    errors.append(f"[Nhạc điệu {line_name}] [CRITICAL!] Sai luật Bằng/Trắc: Từ cuối là Trắc, bắt buộc từ thứ 5 hoặc 6 phải có ít nhất một từ thanh Bằng (hiện tại cả hai đều Trắc).")
            elif t8 == "Bằng":
                if t3 != "Bằng":
                    errors.append(f"[Nhạc điệu {line_name}] [CRITICAL!] Sai luật Bằng/Trắc: Từ cuối là Bằng ('{words[7]}'), bắt buộc từ thứ 3 phải là thanh Bằng (hiện tại '{words[2]}' là {t3}).")
                if t5 != "Trắc" and t6 != "Trắc":
                    errors.append(f"[Nhạc điệu {line_name}] [CRITICAL!] Sai luật Bằng/Trắc: Từ cuối là Bằng, bắt buộc từ thứ 5 hoặc 6 phải có ít nhất một từ thanh Trắc (hiện tại cả hai đều Bằng).")
 
    # --- 3. Kiểm tra Gieo vần (Duyệt theo từng khổ 4 câu) ---
    for i in range(0, n, 4):
        chunk = words_by_line[i:i+4]
        chunk_idx = (i // 4) + 1
        
        if len(chunk) == 4 and all(len(line) == 8 for line in chunk):
            w1, w2, w3, w4 = chunk[0][7], chunk[1][7], chunk[2][7], chunk[3][7]
            
            # Check rhyming patterns
            is_aabb = is_rhyme_match(w1, w2) and is_rhyme_match(w3, w4)
            is_abab = is_rhyme_match(w1, w3) and is_rhyme_match(w2, w4)
            is_abba = is_rhyme_match(w1, w4) and is_rhyme_match(w2, w3)
            
            if is_aabb:
                successes.append(f"[Gieo vần Khổ {chunk_idx}] Đạt chuẩn vần liên tiếp (AABB).")
            elif is_abab:
                successes.append(f"[Gieo vần Khổ {chunk_idx}] Đạt chuẩn vần chéo (ABAB).")
            elif is_abba:
                successes.append(f"[Gieo vần Khổ {chunk_idx}] Đạt chuẩn vần ôm (ABBA).")
            else:
                errors.append(
                    f"[Sai Vần] [CRITICAL!] Khổ {chunk_idx} không tạo được cấu trúc vần cơ bản "
                    f"(AABB, ABAB, hoặc ABBA). Các từ cuối hiện tại: {w1}, {w2}, {w3}, {w4}."
                )
        elif len(chunk) > 1 and all(len(line) == 8 for line in chunk):
            # Nếu mẩu cuối không đủ 4 câu (VD: bài thơ 6 câu) - check liên tiếp 2 câu
            w1, w2 = chunk[0][7], chunk[1][7]
            if is_rhyme_match(w1, w2):
                successes.append(f"[Gieo vần Khổ {chunk_idx}] Đạt vần cặp (câu {i+1} và {i+2}).")
            else:
                sugg = get_suggested_endings(w1)
                errors.append(f"[Sai Vần] Cụm câu cuối không hiệp vần với nhau. Gợi ý cho '{w1}': {sugg}")
 
    # Đánh giá chung: pass nếu không có lỗi CRITICAL (bỏ qua các lỗi nhạc điệu thông thường)
    critical_errors = [e for e in errors if "[CRITICAL!]" in e]
    return len(critical_errors) == 0, errors, successes
 
if __name__ == "__main__":
    test_poem = """Giời sinh ra bác Tản Đà
Quê hương thời có, cửa nhà thời không
Nửa đời Nam, Bắc, Tây, Đông
Bạn bè sum họp, vợ chồng biệt ly
Túi thơ đeo khắp ba kỳ
Lạ chi rừng biển, thiếu gì gió giăng
Thú ăn chơi cũng gọi rằng
Mà xem chửa dễ ai bằng thế gian
Hà tươi cửa biển Tuần Ranh
Long Xuyên chén mắm, Nghệ An chén cà
Sài Gòn nhớ vị cá tra
Cái xe song mã, chén trà Nhất Thiên
Đa tình con mắt Phú Yên
Hữu tình rau bí ông Quyền Thuận An
Cơn ngâm Chợ Lớn chưa tàn
Tiệc xòe lại có văn bàn, vũ lao
Chấn phòng đất khách cơm tàu
Con ca xứ Huế, cô đầu tỉnh Thanh
Mán sừng cái bánh chưng xanh
Hòa Kỳ tiệc bánh Tin Lành nhớ ai
Sơn Dương, sò huyết Hòn Gai
Đồng Sành cá đối, Giáp Lai lợn rừng
Vân Quan, Hoành Lĩnh xe tăng
Con tàu ca nốt trông chừng Mê Kông
Tuồng Bình Định, rạp Phú Phong
Ổ Nam nước mắm, tỉnh Đông chè tàu
Phong lưu chẳng thiếu đâu đâu
Nước non đưa đón khắp hầu gần xa
Nay về bất tất quê nhà
Sông to cá lớn lại là thứ ngon
Vắng bè bạn, có vợ con
Xa xôi xã hội, vuông tròn thất gia
Trăm năm hai chữ Tản Đà
Còn sông, còn núi, còn là ăn chơi
Dở hay muôn sự ở đời
Mây bay nước chảy mặc người thế gian
"""
    is_ok, errors, successes = luc_bat_rule_check(test_poem)
    print("Is OK:", is_ok)
    print("Errors:", errors)
    print("Successes:", successes)