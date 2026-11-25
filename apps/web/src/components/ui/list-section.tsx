import type { ReactNode } from "react";

export type ListItem = { key: string; content: ReactNode };

type ListSectionProps = {
  title: string;
  emptyMessage: string; // shown when there is no item
  items: ListItem[];
  footer?: ReactNode; // e.g. an AddItem button
};

/** A titled card with a list of items, such as the experiences of the profile. */
export function ListSection({
  title,
  emptyMessage,
  items,
  footer,
}: ListSectionProps) {
  return (
    <section className="flex flex-col gap-4 rounded-lg border border-gray-200 p-5 dark:border-gray-800">
      <h2 className="font-semibold">{title}</h2>
      {items.length === 0 ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          {emptyMessage}
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 dark:divide-gray-800">
          {items.map((item) => (
            <li key={item.key} className="py-4 first:pt-0 last:pb-0">
              {item.content}
            </li>
          ))}
        </ul>
      )}
      {footer}
    </section>
  );
}
