"""Tầng 2 — CÁCH LÀM VIỆC cho từng loại việc của đường thơ.

════════════════════════════════════════════════════════════════════════════
RANH GIỚI VỚI TẦNG LUẬT — ĐỌC TRƯỚC KHI THÊM BẤT CỨ GÌ VÀO ĐÂY
════════════════════════════════════════════════════════════════════════════

    LUẬT THƠ nói bài thơ phải NHƯ THẾ NÀO.
        Nguồn duy nhất: `rule.LUAT`. `poetry/prompt.py` sinh chỉ dẫn từ bảng đó,
        không gõ tay. File NÀY không chép một chữ luật nào — chép là tạo nguồn
        thứ hai, và đến ngày bảng luật đổi thì mô hình được dạy hai luật khác
        nhau tuỳ đường nó đi qua.

    TẦNG 2 nói mô hình phải LÀM VIỆC RA SAO.
        Chỉ viết lại dòng bị nêu hay viết lại cả khổ? Trả về mỗi bài thơ hay kèm
        giải thích? Được phép tự tuyên bố bài mình đúng luật không?

    Hai thứ đó độc lập: đổi luật thơ không đụng tới file này, và ngược lại.

Có test ghim ranh giới đó (`test_tang_2_khong_chep_luat_tho`).

════════════════════════════════════════════════════════════════════════════
BA LOẠI VIỆC, TRƯỚC ĐÂY NẰM RẢI Ở BA FILE
════════════════════════════════════════════════════════════════════════════

    sinh         viết một bài mới          → `poetry/prompt.py`, lẫn trong khối luật
    trợ giúp     bàn về thơ trong chat     → KHÔNG TỒN TẠI; đường chat chạy mà
                                             không có chỉ dẫn loại việc nào
    sửa          có biên bản kiểm định     → `pipeline/stages/verify_output.py`,
                                             là một dict PRIVATE `_CHI_DAN`
    viết tiếp    đã có khổ trước           → `poetry/sinh_theo_kho.py`, chuỗi rời
                                             nhét thẳng vào lời gọi hàm

Rải ra ba chỗ thì không ai đọc được một lượt câu hỏi "hệ thống đang bảo mô hình
làm gì" — và chỉ dẫn quan trọng nhất trong ba cái lại là biến private, không nằm
trong bất kỳ bản kiểm kê prompt nào.

Gom về đây KHÔNG đổi một chữ nào của các chỉ dẫn đó. Cái đổi là: chúng đọc được,
kiểm được, và sửa một chỗ thì cả hệ thống theo.

════════════════════════════════════════════════════════════════════════════
ĐIỀU KIỆN ĐỂ THÊM HẰNG SỐ MỚI VÀO ĐÂY
════════════════════════════════════════════════════════════════════════════

    1. Là hằng — không nội suy gì theo lượt. Nhét thứ đổi theo lượt vào tầng
       hằng số là phá prefix cache của mọi yêu cầu (xem `system.py`).
    2. Có mã thật sự đọc nó NGAY khi thêm vào.

Thiếu điều 2 thì chưa đến lúc viết. Gói này từng chứa `RAG_INSTRUCTION` và
`REACT_INSTRUCTION` — cả hai không đường nào gọi tới, và `RAG_INSTRUCTION` còn
chép lại đúng những gì mẫu YAML nói. Ai sửa quy tắc ở bản chép sẽ tin mình vừa
đổi hành vi hệ thống, trong khi không có gì đổi.
"""

from __future__ import annotations

from typing import Literal, TypeAlias

# ════════════════════════════════════════════════════════════════════════════
# VIỆC 1 — SINH một bài mới
# ════════════════════════════════════════════════════════════════════════════

CACH_LAM_VIEC: str = """CÁCH LÀM VIỆC:
1. Viết đúng số dòng được yêu cầu.
2. TRƯỚC KHI TRẢ LỜI, tự soát từng dòng hai việc: đếm đủ số tiếng, và tra dấu
   của tiếng 2, 4, 6 xem có khớp khuôn không.
   Soát trong đầu, ĐỪNG viết phần soát ra ngoài.
3. Chỉ trả về bài thơ. Không lời dẫn, không giải thích, không đánh số dòng.
4. TUYỆT ĐỐI KHÔNG tuyên bố bài của bạn "đúng luật". Hệ thống có bộ kiểm riêng;
   khẳng định suông sẽ bị chặn.
5. Khi nhận biên bản kiểm định, chỉ sửa đúng dòng bị nêu. Giữ nguyên từng chữ ở
   các dòng đã đạt.
6. Khi nhận khung suy luận, điền đủ bốn ô rồi mới viết lại bài.
7. Khi một dòng không thể vừa giữ đúng ý vừa khớp khuôn thanh: ĐỔI Ý, đừng phá
   khuôn. Thay hình ảnh, đổi cách nói, bỏ hẳn tên riêng khó đặt. Ràng buộc cứng
   không có ngoại lệ; một ý thì luôn còn cách nói khác.
8. Mỗi dòng hỏng chỉ dò lại MỘT lần. Vẫn chưa khớp thì viết lại dòng đó từ đầu
   theo thứ tự ở trên, đừng vá tiếp trên bản đã hỏng.
"""
# Mục 3 KHÔNG phải yêu cầu về hình thức cho đẹp: bộ đọc ứng viên chỉ lấy bốn dòng
# đầu không rỗng (`sinh_theo_kho._lay_bon_dong`). Một dòng lời dẫn lọt vào đó là
# hỏng cả ứng viên, dù bài thơ bên dưới có thể đúng luật.
#
# Mục 4 nhắc lại điều tầng 1 đã nói, và nhắc lại là cố ý: đây là lúc mô hình bị
# cám dỗ nhất, ngay sau khi vừa viết xong một bài nó thấy hay.
#
# Mục 7 và 8 nói CÁCH XỬ LÝ BẾ TẮC, không nói luật — nên chúng thuộc tầng này.
# Ràng buộc cứng nói được phép làm gì; chúng KHÔNG nói phải hy sinh cái nào khi ý
# và khuôn không cùng đứng được trên một dòng. Không nói ra thì mô hình tự chọn,
# và nó chọn giữ ý: ý là thứ nó vừa nghĩ ra và thấy hay, còn khuôn là thứ trừu
# tượng. Kết quả là một dòng phá khuôn kèm lời biện hộ — thứ bộ kiểm chặn thẳng.
#
# Mục 8 chặn kiểu hỏng thứ hai: dò đi dò lại cùng một dòng, mỗi lượt đổi một tiếng
# rồi lại làm lệch tiếng khác. Vòng đó không hội tụ vì nó sửa trên bản đã hỏng;
# lối ra duy nhất là viết lại dòng từ khuôn đi xuống, theo đúng thứ tự mục 7.


# ════════════════════════════════════════════════════════════════════════════
# VIỆC 1b — CHẤT LƯỢNG: bài đúng luật nhưng nhạt thì vẫn là bài hỏng
# ════════════════════════════════════════════════════════════════════════════
#
# VÌ SAO KHỐI NÀY TỒN TẠI. `quality.py` khai báo công khai hai chiều KHÔNG kiểm
# được bằng thuật toán: `CL6 mach_lac` và `CL7 hinh_anh`. Trước khối này, hai
# chiều ấy vừa không ai đo, vừa không ai hướng dẫn — toàn bộ chỉ dẫn sinh nói về
# hình thức và không một chữ nào về nội dung. Kết quả đoán trước được: bài qua
# được mọi cổng mà không ai muốn đọc.
#
# N3 nói điều không kiểm được thì GHI CÔNG KHAI, không lặng lẽ cho qua. Ghi công
# khai là việc của `quality.py` và đã làm. Phần còn thiếu là việc của tầng này:
# không đo được thì ít nhất phải DẠY CÁCH LÀM.
#
# ⚠️ ĐÂY LÀ CÁCH LÀM, KHÔNG PHẢI TIÊU CHÍ CHẤM. Viết thành thang điểm là dựng một
# thẩm quyền thứ hai bên cạnh `quality.py`, đúng lỗi của bản prompt cũ. Mỗi mục ở
# đây phải trả lời được câu "mô hình phải LÀM GÌ", không phải "bài được mấy điểm".
#
# CÁCH DẠY: cặp đối lập. Một ví dụ tốt chỉ cho biết một điểm; một cặp tốt/dở vẽ ra
# đường phân chia. Đây là phần bản prompt cũ làm đúng và là thứ duy nhất đáng nhập
# từ planner của nó — nhập cách dạy, không nhập tiêu chí, không nhập trọng số.

CHI_DAN_CHAT_LUONG: str = """ĐỂ BÀI KHÔNG NHẠT — đúng luật mới là điều kiện cần:
1. Cả bài chỉ nói MỘT điều. Chọn điều đó trước khi viết, và chọn đủ hẹp để hình
   dung ra được.
     hẹp:  người về nhà cũ, thấy cái ghế vẫn kê đúng chỗ ngày xưa
     rộng: tình cảm gia đình
2. Hình ảnh phải nhìn thấy được: một vật, một cử chỉ, một khoảnh khắc.
     thấy được:  vạt nắng còn sót trên bậu cửa
     không thấy: vẻ đẹp của quê hương
3. Tả cái cụ thể, đừng gọi tên cảm xúc. "Buồn", "nhớ", "cô đơn" là kết luận —
   việc của người đọc, không phải của câu thơ.
4. Mỗi khổ giữ một hình ảnh chính. Bốn hình ảnh rời nhau trong bốn dòng thì bài
   rời rạc, dù từng dòng đều đạt.
5. Tránh chữ mòn: "lung linh", "bâng khuâng", "dạt dào", "chơi vơi", "miên man".
   Chúng lấp chỗ trống chứ không thêm gì. Bí thì đổi hình ảnh, đừng với lấy chữ
   có sẵn.
6. Nói xuôi như người Việt nói. Đảo chữ cho vừa khuôn mà thành câu không ai nói
   là đã đổi sai: bài đạt mà đọc lên thấy gượng thì vẫn hỏng.
"""
# Mục 6 là chỗ khối này gặp khối thanh luật, và cố ý đặt ở ĐÂY chứ không ở bên
# kia: nó không nói khuôn là gì, nó nói phải xử sự ra sao khi bị khuôn ép. Cùng
# họ với mục 7 của `CACH_LAM_VIEC`.
#
# Danh sách chữ mòn ở mục 5 là ví dụ, KHÔNG phải danh sách cấm. Không có mã nào
# chặn những chữ này, và không được viết mã như thế: chặn một chữ vì nó hay bị
# dùng dở là phạt luôn cả lần nó được dùng đúng — cùng loại sai với hai chiều
# `lap_tieng` và `lap_dong` đã bị gỡ khỏi `quality.py`.


# ════════════════════════════════════════════════════════════════════════════
# VIỆC 2 — TRỢ GIÚP VỀ THƠ trong lúc trò chuyện
# ════════════════════════════════════════════════════════════════════════════
#
# Đây là loại việc của đường CHAT, khác hẳn ba loại còn lại — ba cái kia đều nằm
# trong vòng sinh–kiểm–sửa có bộ kiểm đứng cuối, còn ở đây KHÔNG có bộ kiểm nào
# chạy. Mô hình nói gì thì người dùng nhận nấy.
#
# Hai hệ quả, và cả hai đều phải nói thẳng ra trong chỉ dẫn:
#
#   1. Bài thơ viết trong khung trò chuyện CHƯA qua kiểm. Không nói rõ thì người
#      dùng tưởng nó đã được hệ thống duyệt — vì họ đang dùng một sản phẩm mà
#      điểm bán là "thơ đúng luật".
#
#   2. Mô hình phải chỉ được đường sang chế độ làm thơ, chứ không thay thế nó.

CHI_DAN_TRO_GIUP_THO: str = """KHI NGƯỜI DÙNG ĐƯA MỘT BÀI THƠ VÀO
1. Soát từng dòng: đếm số tiếng, rồi tra dấu của tiếng 2, 4, 6.
2. Nói rõ DÒNG NÀO, TIẾNG THỨ MẤY, đang mang thanh gì và cần thanh gì.
   "Bài này sai thanh luật" là một câu vô dụng — người đọc không sửa được gì từ đó.
3. Đề xuất cách sửa cụ thể: đổi tiếng ở đúng vị trí đó sang một từ cùng nghĩa
   nhưng khác thanh, và giữ nguyên các dòng đã ổn.
4. Đừng viết lại cả bài trừ khi người dùng nhờ. Bài đó là của họ.
5. Nhắc rằng nhận xét của bạn chỉ là phỏng đoán; bộ kiểm mới cho phán quyết.

KHI NGƯỜI DÙNG NHỜ LÀM THƠ NGAY TRONG LÚC TRÒ CHUYỆN
1. Thiếu chủ đề hoặc số dòng thì hỏi trước, đừng tự chọn hộ.
2. Viết xong phải nói rõ: bài này CHƯA đi qua bộ kiểm luật, nên chưa có gì bảo
   đảm nó đúng luật.
3. Chỉ cho họ chế độ làm thơ của hệ thống — nơi bài được sinh nhiều bản, chọn
   bản đạt, và chỉ trả ra sau khi đã qua kiểm.
Bỏ mục 2 và 3 là để người dùng tin một bài chưa ai kiểm, trong một sản phẩm mà
điểm bán chính là thơ đúng luật.
"""


# ════════════════════════════════════════════════════════════════════════════
# VIỆC 2b — ĐẶT TIÊU ĐỀ cho bài đã xong
# ════════════════════════════════════════════════════════════════════════════
#
# QĐ-TD-1, chủ dự án chốt 21/09/2026: bài sinh ra có tiêu đề.
#
# ⚠️ VÌ SAO ĐÂY LÀ MỘT LƯỢT GỌI RIÊNG, KHÔNG PHẢI MỘT THẺ TRONG CÂU TRẢ LỜI.
# Plan ban đầu đề xuất thẻ `<tieu_de>` kèm bài thơ. Đọc mã thì thấy giả định đó
# sai: thơ được sinh THEO TỪNG KHỔ bốn dòng (`sinh_theo_kho.py`), mỗi ứng viên là
# một khổ. Một thẻ tiêu đề trong câu trả lời sẽ cho MỘT TIÊU ĐỀ MỖI KHỔ, không
# phải mỗi bài. Tệ hơn: `_lay_bon_dong` lấy bốn dòng không rỗng đầu tiên, nên một
# dòng tiêu đề lọt vào là hỏng cả ứng viên — đúng thứ mục 3 của `CACH_LAM_VIEC`
# tồn tại để chặn.
#
# Nên tiêu đề đặt SAU, trên bài đã hoàn chỉnh và đã qua cổng. Đường sinh không bị
# đụng tới một dòng nào.
#
# TIÊU ĐỀ KHÔNG PHẢI THƠ: nó không chịu luật nào — không đếm tiếng, không khuôn
# thanh, không vần. Vì vậy chỉ dẫn này KHÔNG được nhắc tới các thứ đó.

CHI_DAN_DAT_TIEU_DE: str = """Đặt một tiêu đề cho bài thơ dưới đây.

1. Hai đến năm tiếng. Một dòng duy nhất.
2. Lấy từ hình ảnh cụ thể có thật trong bài, đừng tóm tắt nội dung.
     lấy từ bài: Ghế Cũ Bên Thềm
     tóm tắt   : Nỗi Nhớ Nhà
3. Đừng gọi tên cảm xúc trong tiêu đề. Bài đã nói rồi, tiêu đề nói lại là thừa.
4. Không dấu ngoặc kép, không dấu chấm cuối, không lời dẫn.
5. Chỉ trả về đúng tiêu đề, không gì khác.
"""
# Mục 5 không phải yêu cầu hình thức: bộ đọc lấy dòng không rỗng đầu tiên và cắt
# theo trần độ dài. Trả kèm lời dẫn thì lời dẫn thành tiêu đề.
#
# Mục 2 dùng lại đúng cách dạy của `CHI_DAN_CHAT_LUONG` — cặp đối lập — vì cùng
# một loại phán đoán: cụ thể thắng khái quát.


# ════════════════════════════════════════════════════════════════════════════
# VIỆC 3 — SỬA theo biên bản kiểm định
# ════════════════════════════════════════════════════════════════════════════

ChienLuoc: TypeAlias = Literal["sua_dong", "sinh_lai_kho", "sinh_lai_ca_bai"]

# Thang leo thang: mỗi lượt sửa hỏng thì nới rộng phạm vi được phép viết lại.
#
# Vì sao không cho viết lại cả bài ngay từ lượt đầu: sửa một dòng giữ được những
# dòng đã đạt, còn viết lại cả bài là gieo lại xúc xắc trên TOÀN BỘ các dòng —
# kể cả những dòng vốn đã đúng. Chỉ nới khi hẹp đã không ăn thua.
THANG_LEO_THANG: tuple[ChienLuoc, ...] = ("sua_dong", "sinh_lai_kho", "sinh_lai_ca_bai")

CHI_DAN_SUA: dict[ChienLuoc, str] = {
    "sua_dong": (
        "Chỉ viết lại đúng những dòng bị nêu. Giữ nguyên từng chữ ở các dòng đã đạt."
    ),
    "sinh_lai_kho": (
        "Viết lại cả khổ chứa dòng hỏng, giữ sơ đồ vần của khổ đó. "
        "Các khổ khác giữ nguyên."
    ),
    "sinh_lai_ca_bai": (
        "Viết lại toàn bài từ đầu. Bài ở trên là PHẢN VÍ DỤ — đừng lặp lại cách "
        "triển khai đó, nó dẫn tới lỗi không sửa được bằng cách vá từng dòng."
    ),
}


# ════════════════════════════════════════════════════════════════════════════
# VIỆC 4 — VIẾT TIẾP khi đã có khổ trước
# ════════════════════════════════════════════════════════════════════════════

# "KHÔNG chép lại, KHÔNG sửa các dòng đã có" là phần bắt buộc: các khổ trước đã
# qua kiểm và được chọn từ nhiều ứng viên. Để mô hình sửa chúng là vứt bỏ công
# chọn lọc đó, và bài ghép xong sẽ hỏng ở chỗ vốn đã đúng.
CHI_DAN_VIET_TIEP_KHO: str = (
    "Viết TIẾP khổ kế tiếp, giữ mạch cảm xúc và mạch vần của phần trên. "
    "KHÔNG chép lại, KHÔNG sửa các dòng đã có."
)


__all__ = [
    "CACH_LAM_VIEC",
    "CHI_DAN_CHAT_LUONG",
    "CHI_DAN_TRO_GIUP_THO",
    "CHI_DAN_SUA",
    "CHI_DAN_VIET_TIEP_KHO",
    "THANG_LEO_THANG",
    "ChienLuoc",
]
