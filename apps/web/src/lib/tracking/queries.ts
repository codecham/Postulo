import "server-only";

import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { Tracking, TrackingBoard } from "@/lib/tracking/types";

/** Every application the user marked as sent, with the count of each status. */
export async function getTrackingBoard(): Promise<TrackingBoard> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/tracking", { headers }));
}

/** The match's tracking, or null when it was not marked as sent. */
export async function getTracking(matchId: string): Promise<Tracking | null> {
  await connection();
  const headers = await requireAuthHeaders();
  const result = await api.GET("/job-search/matches/{match_id}/tracking", {
    headers,
    params: { path: { match_id: matchId } },
  });
  // 422: the id is not a valid UUID; the match query shows the 404 page for it
  if (result.response.status === 404 || result.response.status === 422) {
    return null;
  }
  return requireData(result);
}
