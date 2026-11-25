import { markAsSent } from "@/app/applications/actions";
import { StatusButton } from "@/components/matches/status-button";

/** One click once the application is sent: it moves to the tracking board. */
export function MarkAsSentButton({ matchId }: { matchId: string }) {
  return (
    <form action={markAsSent.bind(null, matchId)}>
      <StatusButton>✓ Mark as sent</StatusButton>
    </form>
  );
}
