import { chuyenTiepSSE } from "../_backend";

/**
 * §43 — chuyển tiếp luồng chat.
 *
 * Đường backend là `/v1/chat`, KHÔNG phải `/api/chat` như §36 của tài liệu ghi.
 *
 * `req.signal` là mắt xích của chuỗi huỷ: trình duyệt huỷ → Next.js huỷ → FastAPI
 * thấy `is_disconnected()` và dừng sinh. Bỏ `signal` đi thì nút Stop vẫn làm chữ
 * ngừng hiện trên màn hình, nhưng backend VẪN sinh tiếp và vẫn tính tiền — người
 * dùng tưởng đã dừng.
 */
export async function POST(req: Request) {
  const than = await req.json().catch(() => null);
  if (!than) return Response.json({ detail: "Thân request không hợp lệ." }, { status: 400 });
  return chuyenTiepSSE("/v1/chat", { ...than, stream: true }, req.signal);
}
