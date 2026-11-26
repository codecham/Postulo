"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTransition } from "react";

import { buttonClassName, inputClassName } from "@/components/ui/styles";
import type { Option } from "@/lib/forms";
import type { FilterOptions } from "@/lib/job-search/filter-options";
import {
  type FilterName,
  hasActiveFilters,
  type MatchFilters,
  matchesHref,
  withFilters,
} from "@/lib/job-search/match-filters";

type MatchFilterBarProps = {
  filters: MatchFilters;
  options: FilterOptions;
  sortOptions: Option[];
};

const FILTER_LABELS: Record<Exclude<FilterName, "sort">, string> = {
  min_score: "Score",
  work_mode: "Work mode",
  country: "Country",
  language: "Language",
  source: "Job board",
  max_age_days: "Posted",
};

/** One select per filter: choosing a value updates the URL, so the list reloads. */
export function MatchFilterBar({
  filters,
  options,
  sortOptions,
}: MatchFilterBarProps) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();

  function change(name: FilterName, value: string) {
    const href = matchesHref(withFilters(filters, { [name]: value }));
    startTransition(() => router.push(href, { scroll: false }));
  }

  return (
    <div
      aria-busy={isPending}
      className={`grid grid-cols-2 items-end gap-3 transition-opacity sm:grid-cols-4 lg:grid-cols-7 ${isPending ? "opacity-60" : ""}`}
    >
      {(Object.keys(FILTER_LABELS) as (keyof typeof FILTER_LABELS)[]).map(
        (name) => (
          <FilterSelect
            key={name}
            label={FILTER_LABELS[name]}
            value={filters[name] ?? ""}
            options={options[name]}
            onChange={(value) => change(name, value)}
          />
        ),
      )}
      <FilterSelect
        label="Sort by"
        value={filters.sort}
        options={sortOptions}
        onChange={(value) => change("sort", value)}
      />
      {hasActiveFilters(filters) && (
        <Link
          href={matchesHref({
            status: filters.status,
            sort: filters.sort,
            page: 1,
          })}
          className={`${buttonClassName("ghost")} justify-self-start`}
        >
          Clear filters
        </Link>
      )}
    </div>
  );
}

type FilterSelectProps = {
  label: string;
  value: string;
  options: Option[];
  onChange: (value: string) => void;
};

function FilterSelect({ label, value, options, onChange }: FilterSelectProps) {
  return (
    <label className="text-muted flex min-w-0 flex-col gap-1 text-xs font-medium">
      {label}
      <select
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className={`${inputClassName} text-fg py-1.5 text-sm`}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
