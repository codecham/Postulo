/** The match score, from 0 to 100, colored by how good it is. */
export function ScoreBadge({ score }: { score: number }) {
  return (
    <span
      title="How well the offer fits your profile, from 0 to 100"
      className={`shrink-0 rounded-full px-2.5 py-1 text-sm font-semibold tabular-nums ${scoreColor(score)}`}
    >
      {score}
    </span>
  );
}

function scoreColor(score: number): string {
  if (score >= 75) {
    return "bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300";
  }
  if (score >= 50) {
    return "bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300";
  }
  return "bg-gray-100 dark:bg-gray-800";
}
