import { formatEventDay } from "@/lib/tracking/dates";
import { TRACKING_STATUS_LABELS, type Tracking } from "@/lib/tracking/types";

/** Every status the application went through, oldest first, as a timeline. */
export function TrackingHistory({ events }: { events: Tracking["events"] }) {
  return (
    <ol className="border-line flex flex-col gap-3 border-l pl-4 text-sm">
      {events.map((event) => (
        <li
          key={`${event.status}-${event.created_at}`}
          className="relative flex flex-col"
        >
          <span
            aria-hidden
            className="bg-line-strong absolute top-1.5 -left-[1.3125rem] size-2 rounded-full"
          />
          <span className="font-medium">
            {TRACKING_STATUS_LABELS[event.status]}
          </span>
          <span className="text-muted text-xs">
            {formatEventDay(event.created_at)}
          </span>
        </li>
      ))}
    </ol>
  );
}
