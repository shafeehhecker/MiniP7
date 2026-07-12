import { useState } from "react";
import { useEvm } from "../hooks/useEvm";
import { Card } from "./common/Card";
import { Input } from "./common/Input";
import { Spinner } from "./common/Spinner";
import { Alert } from "./common/Alert";
import { formatMoney, formatRatio } from "../lib/formatters";

interface EvmPanelProps {
  orgId: string;
  projectId: string;
  currencyCode: string;
  maxDay: number;
}

/** Displays the earned-value snapshot (ADR-0013) for a status day the user
 * can move — SPI/CPI are None from the API when undefined, shown as "—"
 * rather than a misleading 0.00. */
export function EvmPanel({ orgId, projectId, currencyCode, maxDay }: EvmPanelProps) {
  const [statusDay, setStatusDay] = useState(Math.min(maxDay, Math.ceil(maxDay / 2)));
  const { evm, loading, error } = useEvm(orgId, projectId, statusDay);

  return (
    <Card eyebrow="Earned value" title="Cost & schedule performance">
      <div className="mb-4">
        <Input
          label={`Status day (0–${maxDay})`}
          type="number"
          min={0}
          max={maxDay}
          value={statusDay}
          onChange={(e) => setStatusDay(Math.max(0, Math.min(maxDay, Number(e.target.value))))}
        />
      </div>

      {loading && <Spinner label="Computing…" />}
      {error && <Alert type="error" message={error.message} />}

      {evm && (
        <div className="grid grid-cols-2 gap-x-6 gap-y-3 font-mono text-sm">
          <Metric label="BAC" value={formatMoney(evm.bac, currencyCode)} />
          <Metric label="PV (BCWS)" value={formatMoney(evm.pv, currencyCode)} />
          <Metric label="EV (BCWP)" value={formatMoney(evm.ev, currencyCode)} />
          <Metric label="AC (ACWP)" value={formatMoney(evm.ac, currencyCode)} />
          <Metric label="SV" value={formatMoney(evm.sv, currencyCode)} tone={evm.sv < 0 ? "hazard" : "slack"} />
          <Metric label="CV" value={formatMoney(evm.cv, currencyCode)} tone={evm.cv < 0 ? "hazard" : "slack"} />
          <Metric label="SPI" value={formatRatio(evm.spi)} tone={evm.spi !== null && evm.spi < 1 ? "hazard" : "slack"} />
          <Metric label="CPI" value={formatRatio(evm.cpi)} tone={evm.cpi !== null && evm.cpi < 1 ? "hazard" : "slack"} />
          <Metric label="EAC" value={evm.eac !== null ? formatMoney(evm.eac, currencyCode) : "—"} />
          <Metric label="VAC" value={evm.vac !== null ? formatMoney(evm.vac, currencyCode) : "—"} tone={evm.vac !== null && evm.vac < 0 ? "hazard" : "slack"} />
        </div>
      )}
    </Card>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone?: "hazard" | "slack" }) {
  const color = tone === "hazard" ? "text-hazard" : tone === "slack" ? "text-slack" : "text-graphite";
  return (
    <div>
      <div className="font-body text-[11px] uppercase tracking-wide text-steel">{label}</div>
      <div className={`text-base ${color}`}>{value}</div>
    </div>
  );
}
