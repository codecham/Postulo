import { useState } from "react";

/**
 * The values of a list field (tags, multi-select), starting from `defaultValue`.
 *
 * When `defaultValue` changes, for example after a CV import saved new skills, the
 * list follows it. A plain `useState(defaultValue)` would not: Next.js keeps visited
 * pages mounted, so it would keep showing, and then saving, the old values.
 */
export function useListState(defaultValue: string[]) {
  const [values, setValues] = useState(defaultValue);
  const [savedValue, setSavedValue] = useState(defaultValue);

  // Updating state while rendering is React's way to reset it when a prop changes
  if (!haveSameItems(savedValue, defaultValue)) {
    setSavedValue(defaultValue);
    setValues(defaultValue);
  }
  return [values, setValues] as const;
}

function haveSameItems(first: string[], second: string[]): boolean {
  return (
    first.length === second.length &&
    first.every((value, index) => value === second[index])
  );
}
