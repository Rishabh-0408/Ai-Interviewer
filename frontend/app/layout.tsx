import type { Metadata } from "next";
import { Inter, Outfit, Geist_Mono } from "next/font/google";
import { AuthProvider } from "@/providers/auth-provider";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const outfit = Outfit({
  variable: "--font-outfit",
  subsets: ["latin"],
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "AI Interviewer — Evidence-Driven Interview Preparation",
  description:
    "Practice with an AI interviewer that researches your target role and company, analyzes interview patterns, and conducts realistic adaptive interviews.",
  keywords: [
    "AI interview",
    "interview preparation",
    "mock interview",
    "behavioral interview",
    "technical interview",
    "interview practice",
  ],
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${outfit.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
