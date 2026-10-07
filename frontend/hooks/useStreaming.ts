"use client";

import type { ChatStreamEvent } from "@/types/api";

/**
 * Đọc luồng SSE của `/api/chat`.
 *
 * VÌ SAO KHÔNG DÙNG `EventSource`: `EventSource` chỉ gửi được GET và không đặt
 * được header hay thân request. Luồng chat cần POST với danh sách tin nhắn, nên
 * phải tự đọc `fetch().body`.
 *
 * ĐỆM DÒNG: một mẩu TCP có thể cắt ngang giữa một dòng `data: {...}`, nên không
 * được phân giải JSON theo từng mẩu nhận được. Phần đuôi chưa trọn dòng phải giữ
 * lại chờ mẩu sau. Bỏ qua điều này thì lỗi chỉ xuất hiện khi mạng chậm hoặc câu
 * trả lời dài — tức là đúng lúc khó tái hiện nhất.
 */

export interface TayCam {
  onDelta: (chu: string) => void;
  /** Rào chắn chặn GIỮA luồng: phần chữ đã hiện phải bị THU HỒI, không chỉ dừng. */
  onBiChan: (lyDo: string, traceId?: string) => void;
  onXong: (traceId?: string) => void;
  onLoi: (thongBao: string) => void;
}

export async function docLuongSSE(
  than: unknown,
  signal: AbortSignal,
  tay: TayCam,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch("/api/chat", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(than),
      signal,
    });
  } catch (e) {
    if ((e as Error)?.name === "AbortError") return;
    tay.onLoi("Không gửi được yêu cầu.");
    return;
  }

  if (!res.ok || !res.body) {
    const t = await res.text().catch(() => "");
    let chiTiet = `Máy chủ trả về ${res.status}.`;
    try {
      chiTiet = JSON.parse(t)?.detail ?? chiTiet;
    } catch {
      /* thân không phải JSON — giữ thông báo mặc định */
    }
    tay.onLoi(chiTiet);
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let dem = "";
  let traceId: string | undefined;

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      dem += decoder.decode(value, { stream: true });
      const dong = dem.split("\n");
      // Phần tử cuối có thể là một dòng CHƯA TRỌN — giữ lại cho vòng sau.
      dem = dong.pop() ?? "";

      for (const raw of dong) {
        const d = raw.trim();
        if (!d.startsWith("data:")) continue;
        const payload = d.slice(5).trim();
        if (payload === "[DONE]") {
          tay.onXong(traceId);
          return;
        }

        let sk: ChatStreamEvent;
        try {
          sk = JSON.parse(payload) as ChatStreamEvent;
        } catch {
          continue;
        }

        if (sk.trace_id) traceId = sk.trace_id;

        if (sk.finish_reason === "blocked_by_guardrail") {
          tay.onBiChan(sk.error ?? "Nội dung bị rào chắn chặn.", traceId);
          return;
        }
        if (sk.delta) tay.onDelta(sk.delta);

        // ⚠️ `finish_reason` KHÔNG phải dấu chấm hết — chỉ `[DONE]` mới là.
        //
        // Đo được trên luồng thật: rào chắn đầu ra giữ chữ lại trong một cửa sổ
        // đệm rồi mới xả ở bước kết thúc, nên thứ tự sự kiện là
        //
        //     {"delta": "", "finish_reason": "stop"}      ← báo kết thúc TRƯỚC
        //     {"delta": "Chào bạn!…", "finish_reason": null}  ← chữ đến SAU
        //     [DONE]
        //
        // Dừng đọc ở sự kiện đầu tiên thì toàn bộ câu trả lời bị bỏ lại trên
        // đường truyền và người dùng nhìn thấy một ô trống.
        //
        // `[DONE]` là dấu kết thúc chuẩn của SSE và là thứ duy nhất đáng tin ở
        // đây; ghi lại `finish_reason` để dùng, nhưng không dừng vì nó.
      }
    }
    tay.onXong(traceId);
  } catch (e) {
    if ((e as Error)?.name === "AbortError") return;
    tay.onLoi("Kết nối bị gián đoạn.");
  } finally {
    reader.releaseLock();
  }
}
