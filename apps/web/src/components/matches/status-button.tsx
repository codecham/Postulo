"use client";

import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

import { secondaryButtonClassName } from "@/components/ui/styles";

/** A small submit button that shows it is working while its form is sent. */
export function StatusButton({ children }: { children: ReactNode }) {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      className={`${secondaryButtonClassName} disabled:opacity-50`}
    >
      {pending ? "…" : children}
    </button>
  );
}
