import Link from "next/link";

import { MatchCard } from "@/components/matches/match-card";
import { EmptyState } from "@/components/ui/empty-state";
import { BriefcaseIcon } from "@/components/ui/icons";
import { secondaryButtonClassName } from "@/components/ui/styles";
import type { JobMatch, MatchStatus } from "@/lib/job-search/types";

const EMPTY_MESSAGES: Record<MatchStatus, { title: string; text: string }> = {
  new: {
    title: "You are all caught up",
    text: "No offer to review. New matches arrive with each search.",
  },
  saved: {
    title: "No saved offer yet",
    text: "Save the offers you want to apply to: they wait for you here.",
  },
  dismissed: {
    title: "Nothing dismissed",
    text: "Offers you dismiss end up here, in case you change your mind.",
  },
};

type MatchListProps = {
  matches: JobMatch[];
  status: MatchStatus;
  filtered: boolean; // true when filters may hide some matches
  clearFiltersHref: string;
};

export function MatchList({
  matches,
  status,
  filtered,
  clearFiltersHref,
}: MatchListProps) {
  if (matches.length === 0) {
    const message = filtered
      ? { title: "No offer fits these filters", text: "Try a wider search." }
      : EMPTY_MESSAGES[status];
    return (
      <EmptyState
        icon={<BriefcaseIcon className="size-5" />}
        title={message.title}
        description={message.text}
        action={
          filtered && (
            <Link href={clearFiltersHref} className={secondaryButtonClassName}>
              Clear filters
            </Link>
          )
        }
      />
    );
  }
  return (
    <ul className="flex flex-col gap-3">
      {matches.map((match) => (
        <li key={match.id}>
          <MatchCard match={match} />
        </li>
      ))}
    </ul>
  );
}
