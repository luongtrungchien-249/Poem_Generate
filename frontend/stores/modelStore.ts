"use client";

import { create } from "zustand";
import type { ModelInfo } from "@/types/api";

interface ModelState {
  danhSach: ModelInfo[];
  dangChon: string;
  datDanhSach: (ds: ModelInfo[]) => void;
  datDangChon: (ten: string) => void;
}

export const useModelStore = create<ModelState>((set) => ({
  danhSach: [],
  dangChon: "",
  datDanhSach: (ds) => set({ danhSach: ds }),
  datDangChon: (ten) => set({ dangChon: ten }),
}));
