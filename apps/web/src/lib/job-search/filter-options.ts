import "server-only";

import type { Option } from "@/lib/forms";
import {
  countryName,
  languageName,
  WORK_MODE_LABELS,
} from "@/lib/job-search/labels";
import type { MatchFacets } from "@/lib/job-search/types";

/** The choices of each filter of the dashboard ("" means any). */
export type FilterOptions = {
  min_score: Option[];
  work_mode: Option[];
  country: Option[];
  language: Option[];
  source: Option[];
  max_age_days: Option[];
};

export const SORT_OPTIONS: Option[] = [
  { value: "score", label: "Best match" },
  { value: "date", label: "Newest" },
];

/** Countries, languages and sources only list the values found in the matches. */
export function buildFilterOptions(facets: MatchFacets): FilterOptions {
  return {
    min_score: [
      { value: "", label: "Any score" },
      ...[50, 60, 70, 80].map((score) => ({
        value: String(score),
        label: `${score}+`,
      })),
    ],
    work_mode: [
      { value: "", label: "Any work mode" },
      ...Object.entries(WORK_MODE_LABELS).map(([value, label]) => ({
        value,
        label,
      })),
    ],
    country: withAny("Any country", facets.countries, countryName),
    language: withAny("Any language", facets.languages, languageName),
    source: withAny("Any job board", facets.sources, (source) => source),
    max_age_days: [
      { value: "", label: "Any date" },
      { value: "1", label: "Last 24 hours" },
      { value: "3", label: "Last 3 days" },
      { value: "7", label: "Last week" },
      { value: "14", label: "Last 2 weeks" },
    ],
  };
}

function withAny(
  anyLabel: string,
  values: string[],
  toLabel: (value: string) => string,
): Option[] {
  const options = values
    .map((value) => ({ value, label: toLabel(value) }))
    .sort((a, b) => a.label.localeCompare(b.label));
  return [{ value: "", label: anyLabel }, ...options];
}
