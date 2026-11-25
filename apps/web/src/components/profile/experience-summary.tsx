import { formatPeriod } from "@/lib/profile/dates";
import type { Experience } from "@/lib/profile/types";

export function ExperienceSummary({ experience }: { experience: Experience }) {
  const place = [experience.company, experience.location]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="flex flex-col gap-1">
      <h3 className="font-semibold">{experience.title}</h3>
      <p className="text-sm">{place}</p>
      <p className="text-sm text-gray-500">
        {formatPeriod(experience.start_date, experience.end_date)}
      </p>
      {experience.description && (
        <p className="mt-2 text-sm whitespace-pre-line text-gray-700 dark:text-gray-300">
          {experience.description}
        </p>
      )}
    </div>
  );
}
