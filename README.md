# Wandora

Wandora is a web application for AI-assisted group travel planning. It provides a shared workspace for destinations, AI itinerary generation & adjustment, manual activities, group collaboration & roles, AI packing & shared luggage planning, place reviews & notes, trip versioning & history, and trip plan export/sharing.

## Repository Layout

```text
.
├── src/backend/   FastAPI application, SQLAlchemy models, Alembic migrations
├── src/frontend/  React + Vite application
├── tests/e2e/     Selenium/Playwright end-to-end tests and page objects
├── tests/backend/ Backend integration test suites
├── scripts/       One-off operational and manual smoke scripts
├── docs/          Architecture, development, testing, and Supabase runbooks
├── pa/            Course assignment artefacts (not application source)
└── backups/       Ignored local backup files; never commit these
```

## Quick Start

1. Copy `.env.example` to `.env`, set database URL, and set `JWT_SECRET_KEY` (at least 32 characters).
2. Install backend dependencies: `pip install -r src/backend/requirements.txt`.
3. Apply schema migrations: `python -m alembic -c src/backend/alembic.ini upgrade heads`.
4. Run the API: `uvicorn --app-dir src/backend main:app --reload --port 8000`.
5. In another terminal, set up the frontend: `cd src/frontend; npm install; npm run dev`.

Verify database access at `GET http://127.0.0.1:8000/health/db`.

## PA5 Automated Testing

The PA5 Selenium suite is in [`tests/e2e`](tests/e2e/README.md). It automates
two implemented use cases with two scenarios each:

- UC01 - Trip Creation and Preference Input
- UC02 - AI Itinerary Generator

Login/sign-up is handled by the pytest fixture because UC01 and UC02 require an
authenticated user. It is setup for the tested flows, not counted as one of the
two PA5 use cases.

Quick run checklist:

1. Start the backend in Terminal 1:

   ```powershell
   .\.venv\Scripts\alembic.exe -c src/backend/alembic.ini upgrade heads
   .\.venv\Scripts\uvicorn.exe --app-dir src/backend main:app --reload --port 8000
   ```

2. Start the frontend in Terminal 2:

   ```powershell
   npm --prefix src/frontend run dev
   ```

3. Run Selenium tests from the repository root in Terminal 3:

   ```powershell
   .\.venv\Scripts\pip.exe install -r tests/e2e/requirements.txt
   .\.venv\Scripts\pytest.exe tests/e2e/tests -v
   ```

For the full PA5 scenario mapping, browser options, screenshots, and port
troubleshooting, read [`tests/e2e/README.md`](tests/e2e/README.md).

## Features Covered (UC 2.1 - UC 2.17)

- **UC 2.1**: Trip Creation and Preference Input
- **UC 2.2**: AI Itinerary Generator
- **UC 2.3**: AI Itinerary Adjustment
- **UC 2.4**: Manual Places and External Links
- **UC 2.5**: Group Collaboration
- **UC 2.6**: Role and Permission Management
- **UC 2.7**: AI Packing Suggestions
- **UC 2.8**: Shared Luggage Planning
- **UC 2.9**: Manual Place Note Input
- **UC 2.10**: Place Ratings and Reviews
- **UC 2.11**: Share or Export Trip Plan
- **UC 2.12**: User Login and Authentication
- **UC 2.13**: Review and save AI Itinerary
- **UC 2.14**: Post-Scheduling Feature Access
- **UC 2.15**: Group Member Interaction (Voting and Comments)
- **UC 2.16**: Duplicate/Similar Trip Detection
- **UC 2.17**: Trip History

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development notes](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Supabase operations](docs/SUPABASE.md)

