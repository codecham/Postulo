"use server";

import { redirect } from "next/navigation";

import { api } from "@/lib/api/client";
import { requireData, toFormState } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import { readFile, toCvImportApply } from "@/lib/cv-import/form-data";
import { getCvImport } from "@/lib/cv-import/queries";
import type { FormState } from "@/lib/forms";

/** Send the PDF to the API, then open the review page of the draft. */
export async function startCvImport(
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  const file = readFile(formData, "file");
  if (!file) {
    return { status: "error", message: "Choose a PDF file first." };
  }
  const headers = await requireAuthHeaders();
  const result = await api.POST("/profile/imports", {
    headers,
    body: toMultipartBody(file),
  });
  if (!result.data) {
    return toFormState(result, "");
  }
  redirect(`/profile/import/${result.data.id}`);
}

/** Save the reviewed draft into the profile, then go back to the profile. */
export async function applyCvImport(
  importId: string,
  _previousState: FormState,
  formData: FormData,
): Promise<FormState> {
  // The experiences come from the saved draft, not from the browser
  const { draft } = await getCvImport(importId);
  if (!draft) {
    redirect("/profile");
  }
  const headers = await requireAuthHeaders();
  const result = await api.POST("/profile/imports/{import_id}/apply", {
    headers,
    params: { path: { import_id: importId } },
    body: toCvImportApply(formData, draft),
  });
  if (!result.response.ok) {
    return toFormState(result, "");
  }
  redirect("/profile");
}

export async function discardCvImport(importId: string): Promise<void> {
  const headers = await requireAuthHeaders();
  const result = await api.POST("/profile/imports/{import_id}/discard", {
    headers,
    params: { path: { import_id: importId } },
  });
  requireData(result);
  redirect("/profile");
}

/**
 * The API expects a multipart form with a "file" field. The generated types describe
 * a file as a string, so the real FormData is passed through as is (openapi-fetch
 * sends FormData unchanged and lets fetch set the multipart Content-Type).
 */
function toMultipartBody(file: File): { file: string } {
  const body = new FormData();
  body.append("file", file);
  return body as unknown as { file: string };
}
