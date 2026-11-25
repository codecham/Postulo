import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import { dateToMonth } from "@/lib/profile/dates";
import type { Education } from "@/lib/profile/types";

/** The fields of an education form, empty or filled with `education`. */
export function EducationFields({ education }: { education?: Education }) {
  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          label="School"
          name="school"
          required
          maxLength={200}
          placeholder="42 Paris, ULB…"
          defaultValue={education?.school}
        />
        <TextField
          label="Degree"
          name="degree"
          maxLength={200}
          placeholder="Master, RNCP level 7…"
          defaultValue={education?.degree ?? ""}
        />
        <TextField
          label="Field of study"
          name="field_of_study"
          maxLength={200}
          defaultValue={education?.field_of_study ?? ""}
        />
        <TextField
          label="Location"
          name="location"
          maxLength={100}
          defaultValue={education?.location ?? ""}
        />
        <TextField
          label="Start"
          name="start_month"
          type="month"
          defaultValue={dateToMonth(education?.start_date ?? null)}
        />
        <TextField
          label="End"
          name="end_month"
          type="month"
          hint="Leave empty if you are still studying there."
          defaultValue={dateToMonth(education?.end_date ?? null)}
        />
      </div>
      <TextareaField
        label="Description"
        name="description"
        maxLength={5000}
        hint="Projects, specialization, honors."
        defaultValue={education?.description ?? ""}
      />
    </div>
  );
}
