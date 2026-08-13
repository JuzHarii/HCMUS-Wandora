# Testing

## Backend checks

```powershell
python -m compileall src/backend scripts
python -m alembic -c src/backend/alembic.ini check
```

`alembic check` compares SQLAlchemy metadata with the configured Supabase
schema and reports migration drift.

## Authentication and PA4 API smoke flow

After applying migrations, run the API-level Supabase check:

```powershell
python scripts/smoke_api_flow.py
```

It signs up and logs in a unique account, verifies the protected `/auth/me`
endpoint, confirms an unauthenticated workspace request is rejected, then
creates a uniquely named workspace, generates and reloads an itinerary, and
verifies that the API rejects an invalid date range. The backend unit suite also
checks that a temporary AI preview is not persisted until it is accepted, that
regenerating preserves manual activities, and that a saved itinerary version can
be restored.

## End-to-end tests

The browser tests cover PA4's UC01 and UC02. Start the frontend and API first,
then:

```powershell
pip install -r src/backend/requirements.txt
pip install -r tests/e2e/requirements.txt
pytest tests/e2e/tests -v
```

They use `WANDORA_BASE_URL` from `tests/e2e/config.py` (default:
`http://127.0.0.1:5173`). The suite verifies protected-route redirection, the
**My trips** default destination after sign-up/sign-in, and the UI
sign-up/sign-out/sign-in cycle. It also verifies a newly created trip appears
on that dashboard. The UC01/UC02 tests create a unique account through the
sign-up UI, so use a dedicated test Supabase project rather than production.

## Manual smoke flow

The smoke flow and E2E suite may invoke the AI service, but fallback itinerary
generation keeps both UC01 and UC02 testable without a Gemini API key.
