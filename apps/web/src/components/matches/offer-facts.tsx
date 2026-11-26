import { ageLabel, WORK_MODE_LABELS } from "@/lib/job-search/labels";
import type { JobOffer } from "@/lib/job-search/types";

/** Company, place, work mode, salary and age of an offer, on one line. */
export function OfferFacts({ offer }: { offer: JobOffer }) {
  const facts = [
    offer.location,
    offer.work_mode && WORK_MODE_LABELS[offer.work_mode],
    offer.salary,
    offer.published_at && `Posted ${ageLabel(offer.published_at)}`,
    `via ${offer.source}`,
  ].filter(Boolean);

  return (
    <p className="text-muted flex flex-wrap gap-x-2 text-sm">
      {offer.company && (
        <span className="text-fg font-medium">{offer.company}</span>
      )}
      {facts.map((fact, index) => (
        <span key={String(fact)} className="flex gap-2">
          {(index > 0 || offer.company) && (
            <span aria-hidden className="text-line-strong">
              ·
            </span>
          )}
          {fact}
        </span>
      ))}
    </p>
  );
}
