import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { SearchStatus } from "@/components/job-search/search-status";
import { SourceList } from "@/components/job-search/source-list";
import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
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
  matchesHref,
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
    <section className="flex flex-col gap-6">
      <PageHeader
        title="Job matches"
        description="Offers from public job boards that fit your profile, best first."
        action={
          <Link href="/profile" className={secondaryButtonClassName}>
            Edit my criteria
          </Link>
        }
      />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<PageLoading />}>
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
          clearFiltersHref={matchesHref({
            status: filters.status,
            sort: filters.sort,
            page: 1,
          })}
        />
        <Pager filters={filters} total={page.total} />
      </div>
      <SourceList sources={overview.sources} />
    </>
  );
}
