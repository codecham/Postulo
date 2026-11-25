type ChipProps = {
  label: string;
  onRemove: () => void;
};

/** A selected value, with a button to remove it. */
export function Chip({ label, onRemove }: ChipProps) {
  return (
    <li className="flex items-center gap-1 rounded-full bg-gray-100 py-1 pr-1 pl-3 text-sm dark:bg-gray-800">
      {label}
      <button
        type="button"
        onClick={onRemove}
        aria-label={`Remove ${label}`}
        className="rounded-full px-1.5 text-gray-500 hover:bg-gray-200 hover:text-gray-900 dark:hover:bg-gray-700 dark:hover:text-white"
      >
        ×
      </button>
    </li>
  );
}
