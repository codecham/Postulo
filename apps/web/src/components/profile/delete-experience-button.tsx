"use client";

import type { FormEvent } from "react";

import { deleteExperience } from "@/app/profile/actions";
import { secondaryButtonClassName } from "@/components/ui/styles";

export function DeleteExperienceButton({
  experienceId,
}: {
  experienceId: string;
}) {
  function confirmDelete(event: FormEvent<HTMLFormElement>) {
    if (!window.confirm("Delete this experience?")) {
      event.preventDefault();
    }
  }

  return (
    <form
      action={deleteExperience.bind(null, experienceId)}
      onSubmit={confirmDelete}
    >
      <button type="submit" className={secondaryButtonClassName}>
        Delete
      </button>
    </form>
  );
}
