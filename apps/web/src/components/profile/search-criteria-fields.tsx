import { CheckboxField } from "@/components/ui/checkbox-field";
import { CheckboxGroup } from "@/components/ui/checkbox-group";
import { FormSection } from "@/components/ui/form-section";
import { MultiSelect } from "@/components/ui/multi-select";
import { TagInput } from "@/components/ui/tag-input";
import {
  COUNTRY_OPTIONS,
  LANGUAGE_OPTIONS,
  WORK_MODE_OPTIONS,
} from "@/lib/profile/options";
import type { ProfileValues } from "@/lib/profile/types";

export function SearchCriteriaFields({ profile }: { profile: ProfileValues }) {
  return (
    <FormSection
      title="What you are looking for"
      description="Postulo uses these criteria to find matching job offers."
    >
      <TagInput
        label="Job titles"
        name="desired_titles"
        placeholder="Backend developer…"
        defaultValue={profile.desired_titles}
      />
      <CheckboxGroup
        legend="Work modes"
        name="work_modes"
        options={WORK_MODE_OPTIONS}
        defaultValue={profile.work_modes}
      />
      <MultiSelect
        label="Countries"
        name="countries"
        options={COUNTRY_OPTIONS}
        placeholder="Add a country…"
        defaultValue={profile.countries}
      />
      <CheckboxField
        label="Also open to remote jobs based in other countries"
        name="open_to_remote_abroad"
        defaultChecked={profile.open_to_remote_abroad}
      />
      <MultiSelect
        label="Languages of the offers"
        name="offer_languages"
        options={LANGUAGE_OPTIONS}
        placeholder="Add a language…"
        hint="Offers written in other languages are left out. Empty: any language."
        defaultValue={profile.offer_languages}
      />
    </FormSection>
  );
}
