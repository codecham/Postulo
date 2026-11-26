import type { ComponentProps } from "react";

import {
  hintClassName,
  inputClassName,
  labelClassName,
} from "@/components/ui/styles";

type TextareaFieldProps = ComponentProps<"textarea"> & {
  label: string;
  hint?: string;
};

/** A labelled <textarea>. Every other prop goes to the textarea itself. */
export function TextareaField({
  label,
  hint,
  rows = 4,
  className = "",
  ...textareaProps
}: TextareaFieldProps) {
  return (
    <label className={labelClassName}>
      {label}
      <textarea
        className={`${inputClassName} ${className}`}
        rows={rows}
        {...textareaProps}
      />
      {hint && <span className={hintClassName}>{hint}</span>}
    </label>
  );
}
