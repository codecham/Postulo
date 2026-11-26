import type { Metadata } from "next";
import { redirect } from "next/navigation";
import { Suspense } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { Card } from "@/components/ui/card";
import { getCurrentUser } from "@/lib/auth/session";

export const metadata: Metadata = { title: "Account" };

export default function AccountPage() {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
      <PageHeader title="Your account" />
      {/* Reading the session happens per request, so it streams in behind Suspense */}
      <Suspense fallback={<PageLoading blocks={1} />}>
        <AccountDetails />
      </Suspense>
    </section>
  );
}

async function AccountDetails() {
  // The authoritative check: the API validates the token on every request
  const user = await getCurrentUser();
  if (!user) {
    redirect("/login");
  }

  return (
    <Card>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-8 gap-y-3 text-sm">
        <dt className="text-muted">Email</dt>
        <dd className="font-medium">{user.email}</dd>
        <dt className="text-muted">Member since</dt>
        <dd className="font-medium">
          {new Date(user.created_at).toLocaleDateString("en", {
            dateStyle: "long",
          })}
        </dd>
      </dl>
    </Card>
  );
}
