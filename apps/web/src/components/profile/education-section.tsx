import {
  createEducation,
  deleteEducation,
  updateEducation,
} from "@/app/profile/actions";
import { EducationFields } from "@/components/profile/education-fields";
import { EducationSummary } from "@/components/profile/education-summary";
import { AddItem } from "@/components/ui/add-item";
import { DeleteButton } from "@/components/ui/delete-button";
import { EditableItem } from "@/components/ui/editable-item";
import { ItemForm } from "@/components/ui/item-form";
import { ListSection } from "@/components/ui/list-section";
import type { Education } from "@/lib/profile/types";

export function EducationSection({ educations }: { educations: Education[] }) {
  return (
    <ListSection
      title="Education"
      emptyMessage="No education yet. Add your schools, degrees and trainings."
      items={educations.map((education) => ({
        key: education.id,
        content: <EducationItem education={education} />,
      }))}
      footer={
        <AddItem
          label="Add an education"
          form={
            <ItemForm action={createEducation} submitLabel="Add">
              <EducationFields />
            </ItemForm>
          }
        />
      }
    />
  );
}

function EducationItem({ education }: { education: Education }) {
  return (
    <EditableItem
      summary={<EducationSummary education={education} />}
      editForm={
        <ItemForm
          action={updateEducation.bind(null, education.id)}
          submitLabel="Save"
        >
          <EducationFields education={education} />
        </ItemForm>
      }
      actions={
        <DeleteButton
          action={deleteEducation.bind(null, education.id)}
          confirmMessage="Delete this education?"
        />
      }
    />
  );
}
