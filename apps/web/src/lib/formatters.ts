/** Formatting helpers shared across the UI. Pure functions — no React here. */

/** Working-day offset → a plain "day N" label. Real calendar-date mapping
 * (ADR-0012) is a server-side concern; the UI shows working-day offsets
 * until a project has a start_date and the API exposes mapped dates. */
export function formatDay(offset: number): string {
  return `Day ${offset}`;
}

export function formatDuration(days: number): string {
  if (days === 0) return "0d (milestone)";
  return `${days}d`;
}

export function formatFloat(days: number): string {
  if (days === 0) return "0";
  return `${days}d`;
}

export function formatMoney(amount: number, currencyCode: string): string {
  try {
    return new Intl.NumberFormat(undefined, {
      style: "currency",
      currency: currencyCode,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${currencyCode} ${amount.toFixed(0)}`;
  }
}

export function formatRatio(value: number | null): string {
  if (value === null) return "—";
  return value.toFixed(2);
}

export function formatPercent(value: number): string {
  return `${Math.round(value)}%`;
}
