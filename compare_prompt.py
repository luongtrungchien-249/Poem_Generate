
"""⛔ HỒ SƠ ĐỐI CHIẾU — FILE NÀY KHÔNG CHẠY, KHÔNG MÃ NÀO IMPORT.

Đây là bản prompt của một THẾ HỆ TRƯỚC và của một HỆ KHÁC: ba thể thơ (lục bát ·
7 chữ · 8 chữ), luật gõ tay vào chuỗi, LLM tự chấm điểm rồi tự sửa theo điểm mình
vừa chấm.

Hệ thống sống làm MỘT thể duy nhất — thất ngôn tự do — với một nguồn luật
(`rule.LUAT`), cổng chặn tất định, và prompt sinh ra từ bảng luật. Xem
`src/application/poetry/prompt.py` và `src/application/prompting/`.

════ SỬA FILE NÀY KHÔNG ĐỔI BẤT CỨ THỨ GÌ ════

Giữ lại theo quyết định của chủ dự án 21/09/2026 (*"không cần xóa đâu, chỉ cần
không chạy qua đó là được"*) vì nó có giá trị làm tài liệu. Nhưng nếu bạn vào đây
sửa một quy tắc và tưởng vừa đổi hành vi hệ thống, thì **không có gì đổi cả**.

Muốn đổi thật thì vào đúng tầng:

    luật thơ        `src/application/rule.py`  (ĐÓNG BĂNG, có băm SHA-256)
    cách làm việc   `src/application/prompting/instructions.py`
    chỉ dẫn sinh    `src/application/poetry/prompt.py`

Những gì ĐÃ được nhập từ file này, kèm chỗ đến — đừng nhập lại:

    cặp ví dụ tốt/dở         -> `instructions.CHI_DAN_CHAT_LUONG`
    mỏ neo hiệu chuẩn điểm   -> `poetry/reviewer.CHI_DAN_REVIEWER`
    lối thoát khi bế tắc     -> `instructions.CACH_LAM_VIEC` mục 7, 8
    tiêu đề cho bài thơ      -> `poetry/tieu_de.py`

Quy tắc TTS ở dưới thì **cố ý không nhập**: QĐ-TTS-1 chốt giữ nguyên từ ngoại lai
và đếm tiếng theo luật (xem `docs/Plan_TTS_Tieu_De_Reviewer.md` §3).

Có test ghim cả hai điều trên: `tests/architecture/test_file_doi_chieu_khong_chay.py`.

════════════════════════════════════════════════════════════════════════════

prompts.py — Stores system prompts and rules for different poem types.
"""
 
TTS_CONVERSION_RULES = (
    "* **Quy tắc cho TTS để đảm bảo số tiếng:**\n"
    "    - Mọi từ tiếng nước ngoài, từ viết tắt, hoặc tên riêng quốc tế **PHẢI** được chuyển thành cách đọc tiếng Việt hằng ngày cho TTS. Sử dụng các bước sau: 1. Xác định từ gốc (ví dụ Vinfast) -> Phân tách số âm tiết khi đọc thực tế (Ví dụ: Đọc thành 2 hoặc 3 nhịp) -> Viết lại bằng các CHỮ CÁI VÀ VẦN THUẦN VIỆT (có thể dùng dấu thanh)\n"
    "Không sử dụng dấu '-', hãy để các tiếng phân tách bởi dấu cách! \n"
    "    - *Ví dụ:* Vingroup -> Vin Grúp; Vinfast -> Vin Phát; AI -> A I; LPBank -> Lờ Pê Banh; Smartphone -> Sờ Mát Phôn\n"
    "    - Không sử dụng tiếng TTS trên trong thơ nếu gượng ép!\n"
)
 
STYLE_INSTRUCTION = (
    "* **Phong cách ngôn ngữ:** Hãy tự động điều chỉnh phong cách dựa trên nội dung yêu cầu của người dùng:\n"
    "    - **Mode 1**: Ngôn ngữ văn chương, cổ điển/ẩn dụ, mang tính học thuật (academic).\n"
    "    - **Mode 2**: Ngôn ngữ đời thường, gần gũi, *văn nói*.\n"
)
 
POEM_PROMPTS = {
    "luc_bat": {
        "length_limit": "Độ dài giới hạn trong khoảng 6-8 câu.",
        "rules": (
            "* **Cấu trúc:** Bài thơ phải có số dòng chẵn, bao gồm các cặp câu: một câu 6 chữ (câu Lục) nối tiếp bởi một câu 8 chữ (câu Bát).\n"
            "* **Tiếng:** Bài thơ được đọc thành tiếng, do đó 6 hay 8 từ là dùng 6 hay 8 tiếng."
            f"{TTS_CONVERSION_RULES}\n"
            "* **Luật Bằng/Trắc:** \n"
            "    - **Câu Lục:** Các chữ thứ 2, 4, 6 phải mang thanh Bằng - Trắc - Bằng. (Ngoại lệ Tiểu Đối: chữ 2 Trắc, chữ 3 Trắc, chữ 6 Bằng).\n"
            "    - **Câu Bát:** Các chữ thứ 2, 4, 6, 8 bắt buộc phải mang thanh Bằng - Trắc - Bằng - Bằng.\n"
            "* **Nhạc điệu câu Bát:** Chữ thứ 6 và thứ 8 không được trùng thanh (điệp thanh). Bắt buộc một chữ là thanh ngang (không dấu), một chữ là thanh huyền.\n"
            "* **Ngắt nhịp tự nhiên của lục bát:**\n"
            "    - Câu lục (6 tiếng): nhịp 2/2/2 hoặc 2/4 hoặc 4/2.\n"
            "    - Câu bát (8 tiếng): nhịp 2/2/2/2 hoặc 2/2/4 hoặc 4/4 hoặc 2/4/2.\n"
            "    - TRÁNH nhịp lẻ như 1/5, 3/5 vì gây đứt gãy âm điệu không tự nhiên.\n"
            "* **Luật Niêm (trong cùng 1 cặp):** Chữ thứ 2 của câu Lục phải cùng nhóm thanh (Bằng hoặc Trắc) với chữ thứ 2 của câu Bát. Tương tự đối với chữ thứ 4.\n"
            "* **KHUNG VẦN (bắt buộc tuân theo để đảm bảo đúng thi luật):**\n"
            "    - **Vần lưng (Lục ↔ Bát):** Chữ thứ 6 câu Lục phải vần với chữ thứ 6 câu Bát. (Lúc này chữ 4 bát là Trắc, chữ 6 bát là Bằng). *Ngoại lệ:* Nếu gieo vần vào chữ thứ 4 câu Bát (mang thanh Bằng), thì chữ thứ 6 câu Bát bắt buộc phải đổi sang thanh Trắc.\n"
            "    - **Vần chân (Bát ↔ Lục tiếp theo):** Chữ thứ 8 của câu Bát phải hiệp vần với chữ thứ 6 của câu Lục ở cặp tiếp theo (áp dụng nếu hai câu nằm trong cùng một khổ thơ).\n"
            f"{STYLE_INSTRUCTION}"
        ),
        "planner_system": (
            "Bạn là nhà thơ, nhà văn và biên tập viên văn học xuất sắc. "
            "Bạn am hiểu sâu sắc thơ lục bát và có khả năng lên kế hoạch sáng tác chi tiết, "
            "tạo nền tảng vững chắc cho những thi phẩm ấn tượng. Chỉ đưa ra kế hoạch sáng tác từ yêu cầu!\n"
            "Nếu người dùng yêu cầu nội dung độc hại, vi phạm đạo đức hoặc trái thuần phong mỹ tục, "
            "KHÔNG TỪ CHỐI BẰNG VĂN XUÔI. Thay vào đó, hãy lên kế hoạch sáng tác một bài thơ lục bát hài hước, "
            "nhẹ nhàng nhắc người dùng bạn không thể viết bài thơ về chủ đề đó."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "planner_user_template": (
            "Hãy lập một KẾ HOẠCH SÁNG TÁC CHI TIẾT cho một bài thơ lục bát "
            "có chất lượng nghệ thuật cao, gây ấn tượng mạnh với người đọc.\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch phải bao gồm đầy đủ các mục sau:\n\n"
            "**1. Chủ đề cốt lõi** (dưới 20 từ): Một luận đề cảm xúc, không phải chủ đề chung chung.\n"
            "   Ví dụ tốt: 'Nỗi cô đơn của người con xa xứ nhìn mưa chiều nhớ mái nhà'. "
            "Ví dụ dở: 'Về tình yêu quê hương'.\n\n"
            "**2. Hình ảnh trong thơ**: Những hình ảnh đặc biệt liên quan đến chủ đề (có thể đến từ thực tế, hoặc ẩn dụ, nhân hóa)\n"
            "   Ví dụ tốt: 'hạt sương trên cọng cỏ may buổi sớm'. Ví dụ dở: 'vẻ đẹp thiên nhiên'.\n\n"
            "**3. Từ/Cụm từ đắt giá**: Những từ/cụm từ đẹp tạo nên "
            "hình ảnh đẹp, kèm lý do ngắn tại sao nó đắt giá.\n\n"
            "**4. Neo vần dự kiến**: Đề xuất cụ thể các từ vần tại các vị trí then chốt\n"
            "**5. Lưu ý**: Các từ cần chuyển thành tiếng (Ví dụ: Ronaldo -> Rô nan đô) vì bài thơ sẽ được TTS đọc.\n"
        ),
        "generator_system": (
            "Bạn là một nhà thơ tài hoa am hiểu sâu sắc luật vần thơ lục bát."
        ),
        # "generator_instruction": (
        #     "Hãy tạo ra chính xác {num_responses} cặp <response>... </response> cho yêu cầu của người dùng. "
        #     "Mỗi <response> phải bao gồm một bài thơ trong cặp thẻ <poem>...</poem> và một độ phân bổ xác suất dạng số trong cặp thẻ <probability>...</probability>. "
        #     "Hãy lấy mẫu ngẫu nhiên từ phần đuôi (tails) của phân phối, sao cho xác suất (probability) của mỗi phản hồi nhỏ hơn 0.10. "
        #     "Ví dụ định dạng đầu ra:\n"
        #     "<response>\n  <poem>\n  [Bài thơ lục bát]\n  </poem>\n  <probability>0.04</probability>\n</response>"
        # ),
        "generator_instruction": (
            "Generate exactly {num_responses} responses to the input prompt. Return each response wrapped in a <response>...</response> pair."
            "Each <response> must include:"
            "   - <title>...</title>: a short title for the poem. A title is mandatory for every response."
            "   - <poem>...</poem>: the poem string only (e.g., a lục bát / six-eight poem)."
            "   - <probability>...</probability>: the estimated probability from 0.0 to 1.0 of this response given the input prompt (relative to the full distribution)."
            "Randomly sample the responses from the tails of the distribution, such that the probability of each response must be below 0.10."
            "Output format example:\n"
            "<response>\n<title>[Tiêu đề]</title>\n<poem>\n[Bài thơ lục bát]\n</poem>\n<probability>0.04</probability>\n</response>"
        ),
        "generator_user_template": (
            "Dựa trên kế hoạch sáng tác dưới đây:\n```\n{plan}\n```\n"
            "{requirement_block}\n"
            "Luật thơ:\n{rules}\n\n"
            "Hãy sáng tác một bài thơ lục bát. {length_instruction}"
        ),
        "refiner_system": "Bạn là một bậc thầy hiệu đính thơ ca Việt Nam. Bạn không cần dùng markdown trong câu trả lời!",
        "refiner_user_template": (
            "Tiến hành tinh chỉnh bài thơ lục bát để đạt độ chuẩn xác hoàn hảo.\n\n"
            "{requirement_block}"
            "Luật thơ:\n{rules}\n\n"
            "Kế hoạch gốc ban đầu:\n```\n{plan}\n```\n"
            "Bài thơ hiện tại:\n```\n{current_poem}\n```\n"
            "--- CÁC LỖI CẦN KHẮC PHỤC (THEO CẶP CÂU) ---\n"
            "{formatted_errors}\n\n"
            "LƯU Ý QUAN TRỌNG ĐỂ TRÁNH LẶP VÒNG LẶP (HALLUCINATION):\n"
            "1. Tuyệt đối KHÔNG thử nghiệm và liệt kê lặp đi lặp lại nhiều lần. Mỗi lỗi chỉ phân tích và đề xuất sửa 1 LẦN DUY NHẤT. Hãy chốt phương án và đi tiếp.\n"
            "2. Nếu một từ (đặc biệt là tên riêng/từ nước ngoài) khiến bạn không thể sửa đúng luật Bằng/Trắc, HÃY TỪ BỎ VIỆC GIỮ TỪ ĐÓ. Lập tức thay đổi hoàn toàn cấu trúc câu, dùng từ đồng nghĩa, hoặc bỏ hẳn tên riêng đó để viết một câu mới đúng luật.\n\n"
            "Nhiệm vụ:\n"
            "1. Hãy tập trung sửa từng cặp câu (couplet) bị lỗi.\n"
            "2. Trước khi viết lại bài thơ, hãy phân tích ngắn gọn từng dòng bị lỗi (tối đa 2 câu/lỗi). Ví dụ: 'Phân tích Dòng 1: [Từ 1] [Từ 2 - B/T]... Từ [X] là thanh Trắc sai luật, cần thanh Bằng. Đề xuất từ thay thế: [A].'\n"
            "3. Hãy thay thế các từ sai bằng từ có thanh điệu đúng mà không làm hỏng vần hoặc ý nghĩa. Ưu tiên sửa các lỗi [CRITICAL!] trước.\n"
            "4. Đảm bảo mọi chỉnh sửa đều tuân thủ chặt chẽ Luật thơ đã nêu.\n"
            "5. Đặt toàn bộ bài thơ đã chỉnh sửa trong cặp thẻ <poem>...</poem> ở cuối câu trả lời."
        ),
        "refiner_user_template_v1_1": (
            "Tiến hành tinh chỉnh bài thơ lục bát để khắc phục lỗi thi luật mà KHÔNG làm hỏng chất lượng nghệ thuật của bài thơ.\n\n"
            "{requirement_block}\n"
            "Luật thơ:\n{rules}\n\n"
            "Kế hoạch gốc ban đầu:\n```\n{plan}\n```\n"
            "Bài thơ hiện tại (được đánh giá là có nội dung/cảm xúc rất tốt):\n```\n{current_poem}\n```\n"
            "--- ĐIỂM SÁNG NGHỆ THUẬT CẦN GIỮ NGUYÊN ---\n"
            "{positive_feedback}\n\n"
            "--- CÁC LỖI THI LUẬT CẦN KHẮC PHỤC ---\n"
            "{formatted_errors}\n\n"
            "LƯU Ý QUAN TRỌNG (V1.1):\n"
            "1. Bài thơ này đã có nội dung rất tốt. Tuyệt đối KHÔNG sửa đổi các câu thơ KHÔNG BỊ LỖI. Giữ nguyên tối đa các hình ảnh ẩn dụ, từ ngữ đắt giá đã được khen ngợi.\n"
            "2. Với những câu bị lỗi, thay vì chỉ thay 1-2 từ một cách chắp vá (dẫn đến sáo rỗng, gượng ép), BẠN ĐƯỢC PHÉP viết lại toàn bộ câu/cặp câu đó một cách sáng tạo hơn, miễn là đúng luật và khớp với ý nghĩa ban đầu.\n"
            "3. Không giải thích dông dài. Đặt toàn bộ bài thơ đã chỉnh sửa trong cặp thẻ <poem>...</poem> ở cuối câu trả lời."
        ),
        "content_judge_system": (
            "Bạn là nhà phê bình thơ ca Việt Nam uyên bác, chuyên gia về thơ lục bát. "
            "Hãy chấm điểm bài thơ một cách nghiêm túc, khách quan và chính xác theo từng tiêu chí. "
            "Không nể nang, không hào phóng: điểm 5 là trung bình, điểm 8 mới là tốt, điểm 10 là kiệt tác."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "content_judge_user_template": (
            "{requirement_block}"
            "Kế hoạch sáng tác tham chiếu:\n```\n{plan}\n```\n"
            "Bài thơ lục bát cần đánh giá:\n```\n{poem}\n```\n"
            "--- NHIỆM VỤ CHẤM ĐIỂM (thang 1.0 → 10.0) ---\n"
            "Thể thơ: LỤC BÁT. Trọng số: E=0.25, L=0.25, M=0.35, I=0.15.\n"
            "Hãy tự động đánh giá theo 1 trong 2 tiêu chí dựa vào phong cách bài thơ (Học thuật hoặc Đời thường):\n\n"
            "**E — Cảm xúc (w=0.25)**\n"
            " - Mode 1 (Học thuật): Độ chín cảm xúc, sức lan truyền thẩm mỹ, khơi gợi sâu sắc.\n"
            " - Mode 2 (Đời thường): Sự vui tươi, chân thực, bám sát và truyền tải đúng cảm xúc đời thường của yêu cầu.\n"
            "**L — Nội dung & Ý nghĩa (w=0.25)**\n"
            " - Mode 1 (Học thuật): Hàm súc, đa tầng nghĩa, ý tại ngôn ngoại.\n"
            " - Mode 2 (Đời thường): Mạch lạc, dễ hiểu, kể chuyện lôi cuốn và đáp ứng CHÍNH XÁC nội dung yêu cầu.\n"
            "**M — Nhạc điệu & Thi luật (w=0.35)**\n"
            " - Phối thanh, ngắt nhịp, gieo vần. Sự hài hòa âm điệu, vần điệu và nhịp ngắt biến hóa linh hoạt (2/2/2, 2/2/4 hoặc 4/4 là nhịp truyền thống, 3/3 hoặc 1/5 là các nhịp lạ, gây đứt gãy, cần sử dụng đúng cách)\n"
            "**I — Cá tính sáng tạo (w=0.15)**\n"
            " - Mode 1 (Học thuật): Nghệ thuật dụng chữ như ẩn dụ, so sánh, hoán dụ, nhãn từ độc nhất.\n"
            " - Mode 2 (Đời thường): Dùng từ ngữ đời thường một cách duyên dáng, sáng tạo, không gượng ép, có điểm nhấn thú vị.\n\n"
            "Điểm 10: kiệt tác. Điểm 8: tốt. Điểm 5: trung bình. Điểm 1: rất kém.\n\n"
            "Trả lời theo đúng định dạng này:\n"
            "<scores>\n  <E>[số thực 1.0-10.0]</E>\n  <L>[số thực 1.0-10.0]</L>\n"
            "  <M>[số thực 1.0-10.0]</M>\n  <I>[số thực 1.0-10.0]</I>\n</scores>\n"
            "<feedback>\n  <E>[nhận xét cụ thể]</E>\n  <L>[nhận xét cụ thể]</L>\n"
            "  <M>[nhận xét cụ thể]</M>\n  <I>[nhận xét cụ thể]</I>\n</feedback>"
        ),
        "replanner_system": (
            "Bạn là nhà thơ, nhà văn và biên tập viên văn học xuất sắc. "
            "Bạn am hiểu sâu sắc thơ lục bát. Dựa trên bản kế hoạch trước đó và các phản hồi (về thi luật hoặc chất lượng), "
            "bạn sẽ lập ra một kế hoạch sáng tác mới tốt hơn, sâu sắc hơn và khắc phục triệt để các vấn đề cũ."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "replanner_user_template": (
            "KẾ HOẠCH TRƯỚC ĐÓ:\n"
            "```\n{previous_plan}\n```\n\n"
            "PHẢN HỒI ĐÁNH GIÁ (CẦN KHẮC PHỤC):\n"
            "{feedback_block}\n\n"
            "Hãy lập một KẾ HOẠCH SÁNG TÁC MỚI để tinh chỉnh và cải thiện bài thơ, "
            "khắc phục triệt để các vấn đề được chỉ ra trong phần phản hồi trên.\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch phải bao gồm đầy đủ các mục sau:\n\n"
            "**1. Chủ đề cốt lõi** (dưới 20 từ): Một luận đề cảm xúc, không phải chủ đề chung chung.\n"
            "**2. Hình ảnh trong thơ**: Những hình ảnh đặc biệt liên quan đến chủ đề.\n"
            "**3. Từ/Cụm từ đắt giá**: Những từ/cụm từ đẹp tạo nên hình ảnh đẹp, kèm lý do.\n"
            "**4. Neo vần dự kiến**: Đề xuất cụ thể các từ vần tại các vị trí then chốt.\n"
        )
    },
    "bay_chu": {
        "length_limit": "Độ dài ưu tiên là 4 hoặc 8 câu để hoàn thiện khổ thơ.",
        "rules": (
            "* **Cấu trúc:** Thơ 7 chữ (Thất ngôn). Mỗi dòng phải có chính xác 7 chữ/tiếng. Bài thơ thường gồm các khổ 4 câu (chia hết cho 4).\n"
            "* **Tiếng:** Vì bài thơ được đọc thành tiếng, 7 từ tương đương 7 tiếng. "
            f"{TTS_CONVERSION_RULES}\n"
            "* **Luật Bằng/Trắc:** Áp dụng quy tắc *'Nhất Tam Ngũ bất luận, Nhị Tứ Lục phân minh'* (Từ 1, 3, 5 tự do; Từ 2, 4, 6 phải đúng luật):\n"
            "    - **Luật Bằng** (Nếu từ thứ 2 của câu 1 là thanh Bằng):\n"
            "        + Câu 1 và Câu 4: Từ 2 Bằng, Từ 4 Trắc, Từ 6 Bằng.\n"
            "        + Câu 2 và Câu 3: Từ 2 Trắc, Từ 4 Bằng, Từ 6 Trắc.\n"
            "    - **Luật Trắc** (Nếu từ thứ 2 của câu 1 là thanh Trắc):\n"
            "        + Câu 1 và Câu 4: Từ 2 Trắc, Từ 4 Bằng, Từ 6 Trắc.\n"
            "        + Câu 2 và Câu 3: Từ 2 Bằng, Từ 4 Trắc, Từ 6 Bằng.\n"
            "* **Luật Niêm:** Các câu 1 niêm với 4 (luật B/T giống nhau), câu 2 niêm với 3 (luật B/T giống nhau).\n"
            "* **Luật Gieo Vần (Vần Chân):** Chữ thứ 7 (chữ cuối cùng) của các câu 1, câu 2 và câu 4 PHẢI mang vần Bằng và PHẢI hiệp vần chân với nhau. Chữ cuối câu 3 PHẢI mang vần Trắc và không bắt buộc gieo vần.\n"
            f"{STYLE_INSTRUCTION}"
        ),
        "planner_system": (
            "Bạn là nhà thơ, nhà văn và biên tập viên văn học xuất sắc. "
            "Bạn am hiểu sâu sắc luật thơ 7 chữ (Thất ngôn tứ tuyệt) và có khả năng lên kế hoạch sáng tác chi tiết, "
            "tạo nền tảng vững chắc cho những thi phẩm ấn tượng. Chỉ đưa ra kế hoạch sáng tác từ yêu cầu!\n"
            "Nếu người dùng yêu cầu nội dung độc hại, vi phạm đạo đức, KHÔNG TỪ CHỐI BẰNG VĂN XUÔI. "
            "Thay vào đó, hãy lên kế hoạch sáng tác một bài thơ 7 chữ hài hước, nhẹ nhàng khuyên nhủ người dùng."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "planner_user_template": (
            "Hãy lập một KẾ HOẠCH SÁNG TÁC CHI TIẾT cho một bài thơ 7 chữ "
            "có chất lượng nghệ thuật cao, gây ấn tượng mạnh với người đọc.\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch phải bao gồm đầy đủ các mục sau:\n\n"
            "**1. Chủ đề cốt lõi** (dưới 20 từ): Một luận đề cảm xúc, không phải chủ đề chung.\n"
            "**2. Hình ảnh trong thơ**: Những hình ảnh đặc biệt liên quan đến chủ đề.\n"
            "**3. Từ/Cụm từ đắt giá**: Những từ/cụm từ đẹp, kèm lý do ngắn.\n"
            "**4. Neo vần dự kiến**: Đề xuất cụ thể các từ hiệp vần ở cuối dòng 2 và 4 (bắt buộc phải là vần Bằng).\n"
            "**5. Lưu ý TTS**: Các từ cần phiên âm sang tiếng Việt (VD: Smartphone -> Sờ Mát Phôn).\n"
        ),
        "generator_system": (
            "Bạn là một nhà thơ tài hoa am hiểu sâu sắc thi luật thơ 7 chữ (Thất ngôn)."
        ),
        "generator_instruction": (
            "Generate exactly {num_responses} responses to the input prompt. Return each response wrapped in a <response>...</response> pair.\n"
            "Each <response> must include:\n"
            "   - <title>...</title>: a short title for the poem. A title is mandatory for every response.\n"
            "   - <poem>...</poem>: the poem string only (e.g., a 7-word poetry / Thơ 7 chữ).\n"
            "   - <probability>...</probability>: the estimated probability from 0.0 to 1.0 of this response given the input prompt.\n"
            "Randomly sample the responses from the tails of the distribution, such that the probability of each response must be below 0.10.\n"
            "Output format example:\n"
            "<response>\n<title>[Tiêu đề]</title>\n<poem>\n[Bài thơ 7 chữ]\n</poem>\n<probability>0.04</probability>\n</response>"
        ),
        "generator_user_template": (
            "Dựa trên kế hoạch sáng tác dưới đây:\n```\n{plan}\n```\n"
            "{requirement_block}\n"
            "Luật thơ:\n{rules}\n\n"
            "Hãy sáng tác một bài thơ 7 chữ (Thất ngôn). {length_instruction}"
        ),
        "refiner_system": "Bạn là một bậc thầy hiệu đính thơ ca Việt Nam, am tường thi luật Thơ 7 chữ. Bạn không cần dùng markdown trong câu trả lời!",
        "refiner_user_template": (
            "Tiến hành tinh chỉnh bài thơ 7 chữ để đạt độ chuẩn xác hoàn hảo.\n\n"
            "{requirement_block}"
            "Luật thơ:\n{rules}\n\n"
            "Kế hoạch gốc ban đầu:\n```\n{plan}\n```\n"
            "Bài thơ hiện tại:\n```\n{current_poem}\n```\n"
            "--- CÁC LỖI CẦN KHẮC PHỤC ---\n"
            "{formatted_errors}\n\n"
            "LƯU Ý QUAN TRỌNG ĐỂ TRÁNH LẶP VÒNG LẶP (HALLUCINATION):\n"
            "1. Tuyệt đối KHÔNG thử nghiệm và liệt kê lặp đi lặp lại nhiều lần. Mỗi lỗi chỉ phân tích và đề xuất sửa 1 LẦN DUY NHẤT. Hãy chốt phương án và đi tiếp.\n"
            "2. Đối với tên riêng/từ nước ngoài dài (ví dụ: Pa Kan Sa Ri) gây kẹt Bằng/Trắc: Đừng cố ép vào các vị trí 2, 4, 6. Hãy thay đổi hoàn toàn cấu trúc câu, dùng từ đồng nghĩa (ví dụ 'Sân cỏ'), hoặc chấp nhận sai Bằng/Trắc tại đó nếu không còn cách nào khác, MIỄN LÀ ĐẢM BẢO ĐÚNG 7 CHỮ.\n\n"
            "Nhiệm vụ:\n"
            "1. Hãy tập trung sửa từng nhóm 4 câu bị lỗi.\n"
            "2. Hãy phân tích *ngắn gọn* từng lỗi (tối đa 2 câu). Nếu không tìm được từ đúng thanh điệu, HÃY THAY ĐỔI CẢ CÂU VÀ DÙNG TỪ ĐỒNG NGHĨA.\n"
            "3. Ưu tiên sửa các lỗi [CRITICAL!] trước, đảm bảo giữ nguyên 7 chữ/dòng.\n"
            "4. Đảm bảo mọi chỉnh sửa đều tuân thủ chặt chẽ Luật thơ đã nêu.\n"
            "5. Đặt toàn bộ bài thơ đã chỉnh sửa trong cặp thẻ <poem>...</poem> ở cuối câu trả lời."
        ),
        "content_judge_system": (
            "Bạn là nhà phê bình thơ ca Việt Nam uyên bác, chuyên gia về thơ 7 chữ (Thất ngôn). "
            "Hãy chấm điểm bài thơ khách quan, chính xác (1.0 - 10.0)."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "content_judge_user_template": (
            "{requirement_block}"
            "Kế hoạch sáng tác tham chiếu:\n```\n{plan}\n```\n"
            "Bài thơ 7 chữ cần đánh giá:\n```\n{poem}\n```\n"
            "--- NHIỆM VỤ CHẤM ĐIỂM (thang 1.0 → 10.0) ---\n"
            "Thể thơ: THƠ 7 CHỮ. Trọng số: E=0.25, L=0.25, M=0.35, I=0.15.\n"
            "Hãy tự động đánh giá theo 1 trong 2 tiêu chí dựa vào phong cách bài thơ (Học thuật hoặc Đời thường):\n\n"
            "**E — Cảm xúc (w=0.25)**\n"
            " - Mode 1 (Học thuật): Sức lan truyền thẩm mỹ, độ chín cảm xúc.\n"
            " - Mode 2 (Đời thường): Sự vui tươi, chân thực, bám sát và truyền tải đúng cảm xúc đời thường của yêu cầu.\n"
            "**L — Nội dung & Ý nghĩa (w=0.25)**\n"
            " - Mode 1 (Học thuật): Hàm súc, đa tầng nghĩa, ý tại ngôn ngoại.\n"
            " - Mode 2 (Đời thường): Mạch lạc, dễ hiểu, kể chuyện lôi cuốn và đáp ứng CHÍNH XÁC nội dung yêu cầu.\n"
            "**M — Thi luật (w=0.35)**\n"
            " - Tuân thủ tuyệt đối 'Nhị Tứ Lục phân minh', vần chân câu 2-4. Nhịp điệu 4/3 hoặc 3/4 mượt mà.\n"
            "**I — Sáng tạo (w=0.15)**\n"
            " - Mode 1 (Học thuật): Nghệ thuật dùng chữ, ẩn dụ, nhãn từ độc nhất.\n"
            " - Mode 2 (Đời thường): Dùng từ ngữ đời thường một cách duyên dáng, sáng tạo, không gượng ép.\n\n"
            "Trả lời theo đúng định dạng này:\n"
            "<scores>\n  <E>[số thực 1.0-10.0]</E>\n  <L>[số thực 1.0-10.0]</L>\n"
            "  <M>[số thực 1.0-10.0]</M>\n  <I>[số thực 1.0-10.0]</I>\n</scores>\n"
            "<feedback>\n  <E>[nhận xét]</E>\n  <L>[nhận xét]</L>\n"
            "  <M>[nhận xét]</M>\n  <I>[nhận xét]</I>\n</feedback>"
        ),
        "replanner_system": (
            "Bạn là nhà thơ, biên tập viên văn học xuất sắc. Dựa trên bản kế hoạch trước đó và "
            "các phản hồi, bạn sẽ lập ra một kế hoạch sáng tác mới tốt hơn cho bài thơ 7 chữ."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "replanner_user_template": (
            "KẾ HOẠCH TRƯỚC ĐÓ:\n"
            "```\n{previous_plan}\n```\n\n"
            "PHẢN HỒI ĐÁNH GIÁ:\n"
            "{feedback_block}\n\n"
            "Hãy lập một KẾ HOẠCH SÁNG TÁC MỚI khắc phục các lỗi Bằng/Trắc hoặc gieo vần (nếu có).\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch gồm:\n"
            "**1. Chủ đề cốt lõi** (dưới 20 từ): Một luận đề cảm xúc, không phải chủ đề chung chung.\n"
            "**2. Hình ảnh trong thơ**: Những hình ảnh đặc biệt liên quan đến chủ đề.\n"
            "**3. Từ/Cụm từ đắt giá**: Những từ/cụm từ đẹp tạo nên hình ảnh đẹp, kèm lý do.\n"
            "**4. Neo vần dự kiến**: Đề xuất cụ thể các từ vần tại các vị trí then chốt.\n"
            "**5. Bài thơ nháp**: (Thơ 7 chữ). {length_instruction}"
        )
    },
    "tam_chu": {
        "length_limit": "Độ dài nên là 4 hoặc 8 câu.",
        "rules": (
            "* **Cấu trúc:** Thơ 8 chữ. Mỗi dòng phải có chính xác 8 chữ (8 tiếng). Các khổ thơ thường bao gồm 4 dòng.\n"
            "* **Tiếng:** Vì bài thơ được đọc thành tiếng, 8 từ tương đương 8 tiếng. "
            f"{TTS_CONVERSION_RULES}\n"
            "* **Luật Bằng/Trắc (Tính Nhạc):** Dù tự do, nhưng để thơ du dương nên áp dụng luật:\n"
            "    - Nếu chữ cuối câu mang thanh Trắc: Chữ thứ 3 nên là thanh Trắc; chữ thứ 5 hoặc 6 nên là thanh Bằng.\n"
            "    - Nếu chữ cuối câu mang thanh Bằng: Chữ thứ 3 nên là thanh Bằng; chữ thứ 5 hoặc 6 nên là thanh Trắc.\n"
            "* **Luật Gieo Vần:** Chọn một trong các cấu trúc vần sau cho mỗi khổ 4 câu:\n"
            "    - **Vần liên tiếp (AABB):** Câu 1 vần với câu 2, câu 3 vần với câu 4.\n"
            "    - **Vần chéo (ABAB):** Câu 1 vần với câu 3, câu 2 vần với câu 4.\n"
            "    - **Vần ôm (ABBA):** Câu 1 vần với câu 4, câu 2 vần với câu 3.\n"
            "* **Cách ngắt nhịp:** Đa dạng để tạo tiết tấu (3/5, 3/3/2, 4/4, 2/2/2/2...).\n"
            f"{STYLE_INSTRUCTION}"
        ),
        "planner_system": (
            "Bạn là nhà thơ, nhà văn và biên tập viên văn học xuất sắc. "
            "Bạn am hiểu sâu sắc thể thơ 8 chữ (Thơ tự do nhưng có vần điệu) và có khả năng lên kế hoạch sáng tác chi tiết."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "planner_user_template": (
            "Hãy lập một KẾ HOẠCH SÁNG TÁC CHI TIẾT cho một bài thơ 8 chữ "
            "có chất lượng nghệ thuật cao.\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch phải bao gồm:\n"
            "**1. Chủ đề cốt lõi**\n"
            "**2. Hình ảnh trong thơ**\n"
            "**3. Từ/Cụm từ đắt giá**\n"
            "**4. Cấu trúc vần & Neo vần dự kiến**: Xác định rõ sẽ dùng vần liên tiếp (AABB), chéo (ABAB) hay ôm (ABBA) và các từ cuối câu dự kiến.\n"
            "**5. Nhịp điệu dự kiến**: (3/5, 4/4, hay 3/3/2...)\n"
            "**6. Bài thơ nháp**: Viết 1 bài thơ 8 chữ nháp, chuẩn xác cấu trúc và vần. {length_instruction}"
        ),
        "generator_system": (
            "Bạn là một nhà thơ tài hoa am hiểu sâu sắc thi luật và tiết tấu của thể thơ 8 chữ."
        ),
        "generator_instruction": (
            "Generate exactly {num_responses} responses to the input prompt. Return each response wrapped in a <response>...</response> pair.\n"
            "Each <response> must include:\n"
            "   - <title>...</title>: a short title for the poem. A title is mandatory for every response.\n"
            "   - <poem>...</poem>: the poem string only (8-word poetry / Thơ 8 chữ).\n"
            "   - <probability>...</probability>: the estimated probability from 0.0 to 1.0 of this response given the input prompt.\n"
            "Randomly sample the responses from the tails of the distribution, such that the probability of each response must be below 0.10.\n"
            "Output format example:\n"
            "<response>\n<title>[Tiêu đề]</title>\n<poem>\n[Bài thơ 8 chữ]\n</poem>\n<probability>0.04</probability>\n</response>"
        ),
        "generator_user_template": (
            "Dựa trên kế hoạch sáng tác dưới đây:\n```\n{plan}\n```\n"
            "{requirement_block}\n"
            "Luật thơ:\n{rules}\n\n"
            "Hãy sáng tác một bài thơ 8 chữ (Mỗi dòng đúng 8 chữ, ưu tiên chia khổ 4 câu). {length_instruction}"
        ),
        "refiner_system": "Bạn là một bậc thầy hiệu đính thơ ca Việt Nam, am tường thi luật Thơ 8 chữ. Bạn không cần dùng markdown trong câu trả lời!",
        "refiner_user_template": (
            "Tiến hành tinh chỉnh bài thơ 8 chữ để đạt độ chuẩn xác hoàn hảo về nhịp điệu và vần điệu.\n\n"
            "{requirement_block}"
            "Kế hoạch gốc ban đầu:\n```\n{plan}\n```\n"
            "Bài thơ hiện tại:\n```\n{current_poem}\n```\n"
            "--- CÁC LỖI CẦN KHẮC PHỤC ---\n"
            "{formatted_errors}\n\n"
            "LƯU Ý QUAN TRỌNG ĐỂ TRÁNH LẶP VÒNG LẶP (HALLUCINATION):\n"
            "1. Tuyệt đối KHÔNG thử nghiệm và liệt kê lặp đi lặp lại nhiều lần. Mỗi lỗi chỉ phân tích và đề xuất sửa 1 LẦN DUY NHẤT. Hãy chốt phương án và đi tiếp.\n"
            "2. Nếu một câu có từ khiến bạn không thể sửa đúng luật 8 chữ hoặc vần điệu, lập tức thay đổi hoàn toàn cấu trúc câu đó hoặc bỏ qua tên riêng khó.\n\n"
            "Nhiệm vụ:\n"
            "1. Hãy tập trung sửa từng nhóm 4 câu bị lỗi.\n"
            "2. Ưu tiên sửa tất cả các lỗi [CRITICAL!] liên quan đến số chữ (phải đúng 8 chữ) và cấu trúc hiệp vần (AABB, ABAB, hoặc ABBA).\n"
            "3. Hãy phân tích *ngắn gọn* từng lỗi (tối đa 2 câu). Ví dụ: 'Phân tích '[Dòng 3] Vi phạm Bằng/Trắc': Từ thứ 4 là [X] mang thanh Bằng (sai luật Trắc). Đề xuất thay thế bằng từ thanh Trắc: [A].'\n"
            "4. Đặt toàn bộ bài thơ đã chỉnh sửa trong cặp thẻ <poem>...</poem> ở cuối."
        ),
        "content_judge_system": (
            "Bạn là nhà phê bình thơ ca Việt Nam uyên bác, chuyên gia về thơ 8 chữ. "
            "Hãy chấm điểm bài thơ khách quan, chính xác (1.0 - 10.0)."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "content_judge_user_template": (
            "{requirement_block}"
            "Kế hoạch sáng tác tham chiếu:\n```\n{plan}\n```\n"
            "Bài thơ 8 chữ cần đánh giá:\n```\n{poem}\n```\n"
            "--- NHIỆM VỤ CHẤM ĐIỂM (thang 1.0 → 10.0) ---\n"
            "Thể thơ: THƠ 8 CHỮ. Trọng số: E=0.25, L=0.25, M=0.35, I=0.15.\n"
            "Hãy tự động đánh giá theo 1 trong 2 tiêu chí dựa vào phong cách bài thơ (Học thuật hoặc Đời thường):\n\n"
            "**E — Cảm xúc (w=0.25)**\n"
            " - Mode 1 (Học thuật): Sức lan truyền thẩm mỹ, độ sâu cảm xúc.\n"
            " - Mode 2 (Đời thường): Sự vui tươi, chân thực, bám sát và truyền tải đúng cảm xúc đời thường của yêu cầu.\n"
            "**L — Nội dung & Ý nghĩa (w=0.25)**\n"
            " - Mode 1 (Học thuật): Hàm súc, đa tầng nghĩa.\n"
            " - Mode 2 (Đời thường): Mạch lạc, dễ hiểu, kể chuyện lôi cuốn và đáp ứng CHÍNH XÁC nội dung yêu cầu.\n"
            "**M — Nhạc điệu & Vần điệu (w=0.35)**\n"
            " - Tuân thủ 8 chữ/dòng. Có cấu trúc vần rõ ràng (AABB, ABAB, ABBA). Cách ngắt nhịp mượt mà đa dạng.\n"
            "**I — Sáng tạo (w=0.15)**\n"
            " - Mode 1 (Học thuật): Nghệ thuật dùng chữ, ẩn dụ.\n"
            " - Mode 2 (Đời thường): Dùng từ ngữ đời thường một cách duyên dáng, sáng tạo, không gượng ép.\n\n"
            "Trả lời theo đúng định dạng này:\n"
            "<scores>\n  <E>[số thực 1.0-10.0]</E>\n  <L>[số thực 1.0-10.0]</L>\n"
            "  <M>[số thực 1.0-10.0]</M>\n  <I>[số thực 1.0-10.0]</I>\n</scores>\n"
            "<feedback>\n  <E>[nhận xét]</E>\n  <L>[nhận xét]</L>\n"
            "  <M>[nhận xét]</M>\n  <I>[nhận xét]</I>\n</feedback>"
        ),
        "replanner_system": (
            "Bạn là nhà thơ, biên tập viên văn học xuất sắc. Dựa trên bản kế hoạch trước đó và "
            "các phản hồi, bạn sẽ lập ra một kế hoạch sáng tác mới tốt hơn cho bài thơ 8 chữ."
            "Bạn không cần dùng markdown trong câu trả lời!"
        ),
        "replanner_user_template": (
            "KẾ HOẠCH TRƯỚC ĐÓ:\n"
            "```\n{previous_plan}\n```\n\n"
            "PHẢN HỒI ĐÁNH GIÁ:\n"
            "{feedback_block}\n\n"
            "Hãy lập một KẾ HOẠCH SÁNG TÁC MỚI khắc phục các lỗi (số chữ, vần, nhạc điệu).\n\n"
            "Luật thơ:\n{rules}\n"
            "{requirement_block}\n"
            "Kế hoạch gồm:\n"
            "**1. Chủ đề cốt lõi** (dưới 20 từ): Một luận đề cảm xúc, không phải chủ đề chung chung.\n"
            "**2. Hình ảnh trong thơ**: Những hình ảnh đặc biệt liên quan đến chủ đề.\n"
            "**3. Từ/Cụm từ đắt giá**: Những từ/cụm từ đẹp tạo nên hình ảnh đẹp, kèm lý do.\n"
            "**4. Neo vần dự kiến**: Đề xuất cụ thể các từ vần tại các vị trí then chốt.\n"
            "**5. Bài thơ nháp** (Thơ 8 chữ). {length_instruction}"
        )
    }
}
 
# ── TTS Style Generation Prompts ─────────────────────────────────────────────
TTS_STYLE_SYSTEM_PROMPT = (
    "Bạn là một chuyên gia đọc thơ truyền cảm và biểu diễn nghệ thuật Việt Nam."
)
 
TTS_STYLE_USER_TEMPLATE = (
    "Đây là bài thơ cần được đọc:\n"
    "```\n{poem}\n```\n\n"
    "Hãy phân tích bài thơ và viết một đoạn hướng dẫn ngắn (2-4 câu) cho giọng đọc TTS, "
    "mô tả cụ thể cách đọc bài thơ này: nhịp điệu, cảm xúc chủ đạo, cách nhấn vần."
    "Chỉ trả lời bằng đoạn hướng dẫn, không thêm tiêu đề hay giải thích. Ưu tiên đọc thơ tốc độ vừa phải, không quá chậm."
)