# Wandora frontend

React, Vite, and TypeScript client application. Run commands from this folder:

```bash
npm install
npm run dev
npm run build
npm run lint
```

The client must call the FastAPI API; it must not contain Supabase database
credentials.

Set `VITE_API_BASE_URL` in `.env` when the API is not available at
`http://127.0.0.1:8000`. Use the Sign in link to create an account or log in;
the client sends its bearer token only to the configured FastAPI API.
