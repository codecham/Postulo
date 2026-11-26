import type { ReactNode } from "react";

import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";

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
    <Card title={title}>
      {items.length === 0 ? (
        <EmptyState compact description={emptyMessage} />
      ) : (
        <ul className="divide-line flex flex-col divide-y">
          {items.map((item) => (
            <li key={item.key} className="py-4 first:pt-0 last:pb-0">
              {item.content}
            </li>
          ))}
        </ul>
      )}
      {footer}
    </Card>
  );
}
