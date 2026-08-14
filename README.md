# Wandora

Wandora is a web application for collaborative travel planning. It combines a
React frontend with a FastAPI backend and PostgreSQL database.

## Prerequisites

- Node.js 20 or newer
- Python 3.11 or newer
- A PostgreSQL database (Supabase PostgreSQL is supported)

## Run locally

### 1. Create the backend environment

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r src\backend\requirements.txt
Copy-Item .env.example .env
```

Open `.env` and set these values:

- `DATABASE_URL`: your PostgreSQL connection URI
- `JWT_SECRET_KEY`: a random secret with at least 32 characters
- `GEMINI_API_KEY`: optional; the application remains usable without it

### 2. Prepare the frontend

```powershell
Copy-Item src\frontend\.env.example src\frontend\.env
Set-Location src\frontend
npm.cmd install
Set-Location ../..
```

The default frontend configuration calls the local API at
`http://127.0.0.1:8000`. Change `src/frontend/.env` only when the API is hosted
elsewhere.

### 3. Create or update the database schema

```powershell
.\.venv\Scripts\python.exe -m alembic -c src\backend\alembic.ini upgrade head
```

### 4. Start the application

Open two terminals at the repository root.

Terminal 1 - API:

```powershell
.\.venv\Scripts\python.exe -m uvicorn --app-dir src\backend main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 - web client:

```powershell
Set-Location src\frontend
npm.cmd run dev -- --host 127.0.0.1
```

Open [http://127.0.0.1:5173](http://127.0.0.1:5173) in a browser. The API
health endpoint is available at [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health).

## Verify the project

```powershell
.\.venv\Scripts\python.exe -m pytest tests\backend -q --disable-warnings --tb=short

Set-Location src\frontend
npm.cmd run lint
npm.cmd run build
```

## Repository layout

```text
src/backend/    FastAPI application and database migrations
src/frontend/   React and Vite web application
tests/          Backend and browser test suites
docs/           Architecture and development notes
pa/             Course assignment material
```

## Further documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development notes](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Supabase setup](docs/SUPABASE.md)
