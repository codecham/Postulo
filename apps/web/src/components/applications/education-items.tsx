import { ItemCard } from "@/components/applications/item-card";
import { FormSection } from "@/components/ui/form-section";
import { TextField } from "@/components/ui/text-field";
import { EDUCATION_FIELD, itemField } from "@/lib/applications/form-data";
import type { CvEducation } from "@/lib/applications/types";

/** The education of the CV, each item editable. */
export function EducationItems({ education }: { education: CvEducation[] }) {
  return (
    <FormSection title="CV: education">
      {education.map((item, index) => {
        const field = (name: string) => itemField(EDUCATION_FIELD, index, name);
        return (
          <ItemCard key={index} keepField={EDUCATION_FIELD} index={index}>
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField
                label="School"
                name={field("school")}
                required
                maxLength={200}
                defaultValue={item.school}
              />
              <TextField
                label="Degree"
                name={field("degree")}
                maxLength={200}
                defaultValue={item.degree ?? ""}
              />
              <TextField
                label="Field of study"
                name={field("field_of_study")}
                maxLength={200}
                defaultValue={item.field_of_study ?? ""}
              />
              <TextField
                label="Location"
                name={field("location")}
                maxLength={100}
                defaultValue={item.location ?? ""}
              />
              <TextField
                label="Start"
                name={field("start_month")}
                type="month"
                defaultValue={item.start_month ?? ""}
              />
              <TextField
                label="End"
                name={field("end_month")}
                type="month"
                defaultValue={item.end_month ?? ""}
              />
            </div>
            <TextField
              label="Details"
              name={field("details")}
              maxLength={5000}
              defaultValue={item.details ?? ""}
            />
          </ItemCard>
        );
      })}
    </FormSection>
  );
}
