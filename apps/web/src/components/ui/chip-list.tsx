import { Chip } from "@/components/ui/chip";
import type { Option } from "@/lib/forms";

type ChipListProps = {
  name: string;
  items: Option[];
  onRemove: (value: string) => void;
};

/**
 * The selected values as chips, plus one hidden input per value so the form
 * sends them all under `name` (read them with readList()).
 */
export function ChipList({ name, items, onRemove }: ChipListProps) {
  if (items.length === 0) {
    return null;
  }
  return (
    <>
      <ul className="flex flex-wrap gap-2">
        {items.map((item) => (
          <Chip
            key={item.value}
            label={item.label}
            onRemove={() => onRemove(item.value)}
          />
        ))}
      </ul>
      {items.map((item) => (
        <input key={item.value} type="hidden" name={name} value={item.value} />
      ))}
    </>
  );
}
