import type { ReactNode } from "react";

import { CheckIcon } from "@/components/ui/icons";

export type StepState = "done" | "current" | "upcoming";

type ApplyStepProps = {
  number: number;
  title: string;
  state: StepState;
  isLast?: boolean;
  children?: ReactNode; // shown under the title
};

const MARKERS: Record<StepState, string> = {
  done: "bg-success-soft text-success",
  current: "bg-accent text-accent-fg shadow-sm",
  upcoming: "border border-line-strong bg-surface text-muted",
};

/** One step of the way to a sent application, with a line down to the next one. */
export function ApplyStep({
  number,
  title,
  state,
  isLast = false,
  children,
}: ApplyStepProps) {
  return (
    <li
      aria-current={state === "current" ? "step" : undefined}
      className="relative flex gap-4 pb-6 last:pb-0"
    >
      {!isLast && (
        <span
          aria-hidden
          className="bg-line absolute top-8 bottom-0 left-[0.9375rem] w-px"
        />
      )}
      <span
        className={`relative flex size-8 shrink-0 items-center justify-center rounded-full text-sm font-semibold ${MARKERS[state]}`}
      >
        {state === "done" ? <CheckIcon /> : number}
        <span className="sr-only">
          {state === "done" ? " (done)" : state === "current" ? " (next)" : ""}
        </span>
      </span>
      <div className="flex min-w-0 flex-1 flex-col gap-3 pt-1">
        <h3
          className={`text-sm font-semibold ${state === "upcoming" ? "text-muted" : ""}`}
        >
          {title}
        </h3>
        {children}
      </div>
    </li>
  );
}
