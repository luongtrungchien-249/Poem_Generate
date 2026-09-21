import { goiBackend, traLoiLoi } from "../_backend";
import type { ModelInfo } from "@/types/api";

/**
 * §45 · §10 — danh mục model.
 *
 * Tài liệu §10 liệt kê cứng "Gemma 4 / GPT / Claude / Gemini / Local LLM". Cấu
 * hình thật (`configs/models.yaml`) có 8 model và KHÔNG có Gemma, KHÔNG có
 * Gemini. Một danh sách chép tay sẽ mời người dùng chọn model mà backend không
 * định tuyến được, nên ở đây lấy thẳng từ `/v1/models`.
 */
export async function GET() {
  const kq = await goiBackend<ModelInfo[]>("/v1/models");
  if (!kq.ok) return traLoiLoi(kq);
  return Response.json(kq.data);
}
