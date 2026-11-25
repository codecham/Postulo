import { FormSection } from "@/components/ui/form-section";
import { MultiSelect } from "@/components/ui/multi-select";
import { TagInput } from "@/components/ui/tag-input";
import { LANGUAGE_OPTIONS } from "@/lib/profile/options";
import type { Profile } from "@/lib/profile/types";

export function SkillsFields({ profile }: { profile: Profile }) {
  return (
    <FormSection title="Skills and languages">
      <TagInput
        label="Skills"
        name="skills"
        placeholder="Python, SQL, Docker…"
        defaultValue={profile.skills}
      />
      <MultiSelect
        label="Languages you work in"
        name="languages"
        options={LANGUAGE_OPTIONS}
        placeholder="Add a language…"
        defaultValue={profile.languages}
      />
    </FormSection>
  );
}
