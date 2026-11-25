import { ExperienceItem } from "@/components/profile/experience-item";
import { ExperienceSummary } from "@/components/profile/experience-summary";
import { NewExperience } from "@/components/profile/new-experience";
import type { Experience } from "@/lib/profile/types";

export function ExperienceSection({
  experiences,
}: {
  experiences: Experience[];
}) {
  return (
    <section className="flex flex-col gap-4 rounded-lg border border-gray-200 p-5 dark:border-gray-800">
      <h2 className="font-semibold">Experience</h2>
      {experiences.length === 0 ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          No experience yet. Add your jobs, most recent first.
        </p>
      ) : (
        <ul className="flex flex-col divide-y divide-gray-200 dark:divide-gray-800">
          {experiences.map((experience) => (
            <li key={experience.id} className="py-4 first:pt-0 last:pb-0">
              <ExperienceItem experience={experience}>
                <ExperienceSummary experience={experience} />
              </ExperienceItem>
            </li>
          ))}
        </ul>
      )}
      <NewExperience />
    </section>
  );
}
