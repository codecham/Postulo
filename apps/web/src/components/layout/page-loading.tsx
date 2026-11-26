import { Skeleton } from "@/components/ui/skeleton";

/** The Suspense fallback of a page: the shape of its content, pulsing. */
export function PageLoading({ blocks = 3 }: { blocks?: number }) {
  return (
    <div role="status" className="flex flex-col gap-4">
      <span className="sr-only">Loading…</span>
      {Array.from({ length: blocks }, (_, index) => (
        <Skeleton key={index} className="h-32 w-full rounded-xl" />
      ))}
    </div>
  );
}
