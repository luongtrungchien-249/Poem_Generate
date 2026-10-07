# PLAN — Cải thiện `rule.py` sau T8

**Ngày lập:** 21/09/2026
**Tệp mục tiêu:** `src/application/rule.py` (2.238 dòng, 46 hàm, băm `0a0b2488…`)
**Tài liệu luật:** `docs/Luat_Tho_That_Ngon_Tu_Do.md`
**Plan tiền nhiệm:** `docs/Plan_Rule_Phan_Tang.md` (T1 → T8)
**Trạng thái:** 🟡 chờ chủ dự án chốt QĐ-8 và QĐ-9

---

## 0. Kết luận một trang

Ba lỗi đã xác minh bằng cách chạy thật trên bản 2.238 dòng, kèm tác động **đo được**:

| Lỗi | Biểu hiện | Tác động đo được |
| --- | --- | --- |
| **L1** §5b chưa nối | `hiep_van("hoa","ta")` = False; `phan_tich_am_tiet` chỉ được test gọi | trần ở 360 bài (tầng 5 chỉ chặn ngần ấy) |
| **L2** `nghi_duong_luat` luôn False | suy bằng `not tang3.dat`, mà tầng 3 luôn `dat=True` | **4.288 bài** bị ba script báo thành 0 |
| **L3** `doc_so` vỡ ở 10¹² | `_HANG` hết ở "tỷ" → `IndexError` | **0/67.150** bản ghi dính — lỗi bền bỉ, không phải lỗi số liệu |

**Nhưng đòn bẩy lớn nhất không nằm ở ba lỗi đó.** Tầng 4 chặn **30.571/55.297 bài
(55,29%)**, trong đó **6.162 bài phá khuôn đúng MỘT dòng**. Đây không phải lỗi — đó là hệ
quả cố ý của QĐ-1 và QĐ-2. Nhưng nó là chỗ duy nhất trong bảy tầng còn dư địa thật, và
việc quyết định làm gì với nó thuộc về chủ dự án, không thuộc về mã nguồn.

**Thứ tự thi công đề xuất:** G0 (không đụng `rule.py`) → G1 (L3) → G2 (L2) → G3 (tầng 4)
→ G4 (L1). Xếp theo **rủi ro tăng dần**, không theo mức độ nghiêm trọng.

---

## 1. Hai ràng buộc chi phối toàn bộ plan này

### 1.1. Chỉ thị 1 — `rule.py` là file đóng băng

`tests/architecture/test_rule_dong_bang.py` ghim SHA-256 của `rule.py`. Test **không cấm
sửa** — nó buộc người sửa nhìn thấy cái giá trước. Mỗi lần đổi băm phải làm đủ:

1. `python datalake/scripts/kiem_tra_toan_bo.py` — đo lại 67.150 bản ghi
2. `python datalake/scripts/doi_soat_tai_lieu.py` — chạy tới khi xanh
3. ghi lý do vào `docs/Plan_Rule_Phan_Tang.md` thành một mục §
4. chủ dự án duyệt, rồi mới đổi `BAM_DA_CHOT`

**Hệ quả cho plan này:** mỗi giai đoạn đụng `rule.py` là **một lượt đổi băm riêng**, mang
**đúng một lý do** — theo đúng tiền lệ T8 (§12): *"Một lượt sửa file đóng băng mang đúng
một lý do, để sau còn tra được thay đổi nào gây hệ quả nào."* Không gộp L1 + L2 + L3 vào
một lượt, dù làm vậy nhanh hơn.

### 1.2. Bốn nguyên tắc của plan tiền nhiệm vẫn có hiệu lực

N1 (tiêu chí phải trích được từ tài liệu), N2 (điều loại *quyền* không bao giờ đánh
trượt), N3 (điều không kiểm được phải ghi công khai), N4 (mọi số liệu từ một lượt chạy
mới).

**N1 trực tiếp loại một phương án ở G3** — xem §5.3.

---

## 2. Phạm vi — điều plan này CỐ Ý KHÔNG LÀM

| Không làm | Vì sao |
| --- | --- |
| Mở rộng sang thể thơ khác | Phạm vi dự án là **thất ngôn tự do**, cố định |
| Nối `compare_rule.py` / `compare_prompt.py` vào `src/` | Chủ dự án chốt 21/09: *"Không cần xóa đâu, chỉ cần không chạy qua đó là được"*; `test_file_doi_chieu_khong_chay.py` đang canh |
| Làm tầng 6 chặn được thật | Cần bộ tách từ tiếng Việt — việc lớn, đứng riêng. Tầng 6 hiện đã **tự khai báo** là rỗng nghĩa, nên nó không nói dối ai |
| Đổi tiêu chí tầng 5 | Vừa sửa ở T8 và QĐ-7b, chưa có căn cứ mới |
| Tách `rule.py` thành nhiều module | Đụng mọi import, và đổi băm vì lý do không phải luật |

---

## 3. G0 — Ba test kiến trúc chống tái phát

**Không đụng `rule.py`, không đổi băm.** Làm trước tất cả.

Cả ba lỗi L1–L3 cùng một họ: **một đoạn code đúng nhưng không ai gọi, và không test nào
phát hiện được điều đó.** Bằng chứng mạnh nhất là L2 — nó đã **được phát hiện, ghi chú và
né** ở `datalake/scripts/xuat_phan_bo.py:84-87`, nhưng chưa từng được vá ở gốc, nên ba
script khác vẫn đọc cờ hỏng.

Repo đã có sẵn khuôn mẫu đúng (`HAM_KIEM_CUNG` + đối chiếu `MA_CUNG`); G0 chỉ mở rộng
nguyên tắc ấy từ *bảng luật* sang *đường dẫn dữ liệu*.

| Test | Bắt được gì | Bắt được lỗi nào trong ba lỗi |
| --- | --- | --- |
| `test_khong_ham_public_nao_chi_test_goi` | hàm public của `rule.py` mà chỉ `tests/` gọi | **L1** |
| `test_moi_truong_PoemVerdict_deu_song` | trường nhận đúng một giá trị trên ngữ liệu vàng | **L2** |
| `test_chi_tiet_ghi_ra_deu_co_noi_doc` | khoá `chi_tiet[...]` không ai đọc | L2 (chiều ngược) |

Đặt ở `tests/architecture/test_rule_khong_co_ma_chet.py`.

⚠️ **Dự kiến cả ba đỏ ngay khi viết xong** — đó là mục đích. Chúng đỏ cho tới hết G4.
Đánh dấu `xfail` có lý do trỏ về plan này, gỡ dần theo từng giai đoạn.

**Nghiệm thu G0:** ba test tồn tại, đỏ đúng ba lỗi đã biết, không đỏ nhầm chỗ khác.

---

## 4. G1 — L3, `doc_so` không được ném exception

**Lý do một dòng:** một bài thơ chứa số ≥ 10¹² làm sập cả mẻ xử lý corpus thay vì trả về
"bài trượt".

**Vì sao làm trước:** đã đo — **0/67.150** bản ghi chứa chuỗi ≥ 13 chữ số. Nên lượt đổi
băm này gần như chắc chắn cho corpus **y nguyên**, và nó trở thành **bài diễn tập rẻ** cho
đúng quy trình bốn bước của §1.1 trước khi đụng vào lượt sửa thật sự có rủi ro.

```python
if bac > 0:
    if bac >= len(_HANG):
        return _doc_chu_so_roi(chuoi_goc)   # số quá dài thì đọc rời từng chữ số
    ra.append(_HANG[bac])
```

Chọn *đọc rời* thay vì mở rộng `_HANG` sang "triệu tỷ", "nghìn tỷ tỷ": người Việt thật sự
đọc rời khi số quá dài, và mở bảng thì lại phải chọn một quy ước không có trong tài liệu.

**Nghiệm thu G1:**
- test mới cho `10**12`, `10**15`, `10**18` — không ném, trả danh sách âm tiết;
- `kiem_tra_toan_bo.py`: `bai_dat` = **24.366**, không đổi một bài;
- `doi_soat_tai_lieu.py` xanh; §13 viết vào `Plan_Rule_Phan_Tang.md`; băm mới được duyệt.

---

## 5. G2 — L2, nối lại `nghi_duong_luat`

**Lý do một dòng:** cờ cấp bài suy từ `not tang3.dat`, mà tầng 3 luôn `dat=True` kể từ bản
sửa 18/09/2026 — nên cờ ấy chết, và số thật 4.288 bị ba script báo thành 0.

```python
nghi = bool(ket_qua_tang[2].chi_tiet.get("nghi_duong_luat"))
```

**Phân tích rủi ro:** `nghi_duong_luat` **không tham gia** vào `dat` — Đ1 đã chốt tầng 3
chỉ cảnh báo, và `test_rule.py:280` đang ghim đúng tính chất đó. Vậy lượt này đổi **số
liệu báo cáo**, không đổi **phán quyết**. Đây là lý do nó đứng trước G3 và G4.

**Việc kèm theo, bắt buộc trong cùng lượt** (nếu không thì vá gốc mà ngọn vẫn sai):

1. gỡ đoạn né ở `xuat_phan_bo.py:84-87`, đọc thẳng cờ cấp bài trở lại;
2. chạy lại `phan_tich_corpus.py`, `chay_lai_toan_bo.py`, `kiem_tra_toan_bo.py` — ba script
   đang in `nghi là Đường luật: 0 (0.00%)`;
3. cập nhật mọi báo cáo đã trích con số 0 đó.

**Nghiệm thu G2:**
- `nghi_duong_luat` = True trên ít nhất một bài của ngữ liệu vàng (đã có ca thử: bài
  Nguyễn Khuyến 4 dòng độc vận, `chi_tiet` = True mà cờ = False);
- ba script báo **4.288**, khớp với `ghi_nhan_nhung_khong_chan` trong `tong_hop.json`;
- `bai_dat` vẫn **24.366** — nếu đổi thì có gì đó sai, dừng lại;
- `test_moi_truong_PoemVerdict_deu_song` (G0) chuyển xanh.

---

## 6. G3 — Tầng 4: 6.162 bài hỏng đúng một dòng ⭐ CẦN CHỦ DỰ ÁN QUYẾT

### 6.1. Số liệu

Phân bố số dòng phá khuôn trong 30.571 bài bị tầng 4 chặn:

| Số dòng phá | 1 | 2 | 3 | 4 | 5 | ≥6 |
| --- | --- | --- | --- | --- | --- | --- |
| Số bài | **6.162** | 4.295 | 3.626 | 3.005 | 2.382 | 11.101 |

20,2% số bài bị tầng 4 loại chỉ hỏng **một dòng duy nhất**.

### 6.2. Đây KHÔNG phải lỗi

`rule.py` đã ghi rõ: *"Con số đó là hệ quả trực tiếp của QĐ-1 và QĐ-2, không phải do thước
đo hỏng."* Tôi đã đọc lại và xác nhận điều đó đúng. Tài liệu dùng chữ *"nên"*; QĐ-1 nâng
thành *"phải, áp lên toàn bộ dòng"*; QĐ-2 cấm phá khuôn. Thước đo đang làm đúng việc được
giao.

Câu hỏi không phải *"sửa thế nào"* mà là *"có muốn giữ nguyên không"*.

### 6.3. Ba phương án — và vì sao một trong ba bị N1 loại thẳng

| | Phương án | Đánh giá |
| --- | --- | --- |
| **A** | Giữ nguyên. 39,28% là tỷ lệ có chủ ý. | Hợp lệ. Không tốn gì. |
| **B** | Cho ngoại lệ định lượng (ví dụ ≤1 dòng phá khuôn mỗi cụm 4 dòng) | ❌ **N1 loại thẳng.** Tài liệu không cho con số nào. Bản plan đầu tiên đã mắc đúng lỗi này với ngưỡng 0,5 — và tệ hơn, ngưỡng ấy được chọn *vì nó giữ lại 84,82% số bài*. Chọn "1 dòng" ở đây cũng sẽ là nắn luật cho vừa dữ liệu. |
| **C** | Giữ nguyên tiêu chí `dat`, **thêm một trường mô tả** `so_dong_pha_khuon` ở cấp bài | ✅ **Đề xuất.** Không đụng luật, không phạm N1. |

### 6.4. Vì sao đề xuất C

C **không nới luật một chữ nào**. Bài phá khuôn 1 dòng vẫn trượt, vẫn `dat=False`. Nó chỉ
thôi vứt đi một thông tin đang có sẵn trong tay: `_tang4_thanh_luat` đã tính `len(pha)` và
ghi vào `chi_tiet["so_dong_pha_khuon"]`, nhưng cấp bài không thấy.

Ai dùng được thông tin đó:
- `fewshot.py` — phân biệt bài *gần đạt* với bài hỏng nặng khi chọn mẫu;
- vòng sửa (`feedback.py`, `sinh_theo_kho.py`) — biết bài nào đáng sửa tiếp, bài nào nên bỏ;
- báo cáo — nói được *"trượt vì một dòng"* thay vì chỉ *"trượt tầng 4"*.

Đây cùng một tinh thần với `bang_chung` mà bảy tầng đã có: **phán quyết không đổi, nhưng
phải nói rõ trượt thế nào.**

> **QĐ-8 (chờ chốt):** giữ nguyên tiêu chí tầng 4; bổ sung `PoemVerdict.so_dong_pha_khuon`
> là số **mô tả**, không tham gia `dat`, không tham gia `thuoc_the`.

**Nghiệm thu G3:** `bai_dat` vẫn 24.366; trường mới khớp với tổng
`pha_khuon_cua_bai_truot_tang4.tong_bai` = 30.571 và
`theo_so_dong_pha["1"]` = 6.162; test N2 (*không điều QUYỀN nào làm tiêu chí chặn*) vẫn xanh.

---

## 7. G4 — L1, nối §5b vào `hiep_van` ⭐ CẦN CHỦ DỰ ÁN QUYẾT

**Để cuối cùng vì đây là lượt duy nhất có thể đổi phán quyết của bài.**

### 7.1. Lỗi

`hiep_van` (dòng 969) vẫn gọi `van_cua`. Toàn bộ §5b — `AmTiet`, `phan_tich_am_tiet`,
`van_hiep` — chỉ được `tests/unit/application/test_rule_tang.py` gọi. QĐ-3 *"so vần theo
âm chính + âm cuối"* được trích trong `trich_luat` của tầng 5, nhưng **chưa có hiệu lực**.

```
hiep_van("hoa", "ta")   -> False      ❌   (đúng ca mà chú thích §5b nói phải sửa)
hiep_van("hoa", "nhà")  -> False      ❌
```

Docstring `van_cua` hiện ghi *"Phép so vần chính thức nay dùng `phan_tich_am_tiet()`"* —
câu này đang **sai sự thật**.

### 7.2. Đã đo độ rủi ro

Bảng `CAP_VAN_THONG` có **62 khoá / 77 cạnh**. Đổi sang `van_hiep`, chỉ **6 khoá** không
sinh ra được, và **4/6 gập vào khoá đã có sẵn**:

| Khoá | Gập thành | Có trong bảng? | Hệ quả |
| --- | --- | --- | --- |
| `uyên` | `iên` | ✅ | vô hại, cùng nhóm `(en, in, iên, uyên)` |
| `uê` | `ê` | ✅ | vô hại, cùng nhóm `(e, ê, i)` |
| `yêu` | `iêu` | ✅ | vô hại, cùng nhóm |
| `uân` | `ân` | ✅ | ⚠️ **mất một phân biệt có chủ ý** |
| `ia` | `iê` | ❌ | cặp SD-2 `ia~uê` chết |
| `ua` | `uô` | ❌ | cặp SD-2 `o~ua` chết |

### 7.3. Chỗ phải quyết: `uân → ân`

Chú thích `CAP_VAN_THONG` ghi rõ: *"'ăn thông với ân' và 'ăn thông với uân' là hai câu rời
⇒ ân ≁ uân."* Chuẩn hoá ngữ âm bỏ âm đệm làm `uân` và `ân` thành một, tức là luận điểm
**không-bắc-cầu** — thứ cả mục §5 được xây quanh — bị bào mòn ở đúng một cặp.

| | Phương án | Đánh giá |
| --- | --- | --- |
| **A** | Tra `CAP_VAN_THONG` bằng `van` (còn âm đệm), so vần chính bằng `van_hiep` | Giữ được phân biệt. Hai khoá cho hai việc — phức tạp hơn, dễ lệch về sau. |
| **B** | Chấp nhận gập, ghi một mục `Đ` mới nói rõ SD-1 đã nuốt phân biệt này | Ít mã hơn, và **thành thật**: nếu đã chọn chuẩn hoá ngữ âm thì phải chịu hệ quả của nó. |

**Đề xuất B.** Lý do: A tạo ra hai định nghĩa "phần vần" cùng sống trong một file — đúng
cái bệnh mà `_PHU_AM_DAU` / `_AM_DAU` đang mắc (đã xác nhận hai bảng **trùng khít**). Thêm
một cặp khoá song song nữa là nhân đôi bệnh đó.

> **QĐ-9 (chờ chốt):** `hiep_van` so bằng `van_hiep` (âm chính + âm cuối, bỏ âm đệm). Chấp
> nhận `uân` gập vào `ân` và ghi thành quyết định Đ8. Hai cặp SD-2 `ia~uê`, `o~ua` được
> **khoá lại theo dạng đã chuẩn hoá** (`iê~ê`, `o~uô`) chứ không bỏ.

### 7.4. Việc bắt buộc kèm theo

1. **Chuẩn hoá khoá bảng bằng chính hàm đang dùng**, thay vì gõ tay — để bảng không thể
   lệch khỏi phép so vần:

   ```python
   def _khoa_van(k: str) -> str:      # chuẩn hoá một khoá của bảng vần thông
       return phan_tich_am_tiet(k).van_hiep
   ```

2. **Test ghim: mọi khoá trong `CAP_VAN_THONG` phải sinh ra được từ phép so vần đang
   dùng.** Chính test này, nếu có từ đầu, đã bắt được việc §5b không bao giờ được nối.
3. Xoá `_PHU_AM_DAU` (trùng khít `_AM_DAU`), sửa docstring `van_cua`.
4. ⚠️ `dataset.py` và `fewshot.py` **chạy lại** `kiem_tra_bai_tho` chứ không tin nhãn trong
   tệp — nên tập mẫu fewshot sẽ đổi theo. Phải chạy lại `doi_soat_ket_qua.py`.

**Nghiệm thu G4:**
- `hiep_van("hoa","ta")` = True; `hiep_van("gìn","nhìn")` vẫn True (không phá T8);
- ngữ liệu vàng của `test_van_gin.py` giữ nguyên toàn bộ kết quả cũ;
- đo lại 67.150: `bai_dat` **được phép tăng**, trần là +360 (tầng 5 chỉ chặn ngần ấy);
- hướng thay đổi phải một chiều — cặp đang hiệp **không được** mất, đúng như cách T8 đã
  lập luận ở §12.3. Nếu có cặp mất, dừng và xem lại.

---

## 8. Rủi ro

| # | Rủi ro | Phòng |
| --- | --- | --- |
| R1 | G4 làm đổi tập mẫu fewshot → chất lượng thơ sinh ra đổi mà không ai nối được nhân quả | G4 đi **một mình** một lượt băm; chạy `doi_soat_ket_qua.py` trước và sau |
| R2 | Gộp nhiều lỗi vào một lượt băm cho nhanh | Vi phạm tiền lệ T8. Mỗi giai đoạn một lượt, không thương lượng |
| R3 | Chốt QĐ-8 hoặc QĐ-9 theo hướng giữ lại nhiều bài hơn | N1: **không được** chọn phương án dựa trên số bài sống sót. Cả hai QĐ ở trên đều được đề xuất **trước khi** biết chúng giữ thêm bao nhiêu bài |
| R4 | G0 đỏ lâu ngày thành tiếng ồn, rồi bị tắt | Mỗi `xfail` mang lý do trỏ thẳng về giai đoạn sẽ gỡ nó |

---

## 9. Đường găng

```
G0  (test, không đổi băm)  ──┬─> G1 (L3, diễn tập quy trình)
                             │      └─> G2 (L2, đổi báo cáo)
                             │            └─> G3 (QĐ-8) ──> G4 (QĐ-9)
                             └─> [chủ dự án chốt QĐ-8, QĐ-9]  ──────┘
```

G0 và G1 chạy được **ngay**, không cần chờ quyết định nào. G3 chờ QĐ-8; G4 chờ QĐ-9.

---

## 10. Việc tiếp theo ngay

1. **Chủ dự án chốt QĐ-8** (§6.3 — đề xuất C) và **QĐ-9** (§7.3 — đề xuất B).
2. Trong lúc chờ: thi công **G0**, rồi **G1**.

## 11. Nghiệm thu toàn plan

- [ ] `bai_dat` sau G1, G2, G3 vẫn đúng **24.366** — ba giai đoạn ấy không được đổi phán quyết
- [ ] Sau G4, mọi thay đổi phán quyết đều **một chiều** và giải thích được bằng §7.2
- [ ] `doi_soat_tai_lieu.py` xanh sau mỗi lượt đổi băm
- [ ] Ba test G0 xanh hết, không còn `xfail`
- [ ] `Plan_Rule_Phan_Tang.md` có §13, §14, §15, §16 — mỗi giai đoạn một mục, theo khuôn §12
- [ ] `BAM_DA_CHOT` đổi đúng **bốn lần**, mỗi lần một lý do ghi trong chú thích của test
