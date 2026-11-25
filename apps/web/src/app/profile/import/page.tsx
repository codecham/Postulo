import type { Metadata } from "next";

import { CvUploadForm } from "@/components/cv-import/cv-upload-form";
import { PageHeader } from "@/components/layout/page-header";

export const metadata: Metadata = { title: "Import a CV" };

export default function ImportCvPage() {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Import your CV"
        description="Postulo reads your CV with AI and pre-fills your profile. You check everything before it is saved."
      />
      <CvUploadForm />
    </section>
  );
}
