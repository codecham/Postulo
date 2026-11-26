import { CheckIcon } from "@/components/ui/icons";
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
    <ul className="text-muted flex flex-col gap-1 text-sm">
      {reasons.map((reason) => (
        <li key={reason} className="flex items-start gap-2">
          <CheckIcon className="text-success mt-0.5 size-4 shrink-0" />
          {reason}
        </li>
      ))}
    </ul>
  );
}
