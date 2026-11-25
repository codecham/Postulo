import Link from "next/link";

import { DocumentLinks } from "@/components/applications/document-links";
import { WriteApplication } from "@/components/applications/write-application";
import { Card } from "@/components/ui/card";
import { secondaryButtonClassName } from "@/components/ui/styles";
import type { Application } from "@/lib/applications/types";
import type { JobOffer } from "@/lib/job-search/types";

type ApplyPanelProps = {
  matchId: string;
  offer: JobOffer;
  application: Application | null; // null until one is written
  canUseAi: boolean;
};

/** From a match to a sent application: write the documents, download them, apply. */
export function ApplyPanel({
  matchId,
  offer,
  application,
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
      </div>
    </Card>
  );
}
