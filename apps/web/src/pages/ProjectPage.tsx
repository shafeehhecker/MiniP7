import { useState } from "react";
import { useParams, useSearchParams, Link } from "react-router-dom";
import type { Activity } from "@minip7/client";
import { useProject } from "../hooks/useProject";
import { useOrganizations } from "../hooks/useOrganizations";
import { Card } from "../components/common/Card";
import { Button } from "../components/common/Button";
import { Badge } from "../components/common/Badge";
import { Table, type Column } from "../components/common/Table";
import { Spinner } from "../components/common/Spinner";
import { Alert } from "../components/common/Alert";
import { Gantt } from "../components/gantt/Gantt";
import { ActivityModal } from "../components/forms/ActivityModal";
import { EvmPanel } from "../components/EvmPanel";
import { formatDuration, formatFloat } from "../lib/formatters";

export function ProjectPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [searchParams] = useSearchParams();
  const orgId = searchParams.get("org");

  const {
    project,
    loading,
    error,
    schedule,
    scheduling,
    scheduleError,
    isScheduled,
    addActivity,
    updateActivity,
    removeActivity,
    loadSample,
  } = useProject(orgId, projectId ?? null);

  const { organizations } = useOrganizations();
  const currencyCode = organizations.find((o) => o.id === orgId)?.currency?.code ?? "USD";

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<Activity | undefined>(undefined);
  const [showEvm, setShowEvm] = useState(false);

  if (!orgId || !projectId) {
    return <Alert type="error" message="Missing organization or project in the URL." />;
  }
  if (loading) return <Spinner label="Loading project…" />;
  if (error) return <Alert type="error" message={error.message} />;
  if (!project) return null;

  const activities = project.activities ?? [];
  const hasBudget = activities.some((a) => (a.budget ?? 0) > 0);
  const maxDay = Math.max(0, ...activities.map((a) => a.EF ?? 0));

  function openAdd() {
    setEditing(undefined);
    setModalOpen(true);
  }
  function openEdit(a: Activity) {
    setEditing(a);
    setModalOpen(true);
  }

  const columns: Column<Activity>[] = [
    { key: "id", header: "ID", render: (a) => <span className="font-mono text-xs">{a.id}</span> },
    { key: "name", header: "Name", render: (a) => a.name },
    {
      key: "type",
      header: "Type",
      render: (a) => <Badge tone={a.type === "milestone" ? "ink" : "neutral"}>{a.type ?? "task"}</Badge>,
    },
    { key: "duration", header: "Duration", render: (a) => formatDuration(a.duration), align: "right" },
    {
      key: "es",
      header: "ES–EF",
      render: (a) => (isScheduled ? <span className="font-mono text-xs">{a.ES}–{a.EF}</span> : "—"),
      align: "right",
    },
    {
      key: "float",
      header: "Float",
      render: (a) =>
        isScheduled ? (
          <span className={a.is_critical ? "text-hazard" : "text-graphite"}>
            {a.is_critical ? "Critical" : formatFloat(a.total_float ?? 0)}
          </span>
        ) : (
          "—"
        ),
      align: "right",
    },
    {
      key: "actions",
      header: "",
      render: (a) => (
        <div className="flex justify-end gap-2">
          <button
            className="text-xs text-steel hover:text-ink hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              openEdit(a);
            }}
          >
            Edit
          </button>
          <button
            className="text-xs text-hazard hover:underline"
            onClick={(e) => {
              e.stopPropagation();
              removeActivity(a.id);
            }}
          >
            Delete
          </button>
        </div>
      ),
      align: "right",
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <Link to="/" className="text-xs text-steel hover:text-ink hover:underline">
          ← All projects
        </Link>
        <div className="mt-1 flex items-end justify-between">
          <div>
            <h1 className="font-display text-2xl font-bold text-ink">{project.name}</h1>
            <p className="font-mono text-xs text-steel">{project.id}</p>
          </div>
          <div className="flex gap-2">
            {activities.length === 0 && (
              <Button variant="secondary" onClick={loadSample}>
                Load sample
              </Button>
            )}
            <Button variant="secondary" onClick={openAdd}>
              Add activity
            </Button>
            <Button variant="primary" onClick={schedule} loading={scheduling}>
              Schedule
            </Button>
          </div>
        </div>
      </div>

      {scheduleError && <Alert type="error" message={scheduleError} />}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card eyebrow={`${activities.length} activities`} title="Activity list">
          <Table columns={columns} rows={activities} rowKey={(a) => a.id} onRowClick={openEdit} />
        </Card>

        <div className="space-y-4">
          <Card eyebrow="Schedule" title="Gantt">
            {isScheduled ? (
              <Gantt activities={activities} onSelect={openEdit} />
            ) : (
              <p className="border border-dashed border-paper-line px-4 py-8 text-center text-sm text-steel">
                Click "Schedule" above to run CPM and see the Gantt.
              </p>
            )}
          </Card>
        </div>
      </div>

      {hasBudget && isScheduled && (
        <div>
          {!showEvm ? (
            <Button variant="ghost" onClick={() => setShowEvm(true)}>
              Show earned value metrics →
            </Button>
          ) : (
            <EvmPanel orgId={orgId} projectId={projectId} currencyCode={currencyCode} maxDay={maxDay} />
          )}
        </div>
      )}

      <ActivityModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={editing ? updateActivity : addActivity}
        existing={editing}
        otherActivityIds={activities.map((a) => a.id).filter((id) => id !== editing?.id)}
      />
    </div>
  );
}
