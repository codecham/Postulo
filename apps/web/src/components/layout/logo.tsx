import Link from "next/link";

import { site } from "@/lib/site";

/** The app's mark and name, linking home. */
export function Logo() {
  return (
    <Link
      href="/"
      className="flex items-center gap-2 rounded-lg font-semibold tracking-tight"
    >
      <span
        aria-hidden
        className="bg-accent text-accent-fg flex size-7 items-center justify-center rounded-lg text-sm font-bold shadow-sm"
      >
        P
      </span>
      {site.name}
    </Link>
  );
}
