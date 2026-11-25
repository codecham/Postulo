import Link from "next/link";

import { secondaryButtonClassName } from "@/components/ui/styles";
import {
  type MatchFilters,
  matchesHref,
  PAGE_SIZE,
} from "@/lib/job-search/match-filters";

type PagerProps = { filters: MatchFilters; total: number };

/** Previous / next page links, when the matches do not fit on one page. */
export function Pager({ filters, total }: PagerProps) {
  const pages = Math.ceil(total / PAGE_SIZE);
  if (pages <= 1) {
    return null;
  }
  const pageHref = (page: number) => matchesHref({ ...filters, page });

  return (
    <nav
      aria-label="Pages"
      className="flex items-center justify-between text-sm"
    >
      {filters.page > 1 ? (
        <Link
          href={pageHref(filters.page - 1)}
          className={secondaryButtonClassName}
        >
          ← Previous
        </Link>
      ) : (
        <span />
      )}
      <span className="text-gray-500">
        Page {filters.page} of {pages}
      </span>
      {filters.page < pages ? (
        <Link
          href={pageHref(filters.page + 1)}
          className={secondaryButtonClassName}
        >
          Next →
        </Link>
      ) : (
        <span />
      )}
    </nav>
  );
}
