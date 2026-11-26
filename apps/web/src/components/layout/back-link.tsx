import Link from "next/link";

import { ArrowLeftIcon } from "@/components/ui/icons";

type BackLinkProps = { href: string; label: string };

/** "← label": back to the page this one belongs to. */
export function BackLink({ href, label }: BackLinkProps) {
  return (
    <Link
      href={href}
      className="text-muted hover:text-fg flex w-fit max-w-full items-center gap-1.5 text-sm font-medium transition-colors"
    >
      <ArrowLeftIcon />
      <span className="truncate">{label}</span>
    </Link>
  );
}
