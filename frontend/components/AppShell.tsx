"use client";

import { useEffect } from "react";
import { Sidebar } from "@/components/sidebar/Sidebar";
import { Header } from "@/components/Header";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useUiStore, apChuDe, chuDeDaLuu } from "@/stores/uiStore";
import { useChatStore } from "@/stores/chatStore";
import { useConversationStore } from "@/stores/conversationStore";
import { layHoiThoai } from "@/services/api";
import { rememberedJob, rememberedRequest, watchJob, rememberJob } from "@/services/poemJobs";
import { progressMessage, resultMessage } from "@/lib/poemJobMessage";
import type { PoemJob } from "@/types/api";
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
    let con = true;
    const monitor = new AbortController();
    (conversationId ? layHoiThoai(conversationId) : Promise.resolve({ tin_nhan: [] }))
      .then(async (c) => {
        if (!con) return;
        let ds: TinNhan[] = c.tin_nhan
          .filter((m) => m.role !== "system")
          .map((m) => ({
            id: maNgauNhien(),
            vai_tro: m.role === "user" ? "user" : "assistant",
            noi_dung: m.content,
            trang_thai: "xong" as const,
          }));
        datTinNhan(ds);
        let jobId = rememberedJob(conversationId);
        if (!jobId && conversationId) {
          const response = await fetch(`/api/poem/jobs?conversation_id=${encodeURIComponent(conversationId)}`, { signal: monitor.signal });
          if (response.ok) {
            const active: PoemJob[] = await response.json();
            jobId = active[0]?.job_id ?? null;
            if (jobId) rememberJob(conversationId, jobId);
          }
        }
        if (!con || !jobId) return;
        const original = rememberedRequest(conversationId);
        if (!conversationId && original) {
          ds = [{ id: maNgauNhien(), vai_tro: "user", noi_dung: original.yeu_cau, trang_thai: "xong" }];
          datTinNhan(ds);
        }
        const id = maNgauNhien();
        const store = useChatStore.getState();
        store.themTinNhan({ id, vai_tro: "assistant", noi_dung: "", trang_thai: "dang_chay" });
        store.datDangChay(true, monitor);
        try {
          const result = await watchJob(jobId, conversationId, monitor.signal, job => {
            if (con) useChatStore.getState().capNhat(id, progressMessage(job));
          });
          if (con) {
            // SQL completion and history commit together. Refresh the history
            // to avoid duplicating an answer completed just before reload.
            if (conversationId) {
              const fresh = await layHoiThoai(conversationId);
              if (!con) return;
              const history: TinNhan[] = fresh.tin_nhan.filter(m => m.role !== "system").map(m => ({
                id: maNgauNhien(), vai_tro: m.role === "user" ? "user" : "assistant",
                noi_dung: m.content, trang_thai: "xong",
              }));
              ds = history;
              const answer = history.at(-1);
              if (answer?.vai_tro === "assistant" && (result.loai === "tho" || result.loai === "hoi_lai")) {
                answer.id = id;
                datTinNhan(history);
              }
            }
            useChatStore.getState().capNhat(id, resultMessage(result));
            if (result.loai === "hoi_lai") {
              store.datTruongDangHoi(result.data.truong_thieu);
              const question = original?.yeu_cau ?? ds.filter(m => m.vai_tro === "user").at(-1)?.noi_dung;
              if (question) store.datMachTho([question]);
              if (original) store.datGanTho({ chu_de: original.chu_de ?? undefined, so_dong: original.so_dong ?? undefined });
            }
          }
        } catch (error) {
          if (con) useChatStore.getState().capNhat(id, {
            trang_thai: monitor.signal.aborted ? "da_dung" : "loi", tien_trinh: undefined,
            loi: error instanceof Error ? error.message : "Không theo dõi được tác vụ.",
          });
        } finally {
          if (con && useChatStore.getState().huy === monitor) useChatStore.getState().datDangChay(false, null);
        }
      })
      .catch(() => {
        /* 404 = hội thoại không tồn tại hoặc thuộc tenant khác. Để trống. */
      });
    return () => {
      con = false;
      monitor.abort();
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
