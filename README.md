# HCMUS Wandora

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
3. Apply schema migrations: `python -m alembic -c src/backend/alembic.ini upgrade head`.
4. Run the API: `uvicorn --app-dir src/backend main:app --reload --port 8000`.
5. In another terminal, set up the frontend: `cd src/frontend; npm install; npm run dev`.

Verify database access at `GET http://127.0.0.1:8000/health/db`.

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
- [Development workflow](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Supabase operations](docs/SUPABASE.md)

