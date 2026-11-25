import { CheckboxField } from "@/components/ui/checkbox-field";
import type { Option } from "@/lib/forms";

type CheckboxGroupProps = {
  legend: string;
  name: string;
  options: Option[];
  defaultValue?: string[];
};

/** Several checkboxes sent under one name: read them with readList(). */
export function CheckboxGroup({
  legend,
  name,
  options,
  defaultValue = [],
}: CheckboxGroupProps) {
  return (
    <fieldset className="flex flex-col gap-2">
      <legend className="mb-1 text-sm font-medium">{legend}</legend>
      <div className="flex flex-wrap gap-x-6 gap-y-2">
        {options.map((option) => (
          <CheckboxField
            key={option.value}
            name={name}
            value={option.value}
            label={option.label}
            defaultChecked={defaultValue.includes(option.value)}
          />
        ))}
      </div>
    </fieldset>
  );
}
