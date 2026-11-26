import type { Metadata } from "next";
import Link from "next/link";

import { login } from "@/app/(auth)/actions";
import { AuthForm } from "@/components/auth-form";
import { AuthShell } from "@/components/auth-shell";
import { linkClassName } from "@/components/ui/styles";

export const metadata: Metadata = { title: "Log in" };

export default function LoginPage() {
  return (
    <AuthShell
      title="Welcome back"
      description="Log in to see your new job matches."
      footer={
        <>
          No account yet?{" "}
          <Link href="/register" className={linkClassName}>
            Sign up
          </Link>
        </>
      }
    >
      <AuthForm
        action={login}
        submitLabel="Log in"
        passwordAutoComplete="current-password"
        showRememberMe
      />
    </AuthShell>
  );
}
