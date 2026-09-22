"use client";

import { useEffect } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { Header } from "@/components/Header";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useUiStore, apChuDe, chuDeDaLuu } from "@/stores/uiStore";
import { useChatStore } from "@/stores/chatStore";
import { useConversationStore } from "@/stores/conversationStore";
import { layHoiThoai } from "@/services/api";
import { maNgauNhien } from "@/lib/utils";
import type { TinNhan } from "@/lib/types";

export function AppShell({ conversationId }: { conversationId: string | null }) {
  const { datSidebar, datChuDe } = useUiStore();
  const { datTinNhan, donDep } = useChatStore();
  const danhSach = useConversationStore((s) => s.danhSach);

  // Khôi phục chủ đề đã lưu, và thu sidebar trên màn hình hẹp — §28.
  useEffect(() => {
    const v = chuDeDaLuu();
    apChuDe(v);
    datChuDe(v);
    datSidebar(window.innerWidth >= 1024);
  }, [datChuDe, datSidebar]);

  // Nạp lịch sử khi đổi hội thoại. `donDep()` cũng huỷ luồng đang chạy — không
  // huỷ thì chữ của cuộc cũ sẽ chảy tiếp vào khung của cuộc mới.
  useEffect(() => {
    donDep();
    if (!conversationId) return;
    let con = true;
    layHoiThoai(conversationId)
      .then((c) => {
        if (!con) return;
        const ds: TinNhan[] = c.tin_nhan
          .filter((m) => m.role !== "system")
          .map((m) => ({
            id: maNgauNhien(),
            vai_tro: m.role === "user" ? "user" : "assistant",
            noi_dung: m.content,
            trang_thai: "xong" as const,
          }));
        datTinNhan(ds);
      })
      .catch(() => {
        /* 404 = hội thoại không tồn tại hoặc thuộc tenant khác. Để trống. */
      });
    return () => {
      con = false;
    };
  }, [conversationId, datTinNhan, donDep]);

  const tieuDe = danhSach.find((c) => c.conversation_id === conversationId)?.tieu_de;

  return (
    <div className="flex h-dvh overflow-hidden">
      <Sidebar dangMo={conversationId} />
      <main className="flex min-w-0 flex-1 flex-col">
        <Header tieuDe={tieuDe} />
        <ChatWindow sessionId={conversationId} />
      </main>
    </div>
  );
}
