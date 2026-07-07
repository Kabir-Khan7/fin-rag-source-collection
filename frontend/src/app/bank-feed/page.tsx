"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";

import { apiGet, apiPost, apiDelete } from "@/lib/api";
import type { BankFeedCreate, BankFeedResponse } from "@/types/bank_feed";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import {
  Table, TableBody, TableCell, TableHead, TableHeader, TableRow,
} from "@/components/ui/table";

const FIELDS = [
  "Bank_Row_ID",
  "Booking_Date",
  "Value_Date",
  "Transaction_Text_Narrative",
  "Amount",
  "Running_Balance",
] as const;

type FieldName = (typeof FIELDS)[number];
type FormState = Record<FieldName, string>;

const EMPTY_FORM: FormState = FIELDS.reduce(
  (acc, f) => ({ ...acc, [f]: "" }), {} as FormState
);

function isNumeric(value: string): boolean {
  if (value.trim() === "") return false;
  return !isNaN(Number(value.replace(/,/g, "")));
}

export default function BankFeedPage() {
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [errors, setErrors] = useState<Partial<Record<FieldName, string>>>({});
  const [records, setRecords] = useState<BankFeedResponse[]>([]);
  const [loading, setLoading] = useState(false);

  async function loadRecords() {
    try {
      const data = await apiGet<BankFeedResponse[]>("/api/v1/bank-feed?skip=0&limit=25");
      setRecords(data);
    } catch (err) {
      toast.error(`Failed to load records: ${(err as Error).message}`);
    }
  }

  useEffect(() => { loadRecords(); }, []);

  function handleChange(field: FieldName, value: string) {
    setForm((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  function validate(): boolean {
    const e: Partial<Record<FieldName, string>> = {};
    if (form.Bank_Row_ID.trim() === "") e.Bank_Row_ID = "Bank_Row_ID is required";
    if (form.Amount.trim() === "") e.Amount = "Amount is required";
    else if (!isNumeric(form.Amount)) e.Amount = "Amount must be a valid number";
    if (form.Running_Balance.trim() !== "" && !isNumeric(form.Running_Balance))
      e.Running_Balance = "Running_Balance must be numeric";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit() {
    if (!validate()) { toast.error("Please fix the highlighted fields"); return; }
    setLoading(true);
    try {
      await apiPost<BankFeedResponse>("/api/v1/bank-feed", form as BankFeedCreate);
      toast.success("Record created successfully");
      setForm(EMPTY_FORM);
      setErrors({});
      await loadRecords();
    } catch (err) {
      toast.error(`Failed to create: ${(err as Error).message}`);
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(id: number) {
    try {
      await apiDelete(`/api/v1/bank-feed/${id}`);
      toast.success(`Deleted record ${id}`);
      await loadRecords();
    } catch (err) {
      toast.error(`Failed to delete: ${(err as Error).message}`);
    }
  }

  return (
    <main className="max-w-5xl mx-auto p-8 space-y-8">
      <h1 className="text-2xl font-bold">Bank Feed — Data Entry</h1>
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">New Bank Feed Record</h2>
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
              {errors[field] && <p className="text-sm text-red-500">{errors[field]}</p>}
            </div>
          ))}
        </div>
        <div className="mt-6">
          <Button onClick={handleSubmit} disabled={loading}>
            {loading ? "Saving..." : "Create Record"}
          </Button>
        </div>
      </Card>
      <Card className="p-6">
        <h2 className="text-lg font-semibold mb-4">Recent Records ({records.length})</h2>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Bank_Row_ID</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Running_Balance</TableHead>
                <TableHead>Booking_Date</TableHead>
                <TableHead>Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {records.map((r) => (
                <TableRow key={r.id}>
                  <TableCell>{r.id}</TableCell>
                  <TableCell className="max-w-[180px] truncate">{r.Bank_Row_ID}</TableCell>
                  <TableCell>{r.Amount}</TableCell>
                  <TableCell>{r.Running_Balance}</TableCell>
                  <TableCell>{r.Booking_Date}</TableCell>
                  <TableCell>
                    <Button variant="destructive" size="sm" onClick={() => handleDelete(r.id)}>
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