import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { DocumentLinks } from "@/components/applications/document-links";
import { ReviewForm } from "@/components/applications/review-form";
import { BackLink } from "@/components/layout/back-link";
import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { SendActions } from "@/components/tracking/send-actions";
import { Card } from "@/components/ui/card";
import { getApplication } from "@/lib/applications/queries";
import { getMatch } from "@/lib/job-search/queries";
import { getTracking } from "@/lib/tracking/queries";

export const metadata: Metadata = { title: "Your application" };

type ApplicationPageProps = PageProps<"/jobs/[id]/application">;

export default function ApplicationPage({ params }: ApplicationPageProps) {
  return (
    <section className="flex flex-col gap-6">
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<PageLoading />}>
        <ApplicationContent params={params} />
      </Suspense>
    </section>
  );
}

async function ApplicationContent({
  params,
}: Pick<ApplicationPageProps, "params">) {
  const { id } = await params;
  const [match, application, tracking] = await Promise.all([
    getMatch(id),
    getApplication(id),
    getTracking(id),
  ]);
  if (!application) {
    redirect(`/jobs/${id}`); // nothing written yet: write it from the offer
  }
  const { offer } = match;

  return (
    <>
      <PageHeader
        eyebrow={<BackLink href={`/jobs/${id}`} label={offer.title} />}
        title="Your application"
        description={`Tailored to ${offer.company ?? "this offer"}. Edit what you want and save: the PDFs follow.`}
      />
      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
        {/* Everything needed to finish stays in view while the form scrolls */}
        <aside className="flex flex-col gap-6 lg:sticky lg:top-24 lg:order-last">
          <Card title="Download">
            <DocumentLinks application={application} />
          </Card>
          <Card title={tracking ? "Sent" : `Send it on ${offer.source}`}>
            <SendActions matchId={id} offer={offer} tracking={tracking} />
          </Card>
        </aside>
        <ReviewForm application={application} />
      </div>
    </>
  );
}
