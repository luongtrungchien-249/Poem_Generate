"use client";

import {
  AlertTriangle,
  HelpCircle,
  RefreshCw,
  ScrollText,
  ShieldAlert,
  UserCheck,
} from "lucide-react";
import type { CanLamRo, PoemKhongDat } from "@/types/api";

/**
 * ════════════════════════════════════════════════════════════════════════════
 * BỐN TRẠNG THÁI KHÔNG CÓ TRONG §37 CỦA TÀI LIỆU
 * ════════════════════════════════════════════════════════════════════════════
 *
 * Nguyên tắc chung cho cả bốn: CHỈ `loi` mới được dùng màu đỏ.
 *
 * Ba cái còn lại — hỏi lại, không đạt, chờ duyệt — là hệ thống đang làm ĐÚNG
 * việc của nó. Tô đỏ chúng là nói với người dùng rằng có gì đó hỏng, trong khi
 * thứ vừa xảy ra là một quyết định có chủ ý.
 *
 * §29 cũng cấm dùng màu làm tín hiệu duy nhất, nên mỗi thẻ đều có biểu tượng và
 * một nhãn bằng chữ, không chỉ khác nhau ở màu viền.
 */

function Khung({
  mau,
  icon,
  nhan,
  children,
}: {
  mau: string;
  icon: React.ReactNode;
  nhan: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className="anim-slide-up rounded-[var(--radius-card)] border p-4"
      style={{ borderColor: mau, background: "var(--color-surface-2)" }}
    >
      <div className="mb-2 flex items-center gap-2 text-sm font-semibold" style={{ color: mau }}>
        {icon}
        <span>{nhan}</span>
      </div>
      {children}
    </div>
  );
}

/** §30.1 — chưa đủ thông tin. HTTP 200: người dùng KHÔNG làm gì sai. */
export function TheHoiLai({
  data,
  onChon,
}: {
  data: CanLamRo;
  onChon: (traLoi: string, dat?: { so_dong?: number; chu_de?: string }) => void;
}) {
  // Ca 5 = thiếu số dòng. Số dòng phải là bội của 4 (H4, luật cứng), nên gợi ý
  // sẵn vài lựa chọn hợp lệ thay vì để người dùng đoán rồi bị hỏi lại lần nữa.
  const goiYSoDong = data.truong_thieu.includes("so_dong") || data.ca === 5;
  const canChuDe = data.truong_thieu.includes("chu_de");

  return (
    <Khung
      mau="var(--color-info)"
      icon={<HelpCircle size={16} aria-hidden />}
      nhan="Cần làm rõ thêm"
    >
      <p className="text-[15px]">{data.cau_hoi}</p>
      {data.ly_do && (
        <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-secondary)" }}>
          {data.ly_do}
        </p>
      )}

      {goiYSoDong && (
        <div className="mt-3 flex flex-wrap gap-2">
          {[8, 12, 16, 20].map((n) => (
            <button
              key={n}
              // Gửi kèm GIÁ TRỊ SỐ, không chỉ chữ: bấm nút là biết chắc người
              // dùng muốn gì, nên không cần backend đoán lại từ câu chữ — và
              // trường gửi tường minh mang nguồn `nguoi_dung`, thứ duy nhất
              // khiến hệ thống thôi hỏi xác nhận.
              onClick={() => onChon(`${n} dòng`, { so_dong: n })}
              className="rounded-[var(--radius-btn)] border px-3 py-1.5 text-sm transition-transform hover:scale-[1.02]"
              style={{ borderColor: "var(--color-border)" }}
            >
              {n} dòng
            </button>
          ))}
        </div>
      )}
      <p className="mt-3 text-[12px]" style={{ color: "var(--color-text-muted)" }}>
        {/* Backend hỏi "xác nhận chu_de" nhưng KHÔNG nói nó đang đoán là gì, nên
            câu hỏi đó không trả lời được bằng "đúng rồi". Chỉ cách làm cho người
            dùng thoát ra: nói lại chủ đề bằng lời của họ — khi đó nó được gửi
            vào trường tường minh và mang nguồn `nguoi_dung`. */}
        {canChuDe
          ? "Gõ lại chủ đề bằng lời của bạn để xác nhận — yêu cầu cũ vẫn được giữ."
          : "Trả lời ngay bên dưới cũng được — yêu cầu cũ vẫn được giữ."}
      </p>
    </Khung>
  );
}

/** §30.2 — trượt kiểm luật. Response KHÔNG chứa bài thơ, và đó là chủ ý. */
export function TheKhongDat({
  data,
  onThuLai,
}: {
  data: PoemKhongDat;
  onThuLai: () => void;
}) {
  return (
    <Khung
      mau="var(--color-warning)"
      icon={<ScrollText size={16} aria-hidden />}
      nhan="Chưa đạt luật — bài thơ không được trả về"
    >
      <p className="text-[15px]">
        Hệ thống đã sửa {data.so_luot_da_sua} lượt nhưng bài vẫn chưa đúng luật, nên
        nó không trả bài ra.
      </p>
      {data.chan_doan && (
        <pre
          className="scroll-thin mt-3 max-h-56 overflow-auto whitespace-pre-wrap rounded-[10px] border p-3 text-[13px] leading-relaxed"
          style={{
            borderColor: "var(--color-divider)",
            background: "var(--color-surface)",
            fontFamily: "var(--font-mono)",
          }}
        >
          {data.chan_doan}
        </pre>
      )}
      <div className="mt-3 flex items-center gap-3">
        <button
          onClick={onThuLai}
          className="inline-flex items-center gap-1.5 rounded-[var(--radius-btn)] px-3.5 py-2 text-sm font-medium text-white transition-transform hover:scale-[1.02] active:scale-[0.98]"
          style={{ background: "var(--color-pink-600)" }}
        >
          <RefreshCw size={14} aria-hidden />
          Thử lại
        </button>
        <span className="text-[12px]" style={{ color: "var(--color-text-muted)" }}>
          Mỗi lần thử là một lượt sinh mới.
        </span>
      </div>
      {data.trace_id && <MaDoiChieu id={data.trace_id} />}
    </Khung>
  );
}

/** §30.3 — HITL. Đã có bài, nhưng chưa phải là xong. */
export function TheChoDuyet({ lyDo }: { lyDo: string }) {
  return (
    <div
      className="anim-fade mb-3 flex items-start gap-2 rounded-[12px] border px-3 py-2 text-[13px]"
      style={{ borderColor: "var(--color-info)", color: "var(--color-text-secondary)" }}
    >
      <UserCheck size={15} className="mt-0.5 shrink-0" style={{ color: "var(--color-info)" }} aria-hidden />
      <span>
        <strong style={{ color: "var(--color-info)" }}>Chờ người duyệt.</strong>{" "}
        {lyDo || "Chủ đề này được đánh dấu cần người xem lại trước khi dùng."} Bài
        vẫn hiện bên dưới để bạn đọc.
      </span>
    </div>
  );
}

/** Rào chắn chặn GIỮA luồng — chữ đã hiện ra đã bị thu hồi. */
export function TheBiChan({ lyDo, traceId }: { lyDo: string; traceId?: string }) {
  return (
    <Khung
      mau="var(--color-warning)"
      icon={<ShieldAlert size={16} aria-hidden />}
      nhan="Câu trả lời bị rào chắn chặn"
    >
      <p className="text-[15px]">{lyDo}</p>
      <p className="mt-1.5 text-[13px]" style={{ color: "var(--color-text-secondary)" }}>
        Phần chữ đã hiện ra trước đó đã được gỡ bỏ.
      </p>
      {traceId && <MaDoiChieu id={traceId} />}
    </Khung>
  );
}

/** §24 — lỗi thật. Đây là thẻ DUY NHẤT được dùng màu đỏ. */
export function TheLoi({
  thongBao,
  traceId,
  onThuLai,
}: {
  thongBao: string;
  traceId?: string;
  onThuLai?: () => void;
}) {
  return (
    <Khung
      mau="var(--color-error)"
      icon={<AlertTriangle size={16} aria-hidden />}
      nhan="Có lỗi xảy ra"
    >
      <p className="text-[15px]">{thongBao}</p>
      {onThuLai && (
        <button
          onClick={onThuLai}
          className="mt-3 inline-flex items-center gap-1.5 rounded-[var(--radius-btn)] border px-3.5 py-2 text-sm font-medium transition-transform hover:scale-[1.02]"
          style={{ borderColor: "var(--color-border)" }}
        >
          <RefreshCw size={14} aria-hidden />
          Thử lại
        </button>
      )}
      {traceId && <MaDoiChieu id={traceId} />}
    </Khung>
  );
}

/** §24 — "Error ID" của tài liệu chính là `trace_id` của backend. */
function MaDoiChieu({ id }: { id: string }) {
  return (
    <p className="mt-3 text-[11px]" style={{ color: "var(--color-text-muted)" }}>
      Mã đối chiếu: <code style={{ fontFamily: "var(--font-mono)" }}>{id}</code>
    </p>
  );
}
