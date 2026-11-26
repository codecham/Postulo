/** A small spinning circle, shown inside a button while its action runs. */
export function Spinner() {
  return (
    <span
      aria-hidden
      className="size-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
    />
  );
}
