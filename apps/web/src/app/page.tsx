import Link from "next/link";
import { Suspense } from "react";

import { ApiStatus } from "@/components/api-status";
import { FeatureCard } from "@/components/home/feature-card";
import {
  ArrowRightIcon,
  SearchIcon,
  SendIcon,
  SparklesIcon,
} from "@/components/ui/icons";
import { buttonClassName } from "@/components/ui/styles";

const STEPS = [
  {
    icon: <SearchIcon className="size-5" />,
    title: "Find the right offers",
    description:
      "Postulo searches public job boards every day and ranks each offer against your profile, with the reasons why.",
  },
  {
    icon: <SparklesIcon className="size-5" />,
    title: "Apply in a few clicks",
    description:
      "A CV and a cover letter tailored to the offer, in its language, written from your profile only. Review, download, send.",
  },
  {
    icon: <SendIcon className="size-5" />,
    title: "Never miss a follow-up",
    description:
      "Every application you send lands on one board, with its status, your notes and a reminder to follow up.",
  },
];

export default function HomePage() {
  return (
    <div className="flex flex-col gap-16 py-6 sm:py-12">
      <section className="flex flex-col items-start gap-6">
        <span className="border-line bg-surface text-muted rounded-full border px-3 py-1 text-xs font-medium">
          AI-assisted job search
        </span>
        <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-balance sm:text-6xl">
          From job offer to sent application,{" "}
          <span className="text-accent-text">in minutes.</span>
        </h1>
        <p className="text-muted max-w-2xl text-lg">
          Postulo finds the offers that fit you, writes a tailored CV and cover
          letter for each one, and keeps track of everything you sent.
        </p>
        <div className="flex flex-wrap gap-3">
          <Link href="/register" className={buttonClassName("primary", "md")}>
            Get started
            <ArrowRightIcon />
          </Link>
          <Link href="/login" className={buttonClassName("secondary", "md")}>
            I have an account
          </Link>
        </div>
      </section>

      <section aria-labelledby="how-it-works" className="flex flex-col gap-6">
        <h2 id="how-it-works" className="text-xl font-semibold tracking-tight">
          How it works
        </h2>
        <ol className="grid gap-4 md:grid-cols-3">
          {STEPS.map((step, index) => (
            <FeatureCard key={step.title} step={index + 1} {...step} />
          ))}
        </ol>
      </section>

      <Suspense
        fallback={<p className="text-muted text-sm">Checking the API…</p>}
      >
        <ApiStatus />
      </Suspense>
    </div>
  );
}
