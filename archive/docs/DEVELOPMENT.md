# Development workflow

## Prerequisites

- Python 3.11 or later
- Node.js 20 or later
- A Supabase project and a root `.env` based on `.env.example`, including a
  random `JWT_SECRET_KEY` of at least 32 characters

## Run locally

```powershell
pip install -r src/backend/requirements.txt
python -m alembic -c src/backend/alembic.ini upgrade head
uvicorn --app-dir src/backend main:app --reload
```

In a second terminal:

```powershell
cd src/frontend
npm install
npm run dev
```

The API is available at `http://127.0.0.1:8000`; its OpenAPI interface is at
`/docs`. Confirm database availability through `/health/db`.

Open the frontend, select **Sign in**, then choose **Create account**. A
session is saved in the browser and ordinary sign-in opens the **My trips**
dashboard at `/home`. `/` is always the public landing page. Protected trip
routes redirect unauthenticated visitors to the login page and preserve a
requested trip-creation link. To test a separate account, use **Sign out** first.

## Change workflow

1. Keep domain logic inside `src/backend/app/services`, route handling inside
   `src/backend/app/api`, and transport models inside `src/backend/app/schemas`.
2. Make database-model changes in `src/backend/app/models`.
3. Generate and review an Alembic migration before changing deployed schema.
4. Keep frontend-only code in `src/frontend/src`; do not import backend files into
   the Vite project.
5. Run the relevant checks from [Testing](TESTING.md) before committing.

## Operational scripts

`scripts/` is for explicit, manually run tasks. `smoke_api_flow.py` writes
test data using the configured database, so do not run it against production.
