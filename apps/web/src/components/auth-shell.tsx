import type { ReactNode } from "react";

import { cardClassName } from "@/components/ui/card";

type AuthShellProps = {
  title: string;
  description: string;
  footer: ReactNode; // e.g. a link to the other auth page
  children: ReactNode;
};

/** The centered card of the log in and sign up pages. */
export function AuthShell({
  title,
  description,
  footer,
  children,
}: AuthShellProps) {
  return (
    <section className="mx-auto flex w-full max-w-sm flex-col gap-6 py-6 sm:py-12">
      <div className="flex flex-col gap-1.5 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-muted text-sm">{description}</p>
      </div>
      <div className={`${cardClassName} p-6`}>{children}</div>
      <p className="text-muted text-center text-sm">{footer}</p>
    </section>
  );
}
