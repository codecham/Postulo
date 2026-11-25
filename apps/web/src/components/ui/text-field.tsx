import type { ComponentProps } from "react";

import {
  hintClassName,
  inputClassName,
  labelClassName,
} from "@/components/ui/styles";

type TextFieldProps = ComponentProps<"input"> & {
  label: string;
  hint?: string;
};

/** A labelled <input>. Every other prop goes to the input itself. */
export function TextField({ label, hint, ...inputProps }: TextFieldProps) {
  return (
    <label className={labelClassName}>
      {label}
      <input className={inputClassName} {...inputProps} />
      {hint && <span className={hintClassName}>{hint}</span>}
    </label>
  );
}
