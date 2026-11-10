# Project Leon

A full-stack, self-evaluating Retrieval-Augmented Generation (RAG) system for legal
question answering. Its differentiator is **in-loop evaluation**: the system critiques
its own retrieval and citation-groundedness before answering, and takes a corrective
action when confidence is low rather than answering regardless.

> **Specification-first project.** The complete, frozen specification lives in [`docs/`](docs/).
> Implementation strictly follows it — see the Engineering Manual `docs/00-governance/000_ENGINEERING_MANUAL.md`.
> Do not change architecture without a Change Request + ADR (`docs/00-governance/900_DECISION_LOG.md`).

## Layout
- `docs/` — frozen knowledge base (governance, core knowledge, architecture, standards, planning, operations).
- `backend/` — FastAPI service (Python 3.11+).
- `frontend/` — React 18 + TypeScript (Vite).
- `docker-compose.yml` — single-instance demo topology (Postgres+pgvector, backend, frontend).

## Development (phase P0 scaffold)

Backend:
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate   # (Windows) or source .venv/bin/activate
pip install -e ".[dev]"
ruff check . && mypy && pytest
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run lint && npm run typecheck && npm run build
npm run dev
```

Full stack: `cp .env.example .env` then `docker compose up --build`.
Host ports bind to `127.0.0.1` only ([310] SEC-1).

## Status
Implementation phase **P0 (scaffold)** complete. Build order in `docs/40-planning/430_BUILD_ORDER.md`.
