"""
Code-level API smoke test for the Local RAG System — Source Collection backend.

Runs the FastAPI app in-process using Starlette's TestClient and exercises
every endpoint (health, CRUD for all five tables, bulk, and file upload),
verifying each returns the expected HTTP status. Any test record it creates
is deleted again at the end, so it cleans up after itself.

This is a smoke test focused on the CODE layer: it confirms routing, request
validation, serialization, and the service/repository wiring all work
end-to-end. It talks to whatever database your app is configured to use, so
run it against a database you're comfortable writing to.

Usage (from the project root, with your virtual environment active):

    python run_api_tests.py

Requires: httpx (TestClient dependency). If not present:

    uv add --dev httpx
    # or: pip install httpx
"""

from __future__ import annotations

import io
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# ANSI colors for readable output.
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Counters and cleanup registry.
passed = 0
failed = 0
# Track created records so we can delete them: list of (route_prefix, id).
created_records: list[tuple[str, int]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    """Record and print the result of a single assertion."""
    global passed, failed
    if condition:
        passed += 1
        print(f"{GREEN}PASS{RESET}  {name}")
    else:
        failed += 1
        print(f"{RED}FAIL{RESET}  {name}" + (f"  ->  {detail}" if detail else ""))


def section(title: str) -> None:
    """Print a section header."""
    print(f"\n{YELLOW}== {title} =={RESET}")


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
def test_health() -> None:
    section("Health")

    r = client.get("/health")
    check("GET /health returns 200", r.status_code == 200, str(r.status_code))
    check(
        "GET /health status ok",
        r.json().get("status") == "ok",
        r.text,
    )

    r = client.get("/health/ready")
    check(
        "GET /health/ready returns 200 (DB reachable)",
        r.status_code == 200,
        f"{r.status_code} {r.text}",
    )


# ---------------------------------------------------------------------------
# Generic CRUD test, reused for every table
# ---------------------------------------------------------------------------
def run_crud_suite(
    label: str,
    prefix: str,
    create_payload: dict,
    update_payload: dict,
    update_field: str,
    update_value: str,
) -> None:
    """
    Exercise the full CRUD cycle for one table.

    Args:
        label: Human-readable table name for output.
        prefix: Route prefix, e.g. "/api/v1/transactions".
        create_payload: A valid record body for POST.
        update_payload: A body for PUT.
        update_field: A field expected to change after update.
        update_value: The value it should hold after update.
    """
    section(f"CRUD — {label}")

    # CREATE
    r = client.post(prefix, json=create_payload)
    check(f"[{label}] POST returns 201", r.status_code == 201, f"{r.status_code} {r.text}")
    if r.status_code != 201:
        return
    record = r.json()
    record_id = record.get("id")
    check(f"[{label}] POST returns an id", isinstance(record_id, int), str(record))
    if not isinstance(record_id, int):
        return
    created_records.append((prefix, record_id))

    # READ (list)
    r = client.get(prefix)
    check(f"[{label}] GET list returns 200", r.status_code == 200, str(r.status_code))
    check(f"[{label}] GET list returns a list", isinstance(r.json(), list), r.text[:200])

    # READ (by id)
    r = client.get(f"{prefix}/{record_id}")
    check(f"[{label}] GET by id returns 200", r.status_code == 200, str(r.status_code))
    check(
        f"[{label}] GET by id returns matching id",
        r.json().get("id") == record_id,
        r.text[:200],
    )

    # READ (missing id -> 404)
    r = client.get(f"{prefix}/999999999")
    check(f"[{label}] GET missing id returns 404", r.status_code == 404, str(r.status_code))

    # UPDATE
    r = client.put(f"{prefix}/{record_id}", json=update_payload)
    check(f"[{label}] PUT returns 200", r.status_code == 200, f"{r.status_code} {r.text}")
    if r.status_code == 200:
        check(
            f"[{label}] PUT changed the field",
            r.json().get(update_field) == update_value,
            r.text[:200],
        )

    # UPDATE (missing id -> 404)
    r = client.put(f"{prefix}/999999999", json=update_payload)
    check(f"[{label}] PUT missing id returns 404", r.status_code == 404, str(r.status_code))

    # DELETE (missing id -> 404)
    r = client.delete(f"{prefix}/999999999")
    check(f"[{label}] DELETE missing id returns 404", r.status_code == 404, str(r.status_code))

    # Pagination edge case (the bug we fixed): high skip -> empty list, not 503
    r = client.get(f"{prefix}?skip=999999&limit=10")
    check(
        f"[{label}] high skip returns 200 (not 503)",
        r.status_code == 200,
        f"{r.status_code} {r.text[:120]}",
    )


# ---------------------------------------------------------------------------
# Validation error (shared shape check on subledger)
# ---------------------------------------------------------------------------
def test_validation_error() -> None:
    section("Validation")
    # Amount must be a string; sending a number should 422.
    r = client.post("/api/v1/transactions", json={"Amount": 123})
    check(
        "POST invalid type returns 422",
        r.status_code == 422,
        f"{r.status_code} {r.text[:120]}",
    )
    check(
        "422 body carries error_type",
        r.json().get("error_type") == "validation_error",
        r.text[:200],
    )


# ---------------------------------------------------------------------------
# Bulk + file upload (subledger and bank_feed)
# ---------------------------------------------------------------------------
def run_bulk_and_upload(
    label: str,
    prefix: str,
    bulk_payload: list[dict],
    csv_text: str,
) -> None:
    """Exercise the /bulk and /upload endpoints for a table."""
    section(f"Bulk & Upload — {label}")

    # BULK JSON
    r = client.post(f"{prefix}/bulk", json=bulk_payload)
    check(f"[{label}] POST /bulk returns 201", r.status_code == 201, f"{r.status_code} {r.text}")
    if r.status_code == 201:
        check(
            f"[{label}] /bulk inserted expected count",
            r.json().get("inserted_count") == len(bulk_payload),
            r.text[:200],
        )

    # CSV UPLOAD
    files = {"file": ("test_upload.csv", io.BytesIO(csv_text.encode("utf-8")), "text/csv")}
    r = client.post(f"{prefix}/upload", files=files)
    check(f"[{label}] POST /upload (csv) returns 201", r.status_code == 201, f"{r.status_code} {r.text}")

    # BAD FILE TYPE -> 400
    bad = {"file": ("test.txt", io.BytesIO(b"not a spreadsheet"), "text/plain")}
    r = client.post(f"{prefix}/upload", files=bad)
    check(
        f"[{label}] /upload bad extension returns 400",
        r.status_code == 400,
        f"{r.status_code} {r.text[:120]}",
    )


# ---------------------------------------------------------------------------
# Cleanup
# ---------------------------------------------------------------------------
def cleanup() -> None:
    """Delete every record this script created."""
    section("Cleanup")
    remaining = 0
    for prefix, record_id in created_records:
        r = client.delete(f"{prefix}/{record_id}")
        if r.status_code not in (204, 404):
            remaining += 1
            print(f"{RED}  could not delete {prefix}/{record_id}: {r.status_code}{RESET}")
    check(
        "single-record test rows cleaned up",
        remaining == 0,
        f"{remaining} not deleted",
    )
    print(
        f"{YELLOW}  Note: rows created via /bulk and /upload are NOT auto-deleted "
        f"(they have known test prefixes — remove them in SSMS if desired).{RESET}"
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running code-level API smoke tests...\n")

    test_health()

    run_crud_suite(
        label="subledger",
        prefix="/api/v1/transactions",
        create_payload={
            "Transaction_ID": "TEST-CRUD-001",
            "Amount": "100.00",
            "Status": "Posted",
            "Description": "smoke test",
        },
        update_payload={"Status": "Updated"},
        update_field="Status",
        update_value="Updated",
    )

    run_crud_suite(
        label="bank_feed",
        prefix="/api/v1/bank-feed",
        create_payload={
            "Bank_Row_ID": "TEST-BF-001",
            "Amount": "500.00",
            "Running_Balance": "1500.00",
        },
        update_payload={"Amount": "999.00"},
        update_field="Amount",
        update_value="999.00",
    )

    run_crud_suite(
        label="chart_of_accounts",
        prefix="/api/v1/chart-of-accounts",
        create_payload={
            "GL_Account_Code": "TEST-9000",
            "Account_Name": "Test Account",
            "Account_Class": "Asset",
            "Financial_Statement_Section": "Balance Sheet",
        },
        update_payload={"Account_Name": "Updated Account"},
        update_field="Account_Name",
        update_value="Updated Account",
    )

    run_crud_suite(
        label="master_directory",
        prefix="/api/v1/master-directory",
        create_payload={
            "Entity_ID": "TEST-ENT-001",
            "Legal_Name": "Test Corp",
            "Country_Code": "PK",
            "Is_Active": "true",
        },
        update_payload={"Legal_Name": "Updated Corp"},
        update_field="Legal_Name",
        update_value="Updated Corp",
    )

    run_crud_suite(
        label="raw_invoices",
        prefix="/api/v1/raw-invoices",
        create_payload={
            "Vendor_ID": "TEST-VEND-001",
            "Vendor_Name": "Test Vendor",
            "Invoice_Number": "TEST-INV-001",
            "Grand_Total": "250.00",
        },
        update_payload={"Vendor_Name": "Updated Vendor"},
        update_field="Vendor_Name",
        update_value="Updated Vendor",
    )

    test_validation_error()

    run_bulk_and_upload(
        label="subledger",
        prefix="/api/v1/transactions",
        bulk_payload=[
            {"Transaction_ID": "TEST-BULK-001", "Amount": "10.00", "Status": "Posted"},
            {"Transaction_ID": "TEST-BULK-002", "Amount": "20.00", "Status": "Draft"},
        ],
        csv_text=(
            "Transaction_ID,Amount,Status,Description\n"
            "TEST-CSV-001,30.00,Posted,csv row one\n"
            "TEST-CSV-002,40.00,Draft,csv row two\n"
        ),
    )

    run_bulk_and_upload(
        label="bank_feed",
        prefix="/api/v1/bank-feed",
        bulk_payload=[
            {"Bank_Row_ID": "TEST-BF-BULK-001", "Amount": "100.00", "Running_Balance": "1100.00"},
            {"Bank_Row_ID": "TEST-BF-BULK-002", "Amount": "200.00", "Running_Balance": "1300.00"},
        ],
        csv_text=(
            "Bank_Row_ID,Booking_Date,Value_Date,Transaction_Text_Narrative,Amount,Running_Balance\n"
            "TEST-BF-CSV-001,2026-07-07,2026-07-07,csv deposit,300.00,1600.00\n"
        ),
    )

    cleanup()

    # Summary
    print(f"\n{YELLOW}=================== SUMMARY ==================={RESET}")
    print(f"{GREEN}PASSED: {passed}{RESET}")
    print(f"{RED}FAILED: {failed}{RESET}")
    total = passed + failed
    print(f"TOTAL:  {total}")

    if failed == 0:
        print(f"\n{GREEN}All code-level checks passed.{RESET}")
        sys.exit(0)
    else:
        print(f"\n{RED}Some checks failed — see above.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()