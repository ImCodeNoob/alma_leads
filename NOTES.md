# Attribution

This repository was built with Claude Code (Anthropic's coding agent),
directed and reviewed by a human throughout. See
[`docs/AGENT_USAGE.md`](docs/AGENT_USAGE.md) for what was delegated vs.
decided by hand and for a concrete example of agent-produced code that
was wrong on the first pass and how it was fixed, and
[`docs/SESSION_TRANSCRIPT.md`](docs/SESSION_TRANSCRIPT.md) for excerpts
of the actual session.

- **Agent-generated**: all source code — `backend/`, `frontend/`,
  `docker-compose.yml`, the two `Dockerfile`s, and the documentation in
  `docs/`.
- **Human-directed**: the architecture decisions behind that code
  (persistence/runtime, auth mechanism, email/storage approach, and how
  the repo got published), made by answering the agent's explicit
  up-front questions and reviewing its plan before implementation, plus
  ongoing review of the diffs it produced.

No commit-by-commit attribution split is included beyond this file, since
the repository's history is a single agent-directed build rather than a
mix of independently authored commits.
