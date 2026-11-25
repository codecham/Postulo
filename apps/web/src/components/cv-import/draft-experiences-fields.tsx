import { DraftExperienceOption } from "@/components/cv-import/draft-experience-option";
import { FormSection } from "@/components/ui/form-section";
import type { DraftExperience } from "@/lib/cv-import/types";

export function DraftExperiencesFields({
  experiences,
}: {
  experiences: DraftExperience[];
}) {
  return (
    <FormSection
      title="Experience found in your CV"
      description="Checked experiences are added to your profile. You can edit them there afterwards."
    >
      {experiences.length === 0 ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No experience was found.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 dark:divide-gray-800">
          {experiences.map((experience, index) => (
            <li
              key={`${experience.company}-${experience.title}-${experience.start_date}`}
              className="py-4 first:pt-0 last:pb-0"
            >
              <DraftExperienceOption experience={experience} index={index} />
            </li>
          ))}
        </ul>
      )}
    </FormSection>
  );
}
