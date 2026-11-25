import { applyCvImport } from "@/app/profile/import/actions";
import { DraftItemsFields } from "@/components/cv-import/draft-items-fields";
import { EducationSummary } from "@/components/profile/education-summary";
import { ExperienceSummary } from "@/components/profile/experience-summary";
import { IdentityFields } from "@/components/profile/identity-fields";
import { SearchCriteriaFields } from "@/components/profile/search-criteria-fields";
import { SkillsFields } from "@/components/profile/skills-fields";
import { ActionForm } from "@/components/ui/action-form";
import { draftProfileValues } from "@/lib/cv-import/draft";
import { EDUCATION_FIELD, EXPERIENCE_FIELD } from "@/lib/cv-import/form-data";
import type { CvImportDraft } from "@/lib/cv-import/types";

type ImportReviewFormProps = {
  importId: string;
  draft: CvImportDraft;
};

/** The profile form, pre-filled with the draft, plus the items to add. */
export function ImportReviewForm({ importId, draft }: ImportReviewFormProps) {
  const profile = draftProfileValues(draft);
  return (
    <ActionForm
      action={applyCvImport.bind(null, importId)}
      submitLabel="Save to my profile"
    >
      <IdentityFields profile={profile} />
      <SkillsFields profile={profile} />
      <SearchCriteriaFields profile={profile} />
      <DraftItemsFields
        title="Experience found in your CV"
        emptyMessage="No experience was found."
        fieldName={EXPERIENCE_FIELD}
        items={draft.experiences.map((experience, index) => ({
          key: `experience-${index}`,
          summary: <ExperienceSummary experience={experience} />,
          alreadyExists: experience.already_exists ?? false,
        }))}
      />
      <DraftItemsFields
        title="Education found in your CV"
        emptyMessage="No education was found."
        fieldName={EDUCATION_FIELD}
        items={(draft.educations ?? []).map((education, index) => ({
          key: `education-${index}`,
          summary: <EducationSummary education={education} />,
          alreadyExists: education.already_exists ?? false,
        }))}
      />
    </ActionForm>
  );
}
