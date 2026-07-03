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

See [`docs/RUNNING_LOCALLY.md`](docs/RUNNING_LOCALLY.md) for the full
walkthrough, including running each service manually without Docker.

## Docs

- [`docs/RUNNING_LOCALLY.md`](docs/RUNNING_LOCALLY.md) — how to run this,
  two ways
- [`docs/DESIGN.md`](docs/DESIGN.md) — architecture, data model, API
  contract, and the tradeoffs behind each design choice
- [`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) — how this repo was built
  with a coding agent
- [`NOTES.md`](NOTES.md) — attribution

## Repo layout

```
backend/    FastAPI app, SQLAlchemy models, tests
frontend/   Next.js app (public form, login, leads dashboard)
docs/       design + usage docs
docker-compose.yml
```
