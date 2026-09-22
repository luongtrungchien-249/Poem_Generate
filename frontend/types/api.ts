/**
 * Kiểu ánh xạ hợp đồng HTTP của backend.
 *
 * ⚠️ File này phải KHỚP với `/openapi.json`. Chạy `npm run gen:types` để đối
 * chiếu — script sẽ báo nếu backend đã đổi hợp đồng mà file này chưa theo kịp.
 * Gõ tay rồi để lệch thì TypeScript vẫn biên dịch xanh và hỏng lúc chạy, vì
 * TypeScript không biết gì về dữ liệu đến từ mạng.
 */

// ── §45 Model ───────────────────────────────────────────────────────────────
export interface ModelInfo {
  ten: string;
  provider: string;
  tier: string;
  context_window: number;
  max_output_tokens: number;
}

// ── §44 Hội thoại ───────────────────────────────────────────────────────────
export interface Conversation {
  conversation_id: string;
  tieu_de: string;
  model: string;
  tao_luc: string;
  cap_nhat_luc: string;
  so_tin_nhan: number;
}

export type Role = "system" | "user" | "assistant";

export interface BackendMessage {
  role: Role;
  content: string;
}

export interface ConversationDetail extends Conversation {
  tin_nhan: BackendMessage[];
}

// ── Sự kiện SSE của `/v1/chat` ──────────────────────────────────────────────
/**
 * `finish_reason === "blocked_by_guardrail"` là trạng thái mà §37 của tài liệu
 * KHÔNG có: rào chắn chặn GIỮA luồng, sau khi chữ đã hiện ra màn hình. UI phải
 * thu hồi phần đã hiện, không chỉ ngừng nối thêm.
 */
export interface ChatStreamEvent {
  delta: string;
  finish_reason: string | null;
  trace_id?: string;
  error?: string;
  citation_ids?: string[] | null;
}

// ── Thơ: ba kết quả, ba hình dạng khác nhau ─────────────────────────────────
export interface BangChungTang {
  tang: number;
  ten: string;
  ma_luat: string[];
  muc: string;
  /** `false` = tầng CHƯA ĐƯỢC KIỂM vì tầng trước đã chặn — không phải "đã đạt". */
  da_chay: boolean;
  dat: boolean;
  trich_luat: string;
  bang_chung: string;
  chi_tiet: Record<string, unknown>;
}

export interface BangChungChieu {
  ma: string;
  ten: string;
  /** `false` → `dat` không mang ý nghĩa gì, đừng vẽ dấu tích. */
  do_duoc: boolean;
  dat: boolean;
  so_do: number | null;
  nguong: string;
  bang_chung: string;
}

export type QuyetDinhHitl =
  | "AUTO_RESPOND"
  | "HUMAN_REVIEW"
  | "ASK_USER"
  | "REJECT";

export interface PoemResponse {
  poem: string;
  dat: boolean;
  thuoc_the: boolean;
  dat_luat: boolean;
  dat_chat_luong: boolean;
  so_dong: number;
  so_kho: number;
  so_luot_sua: number;
  chien_luoc_cuoi: string | null;
  bang_chung_bay_tang: BangChungTang[];
  chat_luong: BangChungChieu[];
  so_do_van: string[];
  ghi_chu: string[];
  quyet_dinh_hitl: QuyetDinhHitl;
  ly_do_hitl: string;
  duong_di: string[];
  che_do_vi_du: string;
  id_vi_du: string[];
  trace_id: string;
}

/** HTTP 200 — KHÔNG phải lỗi. Người dùng không làm gì sai; hệ thống hỏi lại. */
export interface CanLamRo {
  can_lam_ro: true;
  ca: number;
  cau_hoi: string;
  ly_do: string;
  truong_thieu: string[];
  duong_di: string[];
  trace_id: string;
}

/** HTTP 422 — cố ý KHÔNG có trường nào chứa văn bản thơ. */
export interface PoemKhongDat {
  ma_the: string;
  so_luot_da_sua: number;
  chan_doan: string;
  trace_id: string;
}

export interface PoemRequest {
  yeu_cau: string;
  chu_de?: string | null;
  so_dong?: number | null;
  cam_xuc?: string | null;
  phong_cach?: string | null;
  max_repair_rounds?: number;
  session_id?: string | null;
}

/** Kết quả của một lượt sinh thơ, đã gộp cả ba mã trạng thái về một kiểu. */
export type KetQuaTho =
  | { loai: "tho"; data: PoemResponse }
  | { loai: "hoi_lai"; data: CanLamRo }
  | { loai: "khong_dat"; data: PoemKhongDat };

export function laCanLamRo(x: unknown): x is CanLamRo {
  return !!x && typeof x === "object" && (x as CanLamRo).can_lam_ro === true;
}
