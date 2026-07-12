import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/common/Input";
import { Button } from "../components/common/Button";
import { Alert } from "../components/common/Alert";

export function SignupPage() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", organization_name: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signup(form);
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not sign up.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-blueprint-grid px-4">
      <div className="w-full max-w-sm border border-paper-line bg-white p-8">
        <div className="mb-6 text-center">
          <div className="font-display text-2xl font-bold text-ink">Mini-P7</div>
          <div className="mt-1 font-mono text-[11px] uppercase tracking-widest text-steel">
            Create your workspace
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert type="error" message={error} />}
          <Input
            label="Your name"
            required
            value={form.name}
            onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          />
          <Input
            label="Email"
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
          />
          <Input
            label="Password"
            type="password"
            required
            minLength={8}
            hint="At least 8 characters."
            value={form.password}
            onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          />
          <Input
            label="Organization name"
            required
            value={form.organization_name}
            onChange={(e) => setForm((f) => ({ ...f, organization_name: e.target.value }))}
          />
          <Button type="submit" variant="primary" loading={loading} className="w-full">
            Create workspace
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-steel">
          Already have an account? <Link to="/login" className="text-ink underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
