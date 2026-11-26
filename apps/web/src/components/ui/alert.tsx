import type { ReactNode } from "react";

type AlertTone = "info" | "warning" | "danger" | "success";

const TONES: Record<AlertTone, string> = {
  info: "border-info/25 bg-info-soft",
  warning: "border-warning/25 bg-warning-soft",
  danger: "border-danger/25 bg-danger-soft",
  success: "border-success/25 bg-success-soft",
};

type AlertProps = {
  tone?: AlertTone;
  title?: string;
  children: ReactNode;
};

/** A highlighted note: a warning to read, an error to fix. */
export function Alert({ tone = "info", title, children }: AlertProps) {
  return (
    <div
      role={tone === "danger" ? "alert" : "note"}
      className={`flex flex-col gap-1.5 rounded-xl border p-4 text-sm ${TONES[tone]}`}
    >
      {title && <p className="font-semibold">{title}</p>}
      {children}
    </div>
  );
}
