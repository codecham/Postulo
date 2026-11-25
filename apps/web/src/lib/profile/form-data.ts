import { readChecked, readList, readOptionalText, readText } from "@/lib/forms";
import { monthToDate } from "@/lib/profile/dates";
import type {
  EducationInput,
  ExperienceInput,
  ProfileUpdate,
  WorkMode,
} from "@/lib/profile/types";

// Turn submitted forms into API request bodies. The API validates every value.

export function toProfileUpdate(formData: FormData): ProfileUpdate {
  return {
    full_name: readOptionalText(formData, "full_name"),
    headline: readOptionalText(formData, "headline"),
    summary: readOptionalText(formData, "summary"),
    city: readOptionalText(formData, "city"),
    skills: readList(formData, "skills"),
    languages: readList(formData, "languages"),
    desired_titles: readList(formData, "desired_titles"),
    work_modes: readList(formData, "work_modes") as WorkMode[],
    countries: readList(formData, "countries"),
    open_to_remote_abroad: readChecked(formData, "open_to_remote_abroad"),
  };
}

export function toExperienceInput(formData: FormData): ExperienceInput {
  return {
    title: readText(formData, "title"),
    company: readText(formData, "company"),
    location: readOptionalText(formData, "location"),
    start_date: monthToDate(readText(formData, "start_month")) ?? "",
    end_date: monthToDate(readText(formData, "end_month")),
    description: readOptionalText(formData, "description"),
  };
}

export function toEducationInput(formData: FormData): EducationInput {
  return {
    school: readText(formData, "school"),
    degree: readOptionalText(formData, "degree"),
    field_of_study: readOptionalText(formData, "field_of_study"),
    location: readOptionalText(formData, "location"),
    start_date: monthToDate(readText(formData, "start_month")),
    end_date: monthToDate(readText(formData, "end_month")),
    description: readOptionalText(formData, "description"),
  };
}
