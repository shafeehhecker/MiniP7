interface BadgeProps {
  children: string;
  tone?: "neutral" | "hazard" | "slack" | "ink";
}

const TONES: Record<string, string> = {
  neutral: "border-paper-line text-steel",
  hazard: "border-hazard text-hazard",
  slack: "border-slack text-slack",
  ink: "border-ink text-ink",
};

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return (
    <span
      className={`inline-block border px-1.5 py-0.5 font-mono text-[10px] uppercase tracking-wide ${TONES[tone]}`}
    >
      {children}
    </span>
  );
}
