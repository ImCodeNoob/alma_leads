# Coding-Agent Usage

**Tool**: Claude Code (Sonnet 5), used interactively in a single session
covering the system design, backend, frontend, Docker config, and this
documentation set.

**Delegated vs. hand-written**: Essentially all code — the FastAPI backend
(models, auth, email, file storage, routers, tests), the Next.js frontend
(public form, login, protected dashboard), Dockerfiles/Compose config, and
these docs — was written by the agent. What I did by hand was direct the
architecture: I answered explicit up-front questions on persistence
(Postgres via Docker Compose vs. SQLite), auth mechanism (JWT + seeded
user vs. shared password), email/storage approach (SMTP env vars + local
disk vs. a specific vendor SDK), and how the GitHub repo should get
created — then reviewed the resulting plan before any code was written.
I did not hand-edit any source file; my role was decisions and review, not
typing code. The agent also ran its own verification loop end-to-end
(pytest for the backend, `tsc`/`eslint` for the frontend, and a scripted
Playwright pass through the actual browser flow — submit → email logged →
login → mark reached out → reload) rather than stopping at "it compiles."

**Where the agent produced subtly bad code, and how it was caught**: The
`/leads` page needs to redirect to `/login` if there's no auth token, but
the token only exists in `localStorage`, which the server can't see. The
agent's first pass read the token via `useState(() => Boolean(getToken()))`
— this compiles and typechecks fine, but breaks React hydration, because
the client's very first render (using real `localStorage`) disagreed with
the server-rendered HTML (which has no `localStorage`). This only showed
up as a runtime console error during the Playwright pass, not in `tsc` or
`eslint`. The agent's fix attempt made it worse: switching to
`useSyncExternalStore` (React's sanctioned tool for exactly this kind of
server/client-mismatched state) fixed the hydration warning, but the
redirect `useEffect` depended on that hook's value — and on first commit
that value is necessarily the server snapshot (`false`), so the effect
fired immediately, saw "no token," and redirected a *logged-in* user back
to `/login` before the corrected client value ever propagated. This only
reproduced on a hard page reload while authenticated, and only in the
browser — again invisible to the type checker. It surfaced as a Playwright
step timing out waiting for `REACHED_OUT` to reappear after `page.reload()`,
which was the actual browser log then showing a request for `/login`
instead of `/leads`. The final, correct fix defers *both* the render
decision and the token check to a single post-mount effect (render nothing
until mounted, matching server output; only check `localStorage` and
possibly redirect once safely on the client) — see
[`frontend/lib/useRequireAuth.ts`](../frontend/lib/useRequireAuth.ts). The
takeaway: this class of bug (SSR/client state mismatches) is essentially
invisible to typechecking and linting, and only running the actual app in
a real browser caught it.
