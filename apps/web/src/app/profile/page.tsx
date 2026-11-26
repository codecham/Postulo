import type { Metadata } from "next";
import Link from "next/link";
import { Suspense } from "react";

import { PageHeader } from "@/components/layout/page-header";
import { PageLoading } from "@/components/layout/page-loading";
import { EducationSection } from "@/components/profile/education-section";
import { ExperienceSection } from "@/components/profile/experience-section";
import { ProfileForm } from "@/components/profile/profile-form";
import { secondaryButtonClassName } from "@/components/ui/styles";
import {
  getMyProfile,
  listMyEducations,
  listMyExperiences,
} from "@/lib/profile/queries";

export const metadata: Metadata = { title: "Profile" };

export default function ProfilePage() {
  return (
    <section className="mx-auto flex w-full max-w-3xl flex-col gap-8">
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
      <Suspense fallback={<PageLoading />}>
        <ProfileContent />
      </Suspense>
    </section>
  );
}

async function ProfileContent() {
  // The requests run at the same time; a missing session redirects to /login
  const [profile, experiences, educations] = await Promise.all([
    getMyProfile(),
    listMyExperiences(),
    listMyEducations(),
  ]);

  return (
    <>
      <ProfileForm profile={profile} />
      <ExperienceSection experiences={experiences} />
      <EducationSection educations={educations} />
    </>
  );
}
