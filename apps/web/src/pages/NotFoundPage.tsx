import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="py-24 text-center">
      <p className="font-mono text-xs uppercase tracking-widest text-steel">404</p>
      <h1 className="mt-2 font-display text-2xl font-bold text-ink">Nothing scheduled here</h1>
      <p className="mt-2 text-sm text-steel">The page you're looking for doesn't exist.</p>
      <Link to="/" className="mt-4 inline-block text-sm text-ink underline">
        Back to projects
      </Link>
    </div>
  );
}
