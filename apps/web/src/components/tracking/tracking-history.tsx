import { formatEventDay } from "@/lib/tracking/dates";
import { TRACKING_STATUS_LABELS, type Tracking } from "@/lib/tracking/types";

/** Every status the application went through, oldest first. */
export function TrackingHistory({ events }: { events: Tracking["events"] }) {
  return (
    <ol className="flex flex-col gap-1 text-sm text-gray-600 dark:text-gray-400">
      {events.map((event) => (
        <li key={`${event.status}-${event.created_at}`}>
          {formatEventDay(event.created_at)}:{" "}
          {TRACKING_STATUS_LABELS[event.status]}
        </li>
      ))}
    </ol>
  );
}
