"use client";

import { useState } from "react";
import { Check, Copy, RefreshCw, Sparkles, ThumbsDown, ThumbsUp } from "lucide-react";
import type { TinNhan } from "@/lib/types";
import { thoiLuong } from "@/lib/utils";
import { MarkdownRenderer } from "@/components/markdown/MarkdownRenderer";
import { BienBanBayTang, HaiCo, TienTrinhTho } from "@/components/poem/PoemEvidence";
import {
  TheBiChan,
  TheChoDuyet,
  TheHoiLai,
  TheKhongDat,
  TheLoi,
} from "@/components/states/StateCards";

// ── §14 — tin nhắn người dùng ───────────────────────────────────────────────
export function TinNhanNguoiDung({ t }: { t: TinNhan }) {
  return (
    <div className="anim-slide-up flex justify-end">
      <div
        className="max-w-[min(42rem,88%)] whitespace-pre-wrap rounded-[var(--radius-bubble)] px-4 py-2.5 text-[15px]"
        style={{ background: "var(--color-pink-50)" }}
      >
        {t.noi_dung}
      </div>
    </div>
  );
}

// ── §15 — avatar ────────────────────────────────────────────────────────────
function Avatar({ dangChay }: { dangChay: boolean }) {
  return (
    <div
      className={`grid size-7 shrink-0 place-items-center rounded-full ${dangChay ? "anim-pulse" : ""}`}
      style={{ background: "var(--color-pink-100)", opacity: dangChay ? 1 : 0.85 }}
      aria-hidden
    >
      <Sparkles size={15} style={{ color: "var(--color-pink-600)" }} />
    </div>
  );
}

// ── §16 — đang nghĩ ─────────────────────────────────────────────────────────
function DangNghi() {
  return (
    <div className="flex items-center gap-2 text-[14px]" style={{ color: "var(--color-text-secondary)" }}>
      <span>Đang nghĩ</span>
      <span className="flex gap-1" aria-hidden>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="size-1.5 rounded-full"
            style={{
              background: "var(--color-pink-600)",
              animation: `dotStep 1.2s ease-in-out ${i * 0.16}s infinite`,
            }}
          />
        ))}
      </span>
      {/* Người dùng màn hình đọc không thấy ba chấm — cần một câu thật. */}
      <span className="sr-only" role="status">
        Trợ lý đang soạn câu trả lời.
      </span>
    </div>
  );
}

// ── §14 — tin nhắn trợ lý ───────────────────────────────────────────────────
export function TinNhanTroLy({
  t,
  onSinhLai,
  onTraLoiHoiLai,
}: {
  t: TinNhan;
  onSinhLai: () => void;
  onTraLoiHoiLai: (v: string, dat?: { so_dong?: number; chu_de?: string }) => void;
}) {
  const dangChay = t.trang_thai === "dang_chay" || t.trang_thai === "dang_gui";

  return (
    <div className="anim-slide-up flex gap-3">
      <Avatar dangChay={dangChay} />
      <div className="min-w-0 flex-1">
        {/* Tiến trình sinh thơ — §30.4 */}
        {t.tien_trinh && t.tien_trinh.length > 0 ? (
          <TienTrinhTho buoc={t.tien_trinh} />
        ) : dangChay && !t.noi_dung ? (
          <DangNghi />
        ) : null}

        {/* Bốn trạng thái đặc thù */}
        {t.trang_thai === "hoi_lai" && t.hoi_lai && (
          <TheHoiLai data={t.hoi_lai} onChon={onTraLoiHoiLai} />
        )}
        {t.trang_thai === "khong_dat" && t.khong_dat && (
          <TheKhongDat data={t.khong_dat} onThuLai={onSinhLai} />
        )}
        {t.trang_thai === "bi_chan" && (
          <TheBiChan lyDo={t.loi ?? "Bị rào chắn chặn."} traceId={t.trace_id} />
        )}
        {t.trang_thai === "loi" && (
          <TheLoi
            thongBao={t.loi ?? "Không hoàn tất được câu trả lời."}
            traceId={t.trace_id}
            onThuLai={onSinhLai}
          />
        )}
        {t.trang_thai === "cho_duyet" && <TheChoDuyet lyDo={t.tho?.ly_do_hitl ?? ""} />}

        {/* Nội dung */}
        {t.tho ? (
          <>
            <HaiCo tho={t.tho} />
            <div className="poem-body">{t.tho.poem}</div>
            <BienBanBayTang tho={t.tho} />
          </>
        ) : t.noi_dung ? (
          <>
            <MarkdownRenderer noiDung={t.noi_dung} />
            {/* §17 — con trỏ chỉ ở luồng chat, và biến mất khi xong. */}
            {t.trang_thai === "dang_chay" && (
              <span
                className="anim-blink ml-0.5 inline-block h-[1.05em] w-[2px] align-text-bottom"
                style={{ background: "var(--color-pink-600)" }}
                aria-hidden
              />
            )}
          </>
        ) : null}

        {t.trang_thai === "da_dung" && (
          <p className="mt-1 text-[13px]" style={{ color: "var(--color-text-muted)" }}>
            Đã dừng theo yêu cầu.
          </p>
        )}

        <Latency t={t} />

        {(t.trang_thai === "xong" || t.trang_thai === "cho_duyet") && (
          <ThaoTac noiDung={t.tho?.poem ?? t.noi_dung} onSinhLai={onSinhLai} />
        )}
      </div>
    </div>
  );
}

/**
 * Thời gian lượt này mất.
 *
 * Hiện cho MỌI kết cục, kể cả hỏi lại và không đạt — một lượt trượt luật sau 90
 * giây là thông tin quan trọng hơn hẳn một lượt xong sau 3 giây, và giấu nó đi
 * thì người dùng không có cách nào biết cái nào tốn thời gian của mình.
 *
 * Với luồng thơ, con số này giải thích vì sao phải chờ: mỗi khổ sinh 16 bản rồi
 * mới chọn. Đó là lý do ở đây không có thanh tiến trình hứa hẹn gì — chỉ có con
 * số thật, sau khi đã xong.
 */
function Latency({ t }: { t: TinNhan }) {
  if (t.giay === undefined) return null;
  const phan = [thoiLuong(t.giay)];
  if (t.giay_chu_dau !== undefined) {
    phan.push(`chữ đầu ${thoiLuong(t.giay_chu_dau)}`);
  }
  if (t.tho) {
    phan.push(`${t.tho.so_kho} khổ`);
    if (t.tho.so_luot_sua > 0) phan.push(`sửa ${t.tho.so_luot_sua} lượt`);
  }
  return (
    <p
      className="mt-1.5 text-[11.5px] tabular-nums"
      style={{ color: "var(--color-text-muted)" }}
      // Người dùng màn hình đọc không cần nghe con số này mỗi lượt; nó là thông
      // tin phụ, đọc được khi họ chủ động rà tới.
      aria-label={`Lượt này mất ${phan.join(", ")}`}
    >
      {phan.join(" · ")}
    </p>
  );
}

// ── §14 — hàng thao tác ─────────────────────────────────────────────────────
function ThaoTac({ noiDung, onSinhLai }: { noiDung: string; onSinhLai: () => void }) {
  const [daChep, datDaChep] = useState(false);
  const [danhGia, datDanhGia] = useState<"len" | "xuong" | null>(null);

  async function chep() {
    try {
      await navigator.clipboard.writeText(noiDung);
      datDaChep(true);
      setTimeout(() => datDaChep(false), 1600);
    } catch {
      /* clipboard bị chặn — nút không phản hồi, không làm hỏng gì khác */
    }
  }

  const nut =
    "inline-flex items-center gap-1 rounded-[9px] px-2 py-1 text-[12.5px] transition-colors hover:opacity-75";

  return (
    <div className="mt-2.5 flex items-center gap-1" style={{ color: "var(--color-text-muted)" }}>
      <button onClick={chep} className={nut} aria-label={daChep ? "Đã sao chép" : "Sao chép"}>
        {daChep ? (
          <>
            <Check size={13} aria-hidden style={{ color: "var(--color-success)" }} />
            <span style={{ color: "var(--color-success)" }}>Đã chép</span>
          </>
        ) : (
          <>
            <Copy size={13} aria-hidden />
            Chép
          </>
        )}
      </button>
      <button onClick={onSinhLai} className={nut} aria-label="Sinh lại câu trả lời">
        <RefreshCw size={13} aria-hidden />
        Sinh lại
      </button>
      <button
        onClick={() => datDanhGia(danhGia === "len" ? null : "len")}
        className={nut}
        aria-label="Câu trả lời hữu ích"
        aria-pressed={danhGia === "len"}
        style={{ color: danhGia === "len" ? "var(--color-success)" : undefined }}
      >
        <ThumbsUp size={13} aria-hidden />
      </button>
      <button
        onClick={() => datDanhGia(danhGia === "xuong" ? null : "xuong")}
        className={nut}
        aria-label="Câu trả lời chưa tốt"
        aria-pressed={danhGia === "xuong"}
        style={{ color: danhGia === "xuong" ? "var(--color-warning)" : undefined }}
      >
        <ThumbsDown size={13} aria-hidden />
      </button>
    </div>
  );
}
