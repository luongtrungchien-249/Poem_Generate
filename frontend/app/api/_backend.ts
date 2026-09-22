/**
 * ════════════════════════════════════════════════════════════════════════════
 * BFF — NƠI DUY NHẤT BIẾT KHOÁ API
 * ════════════════════════════════════════════════════════════════════════════
 *
 * Vì sao tồn tại lớp này thay vì cho trình duyệt gọi thẳng FastAPI:
 *
 * Backend xác thực bằng header `x-api-key`, và khoá đó QUYẾT ĐỊNH TENANT — nó
 * không chỉ mở cửa, nó nói người gọi là ai. Nếu trình duyệt gọi thẳng, khoá phải
 * nằm trong JavaScript tải về máy người dùng. Không có cách nào giấu nó ở đó:
 * minify, mã hoá, tách file — tất cả đều bị đọc lại được, vì trình duyệt phải
 * giải mã ra mới gửi đi. Ai mở DevTools cũng lấy được khoá, và lấy được khoá là
 * đọc được TOÀN BỘ dữ liệu của tenant đó.
 *
 * Nên đường đi là:
 *
 *     Trình duyệt ──(same-origin, không khoá)──> Next.js ──(x-api-key)──> FastAPI
 *                                                   └─ khoá dừng ở đây
 *
 * Hệ quả bắt buộc: Next.js phải chạy như một máy chủ. `output: "export"` không
 * dùng được — xem `next.config.ts`.
 */

import "server-only";

const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
const BACKEND_API_KEY = process.env.BACKEND_API_KEY ?? "";

function headersChoBackend(them?: HeadersInit): Headers {
  const h = new Headers(them);
  // Khoá rỗng = backend đang chạy chế độ dev không bật xác thực. Gửi một header
  // rỗng sẽ bị từ chối, nên khi không có khoá thì KHÔNG gửi header nào cả.
  if (BACKEND_API_KEY) h.set("x-api-key", BACKEND_API_KEY);
  return h;
}

/**
 * Nhánh lỗi giữ LẠI thân đã phân giải (`body`), không chỉ một chuỗi `detail`.
 *
 * Vì một số lỗi của backend là dữ liệu có cấu trúc chứ không phải thông báo:
 * `422` của đường sinh thơ mang `so_luot_da_sua`, `chan_doan`, `trace_id` — ép
 * nó về chuỗi là vứt bỏ đúng những thứ UI cần để giải thích cho người dùng.
 */
export type KetQua<T> =
  | { ok: true; data: T }
  | { ok: false; status: number; detail: string; body: unknown };

/** Gọi backend và trả JSON đã phân giải. Không bao giờ ném ra ngoài. */
export async function goiBackend<T>(
  duong: string,
  init?: RequestInit,
): Promise<KetQua<T>> {
  let res: Response;
  try {
    res = await fetch(`${BACKEND_URL}${duong}`, {
      ...init,
      headers: headersChoBackend({
        "content-type": "application/json",
        ...(init?.headers ?? {}),
      }),
      cache: "no-store",
    });
  } catch {
    // Backend chưa chạy hoặc mạng hỏng. 502 chứ không phải 500: lỗi nằm ở
    // thượng nguồn, và phân biệt hai cái đó giúp người đọc log biết tìm ở đâu.
    return { ok: false, status: 502, detail: "Không kết nối được tới backend.", body: null };
  }

  const text = await res.text();
  let body: unknown = null;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = null;
  }

  if (!res.ok) {
    const detail =
      (body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : "") || `Backend trả về ${res.status}.`;
    return { ok: false, status: res.status, detail, body };
  }
  return { ok: true, data: body as T };
}

/**
 * Chuyển tiếp một luồng SSE từ backend ra trình duyệt.
 *
 * `duplex: "half"` là bắt buộc khi thân request là stream — thiếu nó thì Node
 * từ chối. `signal` nối vào request của trình duyệt: khi người dùng bấm Stop,
 * trình duyệt huỷ kết nối, việc huỷ lan tới đây, rồi lan tiếp tới FastAPI —
 * và FastAPI dừng sinh nhờ `raw_request.is_disconnected()`. Cả chuỗi dừng từ
 * một cú bấm, không cần endpoint `/stop` nào.
 */
export async function chuyenTiepSSE(
  duong: string,
  than: unknown,
  signal: AbortSignal,
): Promise<Response> {
  let res: Response;
  try {
    res = await fetch(`${BACKEND_URL}${duong}`, {
      method: "POST",
      headers: headersChoBackend({ "content-type": "application/json" }),
      body: JSON.stringify(than),
      signal,
      cache: "no-store",
    });
  } catch {
    return Response.json({ detail: "Không kết nối được tới backend." }, { status: 502 });
  }

  if (!res.ok || !res.body) {
    const text = await res.text().catch(() => "");
    return Response.json(
      { detail: text || `Backend trả về ${res.status}.` },
      { status: res.ok ? 502 : res.status },
    );
  }

  return new Response(res.body, {
    headers: {
      "content-type": "text/event-stream; charset=utf-8",
      "cache-control": "no-cache, no-transform",
      connection: "keep-alive",
      // Tắt đệm ở reverse proxy. Thiếu dòng này thì nginx gom cả luồng lại rồi
      // mới trả một lần — người dùng ngồi nhìn màn hình trống suốt thời gian sinh.
      "x-accel-buffering": "no",
    },
  });
}

export function traLoiLoi(kq: { status: number; detail: string }): Response {
  return Response.json({ detail: kq.detail }, { status: kq.status });
}
