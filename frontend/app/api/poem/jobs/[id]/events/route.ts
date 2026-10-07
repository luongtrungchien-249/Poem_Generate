import { chuyenTiepSSE } from "../../../../_backend";

export async function GET(req: Request, context: { params: Promise<{ id: string }> }) {
  const { id } = await context.params;
  return chuyenTiepSSE(`/v1/poem/jobs/${encodeURIComponent(id)}/events`, null, req.signal, "GET");
}
