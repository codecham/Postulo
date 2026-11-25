import { Card } from "@/components/ui/card";
import type { JobOffer } from "@/lib/job-search/types";

/**
 * Where the user goes from a match to an application. For now the offer's own page;
 * the tailored CV and cover letter will be generated here, in one click.
 */
export function ApplyPanel({ offer }: { offer: JobOffer }) {
  return (
    <Card
      title="Apply"
      description="Soon: a CV and a cover letter tailored to this offer, in one click."
    >
      <div>
        <a
          href={offer.url}
          target="_blank"
          rel="noopener"
          className="inline-block rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 dark:bg-white dark:text-gray-900"
        >
          Apply on {offer.source} ↗
        </a>
      </div>
    </Card>
  );
}
