// The dashboard's filters live in the URL (/jobs?status=saved&country=BE&page=2):
// shareable, kept on reload, and read by the server to load the matches.
import type {
  MatchQuery,
  MatchSort,
  MatchStatus,
} from "@/lib/job-search/types";
import type { WorkMode } from "@/lib/profile/types";

export const PAGE_SIZE = 20;

export const MATCH_STATUSES: MatchStatus[] = ["new", "saved", "dismissed"];
const SORTS: MatchSort[] = ["score", "date"];
const WORK_MODES: WorkMode[] = ["remote", "hybrid", "onsite"];

/** The filters as the URL holds them. A missing value means "any". */
export type MatchFilters = {
  status: MatchStatus;
  sort: MatchSort;
  page: number;
  min_score?: string;
  work_mode?: string;
  country?: string;
  language?: string;
  source?: string;
  max_age_days?: string;
};

export type FilterName = Exclude<keyof MatchFilters, "status" | "page">;

type SearchParams = Record<string, string | string[] | undefined>;

/** Read the filters from the page's search params, ignoring unknown values. */
export function readMatchFilters(params: SearchParams): MatchFilters {
  const value = (name: string) => firstValue(params[name]);
  return {
    status: oneOf(value("status"), MATCH_STATUSES) ?? "new",
    sort: oneOf(value("sort"), SORTS) ?? "score",
    page: Math.max(positiveInt(value("page")) ?? 1, 1),
    min_score: value("min_score"),
    work_mode: oneOf(value("work_mode"), WORK_MODES),
    country: value("country"),
    language: value("language"),
    source: value("source"),
    max_age_days: value("max_age_days"),
  };
}

/** The API query for these filters. */
export function toMatchQuery(filters: MatchFilters): MatchQuery {
  return {
    status: filters.status,
    sort: filters.sort,
    limit: PAGE_SIZE,
    offset: (filters.page - 1) * PAGE_SIZE,
    min_score: positiveInt(filters.min_score),
    work_mode: listOf(oneOf(filters.work_mode, WORK_MODES)),
    country: listOf(filters.country),
    language: listOf(filters.language),
    source: listOf(filters.source),
    max_age_days: positiveInt(filters.max_age_days),
  };
}

/** The dashboard's URL with these filters, leaving out the default values. */
export function matchesHref(filters: MatchFilters): string {
  const params = new URLSearchParams();
  for (const [name, value] of Object.entries(filters)) {
    if (value !== undefined && value !== "" && !isDefault(name, value)) {
      params.set(name, String(value));
    }
  }
  const query = params.toString();
  return query ? `/jobs?${query}` : "/jobs";
}

/** The same filters with some changed: back to the first page, as the list changes. */
export function withFilters(
  filters: MatchFilters,
  changes: Partial<MatchFilters>,
): MatchFilters {
  return { ...filters, page: 1, ...changes };
}

export function hasActiveFilters(filters: MatchFilters): boolean {
  const names: FilterName[] = [
    "min_score",
    "work_mode",
    "country",
    "language",
    "source",
    "max_age_days",
  ];
  return names.some((name) => Boolean(filters[name]));
}

const DEFAULTS: Record<string, unknown> = {
  status: "new",
  sort: "score",
  page: 1,
};

function isDefault(name: string, value: unknown): boolean {
  return DEFAULTS[name] === value;
}

function firstValue(value: string | string[] | undefined): string | undefined {
  const first = Array.isArray(value) ? value[0] : value;
  return first?.trim() || undefined;
}

function oneOf<T extends string>(
  value: string | undefined,
  allowed: readonly T[],
): T | undefined {
  return allowed.find((item) => item === value);
}

function positiveInt(value: string | undefined): number | undefined {
  const number = Number(value);
  return Number.isInteger(number) && number > 0 ? number : undefined;
}

function listOf<T>(value: T | undefined): T[] | undefined {
  return value === undefined ? undefined : [value];
}
