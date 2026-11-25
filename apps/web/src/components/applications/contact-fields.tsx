import { FormSection } from "@/components/ui/form-section";
import { inputClassName, labelClassName } from "@/components/ui/styles";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import type { ApplicationLanguage, Contact } from "@/lib/applications/types";

const LANGUAGES: { value: ApplicationLanguage; label: string }[] = [
  { value: "en", label: "English" },
  { value: "fr", label: "Français" },
];

type ContactFieldsProps = {
  contact: Contact;
  language: ApplicationLanguage;
};

/** The header of both documents, and the language of their fixed words and dates. */
export function ContactFields({ contact, language }: ContactFieldsProps) {
  return (
    <FormSection
      title="Header"
      description="Shown at the top of the CV and the letter."
    >
      <div className="grid gap-4 sm:grid-cols-2">
        <TextField
          label="Full name"
          name="contact.full_name"
          maxLength={200}
          defaultValue={contact.full_name ?? ""}
        />
        <TextField
          label="Email"
          name="contact.email"
          type="email"
          maxLength={200}
          defaultValue={contact.email ?? ""}
        />
        <TextField
          label="Phone"
          name="contact.phone"
          type="tel"
          maxLength={100}
          defaultValue={contact.phone ?? ""}
        />
        <TextField
          label="City"
          name="contact.city"
          maxLength={100}
          defaultValue={contact.city ?? ""}
        />
      </div>
      <TextareaField
        label="Links"
        name="contact.links"
        rows={2}
        hint="One per line: LinkedIn, GitHub, portfolio…"
        defaultValue={(contact.links ?? []).join("\n")}
      />
      <label className={labelClassName}>
        Document language
        <select
          name="language"
          defaultValue={language}
          className={inputClassName}
        >
          {LANGUAGES.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </label>
    </FormSection>
  );
}
