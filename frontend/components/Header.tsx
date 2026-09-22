"use client";

import { Menu, Monitor, Moon, Sun } from "lucide-react";
import { useUiStore, type ChuDeGiaoDien } from "@/stores/uiStore";

/** §10 — header tối giản. */
export function Header({ tieuDe }: { tieuDe?: string }) {
  const { batTatSidebar, chuDe, datChuDe } = useUiStore();

  return (
    <header
      className="flex h-14 shrink-0 items-center gap-3 border-b px-4"
      style={{ borderColor: "var(--color-divider)", background: "var(--color-bg)" }}
    >
      <button
        onClick={batTatSidebar}
        aria-label="Bật tắt thanh bên"
        className="grid size-8 place-items-center rounded-[10px] transition-colors hover:opacity-70"
      >
        <Menu size={18} />
      </button>

      <h1 className="min-w-0 flex-1 truncate text-[15px] font-medium">
        {tieuDe || "Cuộc trò chuyện mới"}
      </h1>

      <ChonChuDe chuDe={chuDe} datChuDe={datChuDe} />
    </header>
  );
}

/**
 * Ba lựa chọn, không phải hai. "Theo hệ thống" là mặc định và phải giữ được:
 * người đã đặt chế độ tối ở cấp hệ điều hành thường muốn mọi ứng dụng theo đó,
 * và một công tắc hai trạng thái buộc họ chọn lại ở từng ứng dụng.
 */
function ChonChuDe({
  chuDe,
  datChuDe,
}: {
  chuDe: ChuDeGiaoDien;
  datChuDe: (v: ChuDeGiaoDien) => void;
}) {
  const muc: { v: ChuDeGiaoDien; icon: React.ReactNode; nhan: string }[] = [
    { v: "light", icon: <Sun size={14} aria-hidden />, nhan: "Sáng" },
    { v: "dark", icon: <Moon size={14} aria-hidden />, nhan: "Tối" },
    { v: "system", icon: <Monitor size={14} aria-hidden />, nhan: "Theo hệ thống" },
  ];

  return (
    <div
      className="flex items-center rounded-full border p-0.5"
      style={{ borderColor: "var(--color-divider)" }}
      role="group"
      aria-label="Giao diện"
    >
      {muc.map((m) => (
        <button
          key={m.v}
          onClick={() => datChuDe(m.v)}
          aria-label={m.nhan}
          aria-pressed={chuDe === m.v}
          title={m.nhan}
          className="grid size-7 place-items-center rounded-full transition-colors"
          style={
            chuDe === m.v
              ? { background: "var(--color-pink-100)", color: "var(--color-pink-700)" }
              : { color: "var(--color-text-muted)" }
          }
        >
          {m.icon}
        </button>
      ))}
    </div>
  );
}
