import type { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
  loading?: boolean;
}

const VARIANTS: Record<string, string> = {
  primary: "bg-ink text-paper hover:bg-ink/90 border border-ink",
  secondary: "bg-transparent text-ink border border-ink hover:bg-ink/5",
  danger: "bg-transparent text-hazard border border-hazard hover:bg-hazard-dim",
  ghost: "bg-transparent text-steel border border-transparent hover:text-ink hover:border-paper-line",
};

const SIZES: Record<string, string> = {
  sm: "px-2.5 py-1 text-xs",
  md: "px-4 py-2 text-sm",
};

export function Button({
  variant = "primary",
  size = "md",
  loading,
  disabled,
  className = "",
  children,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-body font-medium tracking-tight transition-colors disabled:opacity-40 disabled:cursor-not-allowed ${VARIANTS[variant]} ${SIZES[size]} ${className}`}
      disabled={disabled || loading}
      {...rest}
    >
      {loading && (
        <span className="h-3 w-3 animate-spin border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
}
