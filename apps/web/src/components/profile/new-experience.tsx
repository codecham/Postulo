"use client";

import { useState } from "react";

import { createExperience } from "@/app/profile/actions";
import { ExperienceForm } from "@/components/profile/experience-form";
import { secondaryButtonClassName } from "@/components/ui/styles";

/** An "Add an experience" button that opens an empty experience form. */
export function NewExperience() {
  const [isOpen, setIsOpen] = useState(false);

  if (!isOpen) {
    return (
      <div>
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className={secondaryButtonClassName}
        >
          + Add an experience
        </button>
      </div>
    );
  }

  return (
    <ExperienceForm
      saveAction={createExperience}
      submitLabel="Add"
      onClose={() => setIsOpen(false)}
    />
  );
}
