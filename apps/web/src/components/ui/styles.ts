// Tailwind classes shared by the UI components, so every field and button looks the same.

export const labelClassName = "flex flex-col gap-1.5 text-sm font-medium";

export const inputClassName =
  "rounded-lg border border-line-strong bg-surface px-3 py-2 font-normal shadow-xs transition-colors placeholder:text-muted/70 hover:border-muted/50 focus-visible:border-accent focus-visible:outline-2 focus-visible:outline-offset-0 focus-visible:outline-accent/30";

export const hintClassName = "text-xs font-normal text-muted";

export type ButtonVariant = "primary" | "secondary" | "ghost" | "danger";
export type ButtonSize = "sm" | "md";

const BUTTON_BASE =
  "inline-flex items-center justify-center gap-1.5 rounded-lg font-medium whitespace-nowrap transition-colors disabled:pointer-events-none disabled:opacity-50";

const BUTTON_VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-accent text-accent-fg shadow-sm hover:bg-accent-hover",
  secondary:
    "border border-line-strong bg-surface text-fg shadow-xs hover:bg-subtle",
  ghost: "text-muted hover:bg-subtle hover:text-fg",
  danger:
    "border border-line-strong bg-surface text-danger shadow-xs hover:bg-danger-soft",
};

const BUTTON_SIZES: Record<ButtonSize, string> = {
  sm: "h-8 px-3 text-sm",
  md: "h-10 px-4 text-sm",
};

/** The classes of a button, for <button> and for links that look like one. */
export function buttonClassName(
  variant: ButtonVariant = "secondary",
  size: ButtonSize = "sm",
): string {
  return `${BUTTON_BASE} ${BUTTON_VARIANTS[variant]} ${BUTTON_SIZES[size]}`;
}

export const secondaryButtonClassName = buttonClassName("secondary", "sm");

export const primaryButtonClassName = buttonClassName("primary", "md");

/** A text link inside content. */
export const linkClassName =
  "font-medium text-accent-text underline-offset-4 hover:underline";
