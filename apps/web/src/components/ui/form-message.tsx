import { CheckIcon } from "@/components/ui/icons";
import type { FormState } from "@/lib/forms";

/** The success or error message returned by a server action. */
export function FormMessage({ state }: { state: FormState }) {
  if (!state) {
    return null;
  }
  if (state.status === "error") {
    return (
      <p role="alert" className="text-danger text-sm font-medium">
        {state.message}
      </p>
    );
  }
  return (
    <p
      role="status"
      className="text-success flex items-center gap-1.5 text-sm font-medium"
    >
      <CheckIcon />
      {state.message}
    </p>
  );
}
