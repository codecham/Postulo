"use server";

import { headers } from "next/headers";
import { redirect } from "next/navigation";

import { api } from "@/lib/api/client";
import { createSession, deleteSession } from "@/lib/auth/session";

export type AuthFormState = { error: string } | undefined;

const TOO_MANY_ATTEMPTS =
  "Too many attempts. Wait a few minutes and try again.";

/**
 * Pass the visitor's IP on to the API, which limits login and sign-up attempts per IP.
 * In production the reverse proxy (Caddy) sets X-Forwarded-For to the real client IP.
 */
async function forwardedFor(): Promise<Record<string, string>> {
  const clientIp = (await headers()).get("x-forwarded-for");
  return clientIp ? { "X-Forwarded-For": clientIp } : {};
}

function readCredentials(formData: FormData) {
  return {
    email: String(formData.get("email") ?? ""),
    password: String(formData.get("password") ?? ""),
  };
}

type LoginResult = "ok" | "invalid" | "throttled";

/** Ask the API for an access token and store it in the session cookie. */
async function startSession(
  email: string,
  password: string,
): Promise<LoginResult> {
  const { data, response } = await api.POST("/auth/login", {
    // OAuth2 login is a form post, and calls the email "username"
    body: { username: email, password },
    bodySerializer: (body) =>
      new URLSearchParams(body as Record<string, string>),
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
      ...(await forwardedFor()),
    },
  });
  if (response.status === 429) {
    return "throttled";
  }
  if (!data) {
    return "invalid";
  }
  await createSession(data.access_token, data.expires_in);
  return "ok";
}

export async function login(
  _previousState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const { email, password } = readCredentials(formData);
  const result = await startSession(email, password);
  if (result === "throttled") {
    return { error: TOO_MANY_ATTEMPTS };
  }
  if (result === "invalid") {
    return { error: "Incorrect email or password." };
  }
  redirect("/account");
}

export async function register(
  _previousState: AuthFormState,
  formData: FormData,
): Promise<AuthFormState> {
  const { email, password } = readCredentials(formData);
  const { response } = await api.POST("/auth/register", {
    body: { email, password },
    headers: await forwardedFor(),
  });
  if (response.status === 409) {
    return { error: "An account with this email already exists." };
  }
  if (response.status === 403) {
    return { error: "Sign-up is closed on this server." };
  }
  if (response.status === 429) {
    return { error: TOO_MANY_ATTEMPTS };
  }
  if (!response.ok) {
    return {
      error: "Enter a valid email and a password of 8 to 128 characters.",
    };
  }
  if ((await startSession(email, password)) !== "ok") {
    return { error: "Your account was created, but logging in failed." };
  }
  redirect("/profile"); // first thing to do: fill in the profile
}

export async function logout() {
  await deleteSession();
  redirect("/");
}
