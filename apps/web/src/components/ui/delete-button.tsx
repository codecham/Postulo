"use client";

import type { FormEvent } from "react";

import { secondaryButtonClassName } from "@/components/ui/styles";

type DeleteButtonProps = {
  action: () => Promise<void>; // a server action, with its id already bound
  confirmMessage: string; // e.g. "Delete this experience?"
  label?: string;
};

/** A Delete (or other undo) button that asks for confirmation first. */
export function DeleteButton({
  action,
  confirmMessage,
  label = "Delete",
}: DeleteButtonProps) {
  function confirmDelete(event: FormEvent<HTMLFormElement>) {
    if (!window.confirm(confirmMessage)) {
      event.preventDefault();
    }
  }

  return (
    <form action={action} onSubmit={confirmDelete}>
      <button type="submit" className={secondaryButtonClassName}>
        {label}
      </button>
    </form>
  );
}
