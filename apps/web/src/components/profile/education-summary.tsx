import { formatPeriod } from "@/lib/profile/dates";
import type { EducationInput } from "@/lib/profile/types";

/** Read-only view of an education, saved or found in a CV. */
export function EducationSummary({ education }: { education: EducationInput }) {
  const diploma = [education.degree, education.field_of_study]
    .filter(Boolean)
    .join(", ");
  const period = formatPeriod(
    education.start_date ?? null,
    education.end_date ?? null,
  );

  return (
    <div className="flex flex-col gap-1">
      <h3 className="font-semibold">{education.school}</h3>
      {diploma && <p className="text-sm">{diploma}</p>}
      {(period || education.location) && (
        <p className="text-muted text-sm">
          {[period, education.location].filter(Boolean).join(" · ")}
        </p>
      )}
      {education.description && (
        <p className="text-fg mt-2 text-sm whitespace-pre-line">
          {education.description}
        </p>
      )}
    </div>
  );
}
