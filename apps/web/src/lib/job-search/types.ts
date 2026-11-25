import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type JobSearchOverview = Schemas["JobSearchOverview"];
export type JobSearchRun = Schemas["JobSearchRunRead"];
export type JobSource = Schemas["JobSourceRead"];
export type JobMatch = Schemas["JobMatchRead"];
export type JobOffer = Schemas["JobOfferRead"];
