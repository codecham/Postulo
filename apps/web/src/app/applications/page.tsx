import type { Metadata } from "next";
import { Suspense } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { TrackingBoard } from "@/components/tracking/tracking-board";
import { getTrackingBoard } from "@/lib/tracking/queries";

export const metadata: Metadata = { title: "Applications" };

export default function ApplicationsPage() {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Your applications"
        description="What you sent, where it stands, and when to follow up."
      />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<PageLoading />}>
        <Board />
      </Suspense>
    </section>
  );
}

async function Board() {
  return <TrackingBoard board={await getTrackingBoard()} />;
}
