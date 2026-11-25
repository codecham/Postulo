// Experiences are dated by month: forms use <input type="month"> ("2024-03")
// while the API stores full dates ("2024-03-01").

/** "2024-03" → "2024-03-01". An empty value gives null. */
export function monthToDate(month: string): string | null {
  return month ? `${month}-01` : null;
}

/** "2024-03-01" → "2024-03". Null gives "". */
export function dateToMonth(date: string | null): string {
  return date ? date.slice(0, 7) : "";
}

const monthFormat = new Intl.DateTimeFormat("en", {
  month: "short",
  year: "numeric",
  timeZone: "UTC", // the dates have no time: never shift them to the local zone
});

/** "Mar 2022 – Jun 2024", or "Mar 2022 – Present" for a current job. */
export function formatPeriod(
  startDate: string,
  endDate: string | null,
): string {
  const end = endDate ? monthFormat.format(new Date(endDate)) : "Present";
  return `${monthFormat.format(new Date(startDate))} – ${end}`;
}
