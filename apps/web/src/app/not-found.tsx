import Link from "next/link";

import { EmptyState } from "@/components/ui/empty-state";
import { buttonClassName } from "@/components/ui/styles";

export default function NotFound() {
  return (
    <EmptyState
      title="Page not found"
      description="This page does not exist, or it was removed."
      action={
        <Link href="/jobs" className={buttonClassName("primary", "md")}>
          Back to my job matches
        </Link>
      }
    />
  );
}
