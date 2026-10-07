import { goiBackend, traLoiLoi } from "../_backend";
import type { Conversation } from "@/types/api";

/**
 * §44 — danh sách và tạo hội thoại.
 *
 * Chuyển tiếp q/cursor xuống repository; giữ x-next-cursor cho trang kế tiếp.
 */
export async function GET(req: Request) {
  const params = new URL(req.url).searchParams;
  const query = new URLSearchParams();
  for (const name of ["q", "cursor", "limit"]) {
    const value = params.get(name);
    if (value !== null) query.set(name, value);
  }
  const kq = await goiBackend<Conversation[]>(`/v1/conversations?${query}`);
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data, {
    headers: kq.nextCursor ? { "x-next-cursor": kq.nextCursor } : {},
  });
}

export async function POST(req: Request) {
  const than = await req.json().catch(() => ({}));
  const kq = await goiBackend<Conversation>("/v1/conversations", {
    method: "POST",
    // Chỉ chuyển tiếp hai trường mình hiểu. Chuyển tiếp nguyên xi thân request
    // là để client gửi thêm trường tuỳ ý xuống backend.
    body: JSON.stringify({ tieu_de: than?.tieu_de ?? "", model: than?.model ?? "" }),
  });
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data);
}
