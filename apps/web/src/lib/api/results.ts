import "server-only";

import { redirect } from "next/navigation";

import type { FormState } from "@/lib/forms";

type ApiResult<T> = { data?: T; error?: unknown; response: Response };

/**
 * The body of a successful response. An expired session sends the user to the
 * login page; any other failure throws, and the nearest error.tsx shows it.
 */
export function requireData<T>({ data, response }: ApiResult<T>): T {
  redirectIfUnauthorized(response);
  if (data === undefined) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  return data;
}

/** Check that a request without a response body (such as a DELETE) succeeded. */
export function requireSuccess({ response }: ApiResult<unknown>): void {
  redirectIfUnauthorized(response);
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
}

/** Turn the result of a mutation into the state that a form displays. */
export function toFormState(
  { error, response }: ApiResult<unknown>,
  successMessage: string,
): FormState {
  redirectIfUnauthorized(response);
  if (response.ok) {
    return { status: "success", message: successMessage };
  }
  return { status: "error", message: describeError(error) };
}

function redirectIfUnauthorized(response: Response) {
  if (response.status === 401) {
    redirect("/login");
  }
}

type ValidationIssue = { loc?: (string | number)[]; msg?: string };

/** A readable message from a FastAPI error ("full name: String should have…"). */
function describeError(error: unknown): string {
  const detail = (error as { detail?: unknown } | undefined)?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail) && detail.length > 0) {
    const { loc = [], msg = "Invalid value" } = detail[0] as ValidationIssue;
    const message = msg.replace(/^Value error, /, "");
    // loc is the path to the bad value, such as ["body", "skills", 0]
    const field = loc
      .filter((part) => typeof part === "string" && part !== "body")
      .at(-1);
    return field
      ? `${String(field).replaceAll("_", " ")}: ${message}`
      : message;
  }
  return "Something went wrong. Please try again.";
}
