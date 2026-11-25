"use client";

import { type KeyboardEvent, useState } from "react";

import { ChipList } from "@/components/ui/chip-list";
import {
  hintClassName,
  inputClassName,
  labelClassName,
} from "@/components/ui/styles";
import { useListState } from "@/components/ui/use-list-state";

type TagInputProps = {
  label: string;
  name: string;
  defaultValue?: string[];
  placeholder?: string;
  maxLength?: number;
};

/** Free-text values (skills, job titles…): type one, then press Enter or a comma. */
export function TagInput({
  label,
  name,
  defaultValue = [],
  placeholder,
  maxLength = 100,
}: TagInputProps) {
  const [tags, setTags] = useListState(defaultValue);
  const [draft, setDraft] = useState("");

  function addTags(values: string[]) {
    const next = [...tags];
    for (const value of values.map((item) => item.trim())) {
      const isNew = !next.some(
        (tag) => tag.toLowerCase() === value.toLowerCase(),
      );
      if (value && isNew) {
        next.push(value);
      }
    }
    setTags(next);
  }

  function addDraft() {
    addTags([draft]);
    setDraft("");
  }

  // A comma, typed or pasted ("Python, SQL"), separates tags
  function handleChange(value: string) {
    const parts = value.split(",");
    if (parts.length > 1) {
      addTags(parts.slice(0, -1));
    }
    setDraft(parts.at(-1) ?? "");
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter") {
      event.preventDefault(); // Enter would submit the form
      addDraft();
    } else if (event.key === "Backspace" && !draft && tags.length > 0) {
      setTags(tags.slice(0, -1));
    }
  }

  return (
    <div className="flex flex-col gap-2">
      <label className={labelClassName}>
        {label}
        <input
          value={draft}
          onChange={(event) => handleChange(event.target.value)}
          onKeyDown={handleKeyDown}
          onBlur={addDraft} // keep what was typed when the user clicks Save
          placeholder={placeholder}
          maxLength={maxLength}
          className={inputClassName}
        />
        <span className={hintClassName}>
          Press Enter or type a comma to add.
        </span>
      </label>
      <ChipList
        name={name}
        items={tags.map((tag) => ({ value: tag, label: tag }))}
        onRemove={(value) => setTags(tags.filter((tag) => tag !== value))}
      />
    </div>
  );
}
