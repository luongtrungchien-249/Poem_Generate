"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { MessageSquare, Plus, Search, Sparkles, Trash2, X } from "lucide-react";
import { layDanhSachHoiThoai, taoHoiThoai, xoaHoiThoai } from "@/services/api";
import { useConversationStore } from "@/stores/conversationStore";
import { useUiStore } from "@/stores/uiStore";
import { cx, thoiGianGon } from "@/lib/utils";

/** §11 · §12 · §44 — sidebar quản lý hội thoại. */
export function Sidebar({ dangMo }: { dangMo: string | null }) {
  const router = useRouter();
  const { danhSach, datDanhSach, xoaKhoiDanhSach } = useConversationStore();
  const { timKiem, datTimKiem, sidebarMo, datSidebar } = useUiStore();
  const [dangTai, datDangTai] = useState(true);

  useEffect(() => {
    // Gõ tới đâu gọi tới đó sẽ bắn một request mỗi phím — §49 yêu cầu debounce.
    const h = setTimeout(() => {
      layDanhSachHoiThoai(timKiem)
        .then(datDanhSach)
        .catch(() => datDanhSach([]))
        .finally(() => datDangTai(false));
    }, 220);
    return () => clearTimeout(h);
  }, [timKiem, datDanhSach]);

  async function moiCuocTroChuyen() {
    try {
      const c = await taoHoiThoai();
      router.push(`/chat/${c.conversation_id}`);
      datSidebar(window.innerWidth >= 1024);
    } catch {
      router.push("/");
    }
  }

  async function xoa(id: string, e: React.MouseEvent) {
    e.preventDefault();
    e.stopPropagation();
    // Xoá hội thoại xoá luôn tin nhắn ở backend và không hoàn tác được — hỏi trước.
    if (!confirm("Xoá cuộc trò chuyện này? Toàn bộ tin nhắn trong đó sẽ mất.")) return;
    try {
      await xoaHoiThoai(id);
      xoaKhoiDanhSach(id);
      if (dangMo === id) router.push("/");
    } catch {
      /* xoá hỏng thì giữ nguyên danh sách — người dùng thử lại được */
    }
  }

  return (
    <>
      {/* Lớp phủ khi sidebar là drawer trên mobile — §28. */}
      {sidebarMo && (
        <button
          className="fixed inset-0 z-30 bg-black/30 lg:hidden"
          onClick={() => datSidebar(false)}
          aria-label="Đóng thanh bên"
        />
      )}

      <aside
        className={cx(
          "fixed inset-y-0 left-0 z-40 flex w-[276px] flex-col border-r transition-transform duration-200 lg:static lg:translate-x-0",
          sidebarMo ? "translate-x-0" : "-translate-x-full lg:w-0 lg:overflow-hidden lg:border-r-0",
        )}
        style={{ background: "var(--color-surface-2)", borderColor: "var(--color-divider)" }}
        aria-label="Danh sách cuộc trò chuyện"
      >
        <div className="flex items-center justify-between px-4 pb-2 pt-4">
          <span className="inline-flex items-center gap-1.5 font-semibold">
            <Sparkles size={16} style={{ color: "var(--color-pink-600)" }} aria-hidden />
            Thơ thất ngôn
          </span>
          <button
            className="lg:hidden"
            onClick={() => datSidebar(false)}
            aria-label="Đóng thanh bên"
          >
            <X size={18} />
          </button>
        </div>

        <div className="px-3 pb-2">
          <button
            onClick={moiCuocTroChuyen}
            className="flex w-full items-center justify-center gap-2 rounded-[var(--radius-btn)] py-2.5 text-[14px] font-medium text-white transition-transform hover:scale-[1.02] active:scale-[0.98]"
            // #DB2777 + chữ trắng = 4.60:1. Bản gốc của §12 (#EC4899) chỉ 3.53:1.
            style={{ background: "var(--color-pink-600)", boxShadow: "var(--shadow-pink)" }}
          >
            <Plus size={16} aria-hidden />
            Cuộc trò chuyện mới
          </button>
        </div>

        <div className="px-3 pb-2">
          <div
            className="flex items-center gap-2 rounded-[var(--radius-btn)] border px-2.5 py-1.5"
            style={{ borderColor: "var(--color-border)" }}
          >
            <Search size={14} style={{ color: "var(--color-text-muted)" }} aria-hidden />
            <label htmlFor="o-tim" className="sr-only">
              Tìm cuộc trò chuyện
            </label>
            <input
              id="o-tim"
              value={timKiem}
              onChange={(e) => datTimKiem(e.target.value)}
              placeholder="Tìm…"
              className="w-full bg-transparent text-[13.5px] outline-none"
            />
          </div>
        </div>

        <div className="scroll-thin flex-1 overflow-y-auto px-3 pb-3">
          <p
            className="px-1 pb-1 pt-2 text-[11.5px] font-medium uppercase tracking-wide"
            style={{ color: "var(--color-text-muted)" }}
          >
            Gần đây
          </p>

          {dangTai ? (
            <div className="space-y-1.5 pt-1" aria-hidden>
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="h-10 rounded-[10px]"
                  style={{ background: "var(--color-divider)", opacity: 0.55 }}
                />
              ))}
            </div>
          ) : danhSach.length === 0 ? (
            <p className="px-1 pt-2 text-[13px]" style={{ color: "var(--color-text-muted)" }}>
              {timKiem ? "Không tìm thấy cuộc nào." : "Chưa có cuộc trò chuyện nào."}
            </p>
          ) : (
            <ul className="space-y-0.5">
              {danhSach.map((c) => {
                const dangXem = c.conversation_id === dangMo;
                return (
                  <li key={c.conversation_id}>
                    <a
                      href={`/chat/${c.conversation_id}`}
                      onClick={(e) => {
                        e.preventDefault();
                        router.push(`/chat/${c.conversation_id}`);
                        if (window.innerWidth < 1024) datSidebar(false);
                      }}
                      aria-current={dangXem ? "page" : undefined}
                      className="group relative flex items-center gap-2 rounded-[10px] px-2.5 py-2 text-[13.5px] transition-colors"
                      style={dangXem ? { background: "var(--color-pink-100)" } : undefined}
                    >
                      {/* §20.3 — vạch chỉ báo bên trái, KHÔNG chỉ dựa vào màu nền. */}
                      {dangXem && (
                        <span
                          className="absolute inset-y-1.5 left-0 w-[3px] rounded-full"
                          style={{ background: "var(--color-pink-600)" }}
                          aria-hidden
                        />
                      )}
                      <MessageSquare
                        size={14}
                        className="shrink-0"
                        style={{ color: "var(--color-text-muted)" }}
                        aria-hidden
                      />
                      <span className="min-w-0 flex-1">
                        <span className="block truncate">
                          {c.tieu_de || "Cuộc trò chuyện mới"}
                        </span>
                        <span className="block text-[11px]" style={{ color: "var(--color-text-muted)" }}>
                          {thoiGianGon(c.cap_nhat_luc)}
                        </span>
                      </span>
                      <button
                        onClick={(e) => xoa(c.conversation_id, e)}
                        aria-label={`Xoá ${c.tieu_de || "cuộc trò chuyện"}`}
                        className="shrink-0 opacity-0 transition-opacity group-hover:opacity-100 focus-visible:opacity-100"
                      >
                        <Trash2 size={14} style={{ color: "var(--color-text-muted)" }} />
                      </button>
                    </a>
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </aside>
    </>
  );
}
