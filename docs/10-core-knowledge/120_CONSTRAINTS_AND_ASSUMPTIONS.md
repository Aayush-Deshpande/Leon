---
id: "120"
title: "Constraints and Assumptions"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["leon.md", "100"]
outputs: ["130", "140", "150", "200", "210", "220", "230", "240", "310", "330", "400", "500"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001"]
---

# 120 — Constraints and Assumptions

> Governed by `[000]`, structured per `[001]`. Owns the authoritative, trackable register of project scope boundaries, non-goals, and labeled assumptions (`[000 §3]`). Gates block on unresolved implementation-blocking assumptions here (`[000 §1.7]`, Gate G4/G6). It records constraints — never their solutions.

## Purpose

Consolidate every scope boundary, non-goal, and assumption into one tracked list with resolution status and owner, so gates can block on unresolved items and no assumption is acted on silently.

## Scope

Covers scope boundaries, non-goals, and assumptions with their status. This document does **not** contain solutions, designs, or requirements (owned by Architecture, `[140]`, and Implementation) — it registers constraints and points to where each is resolved.

## Owned Concepts

1. The scope/non-goal boundaries of the project.
2. The authoritative assumption register (IDs, statements, status, resolution owner, blocking flag).

## Must Never Contain

- Solutions to constraints or how to satisfy them — owned by Architecture (200-series) and Implementation (400-series).
- Functional requirements — owned by `[140]`.
- Domain entities — owned by `[110]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | Origin of the assumptions (§11), non-goals and scope (§1). |
| `[100]` | Navigation into the relevant `leon.md` sections. |

## Downstream Consumers (Outputs)

All Architecture, Standards, and Implementation documents, plus every Quality Gate (`[000 §12]`), consume this register.

## Scope Boundaries

| ID | Boundary | Origin |
|----|----------|--------|
| SB-1 | Single-domain, single-jurisdiction legal Q&A system. | `leon.md` §1 "Project scope" |
| SB-2 | Demo-to-production quality on a **bounded, pre-ingested** corpus — not a general legal platform. | `leon.md` §1 "Project scope" |
| SB-3 | Single-turn question answering. | `leon.md` §11.7 |
| SB-4 | English-only corpus and queries. | `leon.md` §11.6 |

## Non-Goals

| ID | Non-goal | Origin |
|----|----------|--------|
| NG-1 | Not a substitute for legal advice; all outputs are informational. | `leon.md` §1 |
| NG-2 | No multi-jurisdictional coverage. | `leon.md` §1 |
| NG-3 | No user authentication/authorization in initial scope. | `leon.md` §1, §11.4 |
| NG-4 | No model fine-tuning (retrieval + prompting + off-the-shelf/API LLMs). | `leon.md` §1 |
| NG-5 | No user-upload of arbitrary legal documents in initial scope. | `leon.md` §1 |

## Assumption Register

Status values: **OPEN** (unresolved), **CONFIRMED** (accepted as stated), **RESOLVED** (settled in the owning document). "Blocks" indicates the gate/phase blocked until resolution (`[000 §12]`).

| ID | Assumption | Status | Resolved by | Blocks |
|----|-----------|--------|-------------|--------|
| A-1 | Corpus scoped to a single statute or small related set (Indian Contract Act, 1872, + bounded curated case law), not all law. **Confirmed** per ADR-0002. | RESOLVED (`[900#ADR-0002]`) | `[130]` | — (was: G4, G6) |
| A-2 | Self-critique uses the same LLM family with a distinct prompt, not a separately trained classifier. | CONFIRMED | `[240]` | — |
| A-3 | Query reformulation retries are capped at a small fixed number (e.g., 2) before an explicit low-confidence response. | CONFIRMED | `[210]` | — |
| A-4 | No authentication/authorization; single-tenant demo/portfolio deployment. | CONFIRMED | `[310]` | — |
| A-5 | A second MCP tool (general web-search fallback) is optional/deferrable and not required for the core system. | CONFIRMED | `[220]` | — |
| A-6 | English-only queries and corpus in initial scope. | CONFIRMED | `[130]` | — |
| A-7 | Single-turn Q&A; no multi-turn conversational memory. | CONFIRMED | `[140]` | — |
| A-8 | Deployment target is a single-instance Docker/AWS demo-scale setup, not a horizontally scaled service. | CONFIRMED | `[500]` | — |

**Note on A-1:** This was the one implementation-blocking assumption. It is now **RESOLVED** in `[130]` per ADR-0002 (`[900#ADR-0002]`); the G4/G6 blocks are cleared.

## Assumptions

This document *is* the assumption register; it introduces no further assumptions of its own.

## References

- `leon.md` §1, §11 — origin of scope, non-goals, assumptions.
- `[100]` — navigation index.
- `[000]` — Engineering Manual (§1.7, §12 gates).

## Open Questions

- **OQ-1 — CLOSED:** A-1 corpus scope confirmed in `[130]` per ADR-0002. No blocking open questions remain.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity — `[000 §8.1.2]`
- [x] No duplication (registers + references, no solutions) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Explicit assumptions labeled and tracked — `[000 §8.1.7]`
- [x] Determinism (registers as tables) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — assumption *status* may update via lightweight amendment (`[000 §9.4]`) as items are confirmed/resolved; a resolved assumption's entry freezes. Scope boundaries and non-goals are hard once frozen (changing them is a scope change requiring escalation per the decision policy).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001). A-1 RESOLVED (ADR-0002).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial register: 4 scope boundaries, 5 non-goals, 8 assumptions. | ADR-0001 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: reconciled `outputs` (M6) — removed spurious 300/320/340 consumers. | — |
