"use server";

import { refresh } from "next/cache";

import { api } from "@/lib/api/client";
import { toFormState } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { FormState } from "@/lib/forms";

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
