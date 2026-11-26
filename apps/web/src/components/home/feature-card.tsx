import type { ReactNode } from "react";

import { cardClassName } from "@/components/ui/card";

type FeatureCardProps = {
  step: number;
  icon: ReactNode;
  title: string;
  description: string;
};

/** One step of how Postulo works, on the home page. */
export function FeatureCard({
  step,
  icon,
  title,
  description,
}: FeatureCardProps) {
  return (
    <li className={`${cardClassName} flex flex-col gap-3 p-6`}>
      <div className="flex items-center justify-between">
        <span className="bg-accent-soft text-accent-text flex size-10 items-center justify-center rounded-lg">
          {icon}
        </span>
        <span className="text-muted text-sm font-medium tabular-nums">
          0{step}
        </span>
      </div>
      <h3 className="font-semibold">{title}</h3>
      <p className="text-muted text-sm">{description}</p>
    </li>
  );
}
