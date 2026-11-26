"use client";

import { useState } from "react";

import { CheckIcon } from "@/components/ui/icons";
import { secondaryButtonClassName } from "@/components/ui/styles";

type CopyButtonProps = {
  text: string;
  label: string;
};

/** Copy `text` to the clipboard, and say so for a moment. */
export function CopyButton({ text, label }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <button type="button" onClick={copy} className={secondaryButtonClassName}>
      {copied ? (
        <>
          <CheckIcon className="text-success size-4" />
          <span aria-live="polite">Copied</span>
        </>
      ) : (
        label
      )}
    </button>
  );
}
