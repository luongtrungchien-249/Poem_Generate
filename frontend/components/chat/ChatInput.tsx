"use client";

import { useEffect, useRef, useState } from "react";
import { ArrowUp, Square } from "lucide-react";
import { useUiStore } from "@/stores/uiStore";
import { ModelSelector } from "@/components/model/ModelSelector";
import { cx } from "@/lib/utils";

/** §18 · §19 — ô nhập và nút gửi/dừng. */
export function ChatInput({
  dangChay,
  onGui,
  onDung,
}: {
  dangChay: boolean;
  onGui: (v: string) => void;
  onDung: () => void;
}) {
  const [van, datVan] = useState("");
  const [dangFocus, datDangFocus] = useState(false);
  const ref = useRef<HTMLTextAreaElement>(null);
  const { cheDo, datCheDo } = useUiStore();

  // Cao theo nội dung, tối đa ~8 dòng rồi mới cuộn.
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  }, [van]);

  function gui() {
    const v = van.trim();
    if (!v || dangChay) return;
    onGui(v);
    datVan("");
  }

  return (
    <div className="px-4 pb-4 pt-2">
      <div className="mx-auto w-full max-w-[900px]">
        <div
          className="rounded-[var(--radius-input)] border transition-shadow"
          style={{
            borderColor: dangFocus ? "var(--color-pink-600)" : "var(--color-border)",
            background: "var(--color-surface)",
            boxShadow: dangFocus ? "var(--shadow-pink)" : "var(--shadow-soft)",
          }}
        >
          <label htmlFor="o-nhap" className="sr-only">
            Nội dung yêu cầu
          </label>
          <textarea
            id="o-nhap"
            ref={ref}
            rows={1}
            value={van}
            onChange={(e) => datVan(e.target.value)}
            onFocus={() => datDangFocus(true)}
            onBlur={() => datDangFocus(false)}
            onKeyDown={(e) => {
              // Enter gửi, Shift+Enter xuống dòng — §18.
              // `isComposing` BẮT BUỘC phải kiểm: gõ tiếng Việt bằng bộ gõ dấu
              // sinh ra Enter để chốt chữ đang soạn. Thiếu dòng này thì câu bị
              // gửi đi giữa chừng mỗi lần người dùng bỏ dấu.
              if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
                e.preventDefault();
                gui();
              }
            }}
            placeholder={
              cheDo === "tho"
                ? "Mô tả bài thơ bạn muốn — chủ đề, số dòng (bội của 4)…"
                : "Hỏi bất cứ điều gì…"
            }
            className="scroll-thin block w-full resize-none bg-transparent px-4 pt-3 text-[15px] outline-none"
            style={{ color: "var(--color-text)" }}
          />

          <div className="flex items-center gap-2 px-3 pb-2.5 pt-1">
            <ChonCheDo cheDo={cheDo} datCheDo={datCheDo} />
            <div className="ml-auto flex items-center gap-2">
              <ModelSelector />
              {dangChay ? (
                <button
                  onClick={onDung}
                  aria-label="Dừng sinh"
                  className="grid size-9 place-items-center rounded-full transition-transform hover:scale-105 active:scale-95"
                  style={{ background: "var(--color-surface-2)", border: "1px solid var(--color-border)" }}
                >
                  <Square size={14} fill="currentColor" aria-hidden />
                </button>
              ) : (
                <button
                  onClick={gui}
                  disabled={!van.trim()}
                  aria-label="Gửi"
                  className={cx(
                    "grid size-9 place-items-center rounded-full text-white transition-transform",
                    van.trim() ? "hover:scale-105 active:scale-95" : "cursor-not-allowed",
                  )}
                  style={{
                    // Nền #DB2777 với chữ trắng = 4.60:1. Bản gốc #EC4899 chỉ đạt
                    // 3.53:1, trượt ngưỡng chữ thường của WCAG AA.
                    background: van.trim() ? "var(--color-pink-600)" : "var(--color-text-muted)",
                  }}
                >
                  <ArrowUp size={16} aria-hidden />
                </button>
              )}
            </div>
          </div>
        </div>

        <p className="mt-2 text-center text-[11.5px]" style={{ color: "var(--color-text-muted)" }}>
          {cheDo === "tho"
            ? "Bài thơ chỉ được trả về sau khi qua đủ bảy tầng kiểm luật."
            : "Enter để gửi · Shift + Enter để xuống dòng"}
        </p>
      </div>
    </div>
  );
}

/** Chuyển giữa hai luồng. Chúng khác nhau về hành vi nên phải chọn tường minh. */
function ChonCheDo({
  cheDo,
  datCheDo,
}: {
  cheDo: "chat" | "tho";
  datCheDo: (v: "chat" | "tho") => void;
}) {
  return (
    <div
      className="flex items-center rounded-full border p-0.5 text-[12.5px]"
      style={{ borderColor: "var(--color-divider)" }}
      role="group"
      aria-label="Chế độ"
    >
      {(["tho", "chat"] as const).map((v) => (
        <button
          key={v}
          onClick={() => datCheDo(v)}
          aria-pressed={cheDo === v}
          className="rounded-full px-2.5 py-1 transition-colors"
          style={
            cheDo === v
              ? { background: "var(--color-pink-100)", color: "var(--color-pink-700)", fontWeight: 600 }
              : { color: "var(--color-text-muted)" }
          }
        >
          {v === "tho" ? "Làm thơ" : "Trò chuyện"}
        </button>
      ))}
    </div>
  );
}
