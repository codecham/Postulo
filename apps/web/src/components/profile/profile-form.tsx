import { saveProfile } from "@/app/profile/actions";
import { IdentityFields } from "@/components/profile/identity-fields";
import { SearchCriteriaFields } from "@/components/profile/search-criteria-fields";
import { SkillsFields } from "@/components/profile/skills-fields";
import { ActionForm } from "@/components/ui/action-form";
import type { Profile } from "@/lib/profile/types";

export function ProfileForm({ profile }: { profile: Profile }) {
  return (
    <ActionForm action={saveProfile} submitLabel="Save profile">
      <IdentityFields profile={profile} />
      <SkillsFields profile={profile} />
      <SearchCriteriaFields profile={profile} />
    </ActionForm>
  );
}
