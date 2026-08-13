# HCMUS Wandora

Wandora is a web application for AI-assisted group travel planning. It provides
a shared workspace for destinations, itinerary drafts, activities, notes, and
packing preparation.

## Repository layout

```text
.
├── src/backend/   FastAPI application, SQLAlchemy models, Alembic migrations
├── src/frontend/  React + Vite application
├── tests/e2e/     Selenium end-to-end tests and page objects
├── scripts/       One-off operational and manual smoke scripts
├── docs/          Architecture, development, testing, and Supabase runbooks
├── pa/            Course assignment artefacts (not application source)
└── backups/       Ignored local backup files; never commit these
```

## Quick start

1. Copy `.env.example` to `.env`, set the Supabase `DATABASE_URL`, and set a
   random `JWT_SECRET_KEY` (at least 32 characters).
2. Install backend dependencies: `pip install -r src/backend/requirements.txt`.
3. Apply schema migrations: `python -m alembic -c src/backend/alembic.ini upgrade head`.
4. Run the API: `uvicorn --app-dir src/backend main:app --reload`.
5. In another terminal, copy `src/frontend/.env.example` to `src/frontend/.env`, then run `cd src/frontend; npm install; npm run dev`.

Verify database access at `GET http://127.0.0.1:8000/health/db`.

## PA4 working flows

Open `http://127.0.0.1:5173` for the public landing page. After sign-in, the
app opens **My trips** at `/home`, where private workspaces are listed. Use
**New trip** to begin planning; a landing-page CTA still takes a signed-in user
directly to the creation flow. Accounts are stored in the application's `users` table on
Supabase PostgreSQL; passwords are Argon2 hashes and the browser receives a
signed bearer session token, never the database credentials. The landing
page leads to the two implemented PA4 use cases:

- **UC01 - Trip Creation and Preference Input:** submit destination, dates,
  group size, budget, travel style, and optional notes. Invalid dates and
  invalid numeric values are rejected in the UI and API.
- **UC02 - AI Itinerary Generation:** review a temporary AI draft before the
  trip is stored in Supabase. The user can edit or regenerate it, then save the
  accepted itinerary. Manual activities survive later regeneration; the previous
  itinerary is saved as a restore point in **History** (the latest 10 versions
  are retained).

Gemini is optional: if `GEMINI_API_KEY` is unset, times out, or returns an
invalid response, Wandora uses a deterministic itinerary fallback so the demo
remains runnable. UC02 clearly labels the saved itinerary as Gemini-generated,
fallback, blank, or restored; `GEMINI_TIMEOUT_SECONDS` defaults to 25 seconds.

## Accounts and access

- `POST /api/v1/auth/signup` creates an account and returns a bearer session.
- `POST /api/v1/auth/login` starts a session for an existing account.
- `GET /api/v1/auth/me` returns the authenticated account.
- Trip and itinerary endpoints require a bearer token and only allow members of
  the corresponding workspace. A newly created trip is owned by its creator.

This is application-managed JWT authentication backed by Supabase PostgreSQL;
it does not require a Supabase Auth project key.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Development workflow](docs/DEVELOPMENT.md)
- [Testing](docs/TESTING.md)
- [Supabase operations](docs/SUPABASE.md)
