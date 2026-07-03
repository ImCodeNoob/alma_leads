# Running Locally

There are two ways to run this. Docker Compose is the primary/recommended
path and matches how this would actually be deployed. The manual path is
useful for fast iteration on one service at a time.

## Option A: Docker Compose (recommended)

Requires Docker Desktop (or another Docker Engine + Compose v2).

```bash
cp .env.example .env       # defaults work as-is for local dev
docker compose up --build
```

This starts three containers:

- `db` — Postgres 16
- `backend` — FastAPI on http://localhost:8000
- `frontend` — Next.js on http://localhost:3000

On first boot the backend creates its tables and seeds one attorney
account from `.env` (`ATTORNEY_EMAIL` / `ATTORNEY_PASSWORD`, default
`attorney@example.com` / `changeme123`).

Open http://localhost:3000 for the public lead form, or
http://localhost:3000/login to sign in as the attorney and view
`/leads`.

Because `SMTP_HOST` is empty by default, emails aren't actually sent —
they're written to `./backend/emails/*.txt` (mounted out of the `backend`
container as a volume) and logged to the `backend` container's stdout. Set
`SMTP_HOST`/`SMTP_PORT`/`SMTP_USERNAME`/`SMTP_PASSWORD`/`SMTP_FROM` in
`.env` to send real email through any SMTP provider (Gmail app password,
Mailtrap, SendGrid SMTP relay, etc.) and restart.

To stop: `docker compose down` (add `-v` to also drop the Postgres volume).

## Option B: Run each service manually (SQLite, no Docker)

Useful for backend/frontend development without waiting on container
rebuilds. Uses a local SQLite file instead of Postgres — same code path,
different `DATABASE_URL`.

**Backend**

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # DATABASE_URL defaults to sqlite:///./app.db
uvicorn app.main:app --reload
```

Runs on http://localhost:8000. Tables are created and the attorney account
is seeded automatically on startup. Run the test suite with:

```bash
pytest
```

**Frontend** (separate terminal)

```bash
cd frontend
npm install
cp .env.example .env.local  # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

Runs on http://localhost:3000.

**Important**: use the same hostname (`localhost`, not `127.0.0.1`) for
both the browser and `NEXT_PUBLIC_API_URL` — the backend's CORS allow-list
(`CORS_ORIGINS` in `backend/.env`) is origin-exact, so `127.0.0.1:3000` and
`localhost:3000` are treated as different origins.

## Logging in

Seeded attorney login (both options, unless you changed the env vars):

- Email: `attorney@example.com`
- Password: `changeme123`

## Troubleshooting

- **CORS errors in the browser console**: check that `CORS_ORIGINS` on the
  backend matches the exact origin (scheme + host + port) the frontend is
  served from.
- **"Resume must be one of..."**: only `.pdf`, `.doc`, `.docx` are
  accepted, capped at 5MB (`MAX_RESUME_SIZE_BYTES`).
- **Emails not arriving**: if `SMTP_HOST` is unset, check
  `backend/emails/` instead — nothing is actually sent.
