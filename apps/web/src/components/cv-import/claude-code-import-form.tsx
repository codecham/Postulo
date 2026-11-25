import { startCvImportFromClaudeCode } from "@/app/profile/import/actions";
import { ActionForm } from "@/components/ui/action-form";
import { FormSection } from "@/components/ui/form-section";
import { TextareaField } from "@/components/ui/textarea-field";

const COMMAND = "/import-cv ~/Downloads/my-cv.pdf";

/** Free import: Claude Code extracts the CV with the user's plan, they paste the result. */
export function ClaudeCodeImportForm() {
  return (
    <ActionForm
      action={startCvImportFromClaudeCode}
      submitLabel="Create the draft"
      pendingLabel="Creating the draft…"
    >
      <FormSection
        title="Extract your CV with Claude Code"
        description="Free with your Claude plan: the extraction runs in your own Claude Code session."
      >
        <ol className="flex list-decimal flex-col gap-1 pl-5 text-sm">
          <li>
            In Claude Code, in this project, run{" "}
            <code className="rounded bg-gray-100 px-1 dark:bg-gray-800">
              {COMMAND}
            </code>{" "}
            with the path of your PDF.
          </li>
          <li>It copies the result to your clipboard: paste it below.</li>
        </ol>
        <TextareaField
          label="Result from Claude Code"
          name="extraction"
          rows={8}
          required
          spellCheck={false}
          placeholder='{"is_cv": true, "full_name": "…", …}'
          className="font-mono text-xs"
        />
      </FormSection>
    </ActionForm>
  );
}
