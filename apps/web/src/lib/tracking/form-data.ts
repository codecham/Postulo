import { readOptionalText, readText } from "@/lib/forms";
import type { TrackingStatus, TrackingUpdate } from "@/lib/tracking/types";

/** The tracking form: status, dates and notes (an empty follow-up removes it). */
export function toTrackingUpdate(formData: FormData): TrackingUpdate {
  return {
    status: readText(formData, "status") as TrackingStatus,
    applied_on: readText(formData, "applied_on"),
    follow_up_on: readOptionalText(formData, "follow_up_on"),
    notes: readOptionalText(formData, "notes"),
  };
}
