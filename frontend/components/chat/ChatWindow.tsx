"use client";

import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";
import { useChatStore } from "@/stores/chatStore";
import { useChat } from "@/hooks/useChat";
import { TinNhanNguoiDung, TinNhanTroLy } from "./Message";
import { ChatInput } from "./ChatInput";

/** §13 — màn hình chào, khi chưa có tin nhắn nào. */
function ManHinhChao({ onChon }: { onChon: (v: string) => void }) {
  const goiY = [
    { nhan: "Thơ mùa thu", cau: "Làm cho tôi một bài thơ 12 dòng về mùa thu Hà Nội" },
    { nhan: "Thơ quê hương", cau: "Viết bài thơ 8 dòng về quê hương, giọng trầm lắng" },
    { nhan: "Thơ tình", cau: "Một bài 8 dòng về nỗi nhớ, nhẹ nhàng" },
    { nhan: "Thơ về biển", cau: "Bài thơ 16 dòng về biển lúc bình minh" },
  ];

  return (
    <div className="flex h-full flex-col items-center justify-center px-6 text-center">
      <div className="anim-float mb-5" aria-hidden>
        <Sparkles size={38} style={{ color: "var(--color-pink-500)" }} />
      </div>
      <h2 className="text-[26px] font-semibold tracking-tight">Xin chào</h2>
      <p className="mt-1.5 max-w-md text-[15px]" style={{ color: "var(--color-text-secondary)" }}>
        Hôm nay bạn muốn làm bài thơ về điều gì?
      </p>

      <div className="mt-7 grid w-full max-w-lg grid-cols-1 gap-2.5 sm:grid-cols-2">
        {goiY.map((g) => (
          <button
            key={g.nhan}
            onClick={() => onChon(g.cau)}
            className="rounded-[var(--radius-card)] border px-4 py-3 text-left transition-all hover:scale-[1.02]"
            style={{ borderColor: "var(--color-divider)", background: "var(--color-surface)" }}
          >
            <span className="block text-[14px] font-medium">{g.nhan}</span>
            <span className="mt-0.5 block text-[12.5px]" style={{ color: "var(--color-text-muted)" }}>
              {g.cau}
            </span>
          </button>
        ))}
      </div>

      <p className="mt-7 max-w-md text-[12px]" style={{ color: "var(--color-text-muted)" }}>
        Số dòng cần là bội của 4. Nếu bạn chưa nói rõ, hệ thống sẽ hỏi lại thay vì tự
        đoán.
      </p>
    </div>
  );
}

export function ChatWindow({ sessionId }: { sessionId: string | null }) {
  const { tinNhan, dangChay } = useChatStore();
  const { gui, dung, sinhLai } = useChat(sessionId);
  const cuoi = useRef<HTMLDivElement>(null);
  const boc = useRef<HTMLDivElement>(null);
  const tuCuon = useRef(true);

  // Chỉ tự cuộn khi người dùng ĐANG ở cuối. Cuộn ép khi họ vừa kéo lên đọc lại
  // là giật thứ họ đang đọc khỏi tay họ — khó chịu nhất lúc câu trả lời đang dài ra.
  useEffect(() => {
    const el = boc.current;
    if (!el) return;
    const kiem = () => {
      tuCuon.current = el.scrollHeight - el.scrollTop - el.clientHeight < 120;
    };
    el.addEventListener("scroll", kiem, { passive: true });
    return () => el.removeEventListener("scroll", kiem);
  }, []);

  useEffect(() => {
    if (tuCuon.current) cuoi.current?.scrollIntoView({ block: "end" });
  }, [tinNhan]);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div ref={boc} className="scroll-thin min-h-0 flex-1 overflow-y-auto">
        {tinNhan.length === 0 ? (
          <ManHinhChao onChon={gui} />
        ) : (
          <div className="mx-auto w-full max-w-[900px] space-y-6 px-4 py-6">
            {tinNhan.map((t) =>
              t.vai_tro === "user" ? (
                <TinNhanNguoiDung key={t.id} t={t} />
              ) : (
                <TinNhanTroLy
                  key={t.id}
                  t={t}
                  onSinhLai={() => sinhLai(t.id, t.yeu_cau_goc ?? "")}
                  onTraLoiHoiLai={(v, dat) => gui(v, dat)}
                />
              ),
            )}
            <div ref={cuoi} />
          </div>
        )}
      </div>

      <ChatInput dangChay={dangChay} onGui={gui} onDung={dung} />
    </div>
  );
}
