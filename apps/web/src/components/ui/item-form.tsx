"use client";

import { createContext, type ReactNode, useContext } from "react";

import { ActionForm } from "@/components/ui/action-form";
import { secondaryButtonClassName } from "@/components/ui/styles";
import type { FormState } from "@/lib/forms";

/** Closes the ItemForm opened by an EditableItem or an AddItem around it. */
export const CloseItemFormContext = createContext<() => void>(() => {});

type ItemFormProps = {
  action: (state: FormState, formData: FormData) => Promise<FormState>;
  submitLabel: string;
  children: ReactNode; // the fields: they can be Server Components
};

/** The form of one list item, to create or edit it. Cancel or a successful save closes it. */
export function ItemForm({ action, submitLabel, children }: ItemFormProps) {
  const close = useContext(CloseItemFormContext);

  async function saveThenClose(state: FormState, formData: FormData) {
    const nextState = await action(state, formData);
    if (nextState?.status === "success") {
      close();
    }
    return nextState;
  }

  return (
    <ActionForm
      action={saveThenClose}
      submitLabel={submitLabel}
      secondaryButton={
        <button
          type="button"
          onClick={close}
          className={secondaryButtonClassName}
        >
          Cancel
        </button>
      }
    >
      {children}
    </ActionForm>
  );
}
