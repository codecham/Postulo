import type { Metadata } from "next";
import { Suspense } from "react";

import { ClaudeCodeImportForm } from "@/components/cv-import/claude-code-import-form";
import { CvUploadForm } from "@/components/cv-import/cv-upload-form";
import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { Tabs } from "@/components/ui/tabs";
import { getCvImportOptions } from "@/lib/cv-import/queries";

export const metadata: Metadata = { title: "Import a CV" };

export default function ImportCvPage() {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
      <PageHeader
        title="Import your CV"
        description="Postulo reads your CV with AI and pre-fills your profile. You check everything before it is saved."
      />
      {/* Read at request time: whether the server can analyse PDFs itself */}
      <Suspense fallback={<PageLoading />}>
        <ImportMethods />
      </Suspense>
    </section>
  );
}

async function ImportMethods() {
  const { pdf_upload: canUploadPdf } = await getCvImportOptions();

  return (
    <Tabs
      label="How to read your CV"
      // Open the method that works: the free one when the server has no API key
      defaultId={canUploadPdf ? "upload" : "claude-code"}
      tabs={[
        {
          id: "upload",
          label: "Upload a PDF",
          content: <CvUploadForm isAvailable={canUploadPdf} />,
        },
        {
          id: "claude-code",
          label: "Claude Code (free)",
          content: <ClaudeCodeImportForm />,
        },
      ]}
    />
  );
}
