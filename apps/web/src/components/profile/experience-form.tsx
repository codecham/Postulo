import { ActionForm } from "@/components/ui/action-form";
import { secondaryButtonClassName } from "@/components/ui/styles";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import type { FormState } from "@/lib/forms";
import { dateToMonth } from "@/lib/profile/dates";
import type { Experience } from "@/lib/profile/types";

type ExperienceFormProps = {
  saveAction: (state: FormState, formData: FormData) => Promise<FormState>;
  experience?: Experience; // to edit; leave it out to create a new one
  submitLabel: string;
  onClose: () => void; // called after a successful save, and on Cancel
};

/** Create or edit an experience. Used by the client components of the list. */
export function ExperienceForm({
  saveAction,
  experience,
  submitLabel,
  onClose,
}: ExperienceFormProps) {
  async function saveThenClose(state: FormState, formData: FormData) {
    const nextState = await saveAction(state, formData);
    if (nextState?.status === "success") {
      onClose();
    }
    return nextState;
  }

  return (
    <ActionForm
      action={saveThenClose}
      submitLabel={submitLabel}
      secondaryButton={
        <button
          type="button"
          onClick={onClose}
          className={secondaryButtonClassName}
        >
          Cancel
        </button>
      }
    >
      <ExperienceFields experience={experience} />
    </ActionForm>
  );
}

function ExperienceFields({ experience }: { experience?: Experience }) {
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
