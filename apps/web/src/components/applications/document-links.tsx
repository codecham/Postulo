import { CopyButton } from "@/components/ui/copy-button";
import { letterText } from "@/lib/applications/letter-text";
import {
  type Application,
  DOCUMENTS,
  type DocumentName,
} from "@/lib/applications/types";

const primaryLinkClassName =
  "rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 dark:bg-white dark:text-gray-900";

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
          className={primaryLinkClassName}
        >
          ↓ {DOCUMENTS[name]} (PDF)
        </a>
      ))}
      <CopyButton
        text={letterText(application.content)}
        label="Copy the letter text"
      />
    </div>
  );
}
