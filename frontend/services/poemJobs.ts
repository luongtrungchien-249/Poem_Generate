import { LoiApi } from "./api";
import { laCanLamRo } from "@/types/api";
import type { KetQuaTho, PoemJob, PoemKhongDat, PoemResponse } from "@/types/api";

const terminal = new Set(["completed", "failed", "cancelled", "expired"]);
const storageKey = (session: string | null) => `poem-job:${session ?? "new"}`;
type JobRequest = Parameters<typeof import("./api").sinhTho>[0];

export function rememberJob(session: string | null, jobId: string, request?: JobRequest) {
  try {
    localStorage.setItem(storageKey(session), jobId);
    if (request) localStorage.setItem(`${storageKey(session)}:request`, JSON.stringify(request));
  } catch { /* optional browser persistence */ }
}

export function rememberedRequest(session: string | null): JobRequest | null {
  try { return JSON.parse(localStorage.getItem(`${storageKey(session)}:request`) ?? "null"); }
  catch { return null; }
}

export function rememberedJob(session: string | null): string | null {
  try { return localStorage.getItem(storageKey(session)); } catch { return null; }
}

export function forgetJob(session: string | null, jobId: string) {
  try {
    if (localStorage.getItem(storageKey(session)) === jobId) {
      localStorage.removeItem(storageKey(session));
      localStorage.removeItem(`${storageKey(session)}:request`);
    }
  } catch { /* optional browser persistence */ }
}

export async function cancelRememberedJob(session: string | null) {
  const id = rememberedJob(session);
  if (!id) return;
  const response = await fetch(`/api/poem/jobs/${encodeURIComponent(id)}`, { method: "DELETE" });
  if (!response.ok) throw new LoiApi("Không gửi được lệnh hủy tác vụ.", response.status);
}

async function fetchJob(id: string, signal: AbortSignal): Promise<PoemJob> {
  const res = await fetch(`/api/poem/jobs/${encodeURIComponent(id)}`, { signal, cache: "no-store" });
  if (!res.ok) throw new LoiApi("Không đọc được trạng thái tác vụ.", res.status);
  return res.json();
}

function resultOf(job: PoemJob): KetQuaTho {
  if (job.result) {
    if (job.result_status === 422) return { loai: "khong_dat", data: job.result as PoemKhongDat };
    if (laCanLamRo(job.result)) return { loai: "hoi_lai", data: job.result };
    return { loai: "tho", data: job.result as PoemResponse };
  }
  if (job.status === "cancelled") throw new DOMException("Đã dừng tác vụ.", "AbortError");
  throw new LoiApi(job.error ?? (job.status === "expired" ? "Tác vụ đã hết thời gian xử lý." : "Tác vụ thất bại."), 502);
}

function delay(ms: number, signal: AbortSignal): Promise<void> {
  return new Promise((resolve, reject) => {
    if (signal.aborted) { reject(new DOMException("Aborted", "AbortError")); return; }
    const timer = setTimeout(() => { signal.removeEventListener("abort", abort); resolve(); }, ms);
    const abort = () => { clearTimeout(timer); reject(new DOMException("Aborted", "AbortError")); };
    signal.addEventListener("abort", abort, { once: true });
  });
}

export async function watchJob(id: string, session: string | null, signal: AbortSignal,
                               onProgress: (job: PoemJob) => void): Promise<KetQuaTho> {
  let last: PoemJob | null = null;
  let stream: ReadableStreamDefaultReader<Uint8Array> | null = null;
  try {
    const response = await fetch(`/api/poem/jobs/${encodeURIComponent(id)}/events`, { signal });
    if (!response.ok || !response.body) throw new Error("SSE unavailable");
    stream = response.body.getReader();
    const decoder = new TextDecoder();
    let pending = "";
    while (!signal.aborted) {
      const { value, done } = await stream.read();
      if (done) break;
      pending += decoder.decode(value, { stream: true }).replace(/\r\n/g, "\n");
      let boundary: number;
      while ((boundary = pending.indexOf("\n\n")) >= 0) {
        const frame = pending.slice(0, boundary); pending = pending.slice(boundary + 2);
        const data = frame.split("\n").filter(line => line.startsWith("data:")).map(line => line.slice(5).trim()).join("\n");
        if (!data) continue;
        last = JSON.parse(data) as PoemJob;
        onProgress(last);
        if (terminal.has(last.status)) break;
      }
      if (last && terminal.has(last.status)) break;
    }
  } catch (error) {
    if (signal.aborted) throw error;
    // Disconnects fall back to polling; the SQL worker continues independently.
  } finally {
    await stream?.cancel().catch(() => {});
  }
  let interval = 1000;
  let failures = 0;
  while (!last || !terminal.has(last.status)) {
    if (signal.aborted) throw new DOMException("Aborted", "AbortError");
    try {
      last = await fetchJob(id, signal);
      failures = 0;
    } catch (error) {
      if (signal.aborted || (error instanceof LoiApi && error.status < 500) || ++failures >= 12) throw error;
      await delay(interval, signal);
      interval = Math.min(5000, interval * 1.5);
      continue;
    }
    onProgress(last);
    if (terminal.has(last.status)) break;
    await delay(interval, signal);
    interval = Math.min(5000, interval * 1.5);
  }
  forgetJob(session, id);
  return resultOf(last);
}

export async function sinhThoJob(body: Parameters<typeof import("./api").sinhTho>[0],
                                 signal: AbortSignal, onProgress: (job: PoemJob) => void): Promise<KetQuaTho> {
  // Admission is short and deliberately not tied to view cancellation. Persist
  // its ID even if navigation occurred while the server was accepting the job.
  const key = crypto.randomUUID();
  let response: Response | null = null;
  for (let attempt = 0; attempt < 2; attempt++) {
    try {
      response = await fetch("/api/poem/jobs", {
        method: "POST", headers: { "content-type": "application/json", "idempotency-key": key },
        body: JSON.stringify(body),
      });
      break;
    } catch (error) { if (attempt === 1) throw error; }
  }
  if (!response) throw new Error("Admission failed");
  const job = await response.json();
  if (!response.ok) throw new LoiApi(job.detail ?? "Không tạo được tác vụ.", response.status);
  rememberJob(body.session_id ?? null, job.job_id, body);
  if (signal.aborted && signal.reason === "cancel-job") {
    await cancelRememberedJob(body.session_id ?? null);
    forgetJob(body.session_id ?? null, job.job_id);
    throw new DOMException("Đã dừng tác vụ.", "AbortError");
  }
  if (signal.aborted) throw new DOMException("Aborted", "AbortError");
  onProgress(job);
  return watchJob(job.job_id, body.session_id ?? null, signal, onProgress);
}
