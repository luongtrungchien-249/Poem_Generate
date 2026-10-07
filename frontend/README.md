# Frontend — Thơ thất ngôn

Giao diện web cho hệ sinh thơ thất ngôn. Next.js (App Router) + Tailwind v4 + Zustand.

## Chạy

Cần backend FastAPI chạy trước:

```bash
# từ thư mục gốc dự án
PYTHONPATH=src python -m uvicorn entrypoints.api.app:app --port 8000
```

Rồi:

```bash
cd frontend
cp .env.example .env.local     # sửa BACKEND_URL / BACKEND_API_KEY nếu cần
npm install
npm run dev                    # http://localhost:3000
```

Kiểm tra frontend còn khớp hợp đồng backend (cần backend đang chạy):

```bash
npm run gen:types
```

## Ba điều cần biết trước khi sửa

### 1. Khoá API không bao giờ ra tới trình duyệt

Mọi lệnh gọi đi qua `app/api/*` — route handler chạy phía máy chủ Next.js. Đó là
nơi duy nhất đọc `BACKEND_API_KEY`. Trình duyệt chỉ gọi same-origin `/api/...` và
không biết backend nằm ở đâu.

Backend xác thực bằng `x-api-key`, và khoá đó **quyết định tenant** — nó không chỉ
mở cửa, nó nói người gọi là ai. Cho trình duyệt gọi thẳng FastAPI nghĩa là nhúng
khoá vào JavaScript tải về máy người dùng; ai mở DevTools cũng lấy được, và lấy
được khoá là đọc được toàn bộ dữ liệu của tenant.

Hệ quả: **không dùng được `output: "export"`**, và không đặt gì nhạy cảm vào biến
`NEXT_PUBLIC_*` (mọi biến có tiền tố đó đều nằm trong bundle client).

### 2. Có bốn trạng thái ngoài "đang chạy / xong / lỗi"

Xem `lib/types.ts` và `components/states/StateCards.tsx`.

| Trạng thái | Backend trả gì | Hiển thị |
|---|---|---|
| `hoi_lai` | HTTP **200** + `can_lam_ro: true` | Thẻ xanh, kèm nút gợi ý số dòng |
| `khong_dat` | HTTP **422** + `chan_doan` | Thẻ vàng, **không có bài thơ** |
| `cho_duyet` | `quyet_dinh_hitl === "HUMAN_REVIEW"` | Dải thông báo, bài vẫn hiện |
| `bi_chan` | `finish_reason: "blocked_by_guardrail"` giữa luồng SSE | Thẻ vàng, **thu hồi chữ đã hiện** |

Chỉ `loi` mới được dùng màu đỏ. Ba cái còn lại là hệ thống đang làm đúng việc của
nó — tô đỏ chúng là nói với người dùng rằng có gì đó hỏng.

`bi_chan` là ca dễ làm sai nhất: nó xảy ra **sau khi** chữ đã hiện ra màn hình, nên
UI phải xoá phần đã hiện chứ không chỉ ngừng nối thêm. Giữ lại phần đó kèm một dòng
cảnh báo là phá bỏ chính lý do rào chắn tồn tại — người dùng sẽ chép nó đi dùng, và
dòng cảnh báo không đi theo.

### 3. Luồng thơ không stream từng chữ

Không thể phát dần một bài thơ rồi mới phát hiện nó sai luật — chữ đã ra rồi. Nên:

- **chế độ "Trò chuyện"** → SSE, chữ chảy dần, có con trỏ nhấp nháy
- **chế độ "Làm thơ"** → chỉ hiện **tiến trình** (`components/poem/PoemEvidence.tsx`),
  bài thơ xuất hiện một lần sau khi qua đủ bảy tầng

Tiến trình đó là **ước lượng**, không phải sự kiện thật: `/v1/poem` trả về một lần,
không stream. Nó cố ý không hứa thời gian — sinh thơ là best-of-16 mỗi khổ nên lâu
hơn hẳn một lượt chat, và một thanh tiến trình giả sẽ nói dối về điều đó.

## Ba token màu đã đổi so với `docs/FRONTEND_PLAN.md`

Bảng màu gốc có ba token trượt WCAG AA. Số đo:

| Token gốc | Tỷ lệ tương phản | Thay bằng |
|---|---|---|
| `#EC4899` làm chữ/nút | 3.53:1 (cần 4.5) | `#DB2777` → 4.60:1 |
| `#9A929D` text muted | 3.01:1 | `#76707A` → 4.81:1 |
| `#F1E8EE` viền ô nhập | 1.20:1 (cần 3.0) | `#A18A98` → 3.18:1 |

`#EC4899` **vẫn được giữ** cho mảng nền và viền, nơi ngưỡng chỉ là 3:1 — nên cảm
giác thị giác của §5 (hồng 10–20%) không đổi. `#F1E8EE` vẫn dùng làm đường phân
cách trang trí (`--color-divider`), tách khỏi viền của thành phần tương tác
(`--color-border`).

Dark mode của tài liệu đạt hết ngưỡng, giữ nguyên.

## Những gì backend làm thay bạn

Khi frontend gửi `session_id = conversation_id`, backend tự lo ba việc — bạn không
cần gọi thêm endpoint nào:

1. **Lưu lượt hỏi–đáp** vào hội thoại (cả đường thơ lẫn đường chat).
2. **Đặt tiêu đề** từ câu hỏi đầu tiên, nếu hội thoại chưa có tên. Tên do bạn tự
   đặt sẽ không bị ghi đè.
3. **Đẩy hội thoại lên đầu sidebar** bằng cách làm mới `cap_nhat_luc`.

Bài thơ trượt luật vẫn ghi CÂU HỎI với câu trả lời rỗng — giấu nó đi sẽ tạo một
khoảng trống khó hiểu khi mở lại hội thoại.

## Một cái bẫy trong luồng SSE

`finish_reason` **không** phải dấu chấm hết. Đo được trên luồng thật:

```
{"delta": "", "finish_reason": "stop"}           ← báo kết thúc TRƯỚC
{"delta": "Chào bạn!…", "finish_reason": null}   ← chữ đến SAU
[DONE]
```

Rào chắn đầu ra giữ chữ trong một cửa sổ đệm rồi mới xả ở bước kết thúc. Client
dừng đọc ở sự kiện đầu tiên sẽ hiện một ô trống. Chỉ `[DONE]` mới là dấu kết thúc
đáng tin — xem `hooks/useStreaming.ts`.

## Chưa làm

- **Upload file** (§46) — backend chỉ nhận JSON có sẵn `content` dạng text, chưa có
  `multipart`, chưa trích xuất PDF. UI cho việc này sẽ là giao diện cho thứ không
  tồn tại.
- **Projects** (§11) — không có bảng và không có endpoint nào ở backend.
- **Tìm kiếm hội thoại** — đang lọc ở `app/api/conversations/route.ts`, tức là tải
  200 bản về rồi mới lọc. Không mở rộng được; cần tham số `q` ở backend.
- **Settings, Profile** (§48, §53) — chưa có.
