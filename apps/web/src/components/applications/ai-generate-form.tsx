import { generateApplication } from "@/app/jobs/[id]/application/actions";
import { ActionForm } from "@/components/ui/action-form";
import { Alert } from "@/components/ui/alert";

type AiGenerateFormProps = {
  matchId: string;
  isAvailable: boolean; // false when the server has no Claude API key
};

/** Paid path: the server asks Claude for the CV and the cover letter, in one click. */
export function AiGenerateForm({ matchId, isAvailable }: AiGenerateFormProps) {
  if (!isAvailable) {
    return (
      <Alert title="Not available on this server">
        AI generation needs a Claude API key on the server. Use the free Claude
        Code tab instead.
      </Alert>
    );
  }
  return (
    <ActionForm
      action={generateApplication.bind(null, matchId)}
      submitLabel="Write my application"
      pendingLabel="Writing… (about 30 seconds)"
    >
      <p className="text-muted text-sm">
        Claude writes a CV and a cover letter for this offer, in its language,
        from your profile only. You review both before downloading them.
      </p>
    </ActionForm>
  );
}
