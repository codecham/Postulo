import { Badge, type BadgeTone } from "@/components/ui/badge";
import {
  TRACKING_STATUS_LABELS,
  type TrackingStatus,
} from "@/lib/tracking/types";

export const TRACKING_STATUS_TONES: Record<TrackingStatus, BadgeTone> = {
  applied: "info",
  interview: "warning",
  offer: "success",
  rejected: "neutral",
  withdrawn: "neutral",
};

/** Where a sent application stands, as a colored pill. */
export function StatusBadge({ status }: { status: TrackingStatus }) {
  return (
    <Badge tone={TRACKING_STATUS_TONES[status]}>
      {TRACKING_STATUS_LABELS[status]}
    </Badge>
  );
}
