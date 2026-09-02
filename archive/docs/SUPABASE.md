# Supabase operations

Supabase is Wandora's managed PostgreSQL database. The browser must never
receive the database password; it talks only to FastAPI.

## Runtime configuration

Copy `.env.example` to `.env` in the repository root and set the Session
pooler URI copied from Supabase **Connect**. Password characters such as `@`
must be URL-encoded.

```dotenv
DATABASE_URL=postgresql+psycopg://postgres.[PROJECT-REF]:[PASSWORD]@aws-[REGION].pooler.supabase.com:5432/postgres?sslmode=require
DB_POOL_MODE=session
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=5
JWT_SECRET_KEY=generate-a-random-secret-of-at-least-32-characters
```

Use Session pooling for the long-running FastAPI service. For a serverless
deployment, select Transaction pooling (port `6543`) and set
`DB_POOL_MODE=transaction`.

## Schema migrations

Alembic is the only schema-migration mechanism. The API never creates or
changes tables at startup.

```powershell
pip install -r src/backend/requirements.txt
python -m alembic -c src/backend/alembic.ini upgrade head
python -m alembic -c src/backend/alembic.ini current
```

The existing Supabase project has been baselined at revision `36c21682e487`.
For each schema change, change the model, generate/review a migration, then
apply it:

```powershell
python -m alembic -c src/backend/alembic.ini revision --autogenerate -m "describe_change"
python -m alembic -c src/backend/alembic.ini upgrade head
python -m alembic -c src/backend/alembic.ini check
```

Run migrations in CI/deployment before starting the API. Review generated SQL
before committing it; `downgrade` can destructively remove production data.

## Historical SQLite import

The one-time import was completed and verified. The original SQLite file now
lives under ignored `backups/` outside version control. To import another
**empty** Supabase project, first apply Alembic migrations, then run:

```powershell
python scripts/migrate_sqlite_to_supabase.py --source path\to\wandora.db
```

The script refuses to write into any Wandora table that already contains rows.

## Verification and security

Start the API and request `GET /health/db`. It returns
`{"status":"ok","database":"connected"}` only when PostgreSQL is reachable.

Keep `.env`, database passwords, `service_role` keys, and local database
backups out of Git. If the frontend later calls Supabase's Data API directly,
design Supabase Auth and Row Level Security before exposing any table.

Wandora currently authenticates through FastAPI: account records and Argon2
password hashes live in the same Supabase PostgreSQL database, while signed JWT
sessions are verified by the API. The frontend only calls the API and never
receives a Supabase database connection string or service key.

## References

- [Connect to Supabase Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [SQLAlchemy with Supabase](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase-FUqebT)
