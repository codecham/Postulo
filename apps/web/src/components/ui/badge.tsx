import type { ReactNode } from "react";

export type BadgeTone =
  "neutral" | "accent" | "success" | "warning" | "danger" | "info";

const TONES: Record<BadgeTone, string> = {
  neutral: "bg-subtle text-muted",
  accent: "bg-accent-soft text-accent-text",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  danger: "bg-danger-soft text-danger",
  info: "bg-info-soft text-info",
};

type BadgeProps = {
  tone?: BadgeTone;
  title?: string;
  children: ReactNode;
};

/** A small colored pill: a status, a count, a score. */
export function Badge({ tone = "neutral", title, children }: BadgeProps) {
  return (
    <span
      title={title}
      className={`inline-flex shrink-0 items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold tabular-nums ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}
