import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import { dateToMonth } from "@/lib/profile/dates";
import type { Experience } from "@/lib/profile/types";

/** The fields of an experience form, empty or filled with `experience`. */
export function ExperienceFields({ experience }: { experience?: Experience }) {
  return (
    <div className="flex flex-col gap-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          label="Job title"
          name="title"
          required
          maxLength={200}
          defaultValue={experience?.title}
        />
        <TextField
          label="Company"
          name="company"
          required
          maxLength={200}
          defaultValue={experience?.company}
        />
        <TextField
          label="Start"
          name="start_month"
          type="month"
          required
          defaultValue={dateToMonth(experience?.start_date ?? null)}
        />
        <TextField
          label="End"
          name="end_month"
          type="month"
          hint="Leave empty if you still work there."
          defaultValue={dateToMonth(experience?.end_date ?? null)}
        />
      </div>
      <TextField
        label="Location"
        name="location"
        maxLength={100}
        defaultValue={experience?.location ?? ""}
      />
      <TextareaField
        label="Description"
        name="description"
        maxLength={5000}
        hint="Your missions and achievements."
        defaultValue={experience?.description ?? ""}
      />
    </div>
  );
}
