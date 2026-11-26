/** A grey placeholder block that pulses while the real content loads. */
export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div
      aria-hidden
      className={`bg-subtle animate-pulse rounded-lg ${className}`}
    />
  );
}
