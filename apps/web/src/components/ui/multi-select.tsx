"use client";

import { useState } from "react";

import { ChipList } from "@/components/ui/chip-list";
import {
  hintClassName,
  inputClassName,
  labelClassName,
} from "@/components/ui/styles";
import type { Option } from "@/lib/forms";

type MultiSelectProps = {
  label: string;
  name: string;
  options: Option[];
  defaultValue?: string[];
  placeholder?: string;
  hint?: string; // shown under the label
};

/**
 * Pick several values from a fixed list (countries, languages…).
 * The <select> has no name: only the chosen values are sent, as hidden inputs.
 */
export function MultiSelect({
  label,
  name,
  options,
  defaultValue = [],
  placeholder = "Add…",
  hint,
}: MultiSelectProps) {
  const [selected, setSelected] = useState(defaultValue);

  const selectedOptions = selected.map(
    (value) =>
      options.find((option) => option.value === value) ?? {
        value,
        label: value,
      },
  );
  const availableOptions = options.filter(
    (option) => !selected.includes(option.value),
  );

  return (
    <div className="flex flex-col gap-2">
      <label className={labelClassName}>
        {label}
        <select
          value=""
          onChange={(event) => setSelected([...selected, event.target.value])}
          className={inputClassName}
        >
          <option value="">{placeholder}</option>
          {availableOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        {hint && <span className={hintClassName}>{hint}</span>}
      </label>
      <ChipList
        name={name}
        items={selectedOptions}
        onRemove={(value) =>
          setSelected(selected.filter((item) => item !== value))
        }
      />
    </div>
  );
}
