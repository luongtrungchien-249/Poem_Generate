"use client";

import { create } from "zustand";
import type { CheDo } from "@/lib/types";

/**
 * §35 — UI State tách riêng khỏi Chat State và Conversation State.
 *
 * Gộp tất cả vào một store nghĩa là mở/đóng sidebar cũng khiến danh sách tin
 * nhắn render lại; với hội thoại dài thì đó là độ trễ nhìn thấy được.
 */

export type ChuDeGiaoDien = "light" | "dark" | "system";

interface UiState {
  sidebarMo: boolean;
  chuDe: ChuDeGiaoDien;
  cheDo: CheDo;
  timKiem: string;
  datSidebar: (v: boolean) => void;
  batTatSidebar: () => void;
  datChuDe: (v: ChuDeGiaoDien) => void;
  datCheDo: (v: CheDo) => void;
  datTimKiem: (v: string) => void;
}

const KHOA_CHU_DE = "poem-ui-theme";

/** Áp chủ đề lên thẻ <html>. Bọc try/catch vì localStorage ném ở chế độ riêng tư. */
export function apChuDe(v: ChuDeGiaoDien): void {
  if (typeof document === "undefined") return;
  const el = document.documentElement;
  if (v === "system") el.removeAttribute("data-theme");
  else el.setAttribute("data-theme", v);
  try {
    localStorage.setItem(KHOA_CHU_DE, v);
  } catch {
    /* chế độ riêng tư hoặc site data bị chặn — bỏ qua, giao diện vẫn chạy */
  }
}

export function chuDeDaLuu(): ChuDeGiaoDien {
  try {
    const v = localStorage.getItem(KHOA_CHU_DE);
    if (v === "light" || v === "dark" || v === "system") return v;
  } catch {
    /* như trên */
  }
  return "system";
}

export const useUiStore = create<UiState>((set) => ({
  sidebarMo: true,
  chuDe: "system",
  cheDo: "tho",
  timKiem: "",
  datSidebar: (v) => set({ sidebarMo: v }),
  batTatSidebar: () => set((s) => ({ sidebarMo: !s.sidebarMo })),
  datChuDe: (v) => {
    apChuDe(v);
    set({ chuDe: v });
  },
  datCheDo: (v) => set({ cheDo: v }),
  datTimKiem: (v) => set({ timKiem: v }),
}));
