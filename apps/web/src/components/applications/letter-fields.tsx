import { FormSection } from "@/components/ui/form-section";
import { TextareaField } from "@/components/ui/textarea-field";
import { TextField } from "@/components/ui/text-field";
import type { CoverLetter } from "@/lib/applications/types";

/** The cover letter: the sender, company and date are added in the PDF. */
export function LetterFields({ letter }: { letter: CoverLetter }) {
  return (
    <FormSection title="Cover letter">
      <TextField
        label="Subject"
        name="letter.subject"
        required
        maxLength={200}
        defaultValue={letter.subject}
      />
      <TextField
        label="Greeting"
        name="letter.greeting"
        required
        maxLength={100}
        defaultValue={letter.greeting}
      />
      <TextareaField
        label="Letter"
        name="letter.paragraphs"
        required
        rows={14}
        hint="Separate the paragraphs with an empty line."
        defaultValue={letter.paragraphs.join("\n\n")}
      />
      <TextField
        label="Closing"
        name="letter.closing"
        required
        maxLength={200}
        defaultValue={letter.closing}
      />
    </FormSection>
  );
}
