import { startCvImport } from "@/app/profile/import/actions";
import { ActionForm } from "@/components/ui/action-form";
import { FileField } from "@/components/ui/file-field";
import { FormSection } from "@/components/ui/form-section";
import { CV_MAX_BYTES, CV_MAX_SIZE_LABEL } from "@/lib/cv-import/limits";

export function CvUploadForm() {
  return (
    <ActionForm
      action={startCvImport}
      submitLabel="Analyse my CV"
      pendingLabel="Analysing your CV… (up to a minute)"
    >
      <FormSection
        title="Upload your CV"
        description="A CV, or your LinkedIn profile saved as PDF (on your profile: More → Save to PDF). Read by the Claude API: this server needs an API key."
      >
        <FileField
          label="PDF file"
          name="file"
          accept="application/pdf,.pdf"
          required
          maxBytes={CV_MAX_BYTES}
          tooLargeMessage={`The file must be under ${CV_MAX_SIZE_LABEL}.`}
          hint={`PDF only, ${CV_MAX_SIZE_LABEL} and 10 pages at most. The file itself is not kept.`}
        />
      </FormSection>
    </ActionForm>
  );
}
