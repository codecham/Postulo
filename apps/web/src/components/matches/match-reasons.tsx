import { placeLabel, relevanceLabel } from "@/lib/job-search/labels";
import type { JobMatch } from "@/lib/job-search/types";

/** Why the offer matches: closeness to the profile, skills it names, and place. */
export function MatchReasons({ match }: { match: JobMatch }) {
  const { explanation, offer } = match;
  const reasons = [
    relevanceLabel(explanation.relevance),
    explanation.matched_skills.length > 0 &&
      `Mentions your skills: ${explanation.matched_skills.join(", ")}`,
    placeLabel(explanation.place, offer),
  ].filter((reason): reason is string => Boolean(reason));

  return (
    <ul className="flex flex-col gap-0.5 text-sm text-gray-600 dark:text-gray-400">
      {reasons.map((reason) => (
        <li key={reason} className="flex gap-2">
          <span aria-hidden className="text-green-600">
            ✓
          </span>
          {reason}
        </li>
      ))}
    </ul>
  );
}
