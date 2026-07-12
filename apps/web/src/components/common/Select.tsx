import { forwardRef, type SelectHTMLAttributes } from "react";

interface Option {
  value: string;
  label: string;
}

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: Option[];
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, options, id, className = "", ...rest }, ref) => {
    const selectId = id ?? rest.name;
    return (
      <label className="block" htmlFor={selectId}>
        {label && (
          <span className="mb-1 block font-mono text-[11px] uppercase tracking-wide text-steel">
            {label}
          </span>
        )}
        <select
          ref={ref}
          id={selectId}
          className={`w-full border border-paper-line bg-white px-3 py-2 text-sm text-graphite outline-none transition-colors focus:border-ink ${className}`}
          {...rest}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </label>
    );
  }
);
Select.displayName = "Select";
