import { goiBackend, traLoiLoi } from "../../_backend";

export async function POST(req: Request) {
  const body = await req.json().catch(() => null);
  if (!body?.yeu_cau) return Response.json({ detail: "Thiếu nội dung yêu cầu." }, { status: 400 });
  const headers: Record<string, string> = {};
  const key = req.headers.get("idempotency-key");
  if (key) headers["idempotency-key"] = key;
  const result = await goiBackend("/v1/poem/jobs", {
    method: "POST", headers, body: JSON.stringify(body),
  });
  if (!result.ok) return traLoiLoi(result);
  return Response.json(result.data, { status: 202 });
}

export async function GET(req: Request) {
  const conversation = new URL(req.url).searchParams.get("conversation_id") ?? "";
  const result = await goiBackend(`/v1/poem/jobs?conversation_id=${encodeURIComponent(conversation)}`);
  if (!result.ok) return traLoiLoi(result);
  return Response.json(result.data);
}
