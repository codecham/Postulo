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
    <div className="border-line bg-canvas/50 flex flex-col gap-4 rounded-lg border p-4">
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
