import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type Application = Schemas["ApplicationRead"];
export type ApplicationContent = Schemas["ApplicationContent"];
export type ApplicationLanguage = Schemas["ApplicationLanguage"];
export type ApplicationOptions = Schemas["ApplicationOptions"];
export type GeneratedApplication = Schemas["GeneratedApplication"];
export type CvExperience = Schemas["CvExperience"];
export type CvEducation = Schemas["CvEducation"];
export type Contact = Schemas["Contact"];
export type CoverLetter = Schemas["CoverLetter"];

// The PDFs a user can download, as named in the URL
export const DOCUMENTS = {
  "cv.pdf": "CV",
  "cover-letter.pdf": "Cover letter",
} as const;

export type DocumentName = keyof typeof DOCUMENTS;

export function isDocumentName(name: string): name is DocumentName {
  return Object.hasOwn(DOCUMENTS, name);
}
