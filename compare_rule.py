

"""⛔ HỒ SƠ ĐỐI CHIẾU — FILE NÀY KHÔNG CHẠY, KHÔNG MÃ NÀO IMPORT.

Bộ kiểm luật **LỤC BÁT** của một hệ khác. Hệ thống sống làm thất ngôn tự do, và bộ
kiểm của nó là `src/application/rule.py` — file ĐÓNG BĂNG, có băm SHA-256 ghim
trong `tests/architecture/test_rule_dong_bang.py`.

File này còn không import nổi: nó dùng import tương đối (`.constants`, `.rhyme`)
trỏ tới một gói không tồn tại trong repo. Giữ lại làm tài liệu theo quyết định của
chủ dự án 21/09/2026 (*"không cần xóa đâu, chỉ cần không chạy qua đó là được"*).

⚠️ **Đừng nhập luật từ đây.** Luật lục bát — niêm, vần lưng, câu Lục/câu Bát —
không thuộc thể mà hệ thống này làm. Một điều luật sai thể lọt vào `rule.LUAT` hay
vào prompt sẽ được mô hình đọc như luật thật.

Có test ghim: `tests/architecture/test_file_doi_chieu_khong_chay.py`.

════════════════════════════════════════════════════════════════════════════

checker.py — deterministic lục bát prosody checker.
Depends on rhyme.py and constants.py. No LLM calls.
"""
import __main__
import re
from typing import List, Set, Tuple
 
from .constants import CRITICAL_ERROR_KEYWORDS
from .rhyme import (
    clean_and_tokenize, get_bang_type, get_suggested_endings,
    get_tone, is_rhyme_match,
)
 
 
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
        
        # Check Bằng/Trắc cho các chữ 2, 4, 6
        if all(len(line) >= 6 for line in chunk):
            t1_2 = get_tone(line1[1])
            is_bang_rule = (t1_2 == "Bằng")
            rule_name = "Luật Bằng" if is_bang_rule else "Luật Trắc"
            successes.append(f"[Khổ {chunk_idx}] Xác định được {rule_name} (do từ 2 câu 1 là thanh {t1_2}).")
 
            if is_bang_rule:
                expected_patterns = {
                    0: ("Bằng", "Trắc", "Bằng"),
                    1: ("Trắc", "Bằng", "Trắc"),
                    2: ("Trắc", "Bằng", "Trắc"),
                    3: ("Bằng", "Trắc", "Bằng"),
                }
            else:
                expected_patterns = {
                    0: ("Trắc", "Bằng", "Trắc"),
                    1: ("Bằng", "Trắc", "Bằng"),
                    2: ("Bằng", "Trắc", "Bằng"),
                    3: ("Trắc", "Bằng", "Trắc"),
                }
 
            for j, line_words in enumerate(chunk):
                global_line = i + j + 1
                exp_2, exp_4, exp_6 = expected_patterns[j]
                t2, t4, t6 = get_tone(line_words[1]), get_tone(line_words[3]), get_tone(line_words[5])
 
                line_errs = []
                if t2 != exp_2: line_errs.append(f"Từ 2 '{line_words[1]}' ({t2} -> cần {exp_2})")
                if t4 != exp_4: line_errs.append(f"Từ 4 '{line_words[3]}' ({t4} -> cần {exp_4})")
                if t6 != exp_6: line_errs.append(f"Từ 6 '{line_words[5]}' ({t6} -> cần {exp_6})")
 
                if line_errs:
                    errors.append(
                        f"[Dòng {global_line}] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(line_errs)}. "
                        f"Câu {j+1} của {rule_name} yêu cầu (Từ 2 {exp_2}, Từ 4 {exp_4}, Từ 6 {exp_6})."
                    )
                else:
                    successes.append(f"[Dòng {global_line}] Niêm luật chuẩn xác (2 {t2} - 4 {t4} - 6 {t6}).")
 
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
        is_bang_rule = get_tone(words_by_line[0][1]) == "Bằng"
        base = ("Bằng", "Trắc", "Bằng") if is_bang_rule else ("Trắc", "Bằng", "Trắc")
        opposite = ("Trắc", "Bằng", "Trắc") if is_bang_rule else ("Bằng", "Trắc", "Bằng")
        expected = [base, opposite, opposite, base, base, opposite, opposite, base]
        for index, (words, pattern) in enumerate(zip(words_by_line[:8], expected), start=1):
            actual = (get_tone(words[1]), get_tone(words[3]), get_tone(words[5]))
            mismatches = [
                f"từ {position} '{words[position - 1]}' ({got} -> cần {want})"
                for position, got, want in zip((2, 4, 6), actual, pattern)
                if got != want
            ]
            if mismatches:
                errors.append(
                    f"[Dòng {index}] Vi phạm Bằng/Trắc [CRITICAL!]: {'; '.join(mismatches)}."
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