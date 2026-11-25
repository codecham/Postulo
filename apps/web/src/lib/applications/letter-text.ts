import type { ApplicationContent } from "@/lib/applications/types";

/** The cover letter as plain text, to paste into an application form or an email. */
export function letterText({ cover_letter, contact }: ApplicationContent) {
  return [
    cover_letter.greeting,
    ...cover_letter.paragraphs,
    cover_letter.closing,
    contact.full_name,
  ]
    .filter(Boolean)
    .join("\n\n");
}
