import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "华南AI岗位聚合 | AI应用工程师招聘",
  description: "聚合腾讯、字节、阿里、华为、网易及央国企AI岗位，专注广州深圳，每日自动更新",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-CN">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">{children}</body>
    </html>
  );
}
