---
id: "300"
title: "Coding Standards"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["200", "220"]
outputs: ["400", "41x", "610", "620"]
category: "Engineering Standards"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0008"]
---

# 300 — Coding Standards

> Governed by `[000]`, structured per `[001]`. Owns language/style/structure conventions for backend and frontend (`[000 §3]`). It contains no feature behavior, architecture (`[200]`), test policy (`[320]`), security rules (`[310]`), or deployment mechanics (`[500]`).

## Purpose

Define concrete, checkable coding conventions so all code (human- or AI-authored) is uniform, reviewable, and consistent with the architecture's module layout.

## Scope

Covers language versions, project/module structure, naming, typing, error-handling patterns, dependency management, and formatting/linting. This document does **not** cover what the code does (Architecture/FRs), how it is tested (`[320]`), security rules (`[310]`), or deployment (`[500]`).

## Owned Concepts

1. Code style and structural conventions (backend + frontend).
2. Language/tooling versions and dependency-management policy.
3. Internal error-handling *patterns* (not wire error shapes — those are `[220]`).

## Must Never Contain

- Feature behavior or architecture — owned by `[200]`/`[210]`/`[240]`.
- Test policy or correctness properties — owned by `[320]`.
- Security rules — owned by `[310]`.
- Wire/API error shapes — owned by `[220]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[200]` | Component/module layout the code structure mirrors (`leon.md` §8). |
| `[220]` | Interface models the code's request/response types align to. |

## Downstream Consumers (Outputs)

`[310]`, `[320]`, Implementation, `[610]`, `[620]`.

## Standards (ADR-0008)

Per ADR-0008 (`[900#ADR-0008]`; SOFT — revisitable conventions).

### Backend (Python)
| Topic | Standard |
|-------|----------|
| Language | Python **3.11+**. |
| Framework | FastAPI + Pydantic v2 for request/response models mirroring `[220]`. |
| Layout | Mirror `leon.md` §8 (`app/api`, `retrieval`, `generation`, `critique`, `orchestration`, `tools`, `ingestion`, `evaluation`, `models`, `config`). One component per package. |
| Typing | Full type hints; `mypy` strict on `app/`. No untyped public functions. |
| Lint/format | `ruff` (lint + format) as the single tool; CI-enforced, zero warnings. |
| Naming | `snake_case` functions/vars, `PascalCase` classes, `UPPER_SNAKE` constants, modules `snake_case`. |
| Errors | Raise typed exceptions internally; translate to `[220]` error shapes only at the API boundary. No bare `except`. |
| Docstrings | Module + public-function docstrings; reference the owning doc ID for behavior. |
| Async | `async def` for I/O-bound handlers/model/store calls; no blocking calls in the event loop. |

### Frontend (React)
| Topic | Standard |
|-------|----------|
| Language | TypeScript (strict), React 18, Vite. |
| Layout | Mirror `leon.md` §8 (`components`, `pages`, `api`, `state`). |
| Lint/format | ESLint + Prettier; `tsc --noEmit` in CI. |
| Naming | Components `PascalCase`; hooks `useX`; files match export. |
| State | Explicit, minimal client state; API types generated from/aligned to `[220]`. |
| Errors | Render `[220]` error shapes; never swallow errors silently. |

### Dependency Management
| Topic | Standard |
|-------|----------|
| Pinning | **Exact pinned versions** with a committed lockfile (backend and frontend). No open ranges. |
| Additions | Prefer well-known, maintained packages; a new dependency is a decision noted in `900` if non-trivial. |
| Config/secrets | Read from environment/config (`config.py`); **never hard-code** (rules owned by `[310]`; env contract by `[500]`). |

## Assumptions

None introduced.

## References

- `leon.md` §8 — module layout.
- `[200]` — components; `[220]` — models the code shapes align to.
- `[900#ADR-0008]`.

## Open Questions

None blocking.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (no behavior/tests/security) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` (none) — `[000 §8.1.7]`
- [x] Determinism (standards tables) — `[000 §8.1.8]`
- [x] Concrete/checkable, not vague — `[000 §8.3]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — conventions may be refined via lightweight amendment (`[000 §9.4]`); does not gate cross-boundary contracts.

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial backend/frontend coding standards. | ADR-0008 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: reconciled dependency graph (M6) — added `[220]` input, corrected outputs. | — |
