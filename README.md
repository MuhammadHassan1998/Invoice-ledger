# Invoice Ledger

Invoice Ledger is a small, self-contained walking skeleton for showing processed invoices from a local data pipeline.

The goal of this project is not to build a huge invoice system. It is to show the shape of a maintainable vertical slice: mock data comes in, dbt turns it into a clean mart, FastAPI exposes that mart through a strict versioned contract, and React displays the result with matching TypeScript types.

The stack is:
- dbt with DuckDB for the data layer
- FastAPI with Pydantic for the backend contract
- React with TypeScript for the frontend

## What This Demonstrates

This project includes the pieces requested in the assessment:

- Mock invoice data generated locally in `backend/dbt/seeds/raw_invoices.csv`
- A dbt project with staging, intermediate, and marts layers
- A stable invoice mart named `main_marts.mart_invoices`
- A versioned API endpoint at `/api/v1/invoices`
- Username/password registration and login
- Pydantic models that strictly validate the response leaving the backend
- React/TypeScript code that consumes the same response shape
- Docker Compose and a local setup script for running the whole stack
- A design that keeps dbt-owned data separate from FastAPI-owned side effects

## Running The Project

You can run the project either with Docker Compose or directly on your machine.

For local development, you need:
- Python 3.12
- Node.js 18 or newer

The quickest local path is:

```bash
chmod +x setup.sh
./setup.sh
```

That script creates the local data directory, installs the Python dependencies, runs dbt, starts FastAPI, installs frontend dependencies, and starts Vite.

After it starts, the app is available here:

- Frontend: http://localhost:5173
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

You can also run everything with Docker:

```bash
docker compose up --build
```

Docker exposes:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

In Docker, the `dbt-runner` service runs first. It seeds the invoice CSV and builds the DuckDB mart. The backend only starts after dbt completes successfully, so the API is not trying to serve a half-built warehouse.

## Manual Commands

If you want to run each layer yourself, start with dbt:

```bash
cd backend/dbt
DBT_DUCKDB_PATH=../data/invoice_ledger.duckdb ../../.venv/bin/dbt seed --profiles-dir .
DBT_DUCKDB_PATH=../data/invoice_ledger.duckdb ../../.venv/bin/dbt run --profiles-dir .
DBT_DUCKDB_PATH=../data/invoice_ledger.duckdb ../../.venv/bin/dbt test --profiles-dir .
```

Then start the backend:

```bash
cd backend
DUCKDB_PATH=./data/invoice_ledger.duckdb ../.venv/bin/uvicorn main:app --reload --port 8000
```

Then start the frontend:

```bash
cd frontend
npm install
npm run dev
```

To check the production frontend build:

```bash
cd frontend
npm run build
```

## API

Authentication endpoints:

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
```

Both endpoints accept only a username and password:

```json
{
  "username": "muhammad",
  "password": "password123"
}
```

On success, the backend returns a bearer token and the public user record. The React app stores that session in local storage and sends the token with invoice requests.

The main endpoint is:

```http
GET /api/v1/invoices
```

It supports:

- `page`: positive integer, default `1`
- `page_size`: positive integer up to `200`, default `20`
- `status`: one of `draft`, `sent`, `paid`, `overdue`, `cancelled`

There are also two invoice-specific endpoints:

- `GET /api/v1/invoices/{invoice_id}/pdf`
- `GET /api/v1/invoices/{invoice_id}/exports`

The invoice endpoints require a bearer token from login or registration.

The list endpoint returns an `InvoiceListResponse` Pydantic model. Each invoice row is validated against the `Invoice` schema before it leaves the API. The models use `extra="forbid"`, so if the mart starts returning unexpected fields, the backend fails loudly instead of quietly changing the contract.

The frontend mirrors this shape in `frontend/src/types/invoice.ts`. That keeps the React side honest: if the API contract changes, the TypeScript type needs to change with it.

## Data Pipeline

The dbt project lives in `backend/dbt`.

The pipeline is intentionally simple:

```text
raw_invoices.csv -> staging -> intermediate -> mart
```

The staging layer is a clean projection of the raw CSV. It renames fields, casts values, and gives the rest of the project a predictable starting point.

The intermediate layer is where invoice business logic lives. This is where fields like `is_overdue`, `days_overdue`, and `collected_amount` are calculated. I kept that logic in dbt because these rules describe the data itself, not how an HTTP endpoint or a UI component should behave.

The marts layer is the API-facing data contract. `mart_invoices` selects only the columns that the backend is allowed to serve. That means adding a helper column upstream does not accidentally expose it to API consumers.

The mart is materialized as a table, so API reads are simple and fast. FastAPI does not rebuild transformations during requests.

## Backend Design

FastAPI is intentionally thin in this project. It reads from the dbt mart, validates the result with Pydantic, and returns a versioned response under `/api/v1`.

Authentication is also owned by FastAPI. Users register and log in with a username and password only. Passwords are stored in SQLite as salted PBKDF2 hashes, and the API returns a signed bearer token for authenticated requests.

DuckDB is opened in read-only mode from the API. That is an important boundary: dbt owns the analytical database, and FastAPI cannot mutate it by accident.

There is one separate write path: PDF export audit records. Those are stored in SQLite, which is owned by the backend. I kept that separate because export history is application behavior, not analytical transformation output.

Alembic runs the SQLite migration on backend startup, so the audit table is ready before the PDF/export endpoints need it.

## Frontend Design

The frontend does not contain invoice business logic. Its job is to fetch the API response and present it clearly.

The main pieces are:

- `src/api/auth.ts` for login and registration
- `src/hooks/useAuth.ts` for session storage
- `src/api/invoices.ts` for API calls
- `src/hooks/useInvoices.ts` for loading and error state
- `src/types/invoice.ts` for the TypeScript contract
- `src/components/InvoiceTable.tsx` for rendering the invoice list

For example, React does not decide whether an invoice is overdue. dbt calculates that, FastAPI validates it, and the UI only displays it.

## Why The Boundaries Are Drawn This Way

I split the work by ownership.

dbt owns transformations because overdue rules, collected amounts, and mart shape are data concerns. They should be testable without starting the API or clicking through the UI.

FastAPI owns the service contract. It gives consumers a stable `/api/v1` surface and uses Pydantic to make sure the data leaving the service matches the documented shape.

FastAPI also owns authentication because credentials and tokens are application concerns. dbt should not know who is logged in, and React should not validate passwords.

React owns presentation. It should be able to trust the API response and focus on rendering, filtering, pagination controls, loading states, and error states.

SQLite owns operational audit data. PDF export logs are useful application records, but they do not belong in the dbt mart.

This keeps the code easier to review. A dbt change is reviewed as a data contract change. A Pydantic change is reviewed as an API contract change. A React change is reviewed as a UI change.

## Idempotency And Side Effects

The data build is repeatable. `dbt seed` loads deterministic mock data, and `dbt run` rebuilds the models from declared dependencies. Running those commands again should produce the same mart for the same input data.

The API avoids hidden side effects by opening DuckDB with `read_only=True`. A request to list invoices cannot change the analytical store.

The mart exposes an explicit column list rather than `select *` from the final API-facing model. That makes contract changes deliberate.

The only application write is the PDF export audit record, and that goes to SQLite. This gives the backend a place to store operational behavior without mixing it into the analytics database.

User registration is also an application write and is stored in SQLite. It does not touch DuckDB or the dbt mart.

Alembic migrations are also scoped to SQLite. They do not touch DuckDB or dbt-managed data.

## Project Structure

```text
invoice-ledger/
|-- backend/
|   |-- alembic/
|   |   `-- versions/001_create_invoice_exports.py
|   |-- alembic.ini
|   |-- dbt/
|   |   |-- profiles.yml
|   |   |-- dbt_project.yml
|   |   |-- seeds/raw_invoices.csv
|   |   `-- models/
|   |       |-- staging/
|   |       |-- intermediate/
|   |       `-- marts/
|   |-- app/
|   |   |-- database.py
|   |   |-- db.py
|   |   |-- models/
|   |   |-- schemas/invoice.py
|   |   |-- services/pdf.py
|   |   `-- routers/v1/invoices.py
|   |-- data/
|   |-- main.py
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- types/invoice.ts
|   |   |-- api/invoices.ts
|   |   |-- hooks/useInvoices.ts
|   |   |-- components/
|   |   `-- App.tsx
|   |-- package.json
|   `-- vite.config.ts
|-- docker-compose.yml
|-- setup.sh
`-- README.md
```

## Repository

Public GitHub repository: https://github.com/MuhammadHassan1998/Invoice-ledger
