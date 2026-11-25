import type { JobSearchRun } from "@/lib/job-search/types";
import { site } from "@/lib/site";

/** True while the worker has not finished the search yet. */
export function isActive(run: JobSearchRun | null): boolean {
  return run?.status === "pending" || run?.status === "running";
}

const STATUS_LABELS: Record<JobSearchRun["status"], string> = {
  pending: "Waiting for the worker…",
  running: "Searching…",
  succeeded: "Done",
  failed: "Failed",
};

export function statusLabel(run: JobSearchRun): string {
  return STATUS_LABELS[run.status];
}

/** "25 Nov 2026, 23:40", in the site's time zone. */
export function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: site.timeZone,
  }).format(new Date(value));
}
