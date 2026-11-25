import { ExperienceSummary } from "@/components/profile/experience-summary";
import { EXPERIENCE_FIELD } from "@/lib/cv-import/form-data";
import type { DraftExperience } from "@/lib/cv-import/types";

type DraftExperienceOptionProps = {
  experience: DraftExperience;
  index: number; // position in the draft: the value sent when checked
};

/** An experience found in the CV, with a checkbox to add it to the profile. */
export function DraftExperienceOption({
  experience,
  index,
}: DraftExperienceOptionProps) {
  return (
    <label className="flex items-start gap-3">
      <input
        type="checkbox"
        name={EXPERIENCE_FIELD}
        value={index}
        // Unchecked when the user already has it, so it is not added twice
        defaultChecked={!experience.already_exists}
        className="mt-1 size-4 shrink-0"
      />
      <div className="flex flex-col gap-1">
        <ExperienceSummary experience={experience} />
        {experience.already_exists && (
          <p className="text-xs text-gray-500">Already in your profile</p>
        )}
      </div>
    </label>
  );
}
