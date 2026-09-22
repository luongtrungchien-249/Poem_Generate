import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Thơ thất ngôn",
  description: "Sinh thơ thất ngôn tự do có kiểm định bảy tầng luật.",
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#fffdfe" },
    { media: "(prefers-color-scheme: dark)", color: "#171318" },
  ],
};

/**
 * Áp chủ đề TRƯỚC khi React dựng cây, nếu không sẽ có một nháy trắng ở chế độ
 * tối: HTML tĩnh về trước với nền sáng, rồi JavaScript mới đổi lại. Script này
 * chạy đồng bộ ở <head> nên người dùng không kịp thấy khung hình sáng nào.
 */
const SCRIPT_CHU_DE = `
try {
  var v = localStorage.getItem('poem-ui-theme');
  if (v === 'light' || v === 'dark') document.documentElement.setAttribute('data-theme', v);
} catch (e) {}
`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: SCRIPT_CHU_DE }} />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
