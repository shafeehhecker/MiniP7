import { forwardRef, type InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, id, className = "", ...rest }, ref) => {
    const inputId = id ?? rest.name;
    return (
      <label className="block" htmlFor={inputId}>
        {label && (
          <span className="mb-1 block font-mono text-[11px] uppercase tracking-wide text-steel">
            {label}
          </span>
        )}
        <input
          ref={ref}
          id={inputId}
          className={`w-full border bg-white px-3 py-2 text-sm text-graphite outline-none transition-colors placeholder:text-steel/60 ${
            error ? "border-hazard" : "border-paper-line focus:border-ink"
          } ${className}`}
          {...rest}
        />
        {error && <span className="mt-1 block text-xs text-hazard">{error}</span>}
        {!error && hint && <span className="mt-1 block text-xs text-steel">{hint}</span>}
      </label>
    );
  }
);
Input.displayName = "Input";
