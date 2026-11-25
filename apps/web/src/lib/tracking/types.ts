import type { components } from "@/lib/api/schema";

type Schemas = components["schemas"];

export type Tracking = Schemas["TrackingRead"];
export type TrackedApplication = Schemas["TrackedApplicationRead"];
export type TrackingBoard = Schemas["TrackingBoard"];
export type TrackingStatus = Schemas["TrackingStatus"];
export type TrackingUpdate = Schemas["TrackingUpdate"];

// In the order an application usually goes through them
export const TRACKING_STATUSES: TrackingStatus[] = [
  "applied",
  "interview",
  "offer",
  "rejected",
  "withdrawn",
];

export const TRACKING_STATUS_LABELS: Record<TrackingStatus, string> = {
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
};
