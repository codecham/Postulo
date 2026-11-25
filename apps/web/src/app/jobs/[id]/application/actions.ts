"use server";

import { refresh } from "next/cache";
import { redirect } from "next/navigation";

import { api } from "@/lib/api/client";
import { toFormState } from "@/lib/api/results";
import {
  readGeneratedApplication,
  toApplicationContent,
} from "@/lib/applications/form-data";
import { getApplication } from "@/lib/applications/queries";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { FormState } from "@/lib/forms";

/** Have the AI write the CV and the cover letter, then open them for review. */
export async function generateApplication(matchId: string): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.POST(
    "/job-search/matches/{match_id}/application/generate",
    { headers, params: { path: { match_id: matchId } } },
  );
  if (!result.data) {
    return toFormState(result, "");
  }
  redirect(reviewPath(matchId));
}

/** Save the JSON that the /tailor-application command produced, then open it. */
export async function createApplicationFromClaudeCode(
  matchId: string,
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const generated = readGeneratedApplication(formData, "application");
  if (!generated) {
    return {
      status: "error",
      message: "This is not the JSON from Claude Code. Paste it again, whole.",
    };
  }
  const headers = await requireAuthHeaders();
  const result = await api.POST(
    "/job-search/matches/{match_id}/application/from-claude-code",
    { headers, params: { path: { match_id: matchId } }, body: generated },
  );
  if (!result.data) {
    return toFormState(result, "");
  }
  redirect(reviewPath(matchId));
}

/** Save the reviewed documents: the next download uses them. */
export async function saveApplication(
  matchId: string,
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  // How many experiences and educations there are comes from the server, not the browser
  const application = await getApplication(matchId);
  if (!application) {
    redirect(`/jobs/${matchId}`);
  }
  const headers = await requireAuthHeaders();
  const result = await api.PUT("/job-search/matches/{match_id}/application", {
    headers,
    params: { path: { match_id: matchId } },
    body: toApplicationContent(formData, application.content),
  });
  if (result.response.ok) {
    refresh(); // the page shows the saved letter (e.g. its "Copy the letter text")
  }
  return toFormState(result, "Saved. The PDFs are up to date.");
}

function reviewPath(matchId: string): string {
  return `/jobs/${matchId}/application`;
}
