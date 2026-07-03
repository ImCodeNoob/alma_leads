# Design Document

## Requirements recap

1. A **public** form where a prospect submits first name, last name, email,
   and a resume/CV.
2. On submission, an email goes to the prospect and to an attorney inside
   the company.
3. An **auth-guarded internal UI** lists all leads with everything the
   prospect submitted.
4. Each lead has a state machine: `PENDING -> REACHED_OUT`, the transition
   made manually by an attorney after they contact the prospect.

## Architecture

```
                    ┌───────────────────┐
  Prospect  ───────▶│  Next.js frontend │
                    │  (public form,    │
  Attorney  ───────▶│   login, leads)   │
                    └─────────┬─────────┘
                              │ REST (JSON / multipart), Bearer JWT
                              ▼
                    ┌───────────────────┐
                    │   FastAPI backend │
                    │  (leads, auth)    │
                    └───┬───────────┬───┘
                        │           │
                 SQLAlchemy      SMTP (or
                        │        console/file
                        ▼        fallback)
                 ┌─────────────┐
                 │  PostgreSQL │   (SQLite in local dev)
                 └─────────────┘
```

Two services, one shared Postgres database, containerized via Docker
Compose. The frontend never talks to the database directly — everything
goes through the FastAPI REST API, so the API is the single source of
truth and the only thing that needs to enforce the state machine and auth
rules.

## Data model

```
Lead
  id               UUID (PK)
  first_name       string
  last_name        string
  email            string
  resume_filename  string   # original filename, shown/downloaded as-is
  resume_path      string   # where the file actually lives on disk
  status           enum(PENDING, REACHED_OUT)
  created_at       timestamp
  updated_at       timestamp

User (attorney account)
  id                UUID (PK)
  email             string (unique)
  hashed_password   string (bcrypt)
```

One `User` table with a single seeded row is enough to satisfy "guarded by
auth" without building out a full user-management system the assignment
didn't ask for — see "What I'd change for real production" below for the
obvious next step.

## API contract

| Method | Path                          | Auth | Purpose |
|---|---|---|---|
| POST | `/api/leads`                   | none | Prospect submits the form (multipart: `first_name`, `last_name`, `email`, `resume`). Validates file type (pdf/doc/docx) and size (≤5MB), persists the lead as `PENDING`, sends both emails. |
| POST | `/api/auth/login`              | none | Attorney logs in with email+password, gets back a JWT. |
| POST | `/api/auth/register`           | invite code | Creates a new attorney account, gated by a shared `ATTORNEY_SIGNUP_CODE` (see "Auth design"). |
| GET  | `/api/leads`                   | JWT  | List all leads, newest first. |
| PATCH| `/api/leads/{id}/status`       | JWT  | Transition a lead's status. Only `PENDING -> REACHED_OUT` is accepted; anything else is a 409. |
| GET  | `/api/leads/{id}/resume`       | JWT  | Stream the original resume file back for download. |

Putting the resume behind an authenticated endpoint (rather than a public
static file mount under `/uploads/...`) was a deliberate choice: prospects'
resumes are personal documents, and a guessable/enumerable public URL would
leak them.

## Auth design

JWT (HS256) issued on login, sent as `Authorization: Bearer <token>` on
every protected request, verified by a FastAPI dependency
(`get_current_user`) that decodes the token and loads the user. One
attorney account is seeded from `ATTORNEY_EMAIL`/`ATTORNEY_PASSWORD` env
vars on startup if it doesn't already exist, so the app is usable with zero
setup.

Additional attorneys can self-register via `POST /api/auth/register` (and
the `/register` page). Registration is gated by a shared
`ATTORNEY_SIGNUP_CODE` env var, checked with a constant-time comparison —
without that gate, anyone who found `/register` could create an account
and pull down every prospect's PII and resume, since there's only one
role in this system and it has full read access to all leads. A shared
invite code is a deliberately lightweight stand-in for real
company-employee verification (SSO, admin-approved invites, a company
email-domain check); it's enough to keep the endpoint from being wide open
to the public internet without building an admin-approval flow the
assignment didn't ask for.

**Frontend gating is client-side**, not via Next.js middleware: the token
lives in `localStorage`, and the `/leads` page checks for it in a
`useEffect` on mount, redirecting to `/login` if it's missing. Every API
call attaches the token as a bearer header. This is simpler than plumbing
an httpOnly cookie across two different origins (`:3000` and `:8000` in
dev) and is enough to satisfy "guarded by auth" for this exercise, but it's
weaker than a production setup: the token is readable by any JS on the
page (XSS exposure), and there's no server-side redirect for a user who
disables JS or hits the route before the client bundle loads. Production
hardening would move to an httpOnly, `SameSite=Lax` cookie set directly by
the backend and checked by Next.js middleware (or a reverse proxy) before
the page ever renders.

## Email design

`email_service.send_email()` sends over SMTP if `SMTP_HOST` is configured
(works with Gmail app passwords, Mailtrap, SendGrid's SMTP relay, or any
other SMTP provider — no vendor SDK lock-in). If `SMTP_HOST` is unset, it
logs the email to `./emails/*.txt` and to stdout instead of failing, so the
app is fully runnable and demoable with zero external credentials. A real
deployment sets `SMTP_HOST`/`SMTP_USERNAME`/`SMTP_PASSWORD` and gets real
delivery with no code changes.

Email sending happens synchronously, inline in the `POST /api/leads`
request, and failures are caught and logged rather than failing the
request — the lead is already committed to the database by that point, so
a flaky SMTP provider shouldn't cost the prospect their submission. The
tradeoff: if email sending is slow, so is the form submission. At real
scale this would move to a background task/queue (see below).

## File storage design

Resumes are validated (extension allow-list, 5MB cap, non-empty) and
written to a local directory (`./uploads`, a Docker volume in Compose)
under a random UUID filename, with the original filename and the on-disk
path both stored on the `Lead` row. This is the simplest thing that could
work for a single-instance deployment. It doesn't survive a multi-instance
deployment (each instance would have its own disk) — the natural
production swap is an S3-compatible object store, which only requires
changing `storage.py`'s two functions (`save_resume` / the download
handler); nothing else in the app needs to know where files physically
live.

## What I'd change for real production

- **Database migrations**: the app uses `Base.metadata.create_all()` on
  startup instead of Alembic migrations. Fine for a from-scratch schema;
  the first real schema change would need Alembic wired in.
- **Object storage** for resumes (S3/GCS) instead of local disk, for
  multi-instance deployments and durability.
- **Background email delivery** (a queue/worker) instead of inline SMTP
  calls, so a slow or down email provider can't slow down lead submission.
- **httpOnly-cookie auth** with server-side route protection instead of
  localStorage + client-side redirect.
- **Rate limiting / basic abuse protection** on the public `POST
  /api/leads` endpoint, since it's the one unauthenticated write path in
  the system.
- **Refresh tokens** and account management (password reset, multiple
  attorney accounts) instead of one long-lived access token for one seeded
  user.
