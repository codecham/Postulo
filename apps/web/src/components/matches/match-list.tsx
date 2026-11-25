import { MatchCard } from "@/components/matches/match-card";
import type { JobMatch, MatchStatus } from "@/lib/job-search/types";

const EMPTY_MESSAGES: Record<MatchStatus, string> = {
  new: "No offer to review. New matches arrive with each search.",
  saved: "No saved offer yet. Save the ones you want to apply to.",
  dismissed: "No dismissed offer.",
};

type MatchListProps = {
  matches: JobMatch[];
  status: MatchStatus;
  filtered: boolean; // true when filters may hide some matches
};

export function MatchList({ matches, status, filtered }: MatchListProps) {
  if (matches.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-gray-300 p-6 text-center text-sm text-gray-600 dark:border-gray-700 dark:text-gray-400">
        {filtered ? "No offer fits these filters." : EMPTY_MESSAGES[status]}
      </p>
    );
  }
  return (
    <ul className="flex flex-col divide-y divide-gray-200 rounded-lg border border-gray-200 dark:divide-gray-800 dark:border-gray-800">
      {matches.map((match) => (
        <li key={match.id} className="p-5">
          <MatchCard match={match} />
        </li>
      ))}
    </ul>
  );
}
