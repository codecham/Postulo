import { BoardItem } from "@/components/tracking/board-item";
import {
  TRACKING_STATUS_LABELS,
  TRACKING_STATUSES,
  type TrackingBoard as Board,
} from "@/lib/tracking/types";

/** The sent applications, grouped by status, in the order they usually move. */
export function TrackingBoard({ board }: { board: Board }) {
  if (board.items.length === 0) {
    return (
      <p className="text-gray-600 dark:text-gray-400">
        Nothing sent yet. On an offer, click “Mark as sent” once you applied.
      </p>
    );
  }
  return (
    <div className="flex flex-col gap-8">
      {TRACKING_STATUSES.filter((status) => board.counts[status] > 0).map(
        (status) => (
          <section key={status} className="flex flex-col gap-3">
            <h2 className="font-semibold">
              {TRACKING_STATUS_LABELS[status]}{" "}
              <span className="text-gray-500 tabular-nums">
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
        ),
      )}
    </div>
  );
}
