import type { ReactNode } from "react";

/** The frame shared by every card-like block: surface, border, rounded corners. */
export const cardClassName =
  "rounded-xl border border-line bg-surface shadow-xs";

type CardProps = {
  title?: string;
  description?: ReactNode;
  action?: ReactNode; // e.g. a button, on the right of the title
  id?: string; // to link to the card (#apply)
  children: ReactNode;
};

/** A titled block of content. */
export function Card({ title, description, action, id, children }: CardProps) {
  return (
    <section
      id={id}
      className={`${cardClassName} flex scroll-mt-24 flex-col gap-4 p-5 sm:p-6`}
    >
      {(title || action) && (
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex flex-col gap-1">
            {title && <h2 className="font-semibold">{title}</h2>}
            {description && <p className="text-muted text-sm">{description}</p>}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
