import type { Metadata } from "next";

import { ClaudeCodeImportForm } from "@/components/cv-import/claude-code-import-form";
import { CvUploadForm } from "@/components/cv-import/cv-upload-form";
import { PageHeader } from "@/components/layout/page-header";
import { Tabs } from "@/components/ui/tabs";

export const metadata: Metadata = { title: "Import a CV" };

export default function ImportCvPage() {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Import your CV"
        description="Postulo reads your CV with AI and pre-fills your profile. You check everything before it is saved."
      />
      <Tabs
        label="How to read your CV"
        tabs={[
          {
            id: "upload",
            label: "Upload a PDF",
            content: <CvUploadForm />,
          },
          {
            id: "claude-code",
            label: "Claude Code (free)",
            content: <ClaudeCodeImportForm />,
          },
        ]}
      />
    </section>
  );
}
