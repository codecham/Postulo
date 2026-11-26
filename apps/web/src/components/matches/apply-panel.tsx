import Link from "next/link";

import { DocumentLinks } from "@/components/applications/document-links";
import { WriteApplication } from "@/components/applications/write-application";
import { ApplyStep, type StepState } from "@/components/matches/apply-step";
import { SendActions } from "@/components/tracking/send-actions";
import { Card } from "@/components/ui/card";
import { PencilIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
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

/**
 * From a match to a sent application, in three steps that light up in turn:
 * write the documents, download them, send and mark as sent.
 */
export function ApplyPanel({
  matchId,
  offer,
  application,
  tracking,
  canUseAi,
}: ApplyPanelProps) {
  const written = application !== null;
  const sent = tracking !== null;
  const steps: Record<"write" | "download" | "send", StepState> = {
    write: written || sent ? "done" : "current",
    download: !written ? "upcoming" : sent ? "done" : "current",
    send: sent ? "done" : written ? "current" : "upcoming",
  };

  return (
    <Card
      id="apply"
      title={sent ? "Application sent" : "Apply"}
      description="A CV and a cover letter tailored to this offer, in its language."
    >
      <ol>
        <ApplyStep
          number={1}
          title="Write your CV and letter"
          state={steps.write}
        >
          {written ? (
            <details className="group text-sm">
              <summary className="text-muted hover:text-fg cursor-pointer">
                Write a new version
              </summary>
              <div className="mt-4">
                <WriteApplication matchId={matchId} canUseAi={canUseAi} />
              </div>
            </details>
          ) : (
            !sent && <WriteApplication matchId={matchId} canUseAi={canUseAi} />
          )}
        </ApplyStep>
        <ApplyStep number={2} title="Check and download" state={steps.download}>
          {application && (
            <>
              <DocumentLinks application={application} />
              <Link
                href={`/jobs/${matchId}/application`}
                className={`${buttonClassName("ghost")} self-start`}
              >
                <PencilIcon />
                Review and edit
              </Link>
            </>
          )}
        </ApplyStep>
        <ApplyStep
          number={3}
          title={`Send it on ${offer.source}`}
          state={steps.send}
          isLast
        >
          <SendActions
            matchId={matchId}
            offer={offer}
            tracking={tracking}
            primary={written}
          />
        </ApplyStep>
      </ol>
    </Card>
  );
}
