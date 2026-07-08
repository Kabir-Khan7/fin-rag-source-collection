"use client";

import { useActivity } from "@/context/ActivityContext";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";

export default function ActivityPage() {
  const { entries, clearActivity } = useActivity();

  return (
    <main className="max-w-6xl mx-auto p-8 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Activity Log</h1>
          <p className="text-slate-500 mt-1">
            Actions performed during this session
          </p>
        </div>
        <Button variant="outline" onClick={clearActivity} disabled={entries.length === 0}>
          Clear Log
        </Button>
      </div>

      <Card className="p-6">
        {entries.length === 0 ? (
          <p className="text-slate-400 text-center py-8">
            No activity yet. Create, upload, or delete a record to see it logged here.
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Time</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Resource</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Detail</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {entries.map((e) => (
                <TableRow key={e.id}>
                  <TableCell className="text-sm text-slate-500">{e.timestamp}</TableCell>
                  <TableCell className="font-medium">{e.action}</TableCell>
                  <TableCell>{e.resource}</TableCell>
                  <TableCell>
                    <span
                      className={
                        e.status === "success" ? "text-green-600" : "text-red-600"
                      }
                    >
                      {e.status}
                    </span>
                  </TableCell>
                  <TableCell className="max-w-[300px] truncate">{e.detail}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </Card>
    </main>
  );
}