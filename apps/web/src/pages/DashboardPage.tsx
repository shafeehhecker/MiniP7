import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useOrganizations } from "../hooks/useOrganizations";
import { useProjects } from "../hooks/useProjects";
import { Card } from "../components/common/Card";
import { Select } from "../components/common/Select";
import { Button } from "../components/common/Button";
import { Input } from "../components/common/Input";
import { Table, type Column } from "../components/common/Table";
import { Spinner } from "../components/common/Spinner";
import { Alert } from "../components/common/Alert";
import { Modal } from "../components/common/Modal";
import type { Project } from "@minip7/client";

export function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { organizations, loading: orgsLoading } = useOrganizations();
  const [orgId, setOrgId] = useState<string | null>(user?.organizationId ?? null);

  useEffect(() => {
    if (!orgId && organizations.length > 0) setOrgId(organizations[0].id);
  }, [organizations, orgId]);

  const { projects, loading, error, createProject } = useProjects(orgId);
  const [modalOpen, setModalOpen] = useState(false);
  const [newProject, setNewProject] = useState({ id: "", name: "" });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState<string | null>(null);

  async function handleCreate() {
    setCreateError(null);
    if (!newProject.id.trim() || !newProject.name.trim()) {
      setCreateError("Project ID and name are required.");
      return;
    }
    setCreating(true);
    try {
      const project = await createProject(newProject.id, newProject.name);
      setModalOpen(false);
      setNewProject({ id: "", name: "" });
      navigate(`/projects/${project.id}?org=${orgId}`);
    } catch (e) {
      setCreateError(e instanceof Error ? e.message : "Could not create project.");
    } finally {
      setCreating(false);
    }
  }

  const columns: Column<Project>[] = [
    { key: "id", header: "ID", render: (p) => <span className="font-mono text-xs">{p.id}</span> },
    { key: "name", header: "Name", render: (p) => p.name },
    {
      key: "activities",
      header: "Activities",
      render: (p) => (p.activities ?? []).length,
      align: "right",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-end justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-ink">Projects</h1>
          <p className="mt-1 text-sm text-steel">
            {organizations.length > 0
              ? "Select an organization, then open or create a project."
              : "You're not a member of any organization yet."}
          </p>
        </div>
        {orgId && (
          <Button variant="primary" onClick={() => setModalOpen(true)}>
            New project
          </Button>
        )}
      </div>

      {orgsLoading && <Spinner label="Loading organizations…" />}

      {organizations.length > 0 && (
        <div className="max-w-xs">
          <Select
            label="Organization"
            options={organizations.map((o) => ({ value: o.id, label: o.name }))}
            value={orgId ?? ""}
            onChange={(e) => setOrgId(e.target.value)}
          />
        </div>
      )}

      <Card>
        {loading && <Spinner label="Loading projects…" />}
        {error && <Alert type="error" message={error.message} />}
        {!loading && !error && (
          <Table
            columns={columns}
            rows={projects}
            rowKey={(p) => p.id}
            onRowClick={(p) => navigate(`/projects/${p.id}?org=${orgId}`)}
            emptyMessage="No projects yet — create one to get started."
          />
        )}
      </Card>

      <Modal
        title="New project"
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <Button variant="ghost" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreate} loading={creating}>
              Create
            </Button>
          </>
        }
      >
        <div className="space-y-3">
          {createError && <Alert type="error" message={createError} />}
          <Input
            label="Project ID"
            hint="Short, unique, e.g. 'office-fitout'."
            value={newProject.id}
            onChange={(e) => setNewProject((p) => ({ ...p, id: e.target.value }))}
          />
          <Input
            label="Project name"
            value={newProject.name}
            onChange={(e) => setNewProject((p) => ({ ...p, name: e.target.value }))}
          />
        </div>
      </Modal>
    </div>
  );
}
