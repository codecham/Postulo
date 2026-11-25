import Link from "next/link";

import { FollowUpNote } from "@/components/tracking/follow-up-note";
import { StatusBadge } from "@/components/tracking/status-badge";
import { formatDay } from "@/lib/tracking/dates";
import type { TrackedApplication } from "@/lib/tracking/types";

/** One sent application on the board: the offer, where it stands, what to do next. */
export function BoardItem({ item }: { item: TrackedApplication }) {
  const { offer } = item;
  return (
    <li className="flex flex-col gap-1 rounded-lg border border-gray-200 p-4 dark:border-gray-800">
      <div className="flex items-start justify-between gap-3">
        <Link href={`/jobs/${item.match_id}`} className="font-medium underline">
          {offer.title}
        </Link>
        <StatusBadge status={item.status} />
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-400">
        {[offer.company, `sent on ${formatDay(item.applied_on)}`]
          .filter(Boolean)
          .join(" · ")}
      </p>
      <p className="text-sm">
        <FollowUpNote tracking={item} />
      </p>
      {item.notes && (
        <p className="line-clamp-2 text-sm text-gray-600 dark:text-gray-400">
          {item.notes}
        </p>
      )}
    </li>
  );
}
