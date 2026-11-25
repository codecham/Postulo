import { setMatchStatus } from "@/app/jobs/actions";
import { StatusButton } from "@/components/matches/status-button";
import type { JobMatch, MatchStatus } from "@/lib/job-search/types";

type Action = { label: string; status: MatchStatus };

// What the user can do with a match, depending on where it stands
const ACTIONS: Record<MatchStatus, Action[]> = {
  new: [
    { label: "Save", status: "saved" },
    { label: "Dismiss", status: "dismissed" },
  ],
  saved: [
    { label: "Unsave", status: "new" },
    { label: "Dismiss", status: "dismissed" },
  ],
  dismissed: [{ label: "Restore", status: "new" }],
};

/** Save, dismiss or restore a match: one click, no confirmation (it can be undone). */
export function MatchActions({ match }: { match: JobMatch }) {
  return (
    <div className="flex gap-2">
      {ACTIONS[match.status].map((action) => (
        <form
          key={action.status}
          action={setMatchStatus.bind(null, match.id, action.status)}
        >
          <StatusButton>{action.label}</StatusButton>
        </form>
      ))}
    </div>
  );
}
