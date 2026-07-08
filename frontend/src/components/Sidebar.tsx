"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// Navigation links — label + route.
const NAV_ITEMS = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Subledger", href: "/subledger" },
  { label: "Bank Feed", href: "/bank-feed" },
  { label: "Chart of Accounts", href: "/chart-of-accounts" },
  { label: "Master Directory", href: "/master-directory" },
  { label: "Raw Invoices", href: "/raw-invoices" },
  { label: "Activity Log", href: "/activity" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-60 min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      <div className="p-6 border-b border-slate-700">
        <h1 className="text-lg font-bold">Local RAG System</h1>
        <p className="text-xs text-slate-400 mt-1">Source Collection</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-4 py-2 rounded-md text-sm transition-colors ${
                isActive
                  ? "bg-slate-700 text-white font-medium"
                  : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-700 text-xs text-slate-400">
        v0.1.0
      </div>
    </aside>
  );
}