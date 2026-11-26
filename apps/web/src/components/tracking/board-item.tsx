import Link from "next/link";

import { FollowUpNote } from "@/components/tracking/follow-up-note";
import { cardClassName } from "@/components/ui/card";
import { formatDay } from "@/lib/tracking/dates";
import type { TrackedApplication } from "@/lib/tracking/types";

/** One sent application on the board: the offer, when it was sent, what to do next. */
export function BoardItem({ item }: { item: TrackedApplication }) {
  const { offer } = item;
  return (
    <li
      className={`${cardClassName} relative flex flex-col gap-2 p-4 transition-shadow hover:shadow-md ${
        item.follow_up_due ? "border-l-warning border-l-4" : ""
      }`}
    >
      {/* The whole card links to the offer; the link text is its title */}
      <Link
        href={`/jobs/${item.match_id}`}
        className="hover:text-accent-text font-medium text-balance after:absolute after:inset-0 after:rounded-xl"
      >
        {offer.title}
      </Link>
      <p className="text-muted text-sm">
        {[offer.company, `sent ${formatDay(item.applied_on)}`]
          .filter(Boolean)
          .join(" · ")}
      </p>
      {item.follow_up_on && (
        <p className="text-sm">
          <FollowUpNote tracking={item} />
        </p>
      )}
      {item.notes && (
        <p className="bg-subtle text-muted line-clamp-2 rounded-lg px-3 py-2 text-sm">
          {item.notes}
        </p>
      )}
    </li>
  );
}
