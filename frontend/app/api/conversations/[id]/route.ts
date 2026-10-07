import { goiBackend, traLoiLoi } from "../../_backend";
import type { Conversation, ConversationDetail } from "@/types/api";

type Ctx = { params: Promise<{ id: string }> };

export async function GET(_req: Request, { params }: Ctx) {
  const { id } = await params;
  const kq = await goiBackend<ConversationDetail>(
    `/v1/conversations/${encodeURIComponent(id)}`,
  );
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data);
}

export async function PATCH(req: Request, { params }: Ctx) {
  const { id } = await params;
  const than = await req.json().catch(() => ({}));
  const kq = await goiBackend<Conversation>(
    `/v1/conversations/${encodeURIComponent(id)}`,
    { method: "PATCH", body: JSON.stringify({ tieu_de: than?.tieu_de, model: than?.model }) },
  );
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data);
}

export async function DELETE(_req: Request, { params }: Ctx) {
  const { id } = await params;
  const kq = await goiBackend<{ da_xoa: boolean }>(
    `/v1/conversations/${encodeURIComponent(id)}`,
    { method: "DELETE" },
  );
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data);
}
