"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import { apiGet } from "@/lib/api";
import { Card } from "@/components/ui/card";

// The tables to show stats for.
const TABLES = [
  { label: "Subledger", path: "/api/v1/transactions", href: "/subledger" },
  { label: "Bank Feed", path: "/api/v1/bank-feed", href: "/bank-feed" },
  { label: "Chart of Accounts", path: "/api/v1/chart-of-accounts", href: "/chart-of-accounts" },
  { label: "Master Directory", path: "/api/v1/master-directory", href: "/master-directory" },
  { label: "Raw Invoices", path: "/api/v1/raw-invoices", href: "/raw-invoices" },
];

export default function DashboardPage() {
  const [counts, setCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    // Fetch a sample from each table to show a recent-count indicator.
    TABLES.forEach(async (table) => {
      try {
        const data = await apiGet<unknown[]>(`${table.path}?skip=0&limit=100`);
        setCounts((prev) => ({ ...prev, [table.label]: data.length }));
      } catch {
        setCounts((prev) => ({ ...prev, [table.label]: -1 }));
      }
    });
  }, []);

  return (
    <main className="max-w-6xl mx-auto p-8 space-y-8">
      <div>
        <h1 className="text-2xl font-bold">Dashboard</h1>
        <p className="text-slate-500 mt-1">
          Source Collection — Bronze layer ingestion overview
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {TABLES.map((table) => (
          <Link key={table.href} href={table.href}>
            <Card className="p-6 hover:shadow-md transition-shadow cursor-pointer">
              <h2 className="text-sm font-medium text-slate-500">{table.label}</h2>
              <p className="text-3xl font-bold mt-2">
                {counts[table.label] === undefined
                  ? "…"
                  : counts[table.label] === -1
                  ? "—"
                  : `${counts[table.label]}${counts[table.label] === 100 ? "+" : ""}`}
              </p>
              <p className="text-xs text-slate-400 mt-1">recent records</p>
            </Card>
          </Link>
        ))}
      </div>
    </main>
  );
}