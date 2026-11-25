import Link from "next/link";

import {
  MATCH_STATUSES,
  type MatchFilters,
  matchesHref,
  withFilters,
} from "@/lib/job-search/match-filters";
import type { JobMatchPage, MatchStatus } from "@/lib/job-search/types";

const LABELS: Record<MatchStatus, string> = {
  new: "To review",
  saved: "Saved",
  dismissed: "Dismissed",
};

type StatusTabsProps = {
  filters: MatchFilters;
  counts: JobMatchPage["counts"];
};

/** Switch between the matches to review, the saved ones and the dismissed ones. */
export function StatusTabs({ filters, counts }: StatusTabsProps) {
  return (
    <nav
      aria-label="Match status"
      className="flex gap-1 border-b border-gray-200 dark:border-gray-800"
    >
      {MATCH_STATUSES.map((status) => {
        const isActive = status === filters.status;
        return (
          <Link
            key={status}
            href={matchesHref(withFilters(filters, { status }))}
            aria-current={isActive ? "page" : undefined}
            className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
              isActive
                ? "border-gray-900 dark:border-white"
                : "border-transparent text-gray-500 hover:text-gray-900 dark:hover:text-white"
            }`}
          >
            {LABELS[status]}{" "}
            <span className="text-gray-500 tabular-nums">{counts[status]}</span>
          </Link>
        );
      })}
    </nav>
  );
}
