import { site } from "@/lib/site";

// A day without time ("2026-11-26"): never shifted to another time zone
const dayFormat = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: "UTC",
});

// The day of a moment, in the user's time zone
const eventDayFormat = new Intl.DateTimeFormat("en-GB", {
  day: "numeric",
  month: "short",
  year: "numeric",
  timeZone: site.timeZone,
});

/** "2026-11-26" → "26 Nov 2026". */
export function formatDay(day: string): string {
  return dayFormat.format(new Date(day));
}

/** "2026-11-25T23:30:00Z" → "26 Nov 2026" in Brussels. */
export function formatEventDay(dateTime: string): string {
  return eventDayFormat.format(new Date(dateTime));
}
