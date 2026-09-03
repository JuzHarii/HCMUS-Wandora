# Wandora

Wandora is a web application for AI-assisted group travel planning. It includes trip creation, itinerary generation, collaboration, packing, reviews, and trip sharing/export workflows.

## Features

- User authentication with sign-up, sign-in, JWT-based sessions, and protected routes.
- Trip creation with destination, travel dates, group capacity, budget, and preference input.
- AI-assisted itinerary generation with deterministic fallback behavior for local/testing environments.
- Itinerary review and saving before opening the full trip workspace.
- Trip workspace features including itinerary management, members, packing, reviews, and sharing.
- Group collaboration support with member roles and trip access control.
- Trip plan sharing/export support for submitting or distributing travel plans.
- Selenium end-to-end automated tests for PA5 UC01 and UC02 scenarios.

## Repository Layout

```text
.
├── src/backend/   FastAPI application, SQLAlchemy models, Alembic migrations
├── src/frontend/  React + Vite application
├── tests/e2e/     Selenium end-to-end tests and page objects
├── tests/         Test suites and test support files
├── pa/            Course assignment artifacts
├── archive/docs/  Legacy documentation kept for reference only
└── backups/       Ignored local backup files; never commit these
```

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer
- Git
- Chrome or Microsoft Edge for Selenium E2E tests
- A development database. SQLite is enough for local testing; Supabase/PostgreSQL can also be used through `DATABASE_URL`.

The commands below are written for Windows PowerShell because the PA5 test workflow was prepared on Windows.

## Clone The Repository

```powershell
git clone https://github.com/JuzHarii/HCMUS-Wandora.git
cd HCMUS-Wandora
```

Run all following commands from the repository root unless a section says otherwise.

## Create And Activate Python Virtual Environment

Create `.venv` once:

```powershell
py -3.11 -m venv .venv
```

If `py -3.11` is not available, use:

```powershell
python -m venv .venv
```

Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

After activation, your prompt should start with `(.venv)`. All Python commands below assume the virtual environment is active.

If PowerShell blocks activation, run this once in the same terminal:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then run `.\.venv\Scripts\Activate.ps1` again.

## Configure Environment Variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

For the simplest local run, set this value in `.env`:

```env
DATABASE_URL=sqlite:///./wandora.db
```

If you use Supabase/PostgreSQL instead, replace the placeholder `DATABASE_URL` from `.env.example` with your real database connection string before running migrations.

Also set `JWT_SECRET_KEY` to any random string with at least 32 characters for local development. Do not commit real secrets.

## Install Dependencies

With `(.venv)` active:

```powershell
python -m pip install --upgrade pip
python -m pip install -r src/backend/requirements.txt
python -m pip install -r tests/e2e/requirements.txt
npm --prefix src/frontend install
```

## Run The App Locally

Use two PowerShell terminals and keep both running. Activate `.venv` in any terminal that runs backend Python commands.

### Terminal 1 - Backend

```powershell
cd HCMUS-Wandora
.\.venv\Scripts\Activate.ps1
python -m alembic -c src/backend/alembic.ini upgrade heads
python -m uvicorn --app-dir src/backend main:app --reload --port 8000
```

The backend is ready when the terminal shows:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:8000
```

Useful backend URLs:

- API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`
- Database health check: `http://127.0.0.1:8000/health/db`

### Terminal 2 - Frontend

```powershell
cd HCMUS-Wandora
npm --prefix src/frontend run dev
```

Open the Vite local URL shown in the terminal, usually:

```text
http://localhost:5173/
```

If Vite starts on another port, use that exact URL in the browser and in Selenium through `WANDORA_BASE_URL`.

## PA5 Automated Testing

The PA5 Selenium suite is documented in [tests/e2e/README.md](tests/e2e/README.md).

It covers the assignment requirement of at least two use cases with two scenarios each:

- UC01 - Trip Creation and Preference Input
- UC02 - AI Itinerary Generator

Login/sign-up is handled by pytest fixtures because UC01 and UC02 require an authenticated user. Authentication is a test precondition, not one of the two PA5 use cases being counted.

After Terminal 1 and Terminal 2 are running, open Terminal 3:

```powershell
cd HCMUS-Wandora
.\.venv\Scripts\Activate.ps1
python -m pytest tests/e2e/tests -v
```

Expected result:

```text
6 passed
```

Failed Selenium screenshots are saved under `tests/e2e/screenshots/`.

## Troubleshooting

- If Alembic reports multiple heads, use `upgrade heads`, not `upgrade head`.
- If Selenium reports `net::ERR_CONNECTION_REFUSED`, the frontend URL is not reachable. Confirm the Vite URL in Terminal 2 and set `$env:WANDORA_BASE_URL` if the port is not `5173`.
- If the browser opens and closes immediately, check the pytest failure message first. This usually means Selenium reached the browser but the app URL, backend, or test precondition failed.
- If Selenium cannot find a driver, install/update Chrome or Edge. Selenium Manager downloads a matching driver automatically when the machine has internet access.
