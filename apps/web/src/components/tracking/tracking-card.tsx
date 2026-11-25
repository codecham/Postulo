import { undoMarkAsSent } from "@/app/applications/actions";
import { FollowUpNote } from "@/components/tracking/follow-up-note";
import { StatusBadge } from "@/components/tracking/status-badge";
import { TrackingForm } from "@/components/tracking/tracking-form";
import { TrackingHistory } from "@/components/tracking/tracking-history";
import { Card } from "@/components/ui/card";
import { DeleteButton } from "@/components/ui/delete-button";
import { formatDay } from "@/lib/tracking/dates";
import type { Tracking } from "@/lib/tracking/types";

/** The follow-up of a sent application, on its offer's page. */
export function TrackingCard({ tracking }: { tracking: Tracking }) {
  return (
    <Card title="Follow-up">
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <StatusBadge status={tracking.status} />
        <span>Sent on {formatDay(tracking.applied_on)}</span>
        <FollowUpNote tracking={tracking} />
      </div>
      <TrackingForm tracking={tracking} />
      <details>
        <summary className="cursor-pointer text-sm text-gray-600 dark:text-gray-400">
          History
        </summary>
        <div className="mt-2 flex flex-col gap-3">
          <TrackingHistory events={tracking.events} />
          <DeleteButton
            action={undoMarkAsSent.bind(null, tracking.match_id)}
            confirmMessage="Undo “Mark as sent”? Its history and notes are deleted."
            label="Undo “Mark as sent”"
          />
        </div>
      </details>
    </Card>
  );
}
