import "server-only";

import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { Application, ApplicationOptions } from "@/lib/applications/types";

/** The match's current application, or null when none was written yet. */
export async function getApplication(
  matchId: string,
): Promise<Application | null> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  const result = await api.GET("/job-search/matches/{match_id}/application", {
    headers,
    params: { path: { match_id: matchId } },
  });
  // 422: the id is not a valid UUID; the match query shows the 404 page for it
  if (result.response.status === 404 || result.response.status === 422) {
    return null;
  }
  return requireData(result);
}

/** Which ways to write an application the API offers (the AI needs an API key). */
export async function getApplicationOptions(): Promise<ApplicationOptions> {
  await connection();
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/applications/options", { headers }));
}
