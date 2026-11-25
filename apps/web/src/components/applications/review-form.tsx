import { saveApplication } from "@/app/jobs/[id]/application/actions";
import { ContactFields } from "@/components/applications/contact-fields";
import { CvSummaryFields } from "@/components/applications/cv-summary-fields";
import { EducationItems } from "@/components/applications/education-items";
import { ExperienceItems } from "@/components/applications/experience-items";
import { LetterFields } from "@/components/applications/letter-fields";
import { ActionForm } from "@/components/ui/action-form";
import type { Application } from "@/lib/applications/types";

/** Every part of the CV and the letter, pre-filled and editable. */
export function ReviewForm({ application }: { application: Application }) {
  const { content } = application;
  return (
    <ActionForm
      action={saveApplication.bind(null, application.match_id)}
      submitLabel="Save changes"
    >
      <ContactFields contact={content.contact} language={content.language} />
      <CvSummaryFields cv={content.cv} />
      <ExperienceItems experiences={content.cv.experiences} />
      <EducationItems education={content.cv.education} />
      <LetterFields letter={content.cover_letter} />
    </ActionForm>
  );
}
