"use client";

import type { ChangeEvent, ComponentProps } from "react";

import {
  hintClassName,
  inputClassName,
  labelClassName,
} from "@/components/ui/styles";

type FileFieldProps = Omit<ComponentProps<"input">, "type"> & {
  label: string;
  hint?: string;
  maxBytes?: number;
  tooLargeMessage?: string;
};

/**
 * A labelled file input. A file over `maxBytes` makes the input invalid, so the
 * browser blocks the submit and shows `tooLargeMessage` before any upload.
 */
export function FileField({
  label,
  hint,
  maxBytes,
  tooLargeMessage = "This file is too large.",
  onChange,
  ...inputProps
}: FileFieldProps) {
  function handleChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0];
    const isTooLarge = maxBytes !== undefined && (file?.size ?? 0) > maxBytes;
    event.currentTarget.setCustomValidity(isTooLarge ? tooLargeMessage : "");
    event.currentTarget.reportValidity();
    onChange?.(event);
  }

  return (
    <label className={labelClassName}>
      {label}
      <input
        type="file"
        className={inputClassName}
        onChange={handleChange}
        {...inputProps}
      />
      {hint && <span className={hintClassName}>{hint}</span>}
    </label>
  );
}
