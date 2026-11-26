"use client";

import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

import { Spinner } from "@/components/ui/spinner";
import { buttonClassName, type ButtonVariant } from "@/components/ui/styles";

type StatusButtonProps = {
  children: ReactNode;
  variant?: ButtonVariant;
};

/** A small submit button that shows it is working while its form is sent. */
export function StatusButton({
  children,
  variant = "secondary",
}: StatusButtonProps) {
  const { pending } = useFormStatus();
  return (
    <button
      type="submit"
      disabled={pending}
      aria-busy={pending}
      className={buttonClassName(variant)}
    >
      {pending ? <Spinner /> : null}
      {children}
    </button>
  );
}
