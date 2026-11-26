import type { Metadata } from "next";
import Link from "next/link";

import { register } from "@/app/(auth)/actions";
import { AuthForm } from "@/components/auth-form";
import { AuthShell } from "@/components/auth-shell";
import { linkClassName } from "@/components/ui/styles";

export const metadata: Metadata = { title: "Sign up" };

export default function RegisterPage() {
  return (
    <AuthShell
      title="Create your account"
      description="Free. Your profile and applications stay yours."
      footer={
        <>
          Already have an account?{" "}
          <Link href="/login" className={linkClassName}>
            Log in
          </Link>
        </>
      }
    >
      <AuthForm
        action={register}
        submitLabel="Create my account"
        passwordAutoComplete="new-password"
      />
    </AuthShell>
  );
}
