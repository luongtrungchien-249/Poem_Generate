"use client";

import { memo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import rehypeHighlight from "rehype-highlight";
import { Check, Copy } from "lucide-react";

/** §27 — khối mã có nhãn ngôn ngữ, nút sao chép, và cuộn ngang. */
function KhoiMa({ className, children }: { className?: string; children?: React.ReactNode }) {
  const [daChep, datDaChep] = useState(false);
  const ngonNgu = /language-(\w+)/.exec(className ?? "")?.[1] ?? "text";
  const ma = String(children ?? "");

  async function chep() {
    try {
      await navigator.clipboard.writeText(ma);
      datDaChep(true);
      setTimeout(() => datDaChep(false), 1600);
    } catch {
      /* clipboard bị chặn (http, quyền) — không làm gì, nút chỉ không phản hồi */
    }
  }

  return (
    <div
      className="my-3 overflow-hidden rounded-[12px] border"
      style={{ borderColor: "var(--color-divider)" }}
    >
      <div
        className="flex items-center justify-between px-3 py-1.5 text-[12px]"
        style={{ background: "var(--color-surface-2)", color: "var(--color-text-secondary)" }}
      >
        <span style={{ fontFamily: "var(--font-mono)" }}>{ngonNgu}</span>
        <button
          onClick={chep}
          aria-label={daChep ? "Đã sao chép" : "Sao chép khối mã"}
          className="inline-flex items-center gap-1 rounded px-1.5 py-0.5 transition-colors hover:opacity-80"
        >
          {daChep ? (
            <>
              <Check size={13} aria-hidden style={{ color: "var(--color-success)" }} />
              Đã chép
            </>
          ) : (
            <>
              <Copy size={13} aria-hidden />
              Chép
            </>
          )}
        </button>
      </div>
      <pre className="scroll-thin overflow-x-auto p-3" style={{ background: "var(--color-surface)" }}>
        <code className={className} style={{ fontFamily: "var(--font-mono)", fontSize: "13px" }}>
          {children}
        </code>
      </pre>
    </div>
  );
}

/**
 * `memo` ở đây KHÔNG phải tối ưu sớm: trong lúc stream, component cha render lại
 * mỗi mẩu chữ tới. Không memo thì cả cây markdown được phân giải lại vài chục
 * lần mỗi giây, và với câu trả lời dài thì giao diện giật thấy rõ.
 */
export const MarkdownRenderer = memo(function MarkdownRenderer({ noiDung }: { noiDung: string }) {
  return (
    <div className="prose-chat">
      <ReactMarkdown
        // `remarkBreaks` BẮT BUỘC với hệ thống này: Markdown chuẩn gộp một lần
        // xuống dòng đơn thành dấu cách, nên một bài thơ tám dòng gõ trong chat
        // hiện ra thành MỘT đoạn văn liền — mất hẳn hình thức của thể thơ.
        //
        // Sửa ở đây chứ không dặn mô hình thêm hai dấu cách cuối dòng: bắt prompt
        // đi vòng quanh một lỗi hiển thị là đặt cách chữa sai tầng, và nó hỏng lại
        // ngay khi văn bản đến từ nguồn khác (lịch sử hội thoại, tài liệu).
        remarkPlugins={[remarkGfm, remarkBreaks]}
        rehypePlugins={[[rehypeHighlight, { detect: true, ignoreMissing: true }]]}
        components={{
          code({ className, children, ...rest }) {
            // Mã nội dòng không có `language-*`; chỉ khối mới bọc khung.
            const laKhoi = /language-/.test(className ?? "");
            if (!laKhoi) {
              return (
                <code className={className} {...rest}>
                  {children}
                </code>
              );
            }
            return <KhoiMa className={className}>{children}</KhoiMa>;
          },
          pre({ children }) {
            // `KhoiMa` đã tự dựng <pre>; bỏ lớp <pre> ngoài để không lồng hai lần.
            return <>{children}</>;
          },
          a({ href, children }) {
            return (
              <a href={href} target="_blank" rel="noopener noreferrer">
                {children}
              </a>
            );
          },
          table({ children }) {
            return (
              <div className="scroll-thin overflow-x-auto">
                <table>{children}</table>
              </div>
            );
          },
        }}
      >
        {noiDung}
      </ReactMarkdown>
    </div>
  );
});
