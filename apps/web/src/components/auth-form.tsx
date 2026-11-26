"use client";

import { useActionState } from "react";

import type { AuthFormState } from "@/app/(auth)/actions";
import { CheckboxField } from "@/components/ui/checkbox-field";
import { SubmitButton } from "@/components/ui/submit-button";
import { TextField } from "@/components/ui/text-field";

type AuthFormProps = {
  action: (state: AuthFormState, formData: FormData) => Promise<AuthFormState>;
  submitLabel: string;
  passwordAutoComplete: "current-password" | "new-password";
  /** Show the "Keep me signed in" checkbox (login only). */
  showRememberMe?: boolean;
};

export function AuthForm({
  action,
  submitLabel,
  passwordAutoComplete,
  showRememberMe = false,
}: AuthFormProps) {
  const [state, formAction] = useActionState(action, undefined);

  return (
    <form action={formAction} className="flex flex-col gap-4">
      <TextField
        label="Email"
        name="email"
        type="email"
        autoComplete="email"
        required
      />
      <TextField
        label="Password"
        name="password"
        type="password"
        autoComplete={passwordAutoComplete}
        hint={
          passwordAutoComplete === "new-password"
            ? "At least 8 characters."
            : undefined
        }
        minLength={8}
        maxLength={128}
        required
      />
      {showRememberMe && (
        <CheckboxField
          label="Keep me signed in for 30 days"
          name="remember_me"
        />
      )}
      {state?.error && (
        <p role="alert" className="text-danger text-sm font-medium">
          {state.error}
        </p>
      )}
      <SubmitButton pendingLabel="Please wait…" fullWidth>
        {submitLabel}
      </SubmitButton>
    </form>
  );
}
