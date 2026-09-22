/**
 * Lớp gọi API — nơi DUY NHẤT trong mã client biết hình dạng của mạng.
 *
 * Mọi đường đều là SAME-ORIGIN `/api/...`, không phải URL của FastAPI. Trình
 * duyệt không biết backend nằm ở đâu và không giữ khoá nào — xem `app/api/_backend.ts`.
 */

import type {
  CanLamRo,
  Conversation,
  ConversationDetail,
  ModelInfo,
  PoemKhongDat,
  PoemResponse,
  KetQuaTho,
} from "@/types/api";
import { laCanLamRo } from "@/types/api";

export class LoiApi extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "LoiApi";
  }
}

async function lay<T>(duong: string, init?: RequestInit): Promise<T> {
  const res = await fetch(duong, init);
  const text = await res.text();
  const body = text ? JSON.parse(text) : null;
  if (!res.ok) {
    throw new LoiApi(body?.detail ?? `Yêu cầu thất bại (${res.status}).`, res.status);
  }
  return body as T;
}

// ── §45 ─────────────────────────────────────────────────────────────────────
export const layDanhSachModel = () => lay<ModelInfo[]>("/api/models");

// ── §44 ─────────────────────────────────────────────────────────────────────
export const layDanhSachHoiThoai = (q = "") =>
  lay<Conversation[]>(`/api/conversations${q ? `?q=${encodeURIComponent(q)}` : ""}`);

export const taoHoiThoai = (tieu_de = "", model = "") =>
  lay<Conversation>("/api/conversations", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ tieu_de, model }),
  });

export const layHoiThoai = (id: string) =>
  lay<ConversationDetail>(`/api/conversations/${encodeURIComponent(id)}`);

export const doiTenHoiThoai = (id: string, tieu_de: string) =>
  lay<Conversation>(`/api/conversations/${encodeURIComponent(id)}`, {
    method: "PATCH",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ tieu_de }),
  });

export const xoaHoiThoai = (id: string) =>
  lay<{ da_xoa: boolean }>(`/api/conversations/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });

// ── Thơ ─────────────────────────────────────────────────────────────────────
/**
 * Gộp ba mã trạng thái về một kiểu có nhãn, thay vì ném lỗi cho 422.
 *
 * 422 KHÔNG được ném: nó không phải sự cố, nó là hệ thống từ chối trả bài sai
 * luật. Ném nó ra nhánh `catch` chung sẽ làm UI hiện thông báo lỗi đỏ cho một
 * hành vi đúng.
 */
export async function sinhTho(than: {
  yeu_cau: string;
  chu_de?: string | null;
  so_dong?: number | null;
  session_id?: string | null;
}): Promise<KetQuaTho> {
  const res = await fetch("/api/poem", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(than),
  });
  const text = await res.text();
  const body = text ? JSON.parse(text) : null;

  if (res.status === 422) return { loai: "khong_dat", data: body as PoemKhongDat };
  if (!res.ok) throw new LoiApi(body?.detail ?? "Sinh thơ thất bại.", res.status);
  if (laCanLamRo(body)) return { loai: "hoi_lai", data: body as CanLamRo };
  return { loai: "tho", data: body as PoemResponse };
}
