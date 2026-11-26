import { Alert } from "@/components/ui/alert";

/** Parts of the CV that could not be imported, so the user can add them by hand. */
export function ImportWarnings({ warnings }: { warnings: string[] }) {
  if (warnings.length === 0) {
    return null;
  }
  return (
    <Alert tone="warning" title="Some parts could not be imported">
      <ul className="list-disc pl-5">
        {warnings.map((warning) => (
          <li key={warning}>{warning}</li>
        ))}
      </ul>
    </Alert>
  );
}
