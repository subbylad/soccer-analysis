import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/layout/Providers";

const inter = Inter({
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Soccer Scout AI - AI-Powered Football Analysis",
  description: "Advanced AI-powered soccer scouting and player analysis tool with GPT-4 intelligence. Compare players, discover talent, and get tactical insights.",
  keywords: ["soccer", "football", "scouting", "AI", "player analysis", "tactics", "GPT-4"],
  authors: [{ name: "Soccer Scout AI Team" }],
  creator: "Soccer Scout AI",
  publisher: "Soccer Scout AI",
  formatDetection: {
    telephone: false,
  },
  metadataBase: new URL("http://localhost:3000"),
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "http://localhost:3000",
    title: "Soccer Scout AI - AI-Powered Football Analysis",
    description: "Advanced AI-powered soccer scouting and player analysis tool with GPT-4 intelligence.",
    siteName: "Soccer Scout AI",
  },
  twitter: {
    card: "summary_large_image",
    title: "Soccer Scout AI - AI-Powered Football Analysis",
    description: "Advanced AI-powered soccer scouting and player analysis tool with GPT-4 intelligence.",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="font-sans antialiased">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
