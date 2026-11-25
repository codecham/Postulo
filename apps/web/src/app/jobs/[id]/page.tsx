import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { ApplyPanel } from "@/components/matches/apply-panel";
import { MatchActions } from "@/components/matches/match-actions";
import { MatchReasons } from "@/components/matches/match-reasons";
import { OfferDescription } from "@/components/matches/offer-description";
import { OfferFacts } from "@/components/matches/offer-facts";
import { ScoreBadge } from "@/components/matches/score-badge";
import { Card } from "@/components/ui/card";
import {
  getApplication,
  getApplicationOptions,
} from "@/lib/applications/queries";
import { getMatch } from "@/lib/job-search/queries";

export const metadata: Metadata = { title: "Job offer" };

export default function MatchPage({ params }: PageProps<"/jobs/[id]">) {
  return (
    <section className="flex flex-col gap-8">
      <Link href="/jobs" className="text-sm underline">
        ← All matches
      </Link>
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<p className="text-gray-500">Loading…</p>}>
        <MatchContent params={params} />
      </Suspense>
    </section>
  );
}

async function MatchContent({
  params,
}: Pick<PageProps<"/jobs/[id]">, "params">) {
  const { id } = await params;
  const [match, application, options] = await Promise.all([
    getMatch(id),
    getApplication(id),
    getApplicationOptions(),
  ]);
  const { offer } = match;

  return (
    <>
      <header className="flex flex-col gap-3">
        <div className="flex items-start justify-between gap-4">
          <h1 className="text-2xl font-bold">{offer.title}</h1>
          <ScoreBadge score={match.score} />
        </div>
        <OfferFacts offer={offer} />
        <MatchActions match={match} />
      </header>
      <Card title="Why it matches">
        <MatchReasons match={match} />
      </Card>
      <ApplyPanel
        matchId={match.id}
        offer={offer}
        application={application}
        canUseAi={options.ai_generation}
      />
      <Card title="The offer">
        <OfferDescription description={offer.description} />
      </Card>
    </>
  );
}
