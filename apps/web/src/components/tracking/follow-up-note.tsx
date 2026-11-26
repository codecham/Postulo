import { BellIcon } from "@/components/ui/icons";
import { formatDay } from "@/lib/tracking/dates";
import type { Tracking } from "@/lib/tracking/types";

/** "Follow up on 3 Dec 2026", highlighted once the day has come. */
export function FollowUpNote({ tracking }: { tracking: Tracking }) {
  if (!tracking.follow_up_on) {
    return null;
  }
  if (tracking.follow_up_due) {
    return (
      <span className="text-warning inline-flex items-center gap-1.5 font-medium">
        <BellIcon />
        Follow up now (since {formatDay(tracking.follow_up_on)})
      </span>
    );
  }
  return (
    <span className="text-muted inline-flex items-center gap-1.5">
      <BellIcon />
      Follow up on {formatDay(tracking.follow_up_on)}
    </span>
  );
}
