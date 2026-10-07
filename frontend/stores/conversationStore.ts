"use client";

import { create } from "zustand";
import type { Conversation } from "@/types/api";

interface ConversationState {
  danhSach: Conversation[];
  datDanhSach: (ds: Conversation[]) => void;
  themVaoDau: (c: Conversation) => void;
  xoaKhoiDanhSach: (id: string) => void;
  doiTen: (id: string, tieu_de: string) => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  danhSach: [],
  datDanhSach: (ds) => set({ danhSach: ds }),
  themVaoDau: (c) =>
    set((s) => ({
      danhSach: [c, ...s.danhSach.filter((x) => x.conversation_id !== c.conversation_id)],
    })),
  xoaKhoiDanhSach: (id) =>
    set((s) => ({ danhSach: s.danhSach.filter((c) => c.conversation_id !== id) })),
  doiTen: (id, tieu_de) =>
    set((s) => ({
      danhSach: s.danhSach.map((c) => (c.conversation_id === id ? { ...c, tieu_de } : c)),
    })),
}));
