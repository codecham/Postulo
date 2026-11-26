import type { ReactNode } from "react";

type PageHeaderProps = {
  title: ReactNode;
  description?: ReactNode;
  eyebrow?: ReactNode; // e.g. a back link, above the title
  action?: ReactNode; // e.g. a button, on the right of the title
};

export function PageHeader({
  title,
  description,
  eyebrow,
  action,
}: PageHeaderProps) {
  return (
    <header className="flex flex-col gap-3">
      {eyebrow}
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="flex max-w-2xl flex-col gap-1.5">
          <h1 className="text-2xl font-semibold tracking-tight text-balance sm:text-3xl">
            {title}
          </h1>
          {description && <p className="text-muted">{description}</p>}
        </div>
        {action && <div className="flex flex-wrap gap-2">{action}</div>}
      </div>
    </header>
  );
}
