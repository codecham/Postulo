import type { ReactNode } from "react";

import { FormSection } from "@/components/ui/form-section";

export type DraftItem = {
  key: string;
  summary: ReactNode;
  alreadyExists: boolean;
};

type DraftItemsFieldsProps = {
  title: string;
  emptyMessage: string;
  fieldName: string; // checked items are sent under this name, by index
  items: DraftItem[];
};

/** Items found in the CV (experiences, education), each with a checkbox to add it. */
export function DraftItemsFields({
  title,
  emptyMessage,
  fieldName,
  items,
}: DraftItemsFieldsProps) {
  return (
    <FormSection
      title={title}
      description="Checked items are added to your profile. You can edit them there afterwards."
    >
      {items.length === 0 ? (
        <p className="text-muted text-sm">{emptyMessage}</p>
      ) : (
        <ul className="divide-line flex flex-col divide-y">
          {items.map((item, index) => (
            <li key={item.key} className="py-4 first:pt-0 last:pb-0">
              <DraftItemOption
                fieldName={fieldName}
                index={index}
                alreadyExists={item.alreadyExists}
              >
                {item.summary}
              </DraftItemOption>
            </li>
          ))}
        </ul>
      )}
    </FormSection>
  );
}

type DraftItemOptionProps = {
  fieldName: string;
  index: number; // position in the draft: the value sent when checked
  alreadyExists: boolean;
  children: ReactNode;
};

function DraftItemOption({
  fieldName,
  index,
  alreadyExists,
  children,
}: DraftItemOptionProps) {
  return (
    <label className="flex items-start gap-3">
      <input
        type="checkbox"
        name={fieldName}
        value={index}
        // Unchecked when the user already has it, so it is not added twice
        defaultChecked={!alreadyExists}
        className="mt-1 size-4 shrink-0"
      />
      <div className="flex flex-col gap-1">
        {children}
        {alreadyExists && (
          <p className="text-muted text-xs">Already in your profile</p>
        )}
      </div>
    </label>
  );
}
