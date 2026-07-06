# Local RAG System — Source Collection Backend

Phase 1 of a Local RAG system: a FastAPI backend that connects to a local
Microsoft SQL Server and exposes CRUD APIs for ingesting raw financial data
into the **Bronze (staging)** layer of a Medallion architecture.

## Overview

This service is the ingestion layer. It accepts raw records and writes them,
as-is, into the `stg_*` staging tables. Type conversion, cleaning, and
transformation into the Silver/Gold layers are handled separately inside SQL
Server (stored procedures) and are out of scope for this backend.

## Tech Stack

- Python 3.13+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- pyodbc (ODBC Driver 17 for SQL Server)
- Uvicorn
- uv (environment & dependency management)

## Staging Tables Covered

| Resource          | Table                       | Route prefix          |
|-------------------|-----------------------------|-----------------------|
| Subledger         | `dbo.stg_subledger`         | `/api/v1/transactions`      |
| Bank Feed         | `dbo.stg_bank_feed`         | `/api/v1/bank-feed`         |
| Chart of Accounts | `dbo.stg_chart_of_accounts` | `/api/v1/chart-of-accounts` |
| Master Directory  | `dbo.stg_master_directory`  | `/api/v1/master-directory`  |
| Raw Invoices      | `dbo.stg_raw_invoices`      | `/api/v1/raw-invoices`      |

Each resource supports full CRUD (POST, GET list, GET by id, PUT, DELETE).

## Project Structure

```
local_rag_system/
├── app/
│   ├── api/v1/          # Endpoints and router
│   ├── core/            # Configuration (settings)
│   ├── database/        # Engine, session, base
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response schemas
│   ├── repositories/    # Data access layer
│   ├── services/        # Business logic layer
│   └── main.py          # FastAPI app entry point
├── tests/
├── .env                 # Local secrets (not committed)
├── .env.example
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Setup

### 1. Prerequisites
- Python 3.13+
- Microsoft SQL Server (local) with the `fin_model` database
- ODBC Driver 17 for SQL Server
- [uv](https://github.com/astral-sh/uv)

### 2. Install dependencies
```bash
uv venv
.venv\Scripts\activate        # Windows
uv pip install -r requirements.txt
```

### 3. Configure environment
Copy `.env.example` to `.env` and set your values:
```env
DB_SERVER=YOUR_SERVER\SQLEXPRESS
DB_NAME=fin_model
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_TRUSTED_CONNECTION=yes
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, interactive docs are available at:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## Notes

- All staging columns are stored as raw strings, matching the Bronze layer.
- Each staging table has a surrogate `id` (auto-increment) primary key for
  safe row-level operations.
- Data validation and typing are intentionally deferred to the SQL
  transformation layer.

## Roadmap

- [ ] Logging and global error handling
- [ ] Test suite (pytest)
- [ ] Bulk / Excel file upload ingestion
- [ ] Frontend portal
- [ ] Embeddings + vector store + retrieval (later RAG phases)