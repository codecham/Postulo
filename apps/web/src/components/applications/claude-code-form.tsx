import { createApplicationFromClaudeCode } from "@/app/jobs/[id]/application/actions";
import { ActionForm } from "@/components/ui/action-form";
import { CopyButton } from "@/components/ui/copy-button";
import { TextareaField } from "@/components/ui/textarea-field";

/** Free path: Claude Code writes the application with the user's plan, they paste it. */
export function ClaudeCodeForm({ matchId }: { matchId: string }) {
  const command = `/tailor-application ${matchId}`;
  return (
    <ActionForm
      action={createApplicationFromClaudeCode.bind(null, matchId)}
      submitLabel="Create my application"
      pendingLabel="Creating…"
    >
      <ol className="flex list-decimal flex-col gap-2 pl-5 text-sm">
        <li>
          <span className="flex flex-wrap items-center gap-2">
            Run in Claude Code, in this project:
            <code className="bg-subtle rounded-md px-1.5 py-0.5 font-mono text-xs break-all">
              {command}
            </code>
            <CopyButton text={command} label="Copy" />
          </span>
        </li>
        <li>It copies the result to your clipboard: paste it below.</li>
      </ol>
      <TextareaField
        label="Result from Claude Code"
        name="application"
        rows={6}
        required
        spellCheck={false}
        placeholder='{"cv": {…}, "cover_letter": {…}}'
        className="font-mono text-xs"
      />
    </ActionForm>
  );
}
