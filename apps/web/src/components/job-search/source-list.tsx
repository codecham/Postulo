import type { JobSource } from "@/lib/job-search/types";

/** Credits the job boards the offers come from (their terms ask for it). */
export function SourceList({ sources }: { sources: JobSource[] }) {
  const enabled = sources.filter((source) => source.enabled);
  const disabled = sources.filter((source) => !source.enabled);

  return (
    <p className="text-muted text-xs">
      Offers from{" "}
      {enabled.map((source, index) => (
        <span key={source.name}>
          {index > 0 && ", "}
          <a
            href={source.url}
            target="_blank"
            rel="noopener"
            className="hover:text-fg underline-offset-2 hover:underline"
          >
            {source.name}
          </a>
        </span>
      ))}
      .
      {disabled.length > 0 &&
        ` Not configured: ${disabled.map((source) => source.name).join(", ")}.`}
    </p>
  );
}
