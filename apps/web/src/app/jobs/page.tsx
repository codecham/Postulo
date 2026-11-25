import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { MatchList } from "@/components/job-search/match-list";
import { SearchStatus } from "@/components/job-search/search-status";
import { SourceList } from "@/components/job-search/source-list";
import { PageHeader } from "@/components/layout/page-header";
import { secondaryButtonClassName } from "@/components/ui/styles";
import { getJobSearchOverview, listMyMatches } from "@/lib/job-search/queries";

export const metadata: Metadata = { title: "Job search" };

export default function JobsPage() {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Job search"
        description="Offers from public job boards that fit your profile and your criteria."
        action={
          <Link href="/profile" className={secondaryButtonClassName}>
            Edit my criteria
          </Link>
        }
      />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<p className="text-gray-500">Loading…</p>}>
        <JobsContent />
      </Suspense>
    </section>
  );
}

async function JobsContent() {
  const [overview, matches] = await Promise.all([
    getJobSearchOverview(),
    listMyMatches(),
  ]);

  return (
    <>
      <SearchStatus run={overview.latest_run} />
      <MatchList matches={matches} />
      <SourceList sources={overview.sources} />
    </>
  );
}
