// Helpers to read the fields of a submitted form (FormData) with the right types.

export type Option = { value: string; label: string };

/** What a server action returns to the form that called it (see useActionState). */
export type FormState =
  | { status: "success"; message: string }
  | { status: "error"; message: string }
  | undefined;

/** A text field, trimmed. An empty or missing field gives "". */
export function readText(formData: FormData, name: string): string {
  return String(formData.get(name) ?? "").trim();
}

/** A text field, trimmed. An empty or missing field gives null. */
export function readOptionalText(
  formData: FormData,
  name: string,
): string | null {
  return readText(formData, name) || null;
}

/** Every value sent under the same name (checkbox group, tag input…). */
export function readList(formData: FormData, name: string): string[] {
  return formData
    .getAll(name)
    .map((value) => String(value).trim())
    .filter(Boolean);
}

/** A single checkbox: browsers only send it when it is checked. */
export function readChecked(formData: FormData, name: string): boolean {
  return formData.has(name);
}
