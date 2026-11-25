import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type Profile = Schemas["ProfileRead"];
export type ProfileUpdate = Schemas["ProfileUpdate"];
export type WorkMode = Schemas["WorkMode"];

export type Experience = Schemas["ExperienceRead"];
export type ExperienceInput = Schemas["ExperienceCreate"];
