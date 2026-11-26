import Link from "next/link";

import { logout } from "@/app/(auth)/actions";
import { LogOutIcon } from "@/components/ui/icons";
import type { User } from "@/lib/auth/session";

/** The logged-in user: a link to their account, and a log out button. */
export function AccountMenu({ user }: { user: User }) {
  return (
    <div className="flex items-center gap-1">
      <Link
        href="/account"
        title="Your account"
        className="text-muted hover:bg-subtle hover:text-fg flex items-center gap-2 rounded-lg px-2 py-1.5 text-sm transition-colors"
      >
        <span
          aria-hidden
          className="bg-accent-soft text-accent-text flex size-7 items-center justify-center rounded-full text-xs font-semibold uppercase"
        >
          {user.email.charAt(0)}
        </span>
        <span className="hidden max-w-48 truncate lg:inline">{user.email}</span>
        <span className="sr-only lg:hidden">Your account</span>
      </Link>
      <form action={logout}>
        <button
          type="submit"
          title="Log out"
          className="text-muted hover:bg-subtle hover:text-fg flex size-9 items-center justify-center rounded-lg transition-colors"
        >
          <LogOutIcon />
          <span className="sr-only">Log out</span>
        </button>
      </form>
    </div>
  );
}
