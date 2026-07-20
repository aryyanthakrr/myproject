import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MergeLab - One-Click AI Model Merging",
  description: "Merge AI models in one click. Select two models, choose a method, and get your custom merged model ready to download or deploy.",
  keywords: ["AI", "Model Merging", "Machine Learning", "LLM", "HuggingFace"],
  authors: [{ name: "intellectlabs", url: "https://intellectlabs.ai" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="bg-background text-white antialiased min-h-screen flex flex-col">
        {children}
      </body>
    </html>
  );
}
