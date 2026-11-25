import type { ReactNode } from "react";

type CardProps = {
  title: string;
  description?: string;
  children: ReactNode;
};

/** A titled block of content, framed like the form sections. */
export function Card({ title, description, children }: CardProps) {
  return (
    <section className="flex flex-col gap-4 rounded-lg border border-gray-200 p-5 dark:border-gray-800">
      <div className="flex flex-col gap-1">
        <h2 className="font-semibold">{title}</h2>
        {description && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {description}
          </p>
        )}
      </div>
      {children}
    </section>
  );
}
