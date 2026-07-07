"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { apiGet, apiPost, apiDelete } from "@/lib/api";
import type { SubledgerCreate, SubledgerResponse } from "@/types/subledger";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

// The form fields, matching the backend schema.
const FIELDS = [
  "Transaction_ID",
  "System_Timestamp",
  "Document_Date",
  "GL_Account_Code",
  "Entity_ID",
  "Amount",
  "Transaction_Type",
  "Status",
  "Description",
] as const;

// A type representing the field names.
type FieldName = (typeof FIELDS)[number];

// The form is a record of field name -> string value.
type FormState = Record<FieldName, string>;

// Build an empty form with every field as an empty string.
const EMPTY_FORM: FormState = FIELDS.reduce(
  (acc, field) => ({ ...acc, [field]: "" }),
  {} as FormState
);

export default function SubledgerPage() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [records, setRecords] = useState<SubledgerResponse[]>([]);
  const [loading, setLoading] = useState(false);

  // Load existing records on page load.
  async function loadRecords() {
    try {
      const data = await apiGet<SubledgerResponse[]>(
        "/api/v1/transactions?skip=0&limit=25"
      );
      setRecords(data);
    } catch (err) {
      toast.error(`Failed to load records: ${(err as Error).message}`);
    }
  }

  useEffect(() => {
    loadRecords();
  }, []);

  // Update a single form field.
  function handleChange(field: FieldName, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  // Submit the form to create a record.
  async function handleSubmit() {
    setLoading(true);
    try {
      // Send the form as the create payload.
      await apiPost<SubledgerResponse>(
        "/api/v1/transactions",
        form as SubledgerCreate
      );
      toast.success("Record created successfully");
      setForm(EMPTY_FORM);
      await loadRecords();
    } catch (err) {
      toast.error(`Failed to create: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  }

  // Delete a record by id.
  async function handleDelete(id: number) {
    try {
      await apiDelete(`/api/v1/transactions/${id}`);
      toast.success(`Deleted record ${id}`);
      await loadRecords();
    } catch (err) {
      toast.error(`Failed to delete: ${(err as Error).message}`);
    }
  }

  return (
    <main className="max-w-5xl mx-auto p-8 space-y-8">
      <h1 className="text-2xl font-bold">Subledger — Data Entry</h1>

      {/* Entry Form */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">New Transaction</h2>
        <div className="grid grid-cols-2 gap-4">
          {FIELDS.map((field) => (
            <div key={field} className="space-y-1">
              <Label htmlFor={field}>{field}</Label>
              <Input
                id={field}
                value={form[field]}
                onChange={(e) => handleChange(field, e.target.value)}
                placeholder={field}
              />
            </div>
          ))}
        </div>
        <div className="mt-6">
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Create Record"}
          </Button>
        </div>
      </Card>

      {/* Records Table */}
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">
          Recent Records ({records.length})
        </h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Transaction_ID</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Description</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.id}</TableCell>
                  <TableCell className="max-w-[180px] truncate">
                    {r.Transaction_ID}
                  </TableCell>
                  <TableCell>{r.Amount}</TableCell>
                  <TableCell>{r.Status}</TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {r.Description}
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={() => handleDelete(r.id)}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </Card>
    </main>
  );
}