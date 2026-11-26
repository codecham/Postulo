import type { Metadata } from "next";

import { AppHeader } from "@/components/layout/app-header";
import { site } from "@/lib/site";

import "./globals.css";

export const metadata: Metadata = {
  title: { default: site.name, template: `%s · ${site.name}` },
  description: site.description,
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <a
          href="#content"
          className="bg-surface sr-only z-30 rounded-lg px-3 py-2 focus:not-sr-only focus:fixed focus:top-3 focus:left-3"
        >
          Skip to content
        </a>
        <AppHeader />
        <main
          id="content"
          className="mx-auto flex w-full max-w-6xl flex-1 flex-col px-4 py-8 sm:px-6 sm:py-10"
        >
          {children}
        </main>
      </body>
    </html>
  );
}
