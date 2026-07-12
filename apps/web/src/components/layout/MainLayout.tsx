import { Outlet } from "react-router-dom";
import { Header } from "./Header";

export function MainLayout() {
  return (
    <div className="min-h-screen bg-blueprint-grid">
      <Header />
      <main className="mx-auto max-w-7xl px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
