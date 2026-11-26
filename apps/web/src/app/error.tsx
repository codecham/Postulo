"use client";

import { EmptyState } from "@/components/ui/empty-state";
import { buttonClassName } from "@/components/ui/styles";

// Shown when a page fails to render (for example when the API is down)
export default function Error({ reset }: { reset: () => void }) {
  return (
    <EmptyState
      title="Something went wrong"
      description="The page could not be loaded. Please try again in a moment."
      action={
        <button
          type="button"
          onClick={reset}
          className={buttonClassName("primary", "md")}
        >
          Try again
        </button>
      }
    />
  );
}
