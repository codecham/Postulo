import { MatchItem } from "@/components/job-search/match-item";
import { ListSection } from "@/components/ui/list-section";
import type { JobMatch } from "@/lib/job-search/types";

export function MatchList({ matches }: { matches: JobMatch[] }) {
  return (
    <ListSection
      title="Best matches"
      emptyMessage="No matching offer yet."
      items={matches.map((match) => ({
        key: match.id,
        content: <MatchItem match={match} />,
      }))}
    />
  );
}
