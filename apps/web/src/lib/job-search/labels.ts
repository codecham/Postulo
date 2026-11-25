// Server only: names come from the Intl API, whose data differs between Node.js and
// browsers. Computing them on the server keeps the HTML identical.
import "server-only";

import type { JobOffer, MatchExplanation } from "@/lib/job-search/types";
import type { WorkMode } from "@/lib/profile/types";

const countryNames = new Intl.DisplayNames(["en"], { type: "region" });
const languageNames = new Intl.DisplayNames(["en"], { type: "language" });

export const WORK_MODE_LABELS: Record<WorkMode, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  onsite: "On site",
};

export function countryName(code: string): string {
  return countryNames.of(code) ?? code;
}

export function languageName(code: string): string {
  return languageNames.of(code) ?? code;
}

/** How close the offer is to the profile, in words. */
export function relevanceLabel(relevance: number): string {
  if (relevance >= 75) {
    return "Very close to your profile";
  }
  if (relevance >= 50) {
    return "Close to your profile";
  }
  return "Related to your profile";
}

/** Why the place of the offer suits the user. */
export function placeLabel(
  place: MatchExplanation["place"],
  offer: JobOffer,
): string {
  if (place === "your_country" && offer.country) {
    return `In ${countryName(offer.country)}, a country you chose`;
  }
  if (place === "remote") {
    return "Remote, open to where you live";
  }
  return "Outside your current criteria";
}

const DAY_MS = 24 * 60 * 60 * 1000;

/** "today", "yesterday", "5 days ago": when the offer was published. */
export function ageLabel(date: string, now: number = Date.now()): string {
  const days = Math.floor((now - new Date(date).getTime()) / DAY_MS);
  if (days <= 0) {
    return "today";
  }
  if (days === 1) {
    return "yesterday";
  }
  return `${days} days ago`;
}
