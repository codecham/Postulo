import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type Profile = Schemas["ProfileRead"];
export type ProfileUpdate = Schemas["ProfileUpdate"];
/** Every profile field with a value: a saved profile or a CV import draft. */
export type ProfileValues = Required<ProfileUpdate>;
export type WorkMode = Schemas["WorkMode"];

export type Experience = Schemas["ExperienceRead"];
export type ExperienceInput = Schemas["ExperienceCreate"];

export type Education = Schemas["EducationRead"];
export type EducationInput = Schemas["EducationCreate"];
