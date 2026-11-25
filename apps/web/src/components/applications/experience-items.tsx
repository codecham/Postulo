import { ItemCard } from "@/components/applications/item-card";
import { FormSection } from "@/components/ui/form-section";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import { EXPERIENCE_FIELD, itemField } from "@/lib/applications/form-data";
import type { CvExperience } from "@/lib/applications/types";

/** The experiences of the CV, each editable, with its bullets one per line. */
export function ExperienceItems({
  experiences,
}: {
  experiences: CvExperience[];
}) {
  return (
    <FormSection title="CV: experience">
      {experiences.map((experience, index) => {
        const field = (name: string) =>
          itemField(EXPERIENCE_FIELD, index, name);
        return (
          <ItemCard key={index} keepField={EXPERIENCE_FIELD} index={index}>
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField
                label="Job title"
                name={field("title")}
                required
                maxLength={200}
                defaultValue={experience.title}
              />
              <TextField
                label="Company"
                name={field("company")}
                required
                maxLength={200}
                defaultValue={experience.company}
              />
              <TextField
                label="Start"
                name={field("start_month")}
                type="month"
                defaultValue={experience.start_month ?? ""}
              />
              <TextField
                label="End"
                name={field("end_month")}
                type="month"
                hint="Empty: you still work there."
                defaultValue={experience.end_month ?? ""}
              />
            </div>
            <TextField
              label="Location"
              name={field("location")}
              maxLength={100}
              defaultValue={experience.location ?? ""}
            />
            <TextareaField
              label="Bullets"
              name={field("bullets")}
              hint="One per line."
              defaultValue={experience.bullets.join("\n")}
            />
          </ItemCard>
        );
      })}
    </FormSection>
  );
}
