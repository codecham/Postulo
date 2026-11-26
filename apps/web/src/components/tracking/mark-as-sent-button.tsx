import { markAsSent } from "@/app/applications/actions";
import { StatusButton } from "@/components/matches/status-button";
import { CheckIcon } from "@/components/ui/icons";
import type { ButtonVariant } from "@/components/ui/styles";

type MarkAsSentButtonProps = {
  matchId: string;
  variant?: ButtonVariant;
};

/** One click once the application is sent: it moves to the tracking board. */
export function MarkAsSentButton({
  matchId,
  variant = "secondary",
}: MarkAsSentButtonProps) {
  return (
    <form action={markAsSent.bind(null, matchId)}>
      <StatusButton variant={variant}>
        <CheckIcon />I sent it
      </StatusButton>
    </form>
  );
}
