import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { Button } from "../common/Button";

export function Header() {
  const { user, logout } = useAuth();

  return (
    <header className="border-b border-ink bg-ink text-paper">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <Link to="/" className="flex items-baseline gap-2">
          <span className="font-display text-lg font-bold tracking-tight">Mini-P7</span>
          <span className="font-mono text-[10px] uppercase tracking-widest text-paper/50">
            CPM Scheduler
          </span>
        </Link>
        {user && (
          <div className="flex items-center gap-4 font-mono text-xs text-paper/70">
            <span>{user.email}</span>
            <Button variant="ghost" size="sm" onClick={logout} className="!text-paper/70 hover:!text-paper">
              Log out
            </Button>
          </div>
        )}
      </div>
    </header>
  );
}
