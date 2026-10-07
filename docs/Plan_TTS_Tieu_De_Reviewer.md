# PLAN — Nhập ba khiếm khuyết từ `compare_prompt.py` vào hệ thống sống

**Ngày lập:** 21/09/2026
**Tệp đối chiếu:** `compare_prompt.py` (bản prompt cũ, KHÔNG mã nào import)
**Tệp mục tiêu:** `src/application/rule.py` · `src/application/poetry/prompt.py` · `src/application/prompting/instructions.py` · `src/application/poetry/quality.py`
**Trạng thái:** 🟡 chờ chủ dự án chốt QĐ-TTS-1, QĐ-TD-1, QĐ-RV-1, QĐ-KH-1. Chưa được thi công T1 trước khi chốt.
**Đã đối chiếu mã nguồn:** 21/09/2026 — mọi khẳng định về code trong plan này đã chạy thử, không suy luận. Một mục đã bị đính chính (§3.4), bốn phát hiện mới được thêm (§3.6, §3.7, §4b, §4c).
**Đã thi công:** §0.1–0.4 (tầng prompt) · QĐ-KH-1 · T5 tiêu đề · T6 Reviewer · T8 lỗi `gìn` — **989 test xanh**. Chỉ còn T7 (xoá `compare_prompt.py`).

> **PHẠM VI — đọc trước tiên.** Hệ thống này làm **một thể duy nhất: thất ngôn tự do**,
> theo `docs/Luat_Tho_That_Ngon_Tu_Do.md`. `compare_prompt.py` là prompt của một hệ
> khác, làm ba thể (lục bát · 7 chữ · 8 chữ). Plan này **chỉ nhập những gì độc lập với
> thể thơ** — cách đếm tiếng khi đọc thành tiếng, tiêu đề, và mỏ neo hiệu chuẩn. Mọi
> câu chữ nói về luật lục bát, luật niêm, vần lưng, khuôn Bằng/Trắc của thể khác đều
> **không được mang sang**, kể cả dưới dạng ví dụ.

---

## 0. ĐÃ THI CÔNG — 21/09/2026, trước khi plan này được chốt

Hai sửa đổi dưới đây **đã áp dụng vào mã**, và cố ý đi trước T0 vì chúng không đụng một
chữ luật nào: cả hai nằm ở tầng *cách làm việc*, nên không cần chờ QĐ-TTS-1. Ghi lại ở
đây để plan phản ánh đúng hiện trạng, không phải để chờ duyệt.

Cả hai là thứ `compare_prompt.py` **làm đúng mà hệ thống sống đã đánh rơi** — không phải
ý mới.

### 0.1. Thang thẩm quyền khi các chỉ dẫn đá nhau — `prompting/system.py`

Hệ thống có **bốn nguồn ra lệnh cùng lúc**: chỉ dẫn hệ thống, `chi_dan_tu_nguoi_dung`
(system message của client đã bị hạ vai), `ke_hoach_bat_buoc`, và `yeu_cau_bai_tho`.
Tầng 1 nói rõ bộ kiểm phán quyết cuối, nhưng **không nói gì về ba nguồn còn lại**. Người
dùng dặn một đằng, kế hoạch bắt buộc ghi một nẻo thì không có quy tắc nào xử lý.

Đã thêm khối `KHI CÁC CHỈ DẪN ĐÁ NHAU`: thang bốn bậc (bộ kiểm → chỉ dẫn hệ thống → yêu
cầu người dùng → mặc định), *cụ thể hơn thắng chung hơn*, và một điều trước đây không có:
**người dùng nhắc lại yêu cầu mà mô hình vừa nêu e ngại thì đó là quyết định của họ** —
ghi nhận rồi làm, không nêu lại lần thứ ba. Giữ đúng một ngoại lệ không nhân nhượng: để
người dùng tin một bài chưa qua kiểm là đã đúng luật.

### 0.2. Lối thoát có thứ tự hy sinh + chặn dò vòng — `prompting/instructions.py`

`CHI_DAN_SINH_THO` nói ràng buộc cứng *"không có ngoại lệ nào"* nhưng **không nói phải hy
sinh gì** khi ý và khuôn không cùng đứng được trên một dòng. Không nói thì mô hình tự
chọn, và nó chọn giữ ý — ý là thứ nó vừa nghĩ ra và thấy hay, khuôn là thứ trừu tượng.
Kết quả: một dòng phá khuôn kèm lời biện hộ, thứ bộ kiểm chặn thẳng và vòng sửa phải trả
tiền lại.

Đã thêm `CACH_LAM_VIEC` mục **7** (không khớp được thì ĐỔI Ý, đừng phá khuôn; bỏ hẳn tên
riêng khó đặt) và mục **8** (mỗi dòng hỏng chỉ dò lại một lần, sau đó viết lại từ đầu —
vá tiếp trên bản đã hỏng thì vòng không hội tụ).

Cả hai kế thừa thẳng từ bản cũ: *"HÃY TỪ BỎ VIỆC GIỮ TỪ ĐÓ"* và *"mỗi lỗi chỉ phân tích
và đề xuất sửa 1 LẦN DUY NHẤT"*.

### 0.3. Khối CHẤT LƯỢNG — `prompting/instructions.py` → `CHI_DAN_CHAT_LUONG`

Khoảng trống lớn nhất của prompt repo, và là **điểm mạnh thật sự** của bản cũ.

`quality.py` khai báo công khai hai chiều không kiểm được — `CL6 mach_lac`, `CL7
hinh_anh`. Trước hôm nay, hai chiều ấy **vừa không ai đo, vừa không ai hướng dẫn**:
toàn bộ `CHI_DAN_SINH_THO` nói về hình thức, không một chữ nào về nội dung. Hệ quả đoán
trước được: bài qua mọi cổng mà không ai muốn đọc.

N3 nói điều không kiểm được thì ghi công khai — `quality.py` đã làm. Phần còn thiếu
thuộc tầng 2: **không đo được thì ít nhất phải dạy cách làm**.

Đã thêm sáu mục, dạy bằng **cặp đối lập** — đó là thứ duy nhất đáng nhập từ planner của
bản cũ, và nhập *cách dạy*, không nhập tiêu chí, không nhập trọng số:

```
hẹp:  người về nhà cũ, thấy cái ghế vẫn kê đúng chỗ ngày xưa
rộng: tình cảm gia đình

thấy được:  vạt nắng còn sót trên bậu cửa
không thấy: vẻ đẹp của quê hương
```

Mục 6 (*"đảo chữ cho vừa khuôn mà thành câu không ai nói là đã đổi sai"*) đặt ở tầng 2
chứ không ở khối thanh luật: nó không nói khuôn là gì, nó nói phải xử sự ra sao khi bị
khuôn ép — cùng họ với mục 7 của `CACH_LAM_VIEC`.

Hai rào chắn đã ghim bằng test: khối này **không được viết thành thang điểm**
(`test_chat_luong_KHONG_phai_thang_diem`), và danh sách chữ mòn **không được biến thành
danh sách cấm trong `quality.py`** (`test_chu_mon_chi_la_VI_DU_khong_co_ma_nao_chan`) —
chặn một chữ vì nó hay bị dùng dở là phạt luôn lần nó được dùng đúng, đúng loại sai với
hai chiều `lap_tieng`/`lap_dong` đã bị gỡ.

### 0.4. 🔴 `KHUON_TRONG_CHI_DAN` từng là lời hứa suông — đã sửa

`poetry/prompt.py` có `KHUON_TRONG_CHI_DAN = KHUON_HOP_LE` kèm chú thích *"để test đối
chiếu prompt với `plan.KHUON_HOP_LE`"*. Hai chuyện sai cùng lúc:

1. **Test đó không tồn tại.** `grep` toàn cây chỉ ra đúng một chỗ nhắc tên hằng số này:
   chính dòng khai báo. Đúng ca `instructions.py:46` đặt luật để cấm.
2. **Kể cả có test cũng vô dụng:** gán bí danh rồi so bí danh với bản gốc là so một giá
   trị với **chính nó** — luôn xanh, không bao giờ bắt được sự lệch giữa bảng khuôn và
   chữ trong prompt.

Nay nó đọc thật chuỗi prompt. Và phép ghim mới **đỏ ngay lần chạy đầu**, vì một lệch có
thật chưa ai thấy: mã khuôn viết **không dấu** (`bang`, `trac`) còn prompt viết **có
dấu** (`khuôn bằng`). Nhịp cầu giữa hai cách viết nay khai báo tường minh ở
`_CHU_CUA_KHUON`, và thiếu một nửa — có mã quên chữ, hoặc có chữ quên prompt — đều đỏ.

### 0.5. Trạng thái kiểm

**826 test unit + architecture · 107 test contract — toàn bộ xanh.**
Riêng tầng prompt: 80/80 (`test_tang_2_chi_dan.py` · `test_system_prompt_duoc_noi.py` ·
`test_tang_prompt_day_du.py`), tăng từ 71 nhờ 6 test mới của §0.3 và §0.4.

Chi phí token: `CHI_DAN_SINH_THO` từ **2.866 → 3.820 ký tự** (~+320 token/lượt sinh).
Đây là hằng số nên vẫn nằm trong prefix cache; không lượt nào trả tiền lại cho nó.

⚠️ **Bẫy bảo trì:** mục 7 và 8 nằm ở tầng 2, nên vẫn chịu `test_tang_2_khong_chep_luat_tho`.
Ai thấy chúng "nói về khuôn" mà thêm số tiếng hay ký hiệu khuôn vào cho rõ hơn sẽ làm test
đỏ — và test đỏ ở đó là **đúng**: hai mục này nói *xử lý bế tắc ra sao*, không nói *bài thơ
phải như thế nào*.

---

## 1. Vì sao có plan này

`compare_prompt.py` là bản prompt của một thế hệ trước: một `dict[thể_thơ][vai_trò]`
cho lục bát / 7 chữ / 8 chữ, tự gõ luật vào chuỗi, tự chấm điểm bằng LLM. Nó **không
được bất kỳ module nào import** — `grep` toàn cây không trả về dòng nào ngoài chính nó.

Hệ thống sống đi xa hơn nó ở sáu trục: một nguồn luật (`rule.LUAT`), cổng chặn tất
định, không còn ngưỡng tuỳ ý, tầng hằng số giữ prefix cache, bọc thẻ phân biệt nguồn,
và thang leo thang khi sửa. Không có gì ở sáu trục đó cần nhập ngược lại.

Nhưng bản cũ **có ba thứ hệ thống sống không có**, và cả ba là khiếm khuyết thật:

| # | Khiếm khuyết | Bằng chứng |
| - | ------------ | ---------- |
| 1 | **TTS** — bài thơ được đọc lên, nên "Vinfast" là mấy tiếng | `grep -ri "tts" src/ docs/` → **không một dòng nào** |
| 2 | **Tiêu đề** — bài sinh ra không có tên | corpus mẫu CÓ `tieu_de` (`poetry/dataset.py:50`), bài sinh ra thì không |
| 3 | **Chấm nội dung** — `mach_lac`, `hinh_anh` bị bỏ ngỏ | `quality.py:280-292` ghi rõ "không kiểm được, thuộc node Reviewer" |
| 4 | **Kế hoạch không có nội dung** — `plan.hinh_anh` luôn rỗng | `sinh_tho.py:142` gọi `lap_ke_hoach_hop_le(yeu_cau)`, không truyền `hinh_anh`/`mach_cam_xuc` → §4b |
| 5 | **Prompt sinh không nói gì về chất lượng** | ✅ **đã sửa 21/09/2026** → §0.3 |

Khiếm khuyết 1 là nghiêm trọng nhất và là phần lớn của plan này: nó không phải thiếu
một đoạn chữ trong prompt, mà là **bộ kiểm và sản phẩm đang đo hai thứ khác nhau**.

---

## 2. Nguyên tắc kế thừa

N1–N4 của `Plan_Rule_Phan_Tang.md` vẫn nguyên hiệu lực. Nhắc lại hai điều sẽ bị đụng
tới nhiều nhất trong plan này:

> **N1** — Tiêu chí phải trích được từ câu chữ tài liệu luật. Chỗ nào tài liệu không
> có tiêu chí đo được thì **không được bịa ra**, phải đưa lên thành quyết định của chủ
> dự án.
>
> **N3** — Điều đòi ngữ nghĩa hoặc ý đồ tác giả thì **ghi công khai là không kiểm
> được**, không lặng lẽ cho qua.

Thêm hai nguyên tắc riêng của plan này, rút ra từ chính chỗ `compare_prompt.py` sai:

| #  | Nguyên tắc |
| -- | ---------- |
| P1 | **Một nguồn luật.** Mọi ràng buộc mới phải vào `rule.LUAT` trước, prompt sinh ra từ đó. Gõ thẳng vào chuỗi prompt là tạo nguồn thứ hai — đúng lỗi khiến `compare_prompt.py` không bảo trì được. |
| P2 | **Không LLM ở cổng chặn.** Thứ gì chặn bài thì phải thuần, đồng bộ, tất định (`ports.OutputVerifier`). LLM chỉ được đứng ở vị trí tư vấn. |

---

## 3. Khiếm khuyết 1 — TTS · ⛔ ĐÃ ĐÓNG, KHÔNG LÀM

> ### ✅ QĐ-TTS-1 — CHỦ DỰ ÁN CHỐT 21/09/2026
>
> > *"Nếu gặp các từ như thế thì nên để nguyên như vậy, chỉ cần đếm đủ tiếng theo
> > luật là được."*
>
> **Không chọn A, không chọn B.** Từ ngoại lai **giữ nguyên mặt chữ** trong bài, và
> phép đếm tiếng **giữ nguyên như `rule.py` đang làm**: `"Vinfast"` là một tiếng.
>
> Hệ quả của quyết định này, ghi ra để sau không ai tưởng là bỏ sót:
>
> - **KHÔNG thêm H5.** Bảng `LUAT` không đổi. `rule.py` giữ nguyên băm đã chốt.
> - **KHÔNG thêm đoạn phiên âm vào tầng 2.** Dạy mô hình viết "Vin Phát" rồi để bộ
>   kiểm đếm thành hai tiếng là tự tạo mâu thuẫn — chính là chiều lệch thứ hai ở
>   §3.1. Giữ nguyên nghĩa là **không dạy phiên âm**.
> - **Văn bản viết là thẩm quyền duy nhất.** Một dòng bảy tiếng viết ra có thể được
>   TTS đọc thành tám tiếng; theo quyết định này, bài đó vẫn **ĐẠT**. Sản phẩm ưu
>   tiên **mặt chữ** hơn **mặt tiếng**.
> - §3.2–3.5 dưới đây giữ lại làm **hồ sơ phân tích**, không phải việc phải làm.
>
> **Đã hoàn nguyên `rule.py`** về đúng băm `9f808d59…` theo chỉ thị *"Rule của tôi
> phải là không được thay đổi"*. Test `test_rule_dong_bang.py` xanh.

### 3.0. 🩸 LỖI `gìn` — T8, CHỦ DỰ ÁN DUYỆT SỬA 21/09/2026

Việc đóng §3 **không đóng** lỗi này. Nó có sẵn từ trước, độc lập với TTS, và đang
ảnh hưởng luật vần chạy hằng ngày:

```
van_cua("gìn")  = "n"     ← sai, phải là "in"
hiep_van("gìn", "nhìn")  ->  False        ❌
```

Bản vá đã viết và đã đo (tập tuyển: sửa xong thì `Gìn`/`gìn` hết bị bắt oan, 300/300
bài vẫn đạt luật), nhưng **đã hoàn nguyên cùng `rule.py`** vì nó nằm trong file đóng
băng. Sửa nó là một quyết định riêng, cần:

1. `python datalake/scripts/kiem_tra_toan_bo.py` — đo lại 67.150 bản ghi
2. `python datalake/scripts/doi_soat_tai_lieu.py` — phải xanh
3. ghi lý do vào `docs/Plan_Rule_Phan_Tang.md`
4. cập nhật `BAM_DA_CHOT` trong `tests/architecture/test_rule_dong_bang.py`

Cách sửa đã biết và nhỏ: khi cắt âm đầu theo khớp dài nhất mà **phần dư không còn
nguyên âm nào**, lùi lại thử âm đầu ngắn hơn. Tiêu chí "có nguyên âm" hẹp hơn "tra
được trong bảng âm chính", nên `gian`, `giết`, `giữ` không bị đụng tới.

#### Phạm vi được phép của T8 — hẹp nhất có thể

**CHỈ** phép lùi âm đầu. **KHÔNG** kèm `_AM_CHINH`, **KHÔNG** kèm `la_am_tiet_hop_le`,
**KHÔNG** kèm H5 — QĐ-TTS-1 đã đóng phần đó. Một lượt sửa file đóng băng phải mang đúng
một lý do; gộp thêm thứ khác vào là làm hỏng chính tác dụng của lớp băm, vì lần sau
không ai tra được thay đổi nào gây ra hệ quả nào.

#### Rủi ro đã lường trước

Phép sửa đụng `van_cua`, mà `van_cua` là đầu vào của `hiep_van` → tầng 5 (sơ đồ vần) →
`bai_dat`. **Số bài đạt có thể đổi.** Nếu đổi, ba báo cáo `.md` đang trích con số
24.366 sẽ lệch, và `doi_soat_tai_lieu.py` sẽ đỏ — đó là cơ chế đúng, không phải sự cố.

Hướng đổi dự đoán được: chỉ **tăng**, không giảm. Phép sửa chỉ khiến những cặp trước
đây *không* nhận ra là hiệp vần nay được nhận ra; không cặp nào đang hiệp bị mất.

#### Quy trình bốn bước, theo đúng `test_rule_dong_bang.py`

| Bước | Việc | Kết quả |
| ---- | ---- | ------- |
| 1 | Viết test ghim ca `gìn` **trước**, xem nó đỏ | ✅ đỏ đúng 2 ca thật (`test_van_gin.py`) |
| 2 | `kiem_tra_toan_bo.py` — đo lại 67.150 bản ghi | ✅ `bai_dat` **24.366 → 24.366**, không đổi |
| 3 | `doi_soat_tai_lieu.py` — phải xanh | ✅ xanh (sau khi cập nhật 3 tài liệu) |
| 4 | Ghi lý do vào `Plan_Rule_Phan_Tang.md` §12, cập nhật `BAM_DA_CHOT` | ✅ băm `9f808d59…` → `0a0b2488…` |

**✅ T8 XONG 21/09/2026 — 989 test xanh.**

Tác động thật, đúng hướng đã lường trước khi chạy — **chỉ tăng nhận diện vần, không bài
nào đổi phán quyết**:

| Thống kê | Trước | Sau |
| -------- | ----- | --- |
| `bai_dat` | 24.366 | **24.366** (0) |
| `cum_co_van_chan` | 189.415 | **189.422** (+7) |
| `bai_dat_co_van_lung` | 13.532 | 13.533 (+1) |

Các sơ đồ vần dịch nhẹ (`xaaa` −2, `axxa` −2, còn lại +1/+2): cụm **chuyển từ sơ đồ ít
vần sang sơ đồ nhiều vần hơn**, không phải mất vần. Bảng đầy đủ ở `Plan_Rule_Phan_Tang`
§12.3.

**Hai việc phát sinh, đã xử lý đúng đường chính thức:**

- `doi_soat_tai_lieu.py` đỏ 20 chỗ ngay sau khi đo — **cơ chế làm đúng việc**, ba tài
  liệu còn trích số cũ. Đã cập nhật số, và `rule.py` 2.200 → 2.238 dòng, 45 → 46 hàm.
- Cột "Trước" của bảng §12.3 lại làm script đỏ tiếp 11 chỗ. Đã đăng ký mười một số đó
  vào `SO_LICH_SU` kèm lý do, thay vì xoá cột đi: **một bảng "trước/sau" mất cột "trước"
  thì không chứng minh được gì**, và lần sau không ai kiểm lại được thay đổi ấy đã làm
  gì với corpus.

---

### 3.1. Phát biểu lỗi cho chính xác *(hồ sơ — không còn là việc phải làm)*

H1 nói *"mỗi dòng phải có đúng 7 tiếng"*. `rule.tach_tieng` đếm **tiếng viết ra**:
tách theo dấu cách, tách tiếp theo gạch nối, quy chữ số về cách đọc (Đ2). Nhưng sản
phẩm đọc bài thơ **thành tiếng**. Hai phép đếm đó lệch nhau ở đúng một chỗ: từ ngoại
lai và viết tắt.

Lệch theo **hai chiều**, và chiều thứ hai mới là chiều tệ:

```
"Vinfast rực sáng giữa trời quê hương"
    bộ kiểm đếm  : 7 tiếng  → H1 ĐẠT
    TTS đọc ra   : 8 tiếng  ("Vin Phát" là 2)  → bài sai khi nghe

"Vin Phát rực sáng giữa trời quê hương"
    bộ kiểm đếm  : 8 tiếng  → H1 TRƯỢT
    TTS đọc ra   : 8 tiếng  → vẫn sai, nhưng mô hình đã làm ĐÚNG việc phiên âm
```

Chiều thứ hai nói rằng hệ thống hiện **phạt mô hình vì làm đúng**: viết sẵn dạng đọc
được là thứ TTS cần, và đó chính là thứ bị H1 đánh trượt. Không prompt nào chữa được
điều này, vì prompt không đổi được cách bộ kiểm đếm.

### 3.2. Vì sao không vá bằng một đoạn chữ trong prompt

Cách của `compare_prompt.py` là nhét `TTS_CONVERSION_RULES` vào chuỗi luật. Nó không
sai về nội dung, nhưng ở hệ thống này sẽ tạo ra tình trạng: prompt dạy mô hình viết
"Vin Phát", còn bộ kiểm đánh trượt đúng câu đó. Hai nguồn sự thật, và mô hình bị kẹt
giữa. Theo P1, ràng buộc phải vào `LUAT` trước.

### 3.3. QĐ-TTS-1 — hai phương án, cần chủ dự án chốt

**Phương án A — văn bản thơ LÀ văn bản đọc.**
Bài thơ chỉ được chứa âm tiết tiếng Việt viết được. Mô hình phải phiên âm ngay lúc
viết ("Vinfast" → "Vin Phát"), và bộ kiểm **không đổi một dòng nào**: viết thế nào thì
đọc đúng thế ấy, hai phép đếm trùng nhau vĩnh viễn.

- ✅ Không cần bảng dữ liệu mới, không có nguồn sự thật thứ hai.
- ✅ Tiêu chí cưỡng chế được và tất định (xem §3.4).
- ⚠️ Bài thơ hiển thị ra màn hình sẽ mang dạng "Vin Phát". Phải chấp nhận rằng sản
  phẩm này ưu tiên **nghe** hơn **nhìn** — nếu không, cần một trường hiển thị riêng,
  và đó là việc của tầng trình bày, không phải của luật.

**Phương án B — bộ kiểm biết đọc.**
Giữ nguyên "Vinfast" trong bài, thêm bảng phiên âm để `tach_tieng` quy từ ngoại lai về
âm tiết trước khi đếm, đúng cách Đ2 đang làm với chữ số.

- ✅ Bài thơ giữ được mặt chữ gốc.
- ❌ **Vấp N1.** Bảng phiên âm không bao giờ đóng: gặp một từ ngoại lai chưa có trong
  bảng thì đếm là mấy tiếng? Mọi câu trả lời đều là một tiêu chí bịa ra. Đ2 làm được
  vì tập chữ số là hữu hạn và cách đọc số có chuẩn; tập từ ngoại lai thì không.

**Khuyến nghị: A.** Không phải vì rẻ hơn, mà vì B đòi một tiêu chí không trích được từ
đâu cả — đúng thứ N1 cấm. A biến một bài toán mở (đọc từ ngoại lai ra sao) thành một
bài toán đóng (văn bản có phải toàn âm tiết tiếng Việt không).

### 3.4. Thiết kế chi tiết nếu chốt A

**Điều luật mới.** Số hiệu tiếp theo trong nhóm H, đặt cạnh H1–H4:

```
H5  "Mọi tiếng trong bài phải là âm tiết tiếng Việt viết được"   loại: đề xuất "cung"
```

Nhưng **không được vào thẳng loại `cung`**. Theo đúng cách plan trước đã làm với ngưỡng
lặp: đo trên ngữ liệu đã, rồi mới quyết định.

**Phép kiểm — tất định, không ngưỡng.** Một tiếng hợp lệ khi tách được thành
`phụ âm đầu + vần + thanh` với phụ âm đầu thuộc bảng đóng các phụ âm đầu tiếng Việt và
vần thuộc bảng vần đã có trong `rule.py` (§5 đã có sẵn bộ tách vần — tái dùng, không
viết lại). Đây không phải ngưỡng dò được mà là cấu trúc âm tiết, tra bảng đóng.

> 🔴 **ĐÍNH CHÍNH 21/09/2026 — bản đầu của mục này SAI.** Nó viết *"cả hai bảng đã có
> sẵn, T1 chỉ hỏi bộ tách vần một câu khác"*. Không đúng. Đã chạy thật:
>
> ```
> phan_tich_am_tiet("Vinfast")    -> am_dau='v'  am_chinh='infas'     am_cuoi='t'
> phan_tich_am_tiet("Smartphone") -> am_dau='s'  am_chinh='martphone' am_cuoi=''
> ```
>
> `phan_tich_am_tiet` là hàm **toàn phần: nó không bao giờ từ chối**. Cắt được bao
> nhiêu thì cắt, phần thừa gán hết cho âm chính. Trong `rule.py` hiện **không có bảng
> âm chính đóng nào** để đối chiếu — chỉ có `_AM_DAU` và `_AM_CUOI`. Vậy phần việc
> thật của T1 nằm ở đây, không phải ở chỗ "hỏi một câu khác".

**Thứ T1 phải dựng: bảng âm chính đóng.** Mười lăm âm chính của tiếng Việt —
`a ă â e ê i o ô ơ u ư y` cộng ba nguyên âm đôi `iê uô ươ` (đã chuẩn hoá qua
`_CHUAN_HOA_AM_CHINH`). Đây là tập đóng của ngữ âm học phổ thông, không phải ngưỡng dò
được, nên không vấp N1. Một tiếng hợp lệ khi **cả ba thành phần đều tra được**: âm đầu ∈
`_AM_DAU` ∪ {rỗng}, âm chính ∈ bảng mới, âm cuối ∈ `_AM_CUOI` ∪ {rỗng}.

**Hai bẫy đã tìm thấy trước khi viết mã** — cả hai sẽ bắt oan nếu làm ẩu:

```
"quà"   -> am_dau = 'q'   ← 'q' KHÔNG có trong _AM_DAU (chỉ có 'qu')
"xoong" -> am_chinh = 'oo' ← không nằm trong 15 âm chính chuẩn
```

Nên phép kiểm phải nhận `q` như một âm đầu hợp lệ, và bảng âm chính phải gồm cả `oo`.

**Bước đo bắt buộc trước khi chặn (N4) — ĐÃ CHẠY.**

Tập đo: `datalake/corpus_tuyen/tho_mau.jsonl` (300 bài, **commit được**). Không dùng
`datalake/analysis/bai_dat.jsonl` (24.366 bài, 266 MB) làm tập ghim vì nó gitignored —
xem §3.6.

```
300 bài · 17 âm chính phân biệt · 5 bài bị bắt
tiếng bị bắt: show(1) · phone(2) · Gìn(1) · gìn(2)
```

Đối chiếu bảng quyết định:

| Kết quả đo | Kết luận |
| ---------- | -------- |
| 0 bài bị bắt | bảng đã đủ → H5 vào loại `cung` |
| Số ít bài bị bắt, **toàn là từ ngoại lai thật** | H5 vào loại `cung`, ghi kèm danh sách ca đã xét |
| ✅ **RƠI VÀO HÀNG NÀY** — có bài bị bắt **oan** | bảng/phép tách còn sai → **sửa trước, đo lại**. Tuyệt đối không hạ H5 xuống `mem` để lách |

`show`, `phone` là bắt **đúng** — đó chính là thứ H5 sinh ra để bắt. `Gìn`, `gìn` là bắt
**oan**, và nguyên nhân không nằm ở H5 mà ở một lỗi có sẵn — §3.6.

### 3.6. 🩸 Lỗi có sẵn trong `rule.py`, lộ ra nhờ bước đo

Phép đo của T1 làm lộ một lỗi **đang sống, độc lập với plan này**:

```
van_cua("gìn")  = "n"     ← sai, phải là "in"
van_cua("nhìn") = "in"
hiep_van("gìn", "nhìn")  ->  False        ❌
hiep_van("gìn", "tin")   ->  False        ❌
```

Nguyên nhân: cắt âm đầu theo khớp **dài nhất** nên `gìn` bị đọc thành `gi` + `n`, trong
khi đúng phải là `g` + `ìn`. Chính chú thích ở `rule.py:592` đã lường trước ca này —
*"'gì' không phải là 'gi' + rỗng, mà là 'g' + 'ì'"* — nhưng phép lùi chỉ chạy khi phần
còn lại **rỗng**, không chạy khi phần còn lại **không hợp lệ**. `gian`, `giết`, `giữ` may
mắn đúng vì phần dư (`an`, `êt`, `ư`) tình cờ hợp lệ.

**Đây không phải việc của H5.** Nó ảnh hưởng luật vần đang chạy hằng ngày: một bài gieo
`gìn` với `nhìn` hiện bị chấm là không hiệp vần. Sửa nó là điều kiện tiên quyết của T2,
và phải có test riêng cho ca vần, không gộp vào test của H5.

**Cách sửa** (đúng một dòng logic, không đổi bảng): sau khi cắt âm đầu, nếu phần còn lại
không có âm chính tra được thì **lùi lại một ký tự** và thử âm đầu ngắn hơn. Bảng âm
chính đóng của T1 chính là thứ cho phép hỏi câu "có tra được không" — nên T1 phải làm
trước, rồi §3.6 mới sửa được.

### 3.7. Hệ quả chưa lường: mẫu few-shot đang chứa từ ngoại lai

`datalake/corpus_tuyen/tho_mau.jsonl` không chỉ là tập đo — nó là **kho mẫu few-shot**
(`tests/unit/application/test_fewshot.py:33` đọc đúng file này, `corpus/jsonl.py:30` nạp
nó). Hai bài trong đó chứa `show`, `phone`.

Nếu H5 vào loại `cung` mà kho mẫu không lọc, hệ thống sẽ **đưa cho mô hình những bài vi
phạm chính điều luật vừa đặt ra**, ngay trong khối `<vi_du_dung_luat>`. Mô hình học khuôn
từ ví dụ; ví dụ sai luật là dạy sai.

Nên T3 phải kèm: lọc kho mẫu theo H5, hoặc sửa hai bài đó. Quyết định thuộc chủ dự án —
sửa văn bản của người khác trong kho mẫu là việc cần cho phép, không tự làm.

**Prompt.** Sau khi H5 vào bảng, `_bang_luat_cung()` tự đưa nó vào `CHI_DAN_SINH_THO` —
không phải gõ thêm. Phần *cách* phiên âm thì thuộc tầng 2 (`instructions.py`), vì nó nói
mô hình làm việc ra sao chứ không nói bài thơ phải như thế nào:

```
Từ nước ngoài, tên riêng quốc tế, chữ viết tắt: viết thẳng bằng cách đọc
tiếng Việt, mỗi tiếng cách nhau bởi dấu cách, không dùng gạch nối.
    Vingroup -> Vin Grúp      AI -> A I      LPBank -> Lờ Pê Banh
Phiên âm xong mới đếm tiếng — dạng đã phiên âm mới là dạng tính.
Nếu phiên âm làm câu thơ gượng, đổi hẳn sang từ thuần Việt. Không có
quy định nào bắt phải giữ tên gốc.
```

Ba ví dụ lấy nguyên từ `compare_prompt.py` — đó là phần bản cũ làm đúng và nên giữ.
Câu cuối là lối thoát có thứ tự ưu tiên, cùng kiểu với mục 7 vừa thêm vào `CACH_LAM_VIEC`.

### 3.5. Test ghim

| Test | Ghim điều gì |
| ---- | ------------ |
| ~~`test_H5_co_ham_kiem`~~ | **Không cần viết.** Cơ chế đã có: `test_rule.py:289` ghim `set(HAM_KIEM_CUNG.keys()) == MA_CUNG`. Thêm H5 vào `LUAT` loại `cung` sẽ tự làm test đó đỏ cho tới khi thêm mục mô tả. Đừng viết test trùng. |
| `test_am_tiet_hop_le` | "Vinfast", "Smartphone", "show", "phone" trượt; "Vin", "Phát", "quà", "xoong", "nghiêng" đạt |
| `test_gin_hiep_van_voi_nhin` | 🩸 §3.6 — ghim lỗi có sẵn: `hiep_van("gìn","nhìn")` phải True. **Viết test này TRƯỚC khi sửa**, để thấy nó đỏ |
| `test_H5_tren_tap_tuyen` | chạy trên `tho_mau.jsonl` (300 bài, commit được): sau khi sửa §3.6, số tiếng bị bắt phải đúng bằng tập `{show, phone}` — không thêm, không bớt |
| `test_kho_mau_fewshot_khong_vi_pham_H5` | §3.7 — ví dụ đưa cho mô hình không được vi phạm luật mình vừa dạy |
| `test_chi_dan_TTS_nam_o_tang_2` | đoạn phiên âm không được chứa số tiếng hay khuôn thanh (`test_tang_2_khong_chep_luat_tho` đã có sẵn cơ chế) |

---

## 4. Khiếm khuyết 2 — Tiêu đề

### QĐ-TD-1 — cần chốt: bài thơ có tiêu đề không?

Corpus mẫu có `tieu_de`; bài sinh ra thì không. Lệch này chưa gây hỏng gì, nhưng nó có
nghĩa là mẫu few-shot và sản phẩm không cùng hình dạng.

Nếu chốt **có**:

- Tiêu đề **KHÔNG** đi qua luật thơ. Nó không phải một dòng thơ, nên không chịu H1, H4,
  không vào phép đếm nào. Ghi thẳng điều này vào bảng luật để không ai nhầm.
- Rào chắn bắt buộc: `sinh_theo_kho._lay_bon_dong` chỉ lấy bốn dòng đầu không rỗng. Một
  dòng tiêu đề lọt vào đó là **hỏng cả ứng viên**. Nên tiêu đề phải ở **thẻ riêng**, và
  bộ đọc ứng viên phải bóc thẻ trước khi đếm dòng — không được để tiêu đề và thơ chung
  một khối văn bản.
- `CACH_LAM_VIEC` mục 3 hiện cấm mọi lời dẫn. Phải sửa thành: cấm lời dẫn, **trừ** thẻ
  tiêu đề. Sửa mục này mà quên sửa bộ đọc là hỏng mọi ứng viên — ghi test đối chiếu.

### 4.1. ✅ QĐ-TD-1 CHỐT: **có tiêu đề** — ĐÃ THI CÔNG, nhưng KHÁC cách plan đề xuất

> 🔴 **Ba gạch đầu dòng ở trên dựa trên một giả định SAI về mã.** Chúng giả định thơ
> được sinh cả bài một lượt, nên "thẻ tiêu đề kèm bài thơ" là khả thi. Đọc mã thì:
>
> **Thơ được sinh THEO TỪNG KHỔ bốn dòng** (`sinh_theo_kho.py:184`) — mỗi ứng viên là
> một khổ, không phải một bài. Một thẻ tiêu đề trong câu trả lời sẽ cho **một tiêu đề
> mỗi khổ**. Và `_lay_bon_dong` lấy bốn dòng không rỗng đầu tiên, nên dòng tiêu đề lọt
> vào là **hỏng cả ứng viên**.

**Cách đã làm:** một lượt gọi riêng, **sau khi bài đã qua cổng** (`poetry/tieu_de.py`).
Đường sinh không bị đụng một dòng nào, `_lay_bon_dong` giữ nguyên, mục 3 của
`CACH_LAM_VIEC` giữ nguyên. Đánh đổi: thêm một lượt gọi mỗi bài.

Hai bất biến, đều có test ghim:

1. **Tiêu đề không đi qua luật thơ** — không đếm tiếng, không khuôn, không vần.
   `test_module_KHONG_goi_rule` ghim bằng cây cú pháp, không bằng mắt.
2. **Hỏng thì rỗng, không ném lỗi** — bài đã qua cổng trước khi lượt này chạy. Để một
   lượt gọi phụ đánh hỏng một bài đã đạt là đổi thứ chắc chắn lấy thứ trang trí.
   `PoemResponse.tieu_de` mặc định `""`, và client phải chịu được rỗng.

Bộ lọc kết quả **bỏ hẳn** tiêu đề quá dài thay vì cắt ngắn: cắt giữa chừng cho ra một
mẩu vô nghĩa mà trông như có chủ ý.

⚠️ Thẻ `bai_tho` mới phải đăng ký trong `THE_RANH_GIOI` — `test_the_ranh_gioi_day_du`
bắt được ngay khi tôi quên, đúng thứ nó sinh ra để bắt.

---

## 4b. Khiếm khuyết 4 — kế hoạch sáng tác KHÔNG CÓ nội dung (phát hiện 21/09/2026)

`PoetryPlan` có hai trường dành riêng cho nội dung: `mach_cam_xuc` và `hinh_anh`. Chính
`planner.py` giải thích vì sao chúng tồn tại:

> *"Phần mô hình LÀM TỐT HƠN là `mach_cam_xuc` và `hinh_anh` — những thứ không suy ra
> được từ luật. Hai trường đó vì vậy nhận từ ngoài vào."*

**Không ai truyền vào.** Đường sinh thơ gọi `lap_ke_hoach_hop_le(yeu_cau)`
(`sinh_tho.py:142`), mà hàm đó chỉ nhận `req` — không có tham số cho hai trường kia. Nên
`plan.hinh_anh` **luôn rỗng**, và nhánh `if plan.hinh_anh:` trong
`mo_ta_ke_hoach_cho_mo_hinh` **chưa bao giờ chạy**.

Kết quả: khối `<ke_hoach_bat_buoc>` gửi cho mô hình chỉ có số khổ, số dòng, khuôn, nhịp —
thuần cấu trúc. Đúng thứ `planner.py` nói là *"suy ra được từ luật"*, và thiếu sạch thứ
nó nói là *"mô hình làm tốt hơn"*.

Đây là **cùng một loại hỏng** với `KHUON_TRONG_CHI_DAN` ở §0.4: một chỗ trống được khai
báo tử tế, có lý do viết rõ, và không đường nào dẫn tới.

### ✅ QĐ-KH-1 — CHỐT 21/09/2026: **phương án B**, ĐÃ THI CÔNG

`lap_ke_hoach_hop_le` nay truyền `mach_cam_xuc` lấy từ `req.cam_xuc`. Đường đi đã có
test ghim (`test_ke_hoach_co_noi_dung.py`), và ghim tới **chuỗi thật gửi cho mô hình**
chứ không dừng ở `PoetryPlan` — đó mới là chỗ bản cũ đứt.

Hai chi tiết cố ý:

- **Một cảm xúc không bị chia đều cho mọi khổ.** Người dùng nêu một thì đó là một.
  Bịa thêm ý cho các khổ sau là quyết định thay tác giả, cùng lý do cổng B1 không tự
  chọn hộ số dòng.
- **`hinh_anh` vẫn rỗng, và đó là giới hạn thật của B:** `PoetryRequirement` có
  trường cảm xúc nhưng **không có trường nào cho hình ảnh**. B chỉ nối được phần có
  nguồn. Phần hình ảnh nay do khối `CHI_DAN_CHAT_LUONG` (§0.3) đảm nhiệm — **dạy mô
  hình cách tự chọn hình ảnh thay vì chọn hộ nó**. Nếu sau này đo thấy chưa đủ, mở
  lại phương án C.

<details>
<summary>Ba phương án đã cân nhắc (hồ sơ)</summary>

| Phương án | Nội dung | Đánh đổi |
| --------- | -------- | -------- |
| **A. Đóng trường** | Xoá `hinh_anh`, `mach_cam_xuc` khỏi `PoetryPlan` | Thành thật với hiện trạng. Nhưng vứt đi phần `planner.py` nói là giá trị nhất |
| **B. Người dùng điền** | Nhận từ `PoetryRequirement` khi người dùng có nêu | Rẻ, tất định, không thêm lượt gọi. Nhưng người dùng thường không nêu |
| **C. Một lượt LLM lập kế hoạch** | Đúng cách bản cũ làm: planner sinh hình ảnh, từ đắt giá | Mạnh nhất về chất lượng. Nhưng thêm một lượt gọi, và phá tính tất định của `lap_ke_hoach` — thứ `planner.py` cố ý dựng |

⚠️ Nếu sau này mở lại C, giữ nguyên `lap_ke_hoach` **thuần và tất định** như hiện nay,
và để lượt LLM đứng *ngoài* nó, truyền kết quả vào qua tham số đã có sẵn. Nhét lời gọi
mô hình vào trong một hàm đang được mô tả là "THUẦN và TẤT ĐỊNH — cùng vào, cùng ra" là
phá một hợp đồng đang có test.

</details>

---

## 4c. Nợ nhỏ đã ghi nhận, CHƯA sửa

**`CACH_LAM_VIEC` mục 5 trùng nguồn với `CHI_DAN_SUA["sua_dong"]`.** Mục 5 nói *"chỉ sửa
đúng dòng bị nêu, giữ nguyên từng chữ ở các dòng đã đạt"* — gần như nguyên văn hằng số
mà `verify_output.py:113` nối vào biên bản. Hai chỗ phát biểu cùng một quy tắc.

Thêm nữa, mục 5 và 6 nói về lượt **sửa** nhưng nằm trong `CHI_DAN_SINH_THO`, nên đi theo
**mọi** lượt sinh, kể cả lượt đầu chưa có biên bản nào.

**Vì sao chưa sửa:** mục 6 (*"khi nhận khung suy luận"*) có đường dùng thật —
`adapters/tools/poem_quality.py:77` dựng khung qua `dung_khung_suy_luan`. Gỡ hai mục này
ra khỏi tầng sinh là một thay đổi có rủi ro với đường sửa, cần đo riêng, và không nên
gộp vào cùng lượt với §0.3. Ghi lại để không ai tưởng là đã bỏ sót.

---

## 5. Khiếm khuyết 3 — Node Reviewer chấm nội dung

`quality.py` khai báo công khai hai chiều không kiểm được:

```
CL6  mach_lac   🔶 semantic_coherence đòi hiểu nội dung — thuộc node Reviewer
CL7  hinh_anh   🔶 imagery đòi hiểu nội dung — thuộc node Reviewer
```

`content_judge_user_template` của `compare_prompt.py` chấm đúng hai chiều đó, và nó đã
có sẵn thứ hiếm: **mỏ neo hiệu chuẩn** (*"điểm 5 là trung bình, 8 mới là tốt, 10 là kiệt
tác"*) — thứ chống điểm phồng tốt hơn hẳn một dòng "hãy chấm khách quan".

### ✅ QĐ-RV-1 CHỐT: **làm, ở vị trí tư vấn** — ĐÃ THI CÔNG

`poetry/reviewer.py`. Chấm đúng hai chiều `rule.py` không với tới: `CL6 mach_lac` và
`CL7 hinh_anh`. Bốn điều đã ghim bằng test:

| Ghim | Test |
| ---- | ---- |
| Không đường import nào từ `verify_output.py` / `quality.py` sang Reviewer | `test_reviewer_khong_noi_vao_cong_chan` |
| `NhanXetReviewer` **không có trường `dat`** — không ai lỡ tay dùng để chặn | `test_nhan_xet_KHONG_co_truong_dat_hay_truot` |
| Chỉ dẫn nói thẳng **"KHÔNG chấm thi luật"**, và không chứa chữ nào của luật | `test_reviewer_KHONG_cham_thi_luat` |
| **Không nhập trọng số** 0,25/0,25/0,35/0,15 của bản cũ | `test_KHONG_nhap_trong_so_cua_ban_cu` |

Hai chi tiết cố ý:

- **Hai chiều đứng riêng, không gộp thành điểm tổng.** Gộp đòi trọng số, trọng số đòi
  một người chốt, và chưa ai chốt (N1). Hai con số rời nói được nhiều hơn một con số
  trung bình che mất cả hai.
- **Điểm ngoài thang 1–10 bị coi là không đọc được, KHÔNG kẹp về biên.** Kẹp là bịa ra
  một con số mô hình không nói rồi trình bày như thể nó có nói. `co_y_kien=False` khác
  hẳn "có ý kiến và điểm thấp" — người đọc phải phân biệt được.

<details>
<summary>Phân tích khi cân nhắc (hồ sơ)</summary>

Chỉ có một vị trí đúng: **tư vấn cho người, không chặn bài**. Lý do đã viết sẵn ở
`quality.py:26-29` — port `OutputVerifier` đòi đồng bộ, thuần, tất định; *"nếu không tất
định, vòng sửa sẽ dao động"*. Một LLM-judge vi phạm cả hai. `compare_prompt.py` chính là
hệ thống mắc đúng lỗi đó: nó để LLM chấm rồi sửa theo điểm LLM vừa chấm, không có điểm
tựa nào ngoài chính mô hình.

**Chỉ nhập mỏ neo, KHÔNG nhập bộ tiêu chí.** Thang E/L/M/I của bản cũ có một chiều **M —
thi luật**, chấm bằng LLM theo luật lục bát. Mang nguyên sang đây là hỏng hai lần: sai
thể, và tệ hơn, **dựng một thẩm quyền thứ hai về luật** bên cạnh `rule.py` — đúng thứ
tầng 1 lẫn tầng 2 đang cấm mô hình tự làm. Reviewer ở hệ thống này chấm **đúng hai chiều
`rule.py` không với tới: `CL6 mach_lac` và `CL7 hinh_anh`**. Thi luật thì đã có chủ, và
chủ đó không phải LLM.

Ràng buộc khi thi công:

- Điểm của Reviewer **không bao giờ** được đọc bởi `verify_output.py` hay `quality.py`.
  Viết test cấm import theo chiều đó.
- `KetQuaChatLuong.dat` giữ nguyên nghĩa cũ. Reviewer không được đụng vào.
- ⚠️ **Va tên:** "G7" trong `quality.py` chỉ *giai đoạn thi công* G7 (HITL, xem
  `Plan_Thi_Cong_DeepAgent.md:81`), còn "chặn G7" trong `verify_output.py:230` là *chặn
  cứng thứ bảy*. Hai thứ khác hẳn nhau. Đổi tên một trong hai trước khi viết thêm mã
  tham chiếu tới "G7", nếu không sẽ có ngày ai đó nối điểm của Reviewer vào cổng chặn vì
  tưởng cùng một thứ. **Chưa sửa** — `reviewer.py` cố ý không nhắc chữ "G7" lần nào để
  không làm va tên nặng thêm.

</details>

### 5.1. Việc còn lại của Reviewer: chưa ai GỌI nó

`reviewer.py` đã có, đã test, và **chưa đường nào gọi tới** — đúng tình trạng mà
`instructions.py:46` đặt luật để cấm ("có mã thật sự đọc nó NGAY khi thêm vào"). Ở đây
là cố ý và có hạn: nó chờ đường HITL của giai đoạn G7, nơi ý kiến tư vấn có người đọc.

**Không được nối tạm vào đường sinh cho "đỡ phí".** Nối vào đó nghĩa là mỗi bài thơ tốn
thêm một lượt gọi mà không ai nhìn kết quả. Khi HITL có mặt, gọi nó ở đó.

---

## 6. Cố ý KHÔNG làm

**Ba thể thơ (lục bát, 7 chữ, 8 chữ).** Không nằm trong thiết kế. Hệ thống này làm một
thể: thất ngôn tự do. Cấu trúc `[thể][vai_trò]` của `compare_prompt.py` không phải một
lộ trình đang chờ, nó là dấu vết của một hệ khác — và toàn bộ giá trị của kiến trúc hiện
tại nằm ở chỗ **một thể, một bảng luật, một bộ kiểm, không có nhánh nào rẽ theo thể**.
Thêm chiều "thể thơ" vào là mở lại chiều mà mọi ràng buộc đang dựa vào để đóng.

Nếu một ngày có yêu cầu thật, nó là một plan riêng bắt đầu từ tài liệu luật của thể mới,
không phải một mục trong plan này. Cho tới lúc đó: **không viết một dòng mã nào nhận
tham số thể thơ**, kể cả "để sẵn cho sau này".

**Ví dụ và câu chữ của thể khác.** Luật niêm, vần lưng, câu Lục / câu Bát, "Nhị Tứ Lục
phân minh" — không mang sang dù chỉ làm ví dụ minh hoạ. Một ví dụ sai thể nằm trong
prompt sẽ được mô hình đọc như luật.

**Trọng số E/L/M/I = 0,25 / 0,25 / 0,35 / 0,15.** Bốn con số không có nguồn gốc. Vi phạm
N1. Nếu Reviewer cần tổng hợp một điểm, trọng số phải do chủ dự án chốt và ghi lại kèm
lý do, không chép từ bản cũ.

---

## 7. `compare_prompt.py` — ✅ XONG 21/09/2026: GIỮ, nhưng chặn đường chạy

> **Chủ dự án chốt:** *"Không cần xóa đâu, chỉ cần không chạy qua đó là được."*

Bản plan đầu đề nghị xoá. Quyết định là **giữ làm hồ sơ đối chiếu** — hợp lý, vì phần
lớn những gì hệ thống sống vừa nhập đều đối chiếu từ đó ra, và xoá đi thì lần sau không
còn gì để so.

Nhưng giữ một file prompt trong repo mà không ai gọi chính là cái bẫy `instructions.py:48-51`
đã đặt tên: *"ai sửa quy tắc ở bản chép sẽ tin mình vừa đổi hành vi hệ thống, trong khi
không có gì đổi"*. Nên giữ thì phải chặn đúng cái bẫy đó, bằng **hai lớp**:

| Lớp | Chặn kiểu hỏng nào | Cách |
| --- | ------------------ | ---- |
| 1 | **Nối vào mã sống** — một `import compare_prompt` lọt vào `src/` | quét cây cú pháp toàn bộ `src/`; bắt theo **tiền tố** `compare_` nên file đối chiếu thêm sau này tự động được bảo vệ |
| 2 | **Hiểu nhầm** — người mở file ra tưởng sửa nó là đổi hành vi | nhãn ở đầu file, có test đòi nhãn phải tồn tại |

Lớp 2 không thay được lớp 1: nhãn thì người đọc mới thấy, test thì máy thấy. Thêm một
phép kiểm nữa: file đối chiếu **không được nằm trong `src/`**, vì nằm trong đó là tự động
vào đường import dù chưa ai import.

`tests/architecture/test_file_doi_chieu_khong_chay.py` — 3 test.

**Nhãn đã gắn cho cả hai file**, và nhãn ghi rõ thứ ĐÃ nhập kèm chỗ đến, để không ai nhập
lại lần nữa:

| Nhập từ bản cũ | Đã vào |
| -------------- | ------ |
| cặp ví dụ tốt/dở | `instructions.CHI_DAN_CHAT_LUONG` |
| mỏ neo hiệu chuẩn điểm | `poetry/reviewer.CHI_DAN_REVIEWER` |
| lối thoát khi bế tắc | `instructions.CACH_LAM_VIEC` mục 7, 8 |
| tiêu đề cho bài thơ | `poetry/tieu_de.py` |
| ~~quy tắc phiên âm TTS~~ | **cố ý không nhập** — QĐ-TTS-1 |

`compare_rule.py` (bộ kiểm **lục bát** của hệ khác) cũng được gắn nhãn, kèm cảnh báo
riêng: đừng nhập luật từ đó, vì một điều luật sai thể lọt vào prompt sẽ được mô hình đọc
như luật thật. File đó vốn cũng không import nổi — nó dùng import tương đối trỏ tới một
gói không tồn tại trong repo.

---

## 8. Thứ tự thi công

| Giai đoạn | Việc | Trạng thái |
| --------- | ---- | ---------- |
| ~~**T-0**~~ | Thang thẩm quyền · lối thoát khi bế tắc · khối CHẤT LƯỢNG · ghim khuôn thật (§0.1–0.4) | ✅ **xong 21/09** |
| ~~**T0**~~ | Chủ dự án chốt bốn QĐ | ✅ **xong 21/09** |
| ~~**T1 → T4**~~ | Bảng âm chính · `la_am_tiet_hop_le` · H5 · đoạn phiên âm | ⛔ **HUỶ** — QĐ-TTS-1 chốt "để nguyên, đếm theo luật" |
| ~~**T6.5**~~ | Nối `mach_cam_xuc` từ yêu cầu người dùng (§4b) | ✅ **xong 21/09** |
| ~~**T5**~~ | Tiêu đề — **một lượt gọi riêng sau cổng**, KHÔNG phải thẻ trong câu trả lời (xem §4.1) | ✅ **xong 21/09** |
| ~~**T6**~~ | Node Reviewer (tư vấn, không chặn) + test ghim chiều import | ✅ **xong 21/09** |
| ~~**T8**~~ | 🩸 Lỗi `gìn` (§3.0) — qua đủ bốn bước, băm đã đổi | ✅ **xong 21/09** |
| ~~**T7**~~ | `compare_prompt.py` — **giữ**, chặn đường chạy bằng 2 lớp test (§7) | ✅ **xong 21/09** |

**🎉 Toàn bộ plan đã thi công xong.** Không còn giai đoạn nào đang chờ.

**Bài học của lượt 21/09 — ghi lại để không lặp:** T1 và T1.5 đã được thi công **trước
khi** ai kiểm `tests/architecture/test_rule_dong_bang.py`, và test đó ghim SHA-256 của
`rule.py` kèm chỉ thị *"Rule của tôi phải là không được thay đổi"*. Toàn bộ phần đó đã
phải hoàn nguyên.

> **Luật cho mọi plan sau:** bất kỳ việc nào chạm `src/application/rule.py` phải đi qua
> bốn bước ở §3.0 và được chủ dự án duyệt **trước khi gõ dòng mã đầu tiên** — không phải
> sau khi test đỏ. Lớp băm cố ý khó chịu: nó buộc người sửa nhìn thấy cái giá trước, và
> lượt này đã chứng minh nó làm đúng việc của nó.

Thêm một hệ quả đã xảy ra: chạy `kiem_tra_toan_bo.py` để lấy số liệu **ghi đè**
`datalake/analysis/`. Sau khi hoàn nguyên `rule.py` phải **chạy lại script đó** bằng bản
luật gốc, nếu không kho phân tích mang số của một bản luật không còn tồn tại.

**Về hai tập ngữ liệu, đừng nhầm:**

| Tập | Số bài | Trạng thái | Dùng để |
| --- | ------ | ---------- | ------- |
| `datalake/corpus_tuyen/tho_mau.jsonl` | 300 | **commit được** | đo, ghim test, nuôi few-shot |
| `datalake/analysis/bai_dat.jsonl` | 24.366 | 266 MB, **gitignored** | đối chiếu diện rộng, KHÔNG ghim test |

Con số "6.000 bài" xuất hiện trong `quality.py` là một mẫu đo cũ, **không phải tên của
tập nào**. Không trích lại nó như một tập ngữ liệu.

Một lượt chạy trên `bai_dat.jsonl` để xem H5 bắt bao nhiêu trong 24.366 bài là việc
**nên** làm ở T2 và ghi số vào §3.4 — nhưng số đó không được đưa vào `assert` của bất kỳ
test nào, vì checkout sạch không có file. Ghim test chỉ trên tập tuyển.

---

## 9. Definition of Done

- [ ] `grep -ri "tts" src/` trả về kết quả, và mọi kết quả trỏ về một nguồn duy nhất.
- [ ] Một bài chứa "Vinfast" bị H5 đánh trượt, kèm lý do chỉ đúng tiếng vi phạm.
- [ ] Một bài chứa "Vin Phát" ĐẠT — tức chiều phạt-vì-làm-đúng ở §3.1 đã hết.
- [ ] Trên `tho_mau.jsonl`: H5 bắt đúng `{show, phone}`, không bắt `gìn` nữa.
- [ ] `hiep_van("gìn", "nhìn")` trả về True — lỗi §3.6 đã hết, có test riêng ghim.
- [ ] Kho mẫu few-shot không còn bài nào vi phạm H5 (§3.7).
- [ ] `test_tang_2_khong_chep_luat_tho` vẫn xanh sau khi thêm đoạn phiên âm.
- [ ] Không đường import nào từ node Reviewer vào `verify_output.py` hay `quality.py`.
- [x] `compare_prompt.py` **giữ lại** làm hồ sơ, có 2 lớp test chặn đường chạy, và phần
      còn giá trị đã nằm ở chỗ có mã đọc tới (§7).
