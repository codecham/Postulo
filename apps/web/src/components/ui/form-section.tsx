import type { ReactNode } from "react";

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
    <fieldset className="flex flex-col gap-4 rounded-lg border border-gray-200 p-5 dark:border-gray-800">
      <legend className="px-1 font-semibold">{title}</legend>
      {description && (
        <p className="-mt-2 text-sm text-gray-600 dark:text-gray-400">
          {description}
        </p>
      )}
      {children}
    </fieldset>
  );
}
