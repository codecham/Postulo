import Link from "next/link";

import { DocumentLinks } from "@/components/applications/document-links";
import { WriteApplication } from "@/components/applications/write-application";
import { MarkAsSentButton } from "@/components/tracking/mark-as-sent-button";
import { StatusBadge } from "@/components/tracking/status-badge";
import { Card } from "@/components/ui/card";
import { secondaryButtonClassName } from "@/components/ui/styles";
import type { Application } from "@/lib/applications/types";
import type { JobOffer } from "@/lib/job-search/types";
import type { Tracking } from "@/lib/tracking/types";

type ApplyPanelProps = {
  matchId: string;
  offer: JobOffer;
  application: Application | null; // null until one is written
  tracking: Tracking | null; // null until marked as sent
  canUseAi: boolean;
};

/** From a match to a sent application: write, download, apply, mark as sent. */
export function ApplyPanel({
  matchId,
  offer,
  application,
  tracking,
  canUseAi,
}: ApplyPanelProps) {
  return (
    <Card
      title="Apply"
      description="A CV and a cover letter tailored to this offer, in its language."
    >
      {application ? (
        <>
          <DocumentLinks application={application} />
          <details className="text-sm">
            <summary className="cursor-pointer text-gray-600 dark:text-gray-400">
              Write a new version
            </summary>
            <div className="mt-4">
              <WriteApplication matchId={matchId} canUseAi={canUseAi} />
            </div>
          </details>
        </>
      ) : (
        <WriteApplication matchId={matchId} canUseAi={canUseAi} />
      )}
      <div className="flex flex-wrap gap-2">
        {application && (
          <Link
            href={`/jobs/${matchId}/application`}
            className={secondaryButtonClassName}
          >
            Review and edit
          </Link>
        )}
        <a
          href={offer.url}
          target="_blank"
          rel="noopener"
          className={secondaryButtonClassName}
        >
          Apply on {offer.source} ↗
        </a>
        {tracking ? (
          <span className="flex items-center gap-2 text-sm">
            Sent <StatusBadge status={tracking.status} />
          </span>
        ) : (
          <MarkAsSentButton matchId={matchId} />
        )}
      </div>
    </Card>
  );
}
