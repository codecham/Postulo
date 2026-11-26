"use client";

import { type ReactNode, useState } from "react";

import { CloseItemFormContext } from "@/components/ui/item-form";
import { PencilIcon } from "@/components/ui/icons";
import { secondaryButtonClassName } from "@/components/ui/styles";

type EditableItemProps = {
  summary: ReactNode; // what the item shows
  editForm: ReactNode; // an ItemForm, shown after a click on Edit
  actions?: ReactNode; // more buttons next to Edit, such as Delete
};

/** A list item: its summary, or its edit form. Every part can be a Server Component. */
export function EditableItem({
  summary,
  editForm,
  actions,
}: EditableItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  if (isEditing) {
    return (
      <CloseItemFormContext value={() => setIsEditing(false)}>
        {editForm}
      </CloseItemFormContext>
    );
  }

  return (
    <div className="flex items-start justify-between gap-4">
      {summary}
      <div className="flex shrink-0 gap-2">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className={secondaryButtonClassName}
        >
          <PencilIcon />
          Edit
        </button>
        {actions}
      </div>
    </div>
  );
}
