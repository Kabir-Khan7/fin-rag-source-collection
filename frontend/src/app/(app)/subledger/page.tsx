"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { useActivity } from "@/context/ActivityContext";

import { AppShell } from "@/components/AppShell";
import { apiGet, apiPost, apiDelete } from "@/lib/api";
import type { SubledgerCreate, SubledgerResponse } from "@/types/subledger";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { BulkUpload } from "@/components/BulkUpload";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

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

type FieldName = (typeof FIELDS)[number];
type FormState = Record<FieldName, string>;

const EMPTY_FORM: FormState = FIELDS.reduce(
  (acc, field) => ({ ...acc, [field]: "" }),
  {} as FormState
);

// Helper: is a string a valid number (allows decimals, negatives, commas)?
function isNumeric(value: string): boolean {
  if (value.trim() === "") return false;
  return !isNaN(Number(value.replace(/,/g, "")));
}

export default function SubledgerPage() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<FieldName, string>>>({});
  const [records, setRecords] = useState<SubledgerResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const { logActivity } = useActivity();

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

  function handleChange(field: FieldName, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    // Clear a field's error as the user edits it.
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  // Validate the form. Returns true if valid; sets error messages if not.
  function validate(): boolean {
    const newErrors: Partial<Record<FieldName, string>> = {};

    // Transaction_ID required
    if (form.Transaction_ID.trim() === "") {
      newErrors.Transaction_ID = "Transaction_ID is required";
    }

    // Amount required + numeric
    if (form.Amount.trim() === "") {
      newErrors.Amount = "Amount is required";
    } else if (!isNumeric(form.Amount)) {
      newErrors.Amount = "Amount must be a valid number";
    }

    // GL_Account_Code: if provided, must be numeric
    if (form.GL_Account_Code.trim() !== "" && !isNumeric(form.GL_Account_Code)) {
      newErrors.GL_Account_Code = "GL_Account_Code must be numeric";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) {
      toast.error("Please fix the highlighted fields");
      return;
    }

    setLoading(true);
    try {
      await apiPost<SubledgerResponse>(
        "/api/v1/transactions",
        form as SubledgerCreate
      );
      toast.success("Record created successfully");
      logActivity({
        action: "Delete",
        resource: "Subledger",
        status: "success",
        detail: `Deleted record ${form.Transaction_ID}`,
      });
      setForm(EMPTY_FORM);
      setErrors({});
      await loadRecords();
    } catch (err) {
      toast.error(`Failed to create: ${(err as Error).message}`);
      logActivity({
        action: "Create",
        resource: "Subledger",
        status: "error",
        detail: (err as Error).message,
      });
    } finally {
      setLoading(false);
    }
  }

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
    <AppShell>
    <main className="max-w-5xl mx-auto p-8 space-y-8">
      <h1 className="text-2xl font-bold">Subledger — Data Entry</h1>

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
                className={errors[field] ? "border-red-500" : ""}
              />
              {errors[field] && (
                <p className="text-sm text-red-500">{errors[field]}</p>
              )}
            </div>
          ))}
        </div>
        <div className="mt-6">
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Create Record"}
          </Button>
        </div>
      </Card>
      {/* Bulk Upload */}
      <BulkUpload
        uploadPath="/api/v1/transactions/upload"
        onSuccess={loadRecords}
        expectedColumns={[
          "Transaction_ID", "System_Timestamp", "Document_Date",
          "GL_Account_Code", "Entity_ID", "Amount",
          "Transaction_Type", "Status", "Description",
        ]}
      />

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
    </AppShell>
  );
}