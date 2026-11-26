import type { Metadata } from "next";
import { Suspense } from "react";

import { BackLink } from "@/components/layout/back-link";
import { PageLoading } from "@/components/layout/page-loading";
import { ApplyPanel } from "@/components/matches/apply-panel";
import { MatchActions } from "@/components/matches/match-actions";
import { MatchReasons } from "@/components/matches/match-reasons";
import { OfferDescription } from "@/components/matches/offer-description";
import { OfferFacts } from "@/components/matches/offer-facts";
import { ScoreBadge } from "@/components/matches/score-badge";
import { TrackingCard } from "@/components/tracking/tracking-card";
import { Card } from "@/components/ui/card";
import { ExternalLinkIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
import {
  getApplication,
  getApplicationOptions,
} from "@/lib/applications/queries";
import { getMatch } from "@/lib/job-search/queries";
import { getTracking } from "@/lib/tracking/queries";

export const metadata: Metadata = { title: "Job offer" };

export default function MatchPage({ params }: PageProps<"/jobs/[id]">) {
  return (
    <section className="flex flex-col gap-6">
      <BackLink href="/jobs" label="All matches" />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<PageLoading />}>
        <MatchContent params={params} />
      </Suspense>
    </section>
  );
}

async function MatchContent({
  params,
}: Pick<PageProps<"/jobs/[id]">, "params">) {
  const { id } = await params;
  const [match, application, tracking, options] = await Promise.all([
    getMatch(id),
    getApplication(id),
    getTracking(id),
    getApplicationOptions(),
  ]);
  const { offer } = match;

  return (
    <>
      <header className="flex flex-col gap-4">
        <div className="flex items-start gap-4">
          <ScoreBadge score={match.score} />
          <div className="flex min-w-0 flex-col gap-1.5">
            <h1 className="text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
              {offer.title}
            </h1>
            <OfferFacts offer={offer} />
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-1">
          <MatchActions match={match} />
          <a
            href={offer.url}
            target="_blank"
            rel="noopener"
            className={buttonClassName("ghost")}
          >
            See on {offer.source}
            <ExternalLinkIcon />
            <span className="sr-only">(opens in a new tab)</span>
          </a>
        </div>
      </header>
      {/* The Apply panel comes first on small screens, and stays in view on large ones */}
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_26rem]">
        <aside className="flex flex-col gap-6 lg:sticky lg:top-24 lg:order-last lg:max-h-[calc(100dvh-7rem)] lg:overflow-y-auto">
          <ApplyPanel
            matchId={match.id}
            offer={offer}
            application={application}
            tracking={tracking}
            canUseAi={options.ai_generation}
          />
        </aside>
        <div className="flex min-w-0 flex-col gap-6">
          {tracking && <TrackingCard tracking={tracking} />}
          <Card title="Why it matches">
            <MatchReasons match={match} />
          </Card>
          <Card title="The offer">
            <OfferDescription description={offer.description} />
          </Card>
        </div>
      </div>
    </>
  );
}
