import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LDK Athlete AI Coach",
  description: "Planning UI for the Athlete AI Coach platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full flex flex-col font-sans">{children}</body>
    </html>
  );
}
