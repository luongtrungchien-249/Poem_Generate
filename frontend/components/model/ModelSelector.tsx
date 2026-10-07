"use client";

import { useEffect, useRef, useState } from "react";
import { ChevronDown } from "lucide-react";
import { layDanhSachModel } from "@/services/api";
import { useModelStore } from "@/stores/modelStore";

/**
 * §45 · §10 — chọn model.
 *
 * Danh sách lấy từ `/api/models`, tức là từ `configs/models.yaml` của backend.
 * §10 của tài liệu liệt kê cứng "Gemma 4 / GPT / Claude / Gemini / Local LLM" —
 * cấu hình thật không có Gemma và không có Gemini, nên một danh sách chép tay sẽ
 * mời người dùng chọn thứ backend không định tuyến được.
 */
export function ModelSelector() {
  const { danhSach, dangChon, datDanhSach, datDangChon } = useModelStore();
  const [mo, datMo] = useState(false);
  const [loi, datLoi] = useState(false);
  const boc = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (danhSach.length > 0) return;
    layDanhSachModel()
      .then((ds) => {
        datDanhSach(ds);
        if (!dangChon && ds[0]) datDangChon(ds[0].ten);
      })
      .catch(() => datLoi(true));
  }, [danhSach.length, dangChon, datDanhSach, datDangChon]);

  // Đóng khi bấm ra ngoài hoặc bấm Esc — bàn phím phải thoát được, §29.
  useEffect(() => {
    if (!mo) return;
    const ngoai = (e: MouseEvent) => {
      if (boc.current && !boc.current.contains(e.target as Node)) datMo(false);
    };
    const phim = (e: KeyboardEvent) => {
      if (e.key === "Escape") datMo(false);
    };
    document.addEventListener("mousedown", ngoai);
    document.addEventListener("keydown", phim);
    return () => {
      document.removeEventListener("mousedown", ngoai);
      document.removeEventListener("keydown", phim);
    };
  }, [mo]);

  if (loi) {
    return (
      <span className="text-[12px]" style={{ color: "var(--color-text-muted)" }}>
        Không tải được danh sách model
      </span>
    );
  }

  const hienTai = danhSach.find((m) => m.ten === dangChon);

  return (
    <div className="relative" ref={boc}>
      <button
        onClick={() => datMo(!mo)}
        aria-haspopup="listbox"
        aria-expanded={mo}
        className="inline-flex items-center gap-1 rounded-[var(--radius-btn)] px-2 py-1 text-[12.5px] transition-colors hover:opacity-80"
        style={{ color: "var(--color-text-secondary)" }}
      >
        {hienTai?.ten ?? "Đang tải…"}
        <ChevronDown size={13} aria-hidden />
      </button>

      {mo && (
        <div
          role="listbox"
          className="anim-scale-in absolute bottom-full right-0 z-20 mb-2 max-h-72 w-64 overflow-auto rounded-[var(--radius-card)] border p-1 scroll-thin"
          style={{
            borderColor: "var(--color-divider)",
            background: "var(--color-surface)",
            boxShadow: "var(--shadow-medium)",
          }}
        >
          {danhSach.map((m) => (
            <button
              key={m.ten}
              role="option"
              aria-selected={m.ten === dangChon}
              onClick={() => {
                datDangChon(m.ten);
                datMo(false);
              }}
              className="block w-full rounded-[10px] px-2.5 py-2 text-left transition-colors"
              style={
                m.ten === dangChon
                  ? { background: "var(--color-pink-50)" }
                  : undefined
              }
            >
              <span className="block text-[13.5px] font-medium">{m.ten}</span>
              <span className="block text-[11.5px]" style={{ color: "var(--color-text-muted)" }}>
                {m.provider} · {m.tier} · ngữ cảnh{" "}
                {m.context_window >= 1000
                  ? `${Math.round(m.context_window / 1000)}K`
                  : m.context_window}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
