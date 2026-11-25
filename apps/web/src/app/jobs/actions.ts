"use server";

import { refresh } from "next/cache";

import { api } from "@/lib/api/client";
import { requireSuccess, toFormState } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { FormState } from "@/lib/forms";
import type { MatchStatus } from "@/lib/job-search/types";

/** Ask the worker to search now; the page then follows the search's progress. */
export async function startJobSearch(): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.POST("/job-search/runs", { headers });
  const state = toFormState(result, "Search started.");
  if (state?.status === "success") {
    refresh();
  }
  return state;
}

/** Save an offer to the shortlist, dismiss it, or put it back to review. */
export async function setMatchStatus(
  matchId: string,
  status: MatchStatus,
): Promise<void> {
  const headers = await requireAuthHeaders();
  const result = await api.PATCH("/job-search/matches/{match_id}", {
    headers,
    params: { path: { match_id: matchId } },
    body: { status },
  });
  requireSuccess(result);
  refresh();
}
