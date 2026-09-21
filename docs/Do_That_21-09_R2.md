# ĐO THẬT VỚI MÔ HÌNH THẬT — trả lời rủi ro R2

**Ngày đo:** 21/09/2026 · **Provider:** OpenAI · **Model:** `gpt-4o-mini`, đối chứng `gpt-4o`
**Sinh lại:** `DEFAULT_PROVIDER=openai python evals/do_that.py 12`
**Không mock gì cả.** Script tự dừng nếu provider là `mock`.

---

## 0. Câu hỏi và câu trả lời

**Rủi ro R2** ghi từ đầu `Plan_Thi_Cong_DeepAgent.md`: tầng 4 (thanh luật) loại
**55,29% thơ NGƯỜI VIẾT** trong corpus 67.150 bài. Liệu mô hình có làm nổi không?

**Sinh cả bài một lần: KHÔNG.** Và không phải vì prompt, cũng không phải vì mô
hình yếu — nó **không điều khiển được lớp thanh điệu tiếng Việt ở một vị trí âm
tiết cho trước**, kể cả khi được chỉ đích danh tiếng nào và phải đổi thành thanh gì.
Bốn giả thuyết sửa chữa đều bị bác bỏ (§3).

**Sinh từng khổ, chọn trong nhiều ứng viên: ĐƯỢC.**

| | Sinh cả bài một lần | Sinh từng khổ |
|---|---:|---:|
| đạt luật | 8,3% | **83,3%** |
| bài 12 dòng | 0% | **đạt cả hai lần chạy** |

Cách sửa **không phải nới luật** mà là phá phép toán `pⁿ`: `p` là giới hạn của mô
hình và không sửa được, nhưng `n` thì cắt được xuống 4 ở mọi bài. Chi tiết §3B.

Và suốt mọi phép đo, hệ thống **đúng ở chỗ quan trọng nhất**: không một bài sai
luật nào đi ra. Cái từng hỏng là NĂNG SUẤT, không phải tính đúng đắn.

---

## 1. Số liệu

### 1.1. Tỉ lệ một BẢN NHÁP đạt luật — 40 bản nháp, `gpt-4o-mini`

| Số dòng | Bản nháp đạt | Tỉ lệ |
|---:|---:|---:|
| 4 | 2/20 | **10%** |
| 8 | 0/10 | **0%** |
| 12 | 0/10 | **0%** |
| **Tổng** | **2/40** | **5,0%** |

### 1.2. Vì sao tỉ lệ sụp theo độ dài

Suy từ số liệu: nếu mỗi dòng độc lập có xác suất khớp khuôn là `p`, thì bài `n`
dòng đạt với xác suất `pⁿ`. Từ 10% ở bài 4 dòng: `p ≈ 0,10^(1/4) ≈ 0,56`.

    ngẫu nhiên thuần  25%   (2 khuôn hợp lệ / 8 tổ hợp B-T ở P2,P4,P6)
    đo được           56%
    cần cho bài 8 dòng ~75% để đạt 10%

Mô hình **khá hơn ngẫu nhiên**, nhưng lỗi nhân lên theo số dòng. Bài 8 dòng cần
`0,56⁸ ≈ 1%` — khớp với 0/10 quan sát được.

### 1.3. Vòng sửa KHÔNG hội tụ

| Lần đo | Đạt lượt đầu | Đạt mọi lượt |
|---|---:|---:|
| Bản gốc | 1/12 | 3/12 |
| Sau khi sửa prompt | 1/12 | 1/12 |
| Sau khi biên bản nêu rõ âm tiết | 0/12 | 0/12 |
| Sau khi sửa leo thang | 1/12 | 1/12 |

⚠️ **Bốn lần đo này KHÔNG phân biệt được với nhiễu lấy mẫu ở n=12.** Tôi đã có lúc
đọc 3/12 → 1/12 là *"thay đổi của tôi làm tệ đi"*; đó là kết luận sai từ một mẫu
quá nhỏ. Điều duy nhất ổn định là chỉ số dưới đây.

**`số lượt sửa trung bình của bài đạt = 0,00`** — mọi bài đạt đều đạt **ngay lượt
đầu**. Trong toàn bộ phép đo, **chưa một bài nào đạt được nhờ sửa**.

### 1.4. Mô hình mạnh hơn không giúp

`gpt-4o` trên 6 đề đầu: **0/6**. Cùng 6 đề ấy `gpt-4o-mini` được 2/6.

Nên đây **không phải giới hạn trí thông minh**. Nó là một giới hạn cụ thể về ngữ âm.

---

## 2. Bằng chứng quyết định

Ghi lại nguyên văn bốn lượt sửa liên tiếp của một yêu cầu. Biên bản nêu **chính
xác** tiếng nào và phải đổi thành thanh gì:

```
LƯỢT 1  D1 "Mùa gặt về, nắng trải thềm xưa"
        P2="gặt"(T) P4="nắng"(T) P6="thềm"(B) => T T B
        -> đổi tiếng thứ 2 ("gặt") thành một tiếng thanh BẰNG

LƯỢT 2  D1 "Mùa gặt về, nắng trải đường xưa"   <- đổi tiếng 6, không phải tiếng 2
LƯỢT 3  D1 "Mùa bát về, nắng trải đường xưa"   <- đổi tiếng 2 nhưng "bát" VẪN LÀ TRẮC
LƯỢT 4  D1 "Mùa gặt về, nắng trải lối xưa"     <- quay lại "gặt"
```

Bốn lượt, chỉ dẫn rõ ràng nhất có thể, và mô hình **chưa một lần** đặt được một
tiếng thanh bằng vào vị trí 2. Ở lượt 3 nó hiểu đúng *vị trí* cần đổi nhưng chọn
một tiếng cùng lớp thanh — dấu hiệu rằng nó không phân loại được thanh điệu.

---

## 3. Bốn giả thuyết đã thử và bác bỏ

| # | Giả thuyết | Cách kiểm | Kết quả |
|---|---|---|---|
| 1 | Prompt chưa dạy đủ về thanh luật | Thêm ví dụ tính thanh từng tiếng + bắt gọi tool tự soi | Không cải thiện · thời gian gấp đôi · **đã hoàn nguyên** |
| 2 | Biên bản sửa chưa đủ cụ thể | Nêu đích danh tiếng nào, đổi thành thanh gì, khuôn gần nhất | Không cải thiện · **giữ lại** vì nghiêm túc hơn |
| 3 | Tool lạ làm mô hình phân tâm | So có/không 5 tool | Mô hình **không gọi tool** ở cả hai — bác bỏ |
| 4 | Mô hình mạnh hơn sẽ làm được | `gpt-4o` | **0/6**, kém hơn `gpt-4o-mini` — bác bỏ |

### Hai lỗi thật tìm được nhờ phép đo, đã sửa

**a) Leo thang theo SỐ LƯỢT thay vì theo bằng chứng** — `verify_output.py`

```
lượt 0 -> sua_dong        lượt 1 -> sinh_lai_kho
lượt 2 -> sinh_lai_ca_bai   <- "viết lại toàn bài từ đầu"
```

Ngay ở lượt sửa **thứ hai**, hệ thống bảo mô hình vứt cả bài — kể cả dòng đã đạt —
và đó thường là lúc bài chỉ còn 1 lỗi. Nay thang chỉ nhích khi **số lỗi không giảm
hai lượt liên tiếp**; số lượt không còn tự nó đẩy thang.

**b) Biên bản S2 không nói tiếng nào ở vị trí nào** — `poem_verifier.py`

Bản cũ viết *"đang có P2/P4/P6 = T T B"*, buộc mô hình tự đếm vị trí — đúng thứ nó
làm sai. Nay nêu `P2="gặt"(T)` và khuôn gần nhất. Vẫn **không viết thơ hộ**: chỉ
nói *lớp thanh* cần có, không bao giờ gợi ý dùng chữ nào.

---

## 3B. ĐÃ GIẢI — sinh từng khổ, chọn trong nhiều ứng viên

Chủ dự án chốt: *"giữ nguyên luật, thời gian lấy nhiều cũng được, thứ tôi cần là
thơ đúng luật"*. Đó là **phương án B mở rộng**, và nó giải được bài toán.

### Ý tưởng: không sửa `p`, mà cắt `n`

`p ≈ 0,56` là giới hạn ngữ âm của mô hình — bốn giả thuyết đã bác bỏ mọi cách sửa
nó. Nhưng bài `n` dòng đạt với `pⁿ`, và **`n` thì cắt được**: sinh từng khổ 4 dòng,
mỗi khổ chọn trong `k` ứng viên.

    P(một khổ đạt) = 1 − (1 − 0,10)^k        k = 16  ->  ~81%
    P(cả bài đạt)  = P(một khổ)^(n/4)        12 dòng ->  ~53%

### Số đo — hai lần chạy ĐỘC LẬP, cùng 12 đề

| | Trước | Sau |
|---|---:|---:|
| đạt lượt đầu | 8,3% | **75,0%** |
| **đạt (mọi lượt)** | **8,3%** | **83,3%** |
| kiệt lượt | 91,7% | **16,7%** |
| thời gian mỗi bài | 6,6s | 7,4–10,3s |

Hai lần chạy cho **đúng 10/12**, nên đây không phải may mắn lấy mẫu.

Quan trọng nhất: **bài 12 dòng từ 0% lên đạt cả hai lần**. Đó là cỡ bài mà cách cũ
gần như không bao giờ làm được.

Giá phải trả: thời gian tăng ~1,5×, và số lượt gọi model tăng theo `k`. Đúng đánh
đổi chủ dự án đã chọn.

### Vì sao KHÔNG vi phạm P2

> P2: *"Bộ kiểm PHÁN, mô hình SỬA. Không hàm nào được sửa văn bản thơ."*

**Mô hình viết từng chữ của mọi ứng viên**, và viết khổ sau khi đã đọc các khổ
trước — mạch thơ là của nó. Hệ thống chỉ **chọn** ứng viên nào qua được luật.

Chọn không phải sửa. Đây đúng là thứ kiến trúc verification-first mở ra: có bộ kiểm
tất định thì sinh nhiều rồi lọc là cách rẻ nhất đổi tính toán lấy độ tin cậy.

Hai bất biến được giữ: khổ nhận vào phải giữ **cả bài** hợp luật (kiểm trên toàn bộ
phần tích luỹ, không kiểm rời), và bài ghép xong **vẫn đi qua cổng kiểm đầy đủ**.

### 16,7% còn lại

Vẫn là S2, và vẫn rơi vào bài 8 dòng. Tăng `so_ung_vien_moi_kho` từ 16 lên 32 sẽ
đưa mỗi khổ từ ~81% lên ~97% theo phép toán trên — đổi bằng gấp đôi số lượt gọi.
Đó là một tham số, `SO_UNG_VIEN_MAC_DINH`, sửa một chỗ.

---

## 4. Nếu muốn đi xa hơn — thuộc về chủ dự án

Bốn đường đi, và **cả bốn đều là quyết định của bạn, không phải của tôi**:

| | Phương án | Hệ quả đo được |
|---|---|---|
| **B** | ✅ **ĐÃ LÀM** — sinh từng khổ, chọn ứng viên | 8,3% → **83,3%** (§3B) |
| **B+** | Tăng `SO_UNG_VIEN_MAC_DINH` 16 → 32 | mỗi khổ ~81% → ~97%; trả bằng gấp đôi lượt gọi. Sửa MỘT hằng số |
| **C** | Nới QĐ-2 | **KHÔNG LÀM** — chủ dự án đã chốt giữ nguyên luật |
| **D** | Dựng dòng theo thanh bằng chương trình | **KHÔNG LÀM** — vi phạm P2, máy viết thơ hộ |

C và D đều đã bị loại, và loại đúng: B đạt 83,3% mà không đụng tới một chữ nào của
`rule.py`.

---

## 5. Điều phép đo KHÔNG bác bỏ

Toàn bộ kiến trúc kiểm định **hoạt động đúng như thiết kế**, và phép đo này là bằng
chứng mạnh nhất cho điều đó:

- **0 bài sai luật đi ra** trong ~40 yêu cầu và ~150 lượt gọi model
- mọi ca không đạt đều kết thúc bằng `OutputKhongDat` kèm chẩn đoán có địa chỉ dòng
- `rule.py` không đổi một byte suốt quá trình

Nói cách khác: hệ thống **từ chối đúng**. Nó chỉ đang từ chối rất nhiều.
