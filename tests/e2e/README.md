# Wandora end-to-end tests

This Selenium suite exercises the two PA4 working flows as a browser user:

- UC01 - Trip Creation and Preference Input
- UC02 - AI Itinerary Generation

It only operates through the UI and never reads the database directly.

## Setup

From the repository root, start the API and Vite frontend, then install the
test dependencies:

```powershell
pip install -r src/backend/requirements.txt
pip install -r tests/e2e/requirements.txt
```

The default frontend URL is `http://127.0.0.1:5173`; set
`WANDORA_BASE_URL` when using another address. The browser tests create data,
so point `DATABASE_URL` to a dedicated Supabase test project.

## Run

```powershell
pytest tests/e2e/tests -v
pytest tests/e2e/tests/test_uc01_trip_creation.py -v
pytest tests/e2e/tests/test_uc02_itinerary_generation.py -v
```

Set `WANDORA_HEADLESS=false` to watch the flows. Failed test screenshots are
saved under `tests/e2e/screenshots/`.
