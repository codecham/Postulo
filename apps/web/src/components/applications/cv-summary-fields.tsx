import { FormSection } from "@/components/ui/form-section";
import { TagInput } from "@/components/ui/tag-input";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import type { ApplicationContent } from "@/lib/applications/types";

/** The top of the CV: title and profile, then the skills and languages lists. */
export function CvSummaryFields({ cv }: { cv: ApplicationContent["cv"] }) {
  return (
    <FormSection title="CV: profile">
      <TextField
        label="Headline"
        name="cv.headline"
        required
        maxLength={200}
        defaultValue={cv.headline}
      />
      <TextareaField
        label="Summary"
        name="cv.summary"
        required
        maxLength={5000}
        defaultValue={cv.summary}
      />
      <TagInput label="Skills" name="cv.skills" defaultValue={cv.skills} />
      <TagInput
        label="Languages"
        name="cv.languages"
        defaultValue={cv.languages}
      />
    </FormSection>
  );
}
