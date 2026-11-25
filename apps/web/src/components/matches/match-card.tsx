import Link from "next/link";

import { MatchActions } from "@/components/matches/match-actions";
import { MatchReasons } from "@/components/matches/match-reasons";
import { OfferFacts } from "@/components/matches/offer-facts";
import { ScoreBadge } from "@/components/matches/score-badge";
import type { JobMatch } from "@/lib/job-search/types";

/** One match in the dashboard: the offer, why it fits, and what to do with it. */
export function MatchCard({ match }: { match: JobMatch }) {
  const { offer } = match;

  return (
    <article className="flex flex-col gap-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex flex-col gap-1">
          <Link
            href={`/jobs/${match.id}`}
            className="font-semibold hover:underline"
          >
            {offer.title}
          </Link>
          <OfferFacts offer={offer} />
        </div>
        <ScoreBadge score={match.score} />
      </div>
      <MatchReasons match={match} />
      <div className="flex flex-wrap items-center justify-between gap-2">
        <MatchActions match={match} />
        <a
          href={offer.url}
          target="_blank"
          rel="noopener"
          className="text-sm underline"
        >
          Open on {offer.source} ↗
        </a>
      </div>
    </article>
  );
}
