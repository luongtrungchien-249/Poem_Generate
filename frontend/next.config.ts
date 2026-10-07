import type { NextConfig } from "next";

/**
 * KHÔNG dùng `output: "export"`.
 *
 * Bản tĩnh không chạy được route handler, mà route handler chính là nơi giữ khoá
 * API (xem `app/api/_backend.ts`). Xuất tĩnh nghĩa là khoá phải nằm trong mã
 * client — tức là công khai. Đây là ràng buộc kiến trúc, không phải tuỳ chọn.
 */
const nextConfig: NextConfig = {
  reactStrictMode: true,
  // Không đặt biến backend vào `env`/`NEXT_PUBLIC_*`: mọi thứ ở đó đều được nhúng
  // vào bundle client. Backend URL và khoá chỉ đọc qua `process.env` phía server.
};

export default nextConfig;
