"use client";

import type { ReactNode } from "react";
import { useFormStatus } from "react-dom";

type SubmitButtonProps = {
  children: ReactNode;
  pendingLabel?: string;
  pending?: boolean; // only needed when the form is not submitted through its `action`
};

/** The submit button of the surrounding form, disabled while it is sent. */
export function SubmitButton({
  children,
  pendingLabel = "Saving…",
  pending,
}: SubmitButtonProps) {
  const status = useFormStatus();
  const isPending = pending ?? status.pending;
  return (
    <button
      type="submit"
      disabled={isPending}
      className="rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50 dark:bg-white dark:text-gray-900"
    >
      {isPending ? pendingLabel : children}
    </button>
  );
}
