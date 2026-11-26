import type { ReactNode } from "react";

type EmptyStateProps = {
  icon?: ReactNode;
  title?: string;
  description: string;
  action?: ReactNode; // e.g. a link to where the user can fill the list
  compact?: boolean; // inside a card: no frame
};

/** What a list shows when it has nothing yet, and how to fill it. */
export function EmptyState({
  icon,
  title,
  description,
  action,
  compact = false,
}: EmptyStateProps) {
  const frame = compact
    ? "py-2"
    : "rounded-xl border border-dashed border-line-strong px-6 py-12";
  return (
    <div className={`flex flex-col items-center gap-3 text-center ${frame}`}>
      {icon && (
        <span className="bg-accent-soft text-accent-text flex size-11 items-center justify-center rounded-full">
          {icon}
        </span>
      )}
      <div className="flex max-w-sm flex-col gap-1">
        {title && <p className="font-semibold">{title}</p>}
        <p className="text-muted text-sm">{description}</p>
      </div>
      {action}
    </div>
  );
}
