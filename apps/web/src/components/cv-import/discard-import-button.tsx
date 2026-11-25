import { discardCvImport } from "@/app/profile/import/actions";
import { secondaryButtonClassName } from "@/components/ui/styles";

/** Drop the draft without changing the profile. */
export function DiscardImportButton({ importId }: { importId: string }) {
  return (
    <form action={discardCvImport.bind(null, importId)}>
      <button type="submit" className={secondaryButtonClassName}>
        Discard this import
      </button>
    </form>
  );
}
