"use server";

import { refresh } from "next/cache";

import { api } from "@/lib/api/client";
import { requireSuccess, toFormState } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { FormState } from "@/lib/forms";
import { toTrackingUpdate } from "@/lib/tracking/form-data";

/** Mark the match's application as sent today, with a follow-up in a week. */
export async function markAsSent(matchId: string): Promise<void> {
  const headers = await requireAuthHeaders();
  const result = await api.POST("/job-search/matches/{match_id}/tracking", {
    headers,
    params: { path: { match_id: matchId } },
    body: {},
  });
  // 409: already marked (e.g. a double click): the page shows it either way
  if (result.response.status !== 409) {
    requireSuccess(result);
  }
  refresh();
}

/** Save the status, the dates and the notes of a sent application. */
export async function updateTracking(
  matchId: string,
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.PATCH("/job-search/matches/{match_id}/tracking", {
    headers,
    params: { path: { match_id: matchId } },
    body: toTrackingUpdate(formData),
  });
  if (result.response.ok) {
    refresh();
  }
  return toFormState(result, "Saved.");
}

/** Undo "Mark as sent", with its history. */
export async function undoMarkAsSent(matchId: string): Promise<void> {
  const headers = await requireAuthHeaders();
  const result = await api.DELETE("/job-search/matches/{match_id}/tracking", {
    headers,
    params: { path: { match_id: matchId } },
  });
  requireSuccess(result);
  refresh();
}
