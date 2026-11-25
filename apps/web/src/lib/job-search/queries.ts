import "server-only";

import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { JobMatch, JobSearchOverview } from "@/lib/job-search/types";

export async function getJobSearchOverview(): Promise<JobSearchOverview> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/job-search", { headers }));
}

export async function listMyMatches(limit = 20): Promise<JobMatch[]> {
  await connection();
  const headers = await requireAuthHeaders();
  return requireData(
    await api.GET("/job-search/matches", {
      headers,
      params: { query: { limit } },
    }),
  );
}
