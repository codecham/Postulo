import { readList, readText } from "@/lib/forms";
import type {
  CvExtraction,
  CvImportApply,
  CvImportDraft,
  DraftEducation,
  DraftExperience,
} from "@/lib/cv-import/types";
import { toProfileUpdate } from "@/lib/profile/form-data";
import type { EducationInput, ExperienceInput } from "@/lib/profile/types";

// Field names of the checkboxes that select the draft items to save
export const EXPERIENCE_FIELD = "experience";
export const EDUCATION_FIELD = "education";

/** The reviewed profile, and the draft items whose checkbox is checked. */
export function toCvImportApply(
  formData: FormData,
  draft: CvImportDraft,
): CvImportApply {
  return {
    profile: toProfileUpdate(formData),
    experiences: pickChecked(formData, EXPERIENCE_FIELD, draft.experiences).map(
      toExperienceInput,
    ),
    educations: pickChecked(
      formData,
      EDUCATION_FIELD,
      draft.educations ?? [],
    ).map(toEducationInput),
  };
}

/** The items whose index was sent by a checked checkbox named `fieldName`. */
function pickChecked<T>(
  formData: FormData,
  fieldName: string,
  items: T[],
): T[] {
  const checked = new Set(readList(formData, fieldName).map(Number));
  return items.filter((_, index) => checked.has(index));
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

/** The API rejects unknown fields: keep only those of an education. */
function toEducationInput(education: DraftEducation): EducationInput {
  return {
    school: education.school,
    degree: education.degree,
    field_of_study: education.field_of_study,
    location: education.location,
    start_date: education.start_date,
    end_date: education.end_date,
    description: education.description,
  };
}
