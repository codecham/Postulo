// Server only: option names come from the Intl API, whose data differs between
// Node.js and browsers. Computing them on the server keeps the HTML identical.
import "server-only";

import type { Option } from "@/lib/forms";
import { COUNTRY_CODES } from "@/lib/profile/country-codes";
import type { WorkMode } from "@/lib/profile/types";

export const WORK_MODE_OPTIONS: { value: WorkMode; label: string }[] = [
  { value: "remote", label: "Remote" },
  { value: "hybrid", label: "Hybrid" },
  { value: "onsite", label: "On site" },
];

// ISO 639-1 codes of the languages most asked for in job offers
// prettier-ignore
const LANGUAGE_CODES = [
  "ar", "cs", "da", "de", "el", "en", "es", "fi", "fr", "he", "hi", "hu",
  "it", "ja", "ko", "nl", "no", "pl", "pt", "ro", "ru", "sv", "tr", "uk", "zh",
];

export const COUNTRY_OPTIONS = toSortedOptions(COUNTRY_CODES, "region");
export const LANGUAGE_OPTIONS = toSortedOptions(LANGUAGE_CODES, "language");

/** Codes with their English names (from the Intl API), sorted by name. */
function toSortedOptions(
  codes: readonly string[],
  type: "region" | "language",
): Option[] {
  const names = new Intl.DisplayNames(["en"], { type });
  return codes
    .map((code) => ({ value: code, label: names.of(code) ?? code }))
    .sort((a, b) => a.label.localeCompare(b.label));
}
