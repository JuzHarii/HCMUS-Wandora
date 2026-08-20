# HCMUS Wandora

Wandora is a web application for AI-assisted group travel planning. The project helps users create trips, collaborate with invited members, generate itinerary suggestions, manage day-by-day activities, handle AI packing suggestions & shared luggage planning, rate places, and export or share trip plans.

## Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic v2
- **Database**: SQLite (default dev / testing) / PostgreSQL compatible via SQLAlchemy & Alembic
- **AI Integration**: Google Gemini API (`gemini-1.5-flash`) via `httpx` async client with deterministic fallback generator
- **Migration & Testing**: Alembic, Pytest

## Project Structure

```text
.
├── docs/                 Project documents and planning materials
├── pa/                   Course assignment submissions and references
└── src/
    ├── backend/          FastAPI backend application & tests
    └── frontend/         React + Vite frontend application
```

## Backend Setup & Runbook

Navigate to backend directory:

```bash
cd src/backend
```

Install dependencies (or use virtual environment):

```bash
pip install -r requirements.txt
```

Run database migrations:

```bash
alembic upgrade head
```

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload --port 8000
```

Run full automated test suite:

```bash
pytest -v
```

Interactive API documentation:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

## Frontend Setup

Navigate to frontend directory:

```bash
cd src/frontend
```

Install dependencies & start server:

```bash
npm install
npm run dev
```

## Current Status

- **Backend (Complete)**: Fully implemented under `src/backend` covering PA3 Use-Cases 2.1 through 2.11 (Workspace creation, AI itinerary generator & adjustment, manual activities, group collaboration & roles, AI packing & shared luggage planning, place reviews & notes, trip sharing & JSON/Markdown export). All 11 integration test suites pass (100% test pass rate).
- **Frontend**: Initialized with React, Vite, and TypeScript.
