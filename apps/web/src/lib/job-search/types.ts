import type { components, paths } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type JobSearchOverview = Schemas["JobSearchOverview"];
export type JobSearchRun = Schemas["JobSearchRunRead"];
export type JobSource = Schemas["JobSourceRead"];
export type JobMatch = Schemas["JobMatchRead"];
export type JobOffer = Schemas["JobOfferRead"];
export type JobMatchPage = Schemas["JobMatchPage"];
export type MatchFacets = Schemas["MatchFacets"];
export type MatchStatus = Schemas["MatchStatus"];
export type MatchPlace = Schemas["MatchPlace"];
export type MatchSort = Schemas["MatchSort"];
export type MatchQuery = NonNullable<
  paths["/job-search/matches"]["get"]["parameters"]["query"]
>;
export type MatchExplanation = Schemas["MatchExplanation"];
