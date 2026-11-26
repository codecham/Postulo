import Link from "next/link";

import { MarkAsSentButton } from "@/components/tracking/mark-as-sent-button";
import { StatusBadge } from "@/components/tracking/status-badge";
import { ExternalLinkIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
import type { JobOffer } from "@/lib/job-search/types";
import type { Tracking } from "@/lib/tracking/types";

type SendActionsProps = {
  matchId: string;
  offer: JobOffer;
  tracking: Tracking | null; // null until marked as sent
  primary?: boolean; // the next thing to do: stand out
};

/** The last mile: open the offer to apply, then say it is sent. */
export function SendActions({
  matchId,
  offer,
  tracking,
  primary = true,
}: SendActionsProps) {
  if (tracking) {
    return (
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <StatusBadge status={tracking.status} />
        <Link
          href="/applications"
          className="text-accent-text font-medium hover:underline"
        >
          Follow it on your board
        </Link>
      </div>
    );
  }
  return (
    <div className="flex flex-wrap gap-2">
      <a
        href={offer.url}
        target="_blank"
        rel="noopener"
        className={buttonClassName(primary ? "primary" : "secondary")}
      >
        Apply on {offer.source}
        <ExternalLinkIcon />
        <span className="sr-only">(opens in a new tab)</span>
      </a>
      <MarkAsSentButton matchId={matchId} />
    </div>
  );
}
