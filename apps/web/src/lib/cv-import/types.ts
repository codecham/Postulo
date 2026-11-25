import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type CvImport = Schemas["CvImportRead"];
export type CvImportDraft = Schemas["CvImportDraft"];
export type DraftExperience = Schemas["DraftExperience"];
export type DraftEducation = Schemas["DraftEducation"];
export type CvImportApply = Schemas["CvImportApply"];
export type CvExtraction = Schemas["CvExtraction"];
export type CvImportOptions = Schemas["CvImportOptions"];
