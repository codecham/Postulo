import type { Metadata } from "next";
import { Suspense } from "react";

import { ExperienceSection } from "@/components/profile/experience-section";
import { ProfileForm } from "@/components/profile/profile-form";
import { getMyProfile, listMyExperiences } from "@/lib/profile/queries";

export const metadata: Metadata = { title: "Profile" };

export default function ProfilePage() {
  return (
    <section className="flex flex-col gap-8">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold">Your profile</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Postulo uses it to find job offers and to write your applications.
        </p>
      </header>
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
