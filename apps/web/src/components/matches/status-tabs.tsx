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
      className="bg-subtle flex w-fit max-w-full gap-1 overflow-x-auto rounded-lg p-1"
    >
      {MATCH_STATUSES.map((status) => {
        const isActive = status === filters.status;
        return (
          <Link
            key={status}
            href={matchesHref(withFilters(filters, { status }))}
            aria-current={isActive ? "page" : undefined}
            className={`flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium whitespace-nowrap transition-colors ${
              isActive
                ? "bg-surface text-fg shadow-sm"
                : "text-muted hover:text-fg"
            }`}
          >
            {LABELS[status]}
            <span
              className={`rounded-full px-1.5 text-xs tabular-nums ${
                isActive ? "bg-accent-soft text-accent-text" : "bg-line"
              }`}
            >
              {counts[status]}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
