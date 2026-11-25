import { FormSection } from "@/components/ui/form-section";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import type { Profile } from "@/lib/profile/types";

export function IdentityFields({ profile }: { profile: Profile }) {
  return (
    <FormSection title="About you">
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          label="Full name"
          name="full_name"
          autoComplete="name"
          maxLength={200}
          defaultValue={profile.full_name ?? ""}
        />
        <TextField
          label="City"
          name="city"
          autoComplete="address-level2"
          maxLength={100}
          defaultValue={profile.city ?? ""}
        />
      </div>
      <TextField
        label="Headline"
        name="headline"
        maxLength={200}
        placeholder="Backend developer, Python and cloud"
        defaultValue={profile.headline ?? ""}
      />
      <TextareaField
        label="Summary"
        name="summary"
        maxLength={5000}
        hint="A few lines about your background and what you are good at."
        defaultValue={profile.summary ?? ""}
      />
    </FormSection>
  );
}
