import {
  TRACKING_STATUS_LABELS,
  type TrackingStatus,
} from "@/lib/tracking/types";

const COLORS: Record<TrackingStatus, string> = {
  applied: "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300",
  interview:
    "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300",
  offer: "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300",
  rejected: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
  withdrawn: "bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400",
};

/** Where a sent application stands, as a colored pill. */
export function StatusBadge({ status }: { status: TrackingStatus }) {
  return (
    <span
      className={`shrink-0 rounded-full px-2.5 py-0.5 text-xs font-semibold ${COLORS[status]}`}
    >
      {TRACKING_STATUS_LABELS[status]}
    </span>
  );
}
