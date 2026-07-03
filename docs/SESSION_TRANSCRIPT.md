# Session Transcript Excerpts

Representative excerpts from the actual Claude Code session used to build
this repo (lightly trimmed for length — tool calls and their raw output
are summarized in `[brackets]`; direct quotes are verbatim). Full context
in [`docs/AGENT_USAGE.md`](AGENT_USAGE.md).

---

## 1. Kickoff — architecture decisions before writing code

**User** pasted the assignment verbatim (lead intake form, email
notifications, auth-guarded internal dashboard, FastAPI + Next.js).

**Agent**, before entering plan mode, asked up front rather than guessing:

> How should data be persisted, and how should the whole stack run
> locally?
> - Docker Compose + Postgres (Recommended)
> - SQLite, no Docker
>
> How should the internal attorney UI be protected?
> - Simple JWT login, seeded user (Recommended)
> - Single shared password / basic auth
>
> How should resumes/CVs and outbound email be handled for local dev?
> - Local disk + SMTP via env vars (Recommended)
> - Local disk + a specific provider SDK
>
> For the GitHub submission repo, what do you want me to do?
> - Create it for you via `gh` (Recommended)
> - You'll create/push it yourself

**User** picked the recommended option on all four. The agent also
discovered mid-session that neither `docker`, `gh`, nor `postgres` were
installed in the sandbox, and asked a follow-up before installing
anything:

> Neither Docker Compose is the primary/recommended path[...] Two things
> need your hands-on-keyboard interaction that I can't do from here[...]

This shaped the whole build: SQLite became the agent's own local
verification path (since it couldn't install/verify Docker itself
immediately), with Postgres via Compose as the documented "real" path,
reconciled once Docker was actually installed later in the session.

---

## 2. Plan review before implementation

The agent used plan mode to lay out the full repo structure, API
contract, auth design, and verification plan *before* writing any code,
and surfaced a real discovery from reading the installed Next.js docs:

> Next.js 16 note (checked `node_modules/next/dist/docs`): Turbopack is
> now default (no `--turbopack` flag needed), and `middleware.ts` is
> deprecated in favor of `proxy.ts`. I'm sidestepping this entirely by
> doing auth-gating client-side [...] so no `proxy.ts`/`middleware.ts` is
> needed.

The user approved the plan as written, and implementation proceeded
file-by-file with tests run after each backend module and `tsc`/`eslint`
after each frontend change.

---

## 3. Catching a real bug during verification (see AGENT_USAGE.md for the full story)

While running the `verify` skill's actual-browser-driven check via
Playwright, the agent's first fix for a hydration warning introduced a
worse bug — a logged-in attorney got bounced back to `/login` on page
reload. The agent's own log of the moment it noticed:

> `[pageerror] A tree hydrated but some attributes of the server rendered
> HTML didn't match the client properties...`
>
> [After first fix attempt] `FAILED page.waitForSelector: Timeout 10000ms
> exceeded. ... waiting for locator('text=REACHED_OUT') to be visible`
> [...] the frontend log's last line is "GET /login 200" — meaning after
> clicking "Mark reached out" and reloading, the frontend served /login,
> not /leads!

This was root-caused and fixed (see `frontend/lib/useRequireAuth.ts`)
entirely from re-reading the actual browser/server logs the verification
run produced — not from re-reading the code in isolation.

---

## 4. Iterative feedback after the initial build

Once the app was running, the user drove real usage and reported issues
conversationally; each became a scoped fix, verified live against the
running Docker stack before committing:

> **User**: "I think on UI, the clicking of 'uploading resume' is not
> very visible."
> **Agent**: styled the file input's button and added an explicit
> "Selected: resume.pdf" line, confirmed via a fresh Playwright screenshot
> before/after.

> **User**: "There is no backend/emails path?"
> **Agent**: traced it to `docker-compose.yml` using named Docker volumes
> instead of bind mounts — fixed, verified the files actually appear on
> the host filesystem after a real submission.

> **User**: "My understanding is we should allow UI to let attorney
> register and we should solve the duplication issue?"
> **Agent**: asked one clarifying question first (open signup vs.
> invite-code-gated, since self-registration grants access to every
> prospect's PII/resume), then implemented `POST /api/auth/register` +
> `/register` gated by `ATTORNEY_SIGNUP_CODE`, with a test asserting
> duplicate emails are rejected.

> **User**: "Since we already added the function to allow new
> registration for attorney. We should also sent notificaitons to new
> attnornies?"
> **Agent**: changed the new-lead notification from one fixed
> `ATTORNEY_EMAIL` to querying every row in `User` and notifying each,
> with independent per-recipient error handling; added a test asserting
> two registered attorneys both get notified.

> **User**: "I think for the email, we should mark if it is sent to the
> prospect or the atternory."
> **Agent**: added a `category` field to the fallback email log (filename
> + header line), scoped to only the local dev fallback, not real SMTP
> content.

---

## 5. Going from file-logged to real email delivery

> **User**: "Do you think we should set up a true email service?"
> **Agent**: "For the actual submission, I'd say yes — it's worth it for
> the screen recording. The code already supports it (just env vars, no
> code changes needed)[...] Want me to walk you through the Gmail
> app-password setup now?"

The user provided a Gmail app password directly in chat; the agent wrote
it straight to the gitignored `.env` (never echoed back, never committed),
restarted the backend, and confirmed real delivery by asking the user to
check their actual inbox rather than assuming success from a 201 response.

---

## 6. Publishing

> **User**: `https://github.com/ImCodeNoob/alma_leads.git`
> **Agent**: attempted `git push`, hit `fatal: could not read Username
> for 'https://github.com': Device not configured` (no TTY for a
> credential prompt in the sandboxed shell), asked the user to run `gh
> auth login` interactively, then pushed once `gh auth status` confirmed
> the login.

Before recording, the user asked to reset the dev database; the agent
ran `docker compose down -v`, cleared the bind-mounted `uploads`/`emails`
folders, brought the stack back up, and confirmed via a direct `psql`
query that only the seeded attorney account remained before handing the
app back over for the screen recording.
