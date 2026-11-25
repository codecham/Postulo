import { ageLabel, WORK_MODE_LABELS } from "@/lib/job-search/labels";
import type { JobOffer } from "@/lib/job-search/types";

/** Company, place, work mode, salary and age of an offer, on one line. */
export function OfferFacts({ offer }: { offer: JobOffer }) {
  const facts = [
    offer.company,
    offer.location,
    offer.work_mode && WORK_MODE_LABELS[offer.work_mode],
    offer.salary,
    offer.published_at && `Posted ${ageLabel(offer.published_at)}`,
    `via ${offer.source}`,
  ].filter(Boolean);

  return <p className="text-sm">{facts.join(" · ")}</p>;
}
