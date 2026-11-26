"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { BriefcaseIcon, SendIcon, UserIcon } from "@/components/ui/icons";

type NavLink = { href: string; label: string; icon: ReactNode };

const LINKS: NavLink[] = [
  { href: "/jobs", label: "Jobs", icon: <BriefcaseIcon /> },
  { href: "/applications", label: "Applications", icon: <SendIcon /> },
  { href: "/profile", label: "Profile", icon: <UserIcon /> },
];

/** The app's main sections; the current one is highlighted. */
export function NavLinks() {
  const pathname = usePathname();

  return (
    <nav aria-label="Main" className="flex gap-1 overflow-x-auto">
      {LINKS.map((link) => {
        const isActive =
          pathname === link.href || pathname.startsWith(`${link.href}/`);
        return (
          <Link
            key={link.href}
            href={link.href}
            aria-current={isActive ? "page" : undefined}
            className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-colors ${
              isActive
                ? "bg-accent-soft text-accent-text"
                : "text-muted hover:bg-subtle hover:text-fg"
            }`}
          >
            {link.icon}
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
