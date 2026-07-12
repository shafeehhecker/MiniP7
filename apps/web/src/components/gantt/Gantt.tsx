import { useMemo, useState } from "react";
import type { Activity, RelationshipType } from "@minip7/client";

interface GanttProps {
  activities: Activity[];
  onSelect?: (activity: Activity) => void;
}

const DAY_WIDTH = 28;
const ROW_HEIGHT = 34;
const LABEL_WIDTH = 180;
const TOP_PAD = 36;
const LEFT_PAD = 12;

const REL_COLOR: Record<RelationshipType, string> = {
  FS: "#5B6B85", // steel — the default, drawn plain
  SS: "#14213D", // ink
  FF: "#14213D",
  SF: "#E8590C", // hazard — SF is the rare, easy-to-misuse one; make it stand out
};

/**
 * Renders a scheduled activity network as a blueprint-style Gantt: graph
 * paper grid, hazard-orange bars for the critical path, diamonds for
 * milestones, and right-angle drafting connectors for all four relationship
 * types (ADR-0011) — not just finish-to-start. Working-day axis only; real
 * calendar dates are a server-side concern (ADR-0012) not yet wired into
 * this endpoint.
 */
export function Gantt({ activities, onSelect }: GanttProps) {
  const [hovered, setHovered] = useState<string | null>(null);

  const scheduled = activities.filter((a) => a.ES !== undefined && a.EF !== undefined);

  const sorted = useMemo(
    () => [...scheduled].sort((a, b) => (a.ES ?? 0) - (b.ES ?? 0) || a.id.localeCompare(b.id)),
    [scheduled]
  );

  const rowIndex = useMemo(() => {
    const map = new Map<string, number>();
    sorted.forEach((a, i) => map.set(a.id, i));
    return map;
  }, [sorted]);

  const maxDay = Math.max(1, ...scheduled.map((a) => a.EF ?? 0));
  const chartWidth = LABEL_WIDTH + maxDay * DAY_WIDTH + LEFT_PAD * 2;
  const chartHeight = TOP_PAD + sorted.length * ROW_HEIGHT + 16;

  function x(day: number) {
    return LABEL_WIDTH + LEFT_PAD + day * DAY_WIDTH;
  }
  function y(index: number) {
    return TOP_PAD + index * ROW_HEIGHT;
  }

  if (scheduled.length === 0) {
    return (
      <p className="border border-dashed border-paper-line px-4 py-8 text-center text-sm text-steel">
        No scheduled activities yet — click "Schedule" to run CPM.
      </p>
    );
  }

  const byId = new Map(scheduled.map((a) => [a.id, a]));

  return (
    <div className="overflow-x-auto border border-paper-line bg-white">
      <div className="flex items-center gap-4 border-b border-paper-line px-3 py-2 font-mono text-[10px] uppercase tracking-wide text-steel">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-4 bg-hazard" /> Critical
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-2 w-4 bg-ink" /> Float
        </span>
        <span className="flex items-center gap-1.5">
          <svg width="10" height="10">
            <polygon points="5,0 10,5 5,10 0,5" fill="#14213D" />
          </svg>
          Milestone
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-px w-4 bg-hazard" /> SF link (verify)
        </span>
      </div>
      <svg width={chartWidth} height={chartHeight} role="img" aria-label="Project Gantt chart">
        <defs>
          <marker id="arrow" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M0,0 L8,4 L0,8 z" fill="#5B6B85" />
          </marker>
        </defs>

        {/* graph-paper day gridlines */}
        {Array.from({ length: maxDay + 1 }, (_, d) => (
          <line
            key={`grid-${d}`}
            x1={x(d)}
            y1={TOP_PAD - 12}
            x2={x(d)}
            y2={chartHeight - 8}
            stroke="#C7D2E0"
            strokeWidth={d % 5 === 0 ? 1 : 0.5}
          />
        ))}
        {Array.from({ length: maxDay + 1 }, (_, d) =>
          d % 5 === 0 ? (
            <text key={`daylabel-${d}`} x={x(d)} y={TOP_PAD - 18} fontSize="10" fontFamily="IBM Plex Mono, monospace" fill="#5B6B85">
              {d}
            </text>
          ) : null
        )}

        {/* relationship connectors, drawn first so bars sit on top */}
        {sorted.map((succ) =>
          (succ.relationships ?? []).map((rel, i) => {
            const pred = byId.get(rel.predecessor_id);
            if (!pred) return null;
            const predRow = rowIndex.get(pred.id)!;
            const succRow = rowIndex.get(succ.id)!;

            const startX = rel.type === "FS" || rel.type === "FF" ? x(pred.EF ?? 0) : x(pred.ES ?? 0);
            const endX = rel.type === "FS" || rel.type === "SS" ? x(succ.ES ?? 0) : x(succ.EF ?? 0);
            const startY = y(predRow) + ROW_HEIGHT / 2;
            const endY = y(succRow) + ROW_HEIGHT / 2;
            const midX = startX + 10;
            const color = REL_COLOR[rel.type ?? "FS"];

            return (
              <polyline
                key={`${succ.id}-${i}`}
                points={`${startX},${startY} ${midX},${startY} ${midX},${endY} ${endX},${endY}`}
                fill="none"
                stroke={color}
                strokeWidth={1}
                markerEnd="url(#arrow)"
                opacity={hovered && hovered !== succ.id && hovered !== pred.id ? 0.15 : 0.8}
              />
            );
          })
        )}

        {/* activity rows: labels, bars, milestones */}
        {sorted.map((a, i) => {
          const isMilestone = a.duration === 0;
          const rowY = y(i);
          const barY = rowY + 6;
          const barH = ROW_HEIGHT - 14;
          const isDim = hovered !== null && hovered !== a.id;

          return (
            <g
              key={a.id}
              opacity={isDim ? 0.35 : 1}
              onMouseEnter={() => setHovered(a.id)}
              onMouseLeave={() => setHovered(null)}
              onClick={() => onSelect?.(a)}
              style={{ cursor: onSelect ? "pointer" : "default" }}
            >
              <text
                x={LABEL_WIDTH - 10}
                y={rowY + ROW_HEIGHT / 2 + 4}
                textAnchor="end"
                fontSize="12"
                fontFamily="IBM Plex Sans, sans-serif"
                fill="#1B1F27"
              >
                {a.name.length > 22 ? `${a.name.slice(0, 21)}…` : a.name}
              </text>

              {isMilestone ? (
                <polygon
                  points={`${x(a.ES ?? 0)},${barY} ${x(a.ES ?? 0) + 8},${barY + barH / 2} ${x(a.ES ?? 0)},${barY + barH} ${x(a.ES ?? 0) - 8},${barY + barH / 2}`}
                  fill={a.is_critical ? "#E8590C" : "#14213D"}
                />
              ) : (
                <>
                  <rect
                    x={x(a.ES ?? 0)}
                    y={barY}
                    width={Math.max(2, x(a.EF ?? 0) - x(a.ES ?? 0))}
                    height={barH}
                    fill={a.is_critical ? "#E8590C" : "#14213D"}
                  />
                  {(a.percent_complete ?? 0) > 0 && (
                    <rect
                      x={x(a.ES ?? 0)}
                      y={barY}
                      width={Math.max(0, (x(a.EF ?? 0) - x(a.ES ?? 0)) * ((a.percent_complete ?? 0) / 100))}
                      height={barH}
                      fill="white"
                      opacity={0.35}
                    />
                  )}
                </>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}
