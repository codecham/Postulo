import type { JobMatch } from "@/lib/job-search/types";

/** One matching offer: where it is, why it fits, and a link to apply on the job board. */
export function MatchItem({ match }: { match: JobMatch }) {
  const { offer } = match;
  const details = [offer.company, offer.location, offer.salary]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="flex items-start justify-between gap-4">
      <div className="flex flex-col gap-1">
        <a
          href={offer.url}
          target="_blank"
          rel="noopener"
          className="font-semibold hover:underline"
        >
          {offer.title}
        </a>
        <p className="text-sm">{details}</p>
        {match.matched_skills.length > 0 && (
          <p className="text-xs text-gray-500">
            Your skills: {match.matched_skills.join(", ")}
          </p>
        )}
        <p className="text-xs text-gray-500">via {offer.source}</p>
      </div>
      <ScoreBadge score={match.score} />
    </div>
  );
}

function ScoreBadge({ score }: { score: number }) {
  return (
    <span
      title="How well the offer fits your profile, from 0 to 100"
      className="rounded-full bg-gray-100 px-2.5 py-1 text-sm font-semibold tabular-nums dark:bg-gray-800"
    >
      {score}
    </span>
  );
}
