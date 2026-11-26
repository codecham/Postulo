import Link from "next/link";

import { BoardItem } from "@/components/tracking/board-item";
import { BoardStats } from "@/components/tracking/board-stats";
import { StatusBadge } from "@/components/tracking/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { SendIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
import {
  TRACKING_STATUS_LABELS,
  TRACKING_STATUSES,
  type TrackingBoard as Board,
} from "@/lib/tracking/types";

/** The sent applications as columns, one per status, in the order they usually move. */
export function TrackingBoard({ board }: { board: Board }) {
  if (board.items.length === 0) {
    return (
      <EmptyState
        icon={<SendIcon className="size-5" />}
        title="Nothing sent yet"
        description="Once you apply to an offer, click “I sent it”: it shows up here, with a reminder to follow up."
        action={
          <Link href="/jobs" className={buttonClassName("primary")}>
            Browse my job matches
          </Link>
        }
      />
    );
  }
  const columns = TRACKING_STATUSES.filter(
    (status) => board.counts[status] > 0,
  );
  return (
    <div className="flex flex-col gap-6">
      <BoardStats board={board} />
      <div className="grid items-start gap-4 md:grid-cols-2 xl:grid-cols-3">
        {columns.map((status) => (
          <section
            key={status}
            aria-label={TRACKING_STATUS_LABELS[status]}
            className="bg-subtle/60 flex flex-col gap-3 rounded-xl p-3"
          >
            <h2 className="flex items-center justify-between px-1">
              <StatusBadge status={status} />
              <span className="text-muted text-sm tabular-nums">
                {board.counts[status]}
              </span>
            </h2>
            <ul className="flex flex-col gap-3">
              {board.items
                .filter((item) => item.status === status)
                .map((item) => (
                  <BoardItem key={item.id} item={item} />
                ))}
            </ul>
          </section>
        ))}
      </div>
    </div>
  );
}
