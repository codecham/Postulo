import type { CSSProperties } from "react";

/** The match score, from 0 to 100, as a ring that fills and colors with it. */
export function ScoreBadge({ score }: { score: number }) {
  const style = {
    background: `conic-gradient(${scoreColor(score)} ${score}%, var(--line) 0)`,
  } satisfies CSSProperties;

  return (
    <span
      title="How well the offer fits your profile, from 0 to 100"
      className="flex size-12 shrink-0 items-center justify-center rounded-full p-1"
      style={style}
    >
      <span className="bg-surface flex size-full flex-col items-center justify-center rounded-full leading-none">
        <span className="text-sm font-semibold tabular-nums">{score}</span>
        <span className="sr-only"> / 100 match</span>
      </span>
    </span>
  );
}

function scoreColor(score: number): string {
  if (score >= 75) {
    return "var(--success-text)";
  }
  if (score >= 50) {
    return "var(--accent)";
  }
  return "var(--muted)";
}
