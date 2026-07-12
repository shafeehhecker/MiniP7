interface AlertProps {
  type?: "error" | "success" | "info";
  message: string;
}

const STYLES: Record<string, string> = {
  error: "border-hazard bg-hazard-dim text-hazard",
  success: "border-slack bg-slack-dim text-slack",
  info: "border-paper-line bg-paper text-steel",
};

export function Alert({ type = "info", message }: AlertProps) {
  return (
    <div className={`border px-3 py-2 text-sm ${STYLES[type]}`} role="alert">
      {message}
    </div>
  );
}
