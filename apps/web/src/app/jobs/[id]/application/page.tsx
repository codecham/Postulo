import type { Metadata } from "next";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { DocumentLinks } from "@/components/applications/document-links";
import { ReviewForm } from "@/components/applications/review-form";
import { PageHeader } from "@/components/layout/page-header";
import { getApplication } from "@/lib/applications/queries";
import { getMatch } from "@/lib/job-search/queries";

export const metadata: Metadata = { title: "Your application" };

type ApplicationPageProps = PageProps<"/jobs/[id]/application">;

export default function ApplicationPage({ params }: ApplicationPageProps) {
  return (
    <section className="flex flex-col gap-8">
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<p className="text-gray-500">Loading…</p>}>
        <ApplicationContent params={params} />
      </Suspense>
    </section>
  );
}

async function ApplicationContent({
  params,
}: Pick<ApplicationPageProps, "params">) {
  const { id } = await params;
  const [match, application] = await Promise.all([
    getMatch(id),
    getApplication(id),
  ]);
  if (!application) {
    redirect(`/jobs/${id}`); // nothing written yet: write it from the offer
  }
  const { offer } = match;

  return (
    <>
      <Link href={`/jobs/${id}`} className="text-sm underline">
        ← {offer.title}
      </Link>
      <PageHeader
        title="Your application"
        description={`Tailored to ${offer.company ?? "this offer"}. Check it, edit what you want, save, then download.`}
      />
      <div className="flex flex-col gap-3">
        <DocumentLinks application={application} />
        <a
          href={offer.url}
          target="_blank"
          rel="noopener"
          className="text-sm underline"
        >
          Apply on {offer.source} ↗
        </a>
      </div>
      <ReviewForm application={application} />
    </>
  );
}
