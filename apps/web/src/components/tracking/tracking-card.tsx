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
    <Card title="Follow-up" action={<StatusBadge status={tracking.status} />}>
      <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm">
        <span>Sent on {formatDay(tracking.applied_on)}</span>
        <FollowUpNote tracking={tracking} />
      </div>
      <TrackingForm tracking={tracking} />
      <details className="border-line border-t pt-4">
        <summary className="text-muted hover:text-fg cursor-pointer text-sm font-medium">
          History
        </summary>
        <div className="mt-4 flex flex-col items-start gap-4">
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
