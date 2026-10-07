import { goiBackend, traLoiLoi } from "../../../_backend";

type Context = { params: Promise<{ id: string }> };

export async function GET(_req: Request, context: Context) {
  const { id } = await context.params;
  const result = await goiBackend(`/v1/poem/jobs/${encodeURIComponent(id)}`);
  if (!result.ok) return traLoiLoi(result);
  return Response.json(result.data);
}

export async function DELETE(_req: Request, context: Context) {
  const { id } = await context.params;
  const result = await goiBackend(`/v1/poem/jobs/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!result.ok) return traLoiLoi(result);
  return Response.json(result.data);
}
