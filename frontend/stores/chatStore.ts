"use client";

import { create } from "zustand";
import type { TinNhan, TrangThaiTinNhan } from "@/lib/types";

interface ChatState {
  tinNhan: TinNhan[];
  dangChay: boolean;
  /** Dùng để huỷ luồng đang chạy khi bấm Stop hoặc rời trang. */
  huy: AbortController | null;

  /**
   * Các mẩu của MỘT yêu cầu làm thơ đang được hoàn thiện dần qua nhiều lượt hỏi lại.
   *
   * `/v1/poem` không có trạng thái: mỗi lần gọi, nó dựng lại yêu cầu từ đúng
   * chuỗi `yeu_cau` nhận được. Nên khi hệ thống hỏi "bao nhiêu dòng?" và người
   * dùng đáp "12 dòng", nếu client chỉ gửi đi hai chữ đó thì chủ đề nói ở lượt
   * trước đã biến mất — và hệ thống lại hỏi tiếp về chủ đề, vòng vo mãi không
   * bao giờ đủ thông tin.
   *
   * Client giữ các mẩu rồi ghép lại. Nó KHÔNG phân tích gì: việc tách chủ đề,
   * số dòng, cảm xúc ra khỏi câu nói là của backend. Ở đây chỉ là không đánh rơi
   * thứ người dùng đã nói.
   */
  machTho: string[];
  datMachTho: (v: string[]) => void;

  /**
   * Các trường đã được người dùng nói RÕ RÀNG, gửi đi dưới dạng trường tường minh
   * của `PoemRequest` thay vì chỉ nằm trong câu chữ.
   *
   * Vì sao cần: backend phân biệt NGUỒN của mỗi trường. Trường trích ra từ câu
   * nói mang nguồn `suy_doan`, và luật của dự án cấm dùng giá trị suy đoán mà
   * chưa hỏi — nên nó xin xác nhận. Nếu client cứ trả lời bằng chữ tự do thì câu
   * trả lời ấy lại bị trích xuất thành `suy_doan` lần nữa, và vòng hỏi không bao
   * giờ khép.
   *
   * Trường gửi tường minh mang nguồn `nguoi_dung` — đó là lối thoát duy nhất, và
   * là lý do `PoemRequest` có sẵn các trường này.
   */
  ganTho: { chu_de?: string; so_dong?: number };
  datGanTho: (v: { chu_de?: string; so_dong?: number }) => void;

  /** Lượt hỏi lại vừa rồi đang thiếu trường nào — để biết câu trả lời tới thuộc về đâu. */
  truongDangHoi: string[];
  datTruongDangHoi: (v: string[]) => void;

  datTinNhan: (ds: TinNhan[]) => void;
  themTinNhan: (t: TinNhan) => void;
  capNhat: (id: string, thay: Partial<TinNhan>) => void;
  /** Nối thêm chữ vào tin nhắn đang chảy — nóng nhất trong cả app. */
  noiChu: (id: string, chu: string) => void;
  datTrangThai: (id: string, tt: TrangThaiTinNhan) => void;
  xoaTuId: (id: string) => void;
  datDangChay: (v: boolean, huy?: AbortController | null) => void;
  donDep: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  tinNhan: [],
  dangChay: false,
  huy: null,
  machTho: [],
  ganTho: {},
  truongDangHoi: [],

  datMachTho: (v) => set({ machTho: v }),
  datGanTho: (v) => set({ ganTho: v }),
  datTruongDangHoi: (v) => set({ truongDangHoi: v }),

  datTinNhan: (ds) => set({ tinNhan: ds }),
  themTinNhan: (t) => set((s) => ({ tinNhan: [...s.tinNhan, t] })),

  capNhat: (id, thay) =>
    set((s) => ({
      tinNhan: s.tinNhan.map((t) => (t.id === id ? { ...t, ...thay } : t)),
    })),

  noiChu: (id, chu) =>
    set((s) => ({
      tinNhan: s.tinNhan.map((t) =>
        t.id === id ? { ...t, noi_dung: t.noi_dung + chu } : t,
      ),
    })),

  datTrangThai: (id, tt) =>
    set((s) => ({
      tinNhan: s.tinNhan.map((t) => (t.id === id ? { ...t, trang_thai: tt } : t)),
    })),

  xoaTuId: (id) =>
    set((s) => {
      const i = s.tinNhan.findIndex((t) => t.id === id);
      return i < 0 ? s : { tinNhan: s.tinNhan.slice(0, i) };
    }),

  datDangChay: (v, huy = null) => set({ dangChay: v, huy }),

  donDep: () => {
    get().huy?.abort();
    set({
      tinNhan: [], dangChay: false, huy: null,
      machTho: [], ganTho: {}, truongDangHoi: [],
    });
  },
}));
