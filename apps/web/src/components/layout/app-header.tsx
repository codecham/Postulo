import { Suspense } from "react";

import { Logo } from "@/components/layout/logo";
import { UserMenu } from "@/components/user-menu";

/** The bar at the top of every page: logo, sections and account. */
export function AppHeader() {
  return (
    <header className="border-line bg-surface/85 sticky top-0 z-20 border-b backdrop-blur">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center gap-x-6 gap-y-2 px-4 py-3 sm:px-6">
        <Logo />
        {/* Reading the session happens per request, so it streams in */}
        <Suspense fallback={null}>
          <UserMenu />
        </Suspense>
      </div>
    </header>
  );
}
