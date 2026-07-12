import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Input } from "../components/common/Input";
import { Button } from "../components/common/Button";
import { Alert } from "../components/common/Alert";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login({ email, password });
      navigate("/");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not log in.");
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
            CPM Scheduler
          </div>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && <Alert type="error" message={error} />}
          <Input
            label="Email"
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <Input
            label="Password"
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button type="submit" variant="primary" loading={loading} className="w-full">
            Log in
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-steel">
          No account? <Link to="/signup" className="text-ink underline">Sign up</Link>
        </p>
      </div>
    </div>
  );
}
