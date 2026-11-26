import { CopyButton } from "@/components/ui/copy-button";
import { DownloadIcon } from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";
import { letterText } from "@/lib/applications/letter-text";
import {
  type Application,
  DOCUMENTS,
  type DocumentName,
} from "@/lib/applications/types";

/** Download the PDFs, and copy the letter for forms that want plain text. */
export function DocumentLinks({ application }: { application: Application }) {
  const names = Object.keys(DOCUMENTS) as DocumentName[];
  return (
    <div className="flex flex-wrap items-center gap-2">
      {names.map((name) => (
        <a
          key={name}
          href={`/jobs/${application.match_id}/application/${name}`}
          download
          className={buttonClassName("secondary")}
        >
          <DownloadIcon />
          {DOCUMENTS[name]}
          <span className="text-muted text-xs">PDF</span>
        </a>
      ))}
      <CopyButton
        text={letterText(application.content)}
        label="Copy the letter text"
      />
    </div>
  );
}
