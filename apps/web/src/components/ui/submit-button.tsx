"use client";

import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

import { Spinner } from "@/components/ui/spinner";
import {
  type ButtonSize,
  buttonClassName,
  type ButtonVariant,
} from "@/components/ui/styles";

type SubmitButtonProps = {
  children: ReactNode;
  pendingLabel?: string;
  pending?: boolean; // only needed when the form is not submitted through its `action`
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
};

/** The submit button of the surrounding form, disabled while it is sent. */
export function SubmitButton({
  children,
  pendingLabel = "Saving…",
  pending,
  variant = "primary",
  size = "md",
  fullWidth = false,
}: SubmitButtonProps) {
  const status = useFormStatus();
  const isPending = pending ?? status.pending;
  return (
    <button
      type="submit"
      disabled={isPending}
      aria-busy={isPending}
      className={`${buttonClassName(variant, size)} ${fullWidth ? "w-full" : ""}`}
    >
      {isPending ? (
        <>
          <Spinner />
          {pendingLabel}
        </>
      ) : (
        children
      )}
    </button>
  );
}
