"use client";

import { type ReactNode, useState } from "react";

import { updateExperience } from "@/app/profile/actions";
import { DeleteExperienceButton } from "@/components/profile/delete-experience-button";
import { ExperienceForm } from "@/components/profile/experience-form";
import { secondaryButtonClassName } from "@/components/ui/styles";
import type { Experience } from "@/lib/profile/types";

type ExperienceItemProps = {
  experience: Experience;
  children: ReactNode; // the summary, rendered on the server
};

/** One experience: its summary, or its edit form after a click on Edit. */
export function ExperienceItem({ experience, children }: ExperienceItemProps) {
  const [isEditing, setIsEditing] = useState(false);

  if (isEditing) {
    return (
      <ExperienceForm
        saveAction={updateExperience.bind(null, experience.id)}
        experience={experience}
        submitLabel="Save"
        onClose={() => setIsEditing(false)}
      />
    );
  }

  return (
    <div className="flex items-start justify-between gap-4">
      {children}
      <div className="flex shrink-0 gap-2">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className={secondaryButtonClassName}
        >
          Edit
        </button>
        <DeleteExperienceButton experienceId={experience.id} />
      </div>
    </div>
  );
}
