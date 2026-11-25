import {
  createExperience,
  deleteExperience,
  updateExperience,
} from "@/app/profile/actions";
import { ExperienceFields } from "@/components/profile/experience-fields";
import { ExperienceSummary } from "@/components/profile/experience-summary";
import { AddItem } from "@/components/ui/add-item";
import { DeleteButton } from "@/components/ui/delete-button";
import { EditableItem } from "@/components/ui/editable-item";
import { ItemForm } from "@/components/ui/item-form";
import { ListSection } from "@/components/ui/list-section";
import type { Experience } from "@/lib/profile/types";

export function ExperienceSection({
  experiences,
}: {
  experiences: Experience[];
}) {
  return (
    <ListSection
      title="Experience"
      emptyMessage="No experience yet. Add your jobs, most recent first."
      items={experiences.map((experience) => ({
        key: experience.id,
        content: <ExperienceItem experience={experience} />,
      }))}
      footer={
        <AddItem
          label="Add an experience"
          form={
            <ItemForm action={createExperience} submitLabel="Add">
              <ExperienceFields />
            </ItemForm>
          }
        />
      }
    />
  );
}

function ExperienceItem({ experience }: { experience: Experience }) {
  return (
    <EditableItem
      summary={<ExperienceSummary experience={experience} />}
      editForm={
        <ItemForm
          action={updateExperience.bind(null, experience.id)}
          submitLabel="Save"
        >
          <ExperienceFields experience={experience} />
        </ItemForm>
      }
      actions={
        <DeleteButton
          action={deleteExperience.bind(null, experience.id)}
          confirmMessage="Delete this experience?"
        />
      }
    />
  );
}
