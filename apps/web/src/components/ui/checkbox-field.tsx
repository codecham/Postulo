import type { ComponentProps } from "react";

type CheckboxFieldProps = Omit<ComponentProps<"input">, "type"> & {
  label: string;
};

export function CheckboxField({ label, ...inputProps }: CheckboxFieldProps) {
  return (
    <label className="flex items-center gap-2 text-sm">
      <input type="checkbox" className="size-4" {...inputProps} />
      {label}
    </label>
  );
}
