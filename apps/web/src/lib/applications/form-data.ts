import { readList, readOptionalText, readText } from "@/lib/forms";
import type {
  ApplicationContent,
  ApplicationLanguage,
  CvEducation,
  CvExperience,
  GeneratedApplication,
} from "@/lib/applications/types";

// Names of the checkboxes that keep an item in the CV (their value is the item's index)
export const EXPERIENCE_FIELD = "experience";
export const EDUCATION_FIELD = "education";

/** The name of one field of a list item: "experience.2.title". */
export function itemField(list: string, index: number, field: string): string {
  return `${list}.${index}.${field}`;
}

/** The reviewed documents. `current` gives how many experiences and educations exist. */
export function toApplicationContent(
  formData: FormData,
  current: ApplicationContent,
): ApplicationContent {
  return {
    language: readText(formData, "language") as ApplicationLanguage,
    contact: {
      full_name: readOptionalText(formData, "contact.full_name"),
      email: readOptionalText(formData, "contact.email"),
      phone: readOptionalText(formData, "contact.phone"),
      city: readOptionalText(formData, "contact.city"),
      links: readLines(formData, "contact.links"),
    },
    cv: {
      headline: readText(formData, "cv.headline"),
      summary: readText(formData, "cv.summary"),
      skills: readList(formData, "cv.skills"),
      languages: readList(formData, "cv.languages"),
      experiences: keptIndexes(
        formData,
        EXPERIENCE_FIELD,
        current.cv.experiences,
      ).map((index) => readExperience(formData, index)),
      education: keptIndexes(
        formData,
        EDUCATION_FIELD,
        current.cv.education,
      ).map((index) => readEducation(formData, index)),
    },
    cover_letter: {
      subject: readText(formData, "letter.subject"),
      greeting: readText(formData, "letter.greeting"),
      paragraphs: readParagraphs(formData, "letter.paragraphs"),
      closing: readText(formData, "letter.closing"),
    },
  };
}

/**
 * The JSON pasted from Claude Code, or null when it is not a JSON object.
 * Its fields are checked by the API.
 */
export function readGeneratedApplication(
  formData: FormData,
  name: string,
): GeneratedApplication | null {
  try {
    const value: unknown = JSON.parse(readText(formData, name));
    return typeof value === "object" && value !== null && !Array.isArray(value)
      ? (value as GeneratedApplication)
      : null;
  } catch {
    return null; // not JSON at all
  }
}

function readExperience(formData: FormData, index: number): CvExperience {
  const field = (name: string) => itemField(EXPERIENCE_FIELD, index, name);
  return {
    title: readText(formData, field("title")),
    company: readText(formData, field("company")),
    location: readOptionalText(formData, field("location")),
    start_month: readOptionalText(formData, field("start_month")),
    end_month: readOptionalText(formData, field("end_month")),
    bullets: readLines(formData, field("bullets")),
  };
}

function readEducation(formData: FormData, index: number): CvEducation {
  const field = (name: string) => itemField(EDUCATION_FIELD, index, name);
  return {
    school: readText(formData, field("school")),
    degree: readOptionalText(formData, field("degree")),
    field_of_study: readOptionalText(formData, field("field_of_study")),
    location: readOptionalText(formData, field("location")),
    start_month: readOptionalText(formData, field("start_month")),
    end_month: readOptionalText(formData, field("end_month")),
    details: readOptionalText(formData, field("details")),
  };
}

/** The indexes of the items whose "keep" checkbox is checked, in their order. */
function keptIndexes(
  formData: FormData,
  fieldName: string,
  items: unknown[],
): number[] {
  const kept = new Set(readList(formData, fieldName).map(Number));
  return items.map((_, index) => index).filter((index) => kept.has(index));
}

/** A textarea with one value per line (bullets, links). */
function readLines(formData: FormData, name: string): string[] {
  return splitAndTrim(readText(formData, name), /\n/);
}

/** A textarea whose paragraphs are separated by an empty line. */
function readParagraphs(formData: FormData, name: string): string[] {
  return splitAndTrim(readText(formData, name), /\n\s*\n/);
}

function splitAndTrim(text: string, separator: RegExp): string[] {
  return text
    .split(separator)
    .map((part) => part.trim())
    .filter(Boolean);
}
