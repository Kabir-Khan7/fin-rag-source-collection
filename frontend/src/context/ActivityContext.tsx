"use client";

import { createContext, useContext, useState, ReactNode } from "react";

export interface ActivityEntry {
  id: string;
  timestamp: string;
  action: string;      // e.g. "Create", "Delete", "Upload"
  resource: string;    // e.g. "Subledger"
  status: "success" | "error";
  detail: string;
}

interface ActivityContextValue {
  entries: ActivityEntry[];
  logActivity: (entry: Omit<ActivityEntry, "id" | "timestamp">) => void;
  clearActivity: () => void;
}

const ActivityContext = createContext<ActivityContextValue | undefined>(undefined);

export function ActivityProvider({ children }: { children: ReactNode }) {
  const [entries, setEntries] = useState<ActivityEntry[]>([]);

  function logActivity(entry: Omit<ActivityEntry, "id" | "timestamp">) {
    const newEntry: ActivityEntry = {
      ...entry,
      id: crypto.randomUUID(),
      timestamp: new Date().toLocaleString(),
    };
    // Newest first; keep the last 100 entries.
    setEntries((prev) => [newEntry, ...prev].slice(0, 100));
  }

  function clearActivity() {
    setEntries([]);
  }

  return (
    <ActivityContext.Provider value={{ entries, logActivity, clearActivity }}>
      {children}
    </ActivityContext.Provider>
  );
}

/** Hook for pages to access and log activity. */
export function useActivity(): ActivityContextValue {
  const ctx = useContext(ActivityContext);
  if (!ctx) {
    throw new Error("useActivity must be used within an ActivityProvider");
  }
  return ctx;
}