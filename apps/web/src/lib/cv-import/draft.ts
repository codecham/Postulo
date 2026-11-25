import type { CvImportDraft } from "@/lib/cv-import/types";
import type { ProfileValues } from "@/lib/profile/types";

/** The API always fills every draft field; this gives the type that says so. */
export function draftProfileValues({ profile }: CvImportDraft): ProfileValues {
  return {
    full_name: profile.full_name ?? null,
    headline: profile.headline ?? null,
    summary: profile.summary ?? null,
    city: profile.city ?? null,
    skills: profile.skills ?? [],
    languages: profile.languages ?? [],
    desired_titles: profile.desired_titles ?? [],
    work_modes: profile.work_modes ?? [],
    countries: profile.countries ?? [],
    open_to_remote_abroad: profile.open_to_remote_abroad ?? false,
    offer_languages: profile.offer_languages ?? [],
  };
}
