import { goiBackend, traLoiLoi } from "../_backend";
import type { Conversation } from "@/types/api";

/**
 * §44 — danh sách và tạo hội thoại.
 *
 * TÌM KIẾM (§44 "Search conversation") được lọc Ở ĐÂY, không ở backend: backend
 * chỉ có tham số `limit`, chưa có tìm kiếm. Lọc phía máy chủ Next.js là bản tạm
 * chấp nhận được khi số hội thoại còn nhỏ, nhưng nó KHÔNG mở rộng được — nó tải
 * về `limit` bản rồi mới lọc, nên thứ nằm ngoài `limit` sẽ không bao giờ tìm thấy.
 * Khi cần đúng, thêm tham số `q` vào `GET /v1/conversations` phía backend.
 */
export async function GET(req: Request) {
  const q = new URL(req.url).searchParams.get("q")?.trim().toLowerCase() ?? "";
  const kq = await goiBackend<Conversation[]>("/v1/conversations?limit=200");
  if (!kq.ok) return traLoiLoi(kq);
  const ds = q
    ? kq.data.filter((c) => (c.tieu_de || "").toLowerCase().includes(q))
    : kq.data;
  return Response.json(ds);
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
