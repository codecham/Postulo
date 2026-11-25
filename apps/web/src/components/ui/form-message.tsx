import type { FormState } from "@/lib/forms";

/** The success or error message returned by a server action. */
export function FormMessage({ state }: { state: FormState }) {
  if (!state) {
    return null;
  }
  if (state.status === "error") {
    return (
      <p role="alert" className="text-sm text-red-600">
        {state.message}
      </p>
    );
  }
  return (
    <p role="status" className="text-sm text-green-700 dark:text-green-500">
      {state.message}
    </p>
  );
}
