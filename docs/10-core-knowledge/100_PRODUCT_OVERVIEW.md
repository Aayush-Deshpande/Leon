---
id: "100"
title: "Product Overview"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["leon.md"]
outputs: ["110", "120", "130", "140", "150", "200"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001"]
---

# 100 — Product Overview

> Governed by `[000]`, structured per `[001]`. This document is a **navigation index into `leon.md`** — it tells readers *where* each product concept lives in the seed. It contains locators and citations only; product intent itself is owned by `leon.md` and must not be restated here (`[000 §3]`, `[000 §1.3]`).

## Purpose

Give every reader and AI assistant a fast, compact map to the relevant part of `leon.md`, so they can locate product intent without loading the entire seed and without a second, drift-prone copy of it existing.

## Scope

Covers orientation only: a topic → `leon.md` section locator map. This document does **not** contain product descriptions, requirements, architecture, or any restatement of `leon.md` prose (owned respectively by `leon.md`, `[140]`, the 200-series, and `leon.md`).

## Owned Concepts

1. The navigation/orientation mapping from product topics to `leon.md` sections. (Product intent itself remains owned by `leon.md`.)

## Must Never Contain

- Any paraphrase or restatement of `leon.md` content (`[000 §1.3]`) — locators and citations only.
- Functional requirements — owned by `[140]`.
- Constraints, assumptions, non-goals — owned by `[120]`.
- Domain entities — owned by `[110]`.
- Architecture, interfaces, data, or AI-pipeline detail — owned by the 200-series.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | The seed specification this document indexes. |

## Downstream Consumers (Outputs)

`[110]`, `[120]`, `[130]`, `[140]`, `[150]`, and the 200-series use this as the orientation entry point into `leon.md`.

## Navigation Index (topic → `leon.md` locator)

Consult the cited `leon.md` section for the authoritative content; this table only tells you where to look.

| Product topic | Where it lives |
|---------------|----------------|
| What Leon is (RAG system with self-evaluating retrieval) | `leon.md` §1 "What it is" |
| Problem solved (ungrounded/fabricated legal citations) | `leon.md` §1 "Problem it solves" |
| Core objective (grounded answer or explicit low-confidence) | `leon.md` §1 "Core objective" |
| High-level workflow (8-step overview) | `leon.md` §1 "High-level workflow" |
| Key innovations (in-loop eval, citation-groundedness, generalized retrieval) | `leon.md` §1 "Key innovations" |
| Project scope (single-domain, single-jurisdiction, demo-to-production) | `leon.md` §1 "Project scope" |
| Explicit non-goals | `leon.md` §1 "Explicit non-goals" (register owned by `[120]`) |
| Core features (hybrid retrieval, grounded generation, self-critique, fallback, MCP, evaluation) | `leon.md` §2.1–§2.6 |
| Complete user flow | `leon.md` §3 (formalized as workflows in `[150]`) |
| System workflow (ingestion → retrieval → generation → critique → decision → logging) | `leon.md` §4 (formalized in `[150]`) |
| AI workflow (embedding, BM25, reranker, generation, self-critique) | `leon.md` §5 (owned by `[240]` for design) |
| Component breakdown | `leon.md` §6 (owned by `[200]` for design) |
| Data flow | `leon.md` §7 (owned by `[200]`/`[210]` for design) |
| API overview | `leon.md` §9 (owned by `[220]` for contracts) |
| Data storage | `leon.md` §10 (owned by `[230]` for schema; `[130]` for corpus) |
| Assumptions | `leon.md` §11 (register owned by `[120]`) |
| Future improvements | `leon.md` §12 |

## Assumptions

None introduced here. All project assumptions are owned by `[120]` (`[000 §1.7]`).

## References

- `leon.md` — Seed specification (source of all product intent).
- `[000]` — Engineering Manual.
- `[001]` — Document Template.
- `[900#ADR-0001]` — Core Knowledge expansion decision.

## Open Questions

None.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity — `[000 §8.1.2]`
- [x] No duplication (locators only, no restatement) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Explicit assumptions in `[120]` (none here) — `[000 §8.1.7]`
- [x] Determinism (index as a table) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — tracks the immutable seed's structure; refinable via lightweight amendment per `[000 §9.4]`.

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial navigation index into `leon.md`. | ADR-0001 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: reconciled `outputs` to actual consumers (M6). | — |
