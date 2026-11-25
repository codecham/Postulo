import { AutoRefresh } from "@/components/job-search/auto-refresh";
import { StartSearchButton } from "@/components/job-search/start-search-button";
import { Card } from "@/components/ui/card";
import { formatDateTime, isActive, statusLabel } from "@/lib/job-search/runs";
import type { JobSearchRun } from "@/lib/job-search/types";

/** The last search, and a button to start a new one. */
export function SearchStatus({ run }: { run: JobSearchRun | null }) {
  const active = isActive(run);

  return (
    <Card
      title="Search"
      description="Postulo searches every day on its own. You can also search now."
    >
      {run ? (
        <RunSummary run={run} />
      ) : (
        <p className="text-sm">No search yet.</p>
      )}
      <StartSearchButton disabled={active} />
      {active && <AutoRefresh />}
    </Card>
  );
}

function RunSummary({ run }: { run: JobSearchRun }) {
  return (
    <div className="flex flex-col gap-1 text-sm">
      <p>
        <span className="font-medium">Last search:</span>{" "}
        {formatDateTime(run.created_at)} · {statusLabel(run)}
      </p>
      {run.status === "succeeded" && (
        <p className="text-gray-600 dark:text-gray-400">
          {run.offers_found} offers checked ({run.offers_new} new),{" "}
          {run.matches_found} match your profile.
        </p>
      )}
      {run.error && <p className="text-red-600">{run.error}</p>}
      {run.failed_sources.length > 0 && (
        <p className="text-amber-700 dark:text-amber-500">
          Could not reach: {run.failed_sources.join(", ")}.
        </p>
      )}
    </div>
  );
}
