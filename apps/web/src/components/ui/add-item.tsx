"use client";

import { type ReactNode, useState } from "react";

import { CloseItemFormContext } from "@/components/ui/item-form";
import { secondaryButtonClassName } from "@/components/ui/styles";

type AddItemProps = {
  label: string; // e.g. "Add an experience"
  form: ReactNode; // an empty ItemForm
};

/** A "+ Add…" button that opens an empty form. */
export function AddItem({ label, form }: AddItemProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (isOpen) {
    return (
      <CloseItemFormContext value={() => setIsOpen(false)}>
        {form}
      </CloseItemFormContext>
    );
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className={secondaryButtonClassName}
      >
        <span aria-hidden>+</span> {label}
      </button>
    </div>
  );
}
