"use server";

import { refresh } from "next/cache";

import { api } from "@/lib/api/client";
import { requireSuccess, toFormState } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { FormState } from "@/lib/forms";
import { toExperienceInput, toProfileUpdate } from "@/lib/profile/form-data";

// Each action re-reads the session: the API checks the token, never the browser.
// After a change, refresh() re-renders the page with the saved data.

export async function saveProfile(
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.PUT("/profile/me", {
    headers,
    body: toProfileUpdate(formData),
  });
  return refreshOnSuccess(toFormState(result, "Profile saved."));
}

export async function createExperience(
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.POST("/experiences", {
    headers,
    body: toExperienceInput(formData),
  });
  return refreshOnSuccess(toFormState(result, "Experience added."));
}

export async function updateExperience(
  experienceId: string,
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const headers = await requireAuthHeaders();
  const result = await api.PUT("/experiences/{experience_id}", {
    headers,
    params: { path: { experience_id: experienceId } },
    body: toExperienceInput(formData),
  });
  return refreshOnSuccess(toFormState(result, "Experience saved."));
}

export async function deleteExperience(experienceId: string): Promise<void> {
  const headers = await requireAuthHeaders();
  const result = await api.DELETE("/experiences/{experience_id}", {
    headers,
    params: { path: { experience_id: experienceId } },
  });
  requireSuccess(result);
  refresh();
}

function refreshOnSuccess(state: FormState): FormState {
  if (state?.status === "success") {
    refresh();
  }
  return state;
}
