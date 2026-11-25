"use client";

import {
  type FormEvent,
  type ReactNode,
  startTransition,
  useActionState,
} from "react";

import { FormMessage } from "@/components/ui/form-message";
import { SubmitButton } from "@/components/ui/submit-button";
import type { FormState } from "@/lib/forms";

type ActionFormProps = {
  action: (state: FormState, formData: FormData) => Promise<FormState>;
  submitLabel: string;
  pendingLabel?: string; // shown on the submit button while the action runs
  secondaryButton?: ReactNode; // e.g. a Cancel button, next to the submit button
  children: ReactNode; // the fields: they can be Server Components
};

/**
 * A form that calls a server action and shows the message it returns.
 * Only this wrapper runs in the browser: the fields passed as children can be
 * rendered on the server.
 */
export function ActionForm({
  action,
  submitLabel,
  pendingLabel,
  secondaryButton,
  children,
}: ActionFormProps) {
  const [state, formAction, isPending] = useActionState(action, undefined);

  // With <form action={...}>, React empties the fields after every submit, so a
  // rejected form would lose what the user typed. Submitting by hand keeps it.
  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    startTransition(() => formAction(formData));
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-6">
      {children}
      <div className="flex flex-wrap items-center gap-4">
        <SubmitButton pending={isPending} pendingLabel={pendingLabel}>
          {submitLabel}
        </SubmitButton>
        {secondaryButton}
        <FormMessage state={state} />
      </div>
    </form>
  );
}
