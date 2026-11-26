import type { ReactNode } from "react";

import { cardClassName } from "@/components/ui/card";

type FormSectionProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

/** A titled group of fields inside a form. */
export function FormSection({
  title,
  description,
  children,
}: FormSectionProps) {
  return (
    <fieldset
      className={`${cardClassName} flex min-w-0 flex-col gap-4 p-5 sm:p-6`}
    >
      {/* A float legend sits inside the card like a heading, instead of on its border */}
      <legend className="float-left mb-1 w-full font-semibold">{title}</legend>
      {description && <p className="text-muted -mt-3 text-sm">{description}</p>}
      {children}
    </fieldset>
  );
}
