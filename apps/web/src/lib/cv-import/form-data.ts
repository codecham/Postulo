import { readList, readText } from "@/lib/forms";
import type {
  CvExtraction,
  CvImportApply,
  CvImportDraft,
  DraftExperience,
} from "@/lib/cv-import/types";
import { toProfileUpdate } from "@/lib/profile/form-data";
import type { ExperienceInput } from "@/lib/profile/types";

// Field name of the checkboxes that select the experiences to save
export const EXPERIENCE_FIELD = "experience";

/** The reviewed profile, and the draft experiences whose checkbox is checked. */
export function toCvImportApply(
  formData: FormData,
  draft: CvImportDraft,
): CvImportApply {
  const selected = new Set(readList(formData, EXPERIENCE_FIELD).map(Number));
  return {
    profile: toProfileUpdate(formData),
    experiences: draft.experiences
      .filter((_, index) => selected.has(index))
      .map(toExperienceInput),
  };
}

/**
 * The JSON pasted from Claude Code, or null when it is not a JSON object.
 * Its fields are checked by the API.
 */
export function readExtraction(
  formData: FormData,
  name: string,
): CvExtraction | null {
  try {
    const value: unknown = JSON.parse(readText(formData, name));
    return typeof value === "object" && value !== null && !Array.isArray(value)
      ? (value as CvExtraction)
      : null;
  } catch {
    return null; // not JSON at all
  }
}

/** The uploaded file, or null when the form has no (or an empty) file. */
export function readFile(formData: FormData, name: string): File | null {
  const file = formData.get(name);
  return file instanceof File && file.size > 0 ? file : null;
}

/** The API rejects unknown fields: keep only those of an experience. */
function toExperienceInput(experience: DraftExperience): ExperienceInput {
  return {
    title: experience.title,
    company: experience.company,
    location: experience.location,
    start_date: experience.start_date,
    end_date: experience.end_date,
    description: experience.description,
  };
}
