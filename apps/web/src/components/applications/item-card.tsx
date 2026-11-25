import type { ReactNode } from "react";

import { CheckboxField } from "@/components/ui/checkbox-field";

type ItemCardProps = {
  keepField: string; // name of the "keep it" checkbox; its value is the item's index
  index: number;
  children: ReactNode;
};

/** One experience or education of the CV, with a checkbox to leave it out. */
export function ItemCard({ keepField, index, children }: ItemCardProps) {
  return (
    <div className="flex flex-col gap-4 rounded-md border border-gray-200 p-4 dark:border-gray-800">
      <CheckboxField
        label="Keep in the CV"
        name={keepField}
        value={index}
        defaultChecked
      />
      {children}
    </div>
  );
}
