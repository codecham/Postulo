import { cardClassName } from "@/components/ui/card";
import type { TrackingBoard } from "@/lib/tracking/types";

type Stat = { label: string; value: number; highlight?: boolean };

/** The numbers that matter at a glance: sent, in progress, follow-ups due. */
export function BoardStats({ board }: { board: TrackingBoard }) {
  const { counts } = board;
  const due = board.items.filter((item) => item.follow_up_due).length;
  const stats: Stat[] = [
    { label: "Sent", value: board.items.length },
    { label: "Interviews", value: counts.interview },
    { label: "Offers", value: counts.offer },
    { label: "Follow-ups due", value: due, highlight: due > 0 },
  ];

  return (
    <dl className="grid grid-cols-2 gap-3 sm:grid-cols-4">
      {stats.map((stat) => (
        <div key={stat.label} className={`${cardClassName} p-4`}>
          <dt className="text-muted text-sm">{stat.label}</dt>
          <dd
            className={`text-2xl font-semibold tabular-nums ${stat.highlight ? "text-warning" : ""}`}
          >
            {stat.value}
          </dd>
        </div>
      ))}
    </dl>
  );
}
