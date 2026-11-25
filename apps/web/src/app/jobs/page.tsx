import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { SearchStatus } from "@/components/job-search/search-status";
import { SourceList } from "@/components/job-search/source-list";
import { PageHeader } from "@/components/layout/page-header";
import { MatchFilterBar } from "@/components/matches/match-filter-bar";
import { MatchList } from "@/components/matches/match-list";
import { Pager } from "@/components/matches/pager";
import { StatusTabs } from "@/components/matches/status-tabs";
import { secondaryButtonClassName } from "@/components/ui/styles";
import {
  buildFilterOptions,
  SORT_OPTIONS,
} from "@/lib/job-search/filter-options";
import {
  hasActiveFilters,
  readMatchFilters,
  toMatchQuery,
} from "@/lib/job-search/match-filters";
import {
  getJobSearchOverview,
  getMatchFacets,
  listMyMatches,
} from "@/lib/job-search/queries";

export const metadata: Metadata = { title: "Job matches" };

export default function JobsPage({ searchParams }: PageProps<"/jobs">) {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Job matches"
        description="Offers from public job boards that fit your profile, best first. Save the ones you want, dismiss the others."
        action={
          <Link href="/profile" className={secondaryButtonClassName}>
            Edit my criteria
          </Link>
        }
      />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<p className="text-gray-500">Loading…</p>}>
        <JobsContent searchParams={searchParams} />
      </Suspense>
    </section>
  );
}

async function JobsContent({
  searchParams,
}: Pick<PageProps<"/jobs">, "searchParams">) {
  const filters = readMatchFilters(await searchParams);
  const [overview, page, facets] = await Promise.all([
    getJobSearchOverview(),
    listMyMatches(toMatchQuery(filters)),
    getMatchFacets(),
  ]);

  return (
    <>
      <SearchStatus run={overview.latest_run} />
      <div className="flex flex-col gap-4">
        <StatusTabs filters={filters} counts={page.counts} />
        <MatchFilterBar
          filters={filters}
          options={buildFilterOptions(facets)}
          sortOptions={SORT_OPTIONS}
        />
        <MatchList
          matches={page.items}
          status={filters.status}
          filtered={hasActiveFilters(filters)}
        />
        <Pager filters={filters} total={page.total} />
      </div>
      <SourceList sources={overview.sources} />
    </>
  );
}
