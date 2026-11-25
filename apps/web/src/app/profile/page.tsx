import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { ExperienceSection } from "@/components/profile/experience-section";
import { ProfileForm } from "@/components/profile/profile-form";
import { secondaryButtonClassName } from "@/components/ui/styles";
import { getMyProfile, listMyExperiences } from "@/lib/profile/queries";

export const metadata: Metadata = { title: "Profile" };

export default function ProfilePage() {
  return (
    <section className="flex flex-col gap-8">
      <PageHeader
        title="Your profile"
        description="Postulo uses it to find job offers and to write your applications."
        action={
          <Link href="/profile/import" className={secondaryButtonClassName}>
            Import from a CV
          </Link>
        }
      />
      {/* Per-user data, read at request time: it streams in behind Suspense */}
      <Suspense fallback={<p className="text-gray-500">Loading…</p>}>
        <ProfileContent />
      </Suspense>
    </section>
  );
}

async function ProfileContent() {
  // Both requests run at the same time; a missing session redirects to /login
  const [profile, experiences] = await Promise.all([
    getMyProfile(),
    listMyExperiences(),
  ]);

  return (
    <>
      <ProfileForm profile={profile} />
      <ExperienceSection experiences={experiences} />
    </>
  );
}
