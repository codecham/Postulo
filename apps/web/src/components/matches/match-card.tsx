import Link from "next/link";

import { MatchActions } from "@/components/matches/match-actions";
import { MatchReasons } from "@/components/matches/match-reasons";
import { OfferFacts } from "@/components/matches/offer-facts";
import { ScoreBadge } from "@/components/matches/score-badge";
import { cardClassName } from "@/components/ui/card";
import { ArrowRightIcon, ExternalLinkIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
import type { JobMatch } from "@/lib/job-search/types";

/** One match in the dashboard: the offer, why it fits, and what to do with it. */
export function MatchCard({ match }: { match: JobMatch }) {
  const { offer } = match;

  return (
    <article
      className={`${cardClassName} flex flex-col gap-4 p-5 transition-shadow hover:shadow-md`}
    >
      <div className="flex items-start gap-4">
        <ScoreBadge score={match.score} />
        <div className="flex min-w-0 flex-col gap-1">
          <h2 className="font-semibold text-balance">
            <Link href={`/jobs/${match.id}`} className="hover:text-accent-text">
              {offer.title}
            </Link>
          </h2>
          <OfferFacts offer={offer} />
        </div>
      </div>
      <MatchReasons match={match} />
      <div className="border-line flex flex-wrap items-center justify-between gap-2 border-t pt-4">
        <MatchActions match={match} />
        <div className="flex flex-wrap gap-2">
          <a
            href={offer.url}
            target="_blank"
            rel="noopener"
            className={buttonClassName("ghost")}
          >
            {offer.source}
            <ExternalLinkIcon />
            <span className="sr-only">(opens in a new tab)</span>
          </a>
          {/* The shortest path to a sent application: straight to the Apply panel */}
          <Link
            href={`/jobs/${match.id}#apply`}
            className={buttonClassName("primary")}
          >
            Apply
            <ArrowRightIcon />
          </Link>
        </div>
      </div>
    </article>
  );
}
