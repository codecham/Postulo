import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { DiscardImportButton } from "@/components/cv-import/discard-import-button";
import { ImportReviewForm } from "@/components/cv-import/import-review-form";
import { ImportWarnings } from "@/components/cv-import/import-warnings";
import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { getCvImport } from "@/lib/cv-import/queries";

export const metadata: Metadata = { title: "Review your CV import" };

type ReviewPageProps = { params: Promise<{ id: string }> };

export default function ReviewCvImportPage({ params }: ReviewPageProps) {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<PageLoading />}>
        <ReviewContent params={params} />
      </Suspense>
    </section>
  );
}

async function ReviewContent({ params }: ReviewPageProps) {
  const { id } = await params;
  const { draft } = await getCvImport(id);
  if (!draft) {
    redirect("/profile"); // already applied or discarded
  }

  return (
    <>
      <PageHeader
        title="Review your profile"
        description="Your current profile, completed with your CV. Check and edit it, then save."
        action={<DiscardImportButton importId={id} />}
      />
      <ImportWarnings warnings={draft.warnings} />
      <ImportReviewForm importId={id} draft={draft} />
    </>
  );
}
