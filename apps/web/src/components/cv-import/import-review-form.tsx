import { applyCvImport } from "@/app/profile/import/actions";
import { DraftExperiencesFields } from "@/components/cv-import/draft-experiences-fields";
import { IdentityFields } from "@/components/profile/identity-fields";
import { SearchCriteriaFields } from "@/components/profile/search-criteria-fields";
import { SkillsFields } from "@/components/profile/skills-fields";
import { ActionForm } from "@/components/ui/action-form";
import { draftProfileValues } from "@/lib/cv-import/draft";
import type { CvImportDraft } from "@/lib/cv-import/types";

type ImportReviewFormProps = {
  importId: string;
  draft: CvImportDraft;
};

/** The profile form, pre-filled with the draft, plus the experiences to add. */
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
      <DraftExperiencesFields experiences={draft.experiences} />
    </ActionForm>
  );
}
