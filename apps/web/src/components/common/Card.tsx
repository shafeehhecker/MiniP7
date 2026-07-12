import type { ReactNode } from "react";

interface CardProps {
  title?: string;
  eyebrow?: string;
  children: ReactNode;
  className?: string;
}

export function Card({ title, eyebrow, children, className = "" }: CardProps) {
  return (
    <div className={`border border-paper-line bg-white ${className}`}>
      {(title || eyebrow) && (
        <div className="border-b border-paper-line px-4 py-3">
          {eyebrow && (
            <div className="font-mono text-[11px] uppercase tracking-wide text-steel">
              {eyebrow}
            </div>
          )}
          {title && <div className="font-display text-sm font-semibold text-ink">{title}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
