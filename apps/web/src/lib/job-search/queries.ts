import "server-only";

import { notFound } from "next/navigation";
import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type {
  JobMatch,
  JobMatchPage,
  JobSearchOverview,
  MatchFacets,
  MatchQuery,
} from "@/lib/job-search/types";

export async function getJobSearchOverview(): Promise<JobSearchOverview> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/job-search", { headers }));
}

export async function listMyMatches(query: MatchQuery): Promise<JobMatchPage> {
  await connection();
  const headers = await requireAuthHeaders();
  return requireData(
    await api.GET("/job-search/matches", { headers, params: { query } }),
  );
}

export async function getMatchFacets(): Promise<MatchFacets> {
  await connection();
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/job-search/matches/facets", { headers }));
}

/** The user's match, or the 404 page when it does not exist (or is someone else's). */
export async function getMatch(matchId: string): Promise<JobMatch> {
  await connection();
  const headers = await requireAuthHeaders();
  const result = await api.GET("/job-search/matches/{match_id}", {
    headers,
    params: { path: { match_id: matchId } },
  });
  if (result.response.status === 404 || result.response.status === 422) {
    notFound(); // 422: the id in the URL is not even a valid UUID
  }
  return requireData(result);
}
