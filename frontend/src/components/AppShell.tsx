import { Sidebar } from "@/components/Sidebar";

/**
 * Wraps page content with the persistent sidebar navigation.
 */
export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 bg-slate-50 min-h-screen">{children}</div>
    </div>
  );
}