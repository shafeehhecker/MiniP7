import { useState, useEffect } from "react";
import type { Activity, ActivityType } from "@minip7/client";
import { RelationshipType } from "@minip7/client";
import { Modal } from "../common/Modal";
import { Input } from "../common/Input";
import { Select } from "../common/Select";
import { Button } from "../common/Button";
import { Alert } from "../common/Alert";

interface ActivityModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (activity: Activity) => Promise<void>;
  existing?: Activity;
  otherActivityIds: string[];
}

const TYPE_OPTIONS = [
  { value: "task", label: "Task" },
  { value: "milestone", label: "Milestone" },
  { value: "level_of_effort", label: "Level of effort" },
  { value: "summary", label: "Summary" },
];

const REL_OPTIONS = [
  { value: "FS", label: "FS — finish to start" },
  { value: "SS", label: "SS — start to start" },
  { value: "FF", label: "FF — finish to finish" },
  { value: "SF", label: "SF — start to finish" },
];

function emptyActivity(): Activity {
  return {
    id: "",
    name: "",
    duration: 1,
    type: "task" as ActivityType,
    relationships: [],
    budget: 0,
    actual_cost: 0,
    percent_complete: 0,
  };
}

export function ActivityModal({ isOpen, onClose, onSave, existing, otherActivityIds }: ActivityModalProps) {
  const [form, setForm] = useState<Activity>(existing ?? emptyActivity());
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newPred, setNewPred] = useState({ predecessor_id: "", type: RelationshipType.FS, lag: 0 });

  useEffect(() => {
    setForm(existing ?? emptyActivity());
    setError(null);
  }, [existing, isOpen]);

  const isMilestone = form.type === "milestone";

  async function handleSubmit() {
    setError(null);
    if (!form.id.trim() || !form.name.trim()) {
      setError("ID and name are required.");
      return;
    }
    setSaving(true);
    try {
      await onSave({ ...form, duration: isMilestone ? 0 : form.duration });
      onClose();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not save activity.");
    } finally {
      setSaving(false);
    }
  }

  function addRelationship() {
    if (!newPred.predecessor_id) return;
    setForm((f) => ({
      ...f,
      relationships: [...(f.relationships ?? []), { ...newPred }],
    }));
    setNewPred({ predecessor_id: "", type: RelationshipType.FS, lag: 0 });
  }

  function removeRelationship(index: number) {
    setForm((f) => ({
      ...f,
      relationships: (f.relationships ?? []).filter((_, i) => i !== index),
    }));
  }

  return (
    <Modal
      title={existing ? `Edit ${existing.id}` : "Add activity"}
      isOpen={isOpen}
      onClose={onClose}
      footer={
        <>
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} loading={saving}>
            Save activity
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {error && <Alert type="error" message={error} />}

        <div className="grid grid-cols-2 gap-3">
          <Input
            label="ID"
            value={form.id}
            disabled={!!existing}
            onChange={(e) => setForm((f) => ({ ...f, id: e.target.value }))}
            placeholder="e.g. B"
          />
          <Select
            label="Type"
            options={TYPE_OPTIONS}
            value={form.type ?? "task"}
            onChange={(e) => setForm((f) => ({ ...f, type: e.target.value as ActivityType }))}
          />
        </div>

        <Input
          label="Name"
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          placeholder="e.g. Pour foundation"
        />

        <div className="grid grid-cols-2 gap-3">
          <Input
            label="Duration (days)"
            type="number"
            min={0}
            value={isMilestone ? 0 : form.duration}
            disabled={isMilestone}
            onChange={(e) => setForm((f) => ({ ...f, duration: Number(e.target.value) }))}
            hint={isMilestone ? "Milestones are always 0 days." : undefined}
          />
          <Input
            label="Resource"
            value={form.resource ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, resource: e.target.value || null }))}
            placeholder="Optional"
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <Input
            label="Budget"
            type="number"
            min={0}
            value={form.budget ?? 0}
            onChange={(e) => setForm((f) => ({ ...f, budget: Number(e.target.value) }))}
          />
          <Input
            label="Actual cost"
            type="number"
            min={0}
            value={form.actual_cost ?? 0}
            onChange={(e) => setForm((f) => ({ ...f, actual_cost: Number(e.target.value) }))}
          />
          <Input
            label="% complete"
            type="number"
            min={0}
            max={100}
            value={form.percent_complete ?? 0}
            onChange={(e) => setForm((f) => ({ ...f, percent_complete: Number(e.target.value) }))}
          />
        </div>

        <div>
          <span className="mb-1 block font-mono text-[11px] uppercase tracking-wide text-steel">
            Predecessors
          </span>
          <div className="space-y-1">
            {(form.relationships ?? []).map((r, i) => (
              <div key={i} className="flex items-center justify-between border border-paper-line px-2 py-1 text-xs">
                <span className="font-mono">
                  {r.predecessor_id} · {r.type}{r.lag ? ` +${r.lag}d` : ""}
                </span>
                <button onClick={() => removeRelationship(i)} className="text-hazard hover:underline">
                  Remove
                </button>
              </div>
            ))}
          </div>
          <div className="mt-2 grid grid-cols-[1fr_1fr_70px_auto] gap-2">
            <Select
              options={[{ value: "", label: "Predecessor…" }, ...otherActivityIds.map((id) => ({ value: id, label: id }))]}
              value={newPred.predecessor_id}
              onChange={(e) => setNewPred((p) => ({ ...p, predecessor_id: e.target.value }))}
            />
            <Select
              options={REL_OPTIONS}
              value={newPred.type}
              onChange={(e) => setNewPred((p) => ({ ...p, type: e.target.value as RelationshipType }))}
            />
            <Input
              type="number"
              placeholder="Lag"
              value={newPred.lag}
              onChange={(e) => setNewPred((p) => ({ ...p, lag: Number(e.target.value) }))}
            />
            <Button variant="secondary" size="sm" onClick={addRelationship}>
              Add
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
