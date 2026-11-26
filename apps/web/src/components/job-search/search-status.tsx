import { AutoRefresh } from "@/components/job-search/auto-refresh";
import { StartSearchButton } from "@/components/job-search/start-search-button";
import { cardClassName } from "@/components/ui/card";
import { SearchIcon } from "@/components/ui/icons";
import { formatDateTime, isActive, statusLabel } from "@/lib/job-search/runs";
import type { JobSearchRun } from "@/lib/job-search/types";

/** The last search, in one line, and a button to start a new one. */
export function SearchStatus({ run }: { run: JobSearchRun | null }) {
  const active = isActive(run);

  return (
    <section
      aria-label="Search"
      className={`${cardClassName} flex flex-wrap items-center justify-between gap-4 p-4`}
    >
      <div className="flex items-start gap-3">
        <span className="bg-accent-soft text-accent-text flex size-9 shrink-0 items-center justify-center rounded-lg">
          <SearchIcon className={`size-4 ${active ? "animate-pulse" : ""}`} />
        </span>
        {run ? (
          <RunSummary run={run} />
        ) : (
          <div className="text-sm">
            <p className="font-medium">No search yet</p>
            <p className="text-muted">
              Postulo searches every day on its own. Start the first one now.
            </p>
          </div>
        )}
      </div>
      <StartSearchButton disabled={active} />
      {active && <AutoRefresh />}
    </section>
  );
}

function RunSummary({ run }: { run: JobSearchRun }) {
  return (
    <div className="flex flex-col gap-0.5 text-sm">
      <p className="font-medium">
        Last search {formatDateTime(run.created_at)}
        <span className="text-muted font-normal"> · {statusLabel(run)}</span>
      </p>
      {run.status === "succeeded" && (
        <p className="text-muted">
          {run.offers_found} offers checked ({run.offers_new} new),{" "}
          {run.matches_found} match your profile. Next one runs on its own
          tomorrow.
        </p>
      )}
      {run.error && <p className="text-danger">{run.error}</p>}
      {run.failed_sources.length > 0 && (
        <p className="text-warning">
          Could not reach: {run.failed_sources.join(", ")}.
        </p>
      )}
    </div>
  );
}
