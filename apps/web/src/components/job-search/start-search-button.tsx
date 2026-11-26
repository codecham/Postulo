"use client";

import { useActionState } from "react";

import { startJobSearch } from "@/app/jobs/actions";
import { FormMessage } from "@/components/ui/form-message";
import { SubmitButton } from "@/components/ui/submit-button";

/** Starts a search now, instead of waiting for the daily one. */
export function StartSearchButton({ disabled }: { disabled: boolean }) {
  const [state, formAction] = useActionState(startJobSearch, undefined);

  return (
    <form
      action={formAction}
      className="flex flex-row-reverse flex-wrap items-center gap-3"
    >
      {/* While a search runs, the button stays disabled until the page refreshes */}
      <SubmitButton
        pending={disabled || undefined}
        pendingLabel={disabled ? "Searching…" : "Starting…"}
        variant="secondary"
        size="sm"
      >
        Search now
      </SubmitButton>
      <FormMessage state={state} />
    </form>
  );
}
