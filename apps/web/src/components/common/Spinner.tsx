export function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-steel" role="status">
      <span className="h-4 w-4 animate-spin border-2 border-steel border-t-transparent" />
      {label}
    </div>
  );
}
