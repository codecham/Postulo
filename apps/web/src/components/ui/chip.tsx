type ChipProps = {
  label: string;
  onRemove: () => void;
};

/** A selected value, with a button to remove it. */
export function Chip({ label, onRemove }: ChipProps) {
  return (
    <li className="bg-accent-soft text-accent-text flex items-center gap-1 rounded-full py-1 pr-1 pl-3 text-sm">
      {label}
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${label}`}
        className="hover:bg-accent/15 flex size-5 items-center justify-center rounded-full"
      >
        ×
      </button>
    </li>
  );
}
