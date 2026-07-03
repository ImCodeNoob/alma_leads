# Lead Management

A small lead-intake system: a public form for prospects to apply
(name, email, resume/CV), automatic email notifications, and an
auth-guarded internal dashboard for attorneys to review leads and mark
them as contacted.

- **Backend**: FastAPI + SQLAlchemy (`backend/`)
- **Frontend**: Next.js + Tailwind (`frontend/`)
- **Storage**: Postgres (Docker) / SQLite (local dev) + local disk for
  resumes
- **Email**: SMTP, with a zero-config console/file fallback for local dev

## Quickstart

```bash
cp .env.example .env
docker compose up --build
```

Then open:
- http://localhost:3000 — public lead form
- http://localhost:3000/login — attorney login (`attorney@example.com` /
  `changeme123` by default)
- http://localhost:3000/register — create an additional attorney account;
  requires the invite code in `ATTORNEY_SIGNUP_CODE` (default
  `change-me-invite-code` — change it before deploying anywhere real,
  since anyone with the code can register and see every lead's PII/resume)

See [`docs/RUNNING_LOCALLY.md`](docs/RUNNING_LOCALLY.md) for the full
walkthrough, including running each service manually without Docker.

## Demo

[`demo/e2e-walkthrough.mov`](demo/e2e-walkthrough.mov) — screen recording
of the full flow: submitting the public form, the resulting emails,
logging in as the attorney, and marking a lead as reached out.

## Docs

- [`docs/RUNNING_LOCALLY.md`](docs/RUNNING_LOCALLY.md) — how to run this,
  two ways
- [`docs/DESIGN.md`](docs/DESIGN.md) — architecture, data model, API
  contract, and the tradeoffs behind each design choice
- [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) — how this repo was built
  with a coding agent
- [`docs/SESSION_TRANSCRIPT.md`](docs/SESSION_TRANSCRIPT.md) —
  representative excerpts from the actual agent session
- [`NOTES.md`](NOTES.md) — attribution

## Repo layout

```
backend/    FastAPI app, SQLAlchemy models, tests
frontend/   Next.js app (public form, login, leads dashboard)
docs/       design + usage docs
docker-compose.yml
```
