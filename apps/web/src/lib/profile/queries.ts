import "server-only";

import { connection } from "next/server";

import { api } from "@/lib/api/client";
import { requireData } from "@/lib/api/results";
import { requireAuthHeaders } from "@/lib/auth/session";
import type { Experience, Profile } from "@/lib/profile/types";

export async function getMyProfile(): Promise<Profile> {
  await connection(); // per-user data: never prerender it
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/profile/me", { headers }));
}

export async function listMyExperiences(): Promise<Experience[]> {
  await connection();
  const headers = await requireAuthHeaders();
  return requireData(await api.GET("/experiences", { headers }));
}
