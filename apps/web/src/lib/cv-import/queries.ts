import "server-only";

import { notFound } from "next/navigation";
import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { CvImport } from "@/lib/cv-import/types";

/** The user's import, or the 404 page when it does not exist (or is someone else's). */
export async function getCvImport(importId: string): Promise<CvImport> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  const result = await api.GET("/profile/imports/{import_id}", {
    headers,
    params: { path: { import_id: importId } },
  });
  if (result.response.status === 404 || result.response.status === 422) {
    notFound(); // 422: the id in the URL is not even a valid UUID
  }
  return requireData(result);
}
