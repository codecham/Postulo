import { updateTracking } from "@/app/applications/actions";
import { ActionForm } from "@/components/ui/action-form";
import { inputClassName, labelClassName } from "@/components/ui/styles";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import {
  TRACKING_STATUS_LABELS,
  TRACKING_STATUSES,
  type Tracking,
} from "@/lib/tracking/types";

/** Change where the application stands, its dates and the user's notes. */
export function TrackingForm({ tracking }: { tracking: Tracking }) {
  return (
    <ActionForm
      action={updateTracking.bind(null, tracking.match_id)}
      submitLabel="Save"
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <label className={labelClassName}>
          Status
          <select
            name="status"
            defaultValue={tracking.status}
            className={inputClassName}
          >
            {TRACKING_STATUSES.map((status) => (
              <option key={status} value={status}>
                {TRACKING_STATUS_LABELS[status]}
              </option>
            ))}
          </select>
        </label>
        <TextField
          label="Sent on"
          name="applied_on"
          type="date"
          required
          defaultValue={tracking.applied_on}
        />
        <TextField
          label="Follow up on"
          name="follow_up_on"
          type="date"
          hint="Empty: no reminder."
          defaultValue={tracking.follow_up_on ?? ""}
        />
      </div>
      <TextareaField
        label="Notes"
        name="notes"
        rows={3}
        maxLength={5000}
        placeholder="Contact person, interview dates, salary discussed…"
        defaultValue={tracking.notes ?? ""}
      />
    </ActionForm>
  );
}
