---
id: "200"
title: "System Architecture"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["100", "110", "120", "140", "150"]
outputs: ["210", "220", "230", "240", "300", "310", "320", "400", "41x", "500", "610"]
category: "Architecture"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0003"]
---

# 200 — System Architecture

> Governed by `[000]`, structured per `[001]`. Owns component decomposition, responsibilities, boundaries, and the component-level data flow (`[000 §3]`). It does not contain interface bodies (`[220]`), storage schemas (`[230]`), control-flow mechanics (`[210]`), model choices (`[240]`), prompts (`[330]`), deployment topology (`[500]`), or code.

## Purpose

Define the components Leon is composed of, what each is responsible for, where their boundaries lie, and how they connect — the single source of truth for "what talks to what."

## Scope

Covers the component map, per-component responsibility and boundary, and the architectural (component-to-component) data flow. This document does **not** cover the agent control-flow logic (`[210]`), interface shapes (`[220]`), data schemas (`[230]`), AI model choices (`[240]`), or deployment (`[500]`).

## Owned Concepts

1. The component decomposition and each component's responsibility.
2. Component boundaries (what each component may and may not do).
3. The component-to-component data flow.

## Must Never Contain

- API/MCP request/response bodies, status codes — owned by `[220]`.
- Storage schemas, indexes, field types — owned by `[230]`.
- Control-flow state machine, routing, thresholds, retry policy — owned by `[210]`.
- Model/algorithm choices and AI-stage I/O contracts — owned by `[240]`.
- Prompt text — owned by `[330]`; deployment topology — owned by `[500]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[100]` | Product orientation into `leon.md`. |
| `[110]` | Domain entities the components operate on. |
| `[120]` | Scope/non-goals/assumptions constraining the architecture (e.g., A-8 single-instance, NG-3 no auth). |
| `[140]` | Functional requirements each component must collectively satisfy. |
| `[150]` | Workflows the component data flow must realize. |

## Downstream Consumers (Outputs)

`[210]`, `[220]`, `[230]`, `[240]`, `[300]`, `[310]`, the Implementation phases, `[500]`, and `[610]` build on this decomposition.

## Component Map

| # | Component | Responsibility (boundary) | Realizes |
|---|-----------|---------------------------|----------|
| C1 | **Frontend (React)** | Chat UI; render answer, citations (viewable source passage), confidence indicator. No business logic. | FR-1, FR-21, FR-23, FR-15 |
| C2 | **Backend API (FastAPI)** | HTTP surface + streaming; validate requests; invoke Orchestration; return responses. No retrieval/generation logic itself. | FR-1, FR-21, FR-22 |
| C3 | **Ingestion Service** | Offline: extract → clean → chunk → embed → dual-index (per `[130]` strategy). Not invoked at query time. | (corpus for FR-2/4/16) |
| C4 | **Retrieval Service** | Given a query, run dense + sparse search, merge (fusion), rerank; return ranked context. Sub-modules: C4a dense, C4b sparse, C4c reranker. *Fusion method (RRF) and sizing owned by `[240]`.* | FR-2, FR-3, FR-4 |
| C5 | **Generation Service** | Build prompt from query+context, call generation model, parse citation markers. No evaluation. | FR-5, FR-6, FR-7 |
| C6 | **Critique Service** | Independently score relevance + groundedness of a draft answer; flag unverifiable citations. Distinct from C5. | FR-8, FR-9, FR-10 |
| C7 | **Orchestration / Agent Controller** | Route among return / reformulate / tool / low-confidence based on critique; enforce retry bound. Owns the *invocation* of C4–C8; owns no scoring itself. | FR-11–FR-15 |
| C8 | **MCP Tool Layer** | Expose citation-verification (and optional web-search) as callable tools over MCP. | FR-16, FR-17 |
| C9 | **Evaluation Logging Service** | Assemble and persist the per-query Trace asynchronously; serve aggregate metrics. | FR-18, FR-19, FR-20 |
| D1 | **Vector store** | Persist chunk embeddings for dense search. (Schema owned by `[230]`.) | — |
| D2 | **Sparse index** | Persist tokenized chunks for BM25 search. (Structure owned by `[230]`.) | — |
| D3 | **Relational store** | Persist Traces and corpus metadata. (Schema owned by `[230]`.) | — |
| D4 | **Raw document store** | Persist original source documents as citation ground truth. (Owned by `[230]`; data by `[130]`.) | — |

## Boundaries and Interaction

| From | To | Nature of interaction |
|------|----|-----------------------|
| C1 | C2 | Query submission; streamed answer + metadata (shape owned by `[220]`). |
| C2 | C7 | Delegates each query to the Orchestration Controller. |
| C7 | C4 | Requests ranked context (and re-requests on reformulation). |
| C4 | D1, D2 | Reads dense/sparse candidates. |
| C7 | C5 | Requests a draft answer for query + context. |
| C7 | C6 | Requests a critique of the draft answer against context. |
| C7 | C8 | Invokes MCP tools on fallback. |
| C8 | D4 | Citation-verification reads raw ground-truth text. |
| C7 | C9 | Emits the completed Trace (non-blocking). |
| C9 | D3 | Persists Traces; reads aggregates. |
| C3 | D1, D2, D3, D4 | Offline population of stores and metadata. |

**Key boundary rule (protects the differentiator):** Generation (C5) and Critique (C6) are separate components; the Orchestration Controller (C7) calls them independently. Critique is never folded into Generation (`leon.md` §5.5, FR-10). The *routing logic* C7 uses is owned by `[210]`, not here.

## Component-Level Data Flow

Realizes workflow `[150]` W-2/W-3 (functional ordering owned by `[150]`; this shows the structural path):

```
C1 ──query──> C2 ──> C7 ──> C4 ──> {D1,D2} ──ranked context──> C7
                         C7 ──> C5 ──draft+citations──> C7
                         C7 ──> C6 ──critique──> C7
        C7 ─decision(logic in [210])─> return via C2 ──> C1
                                    └─fallback─> C4 (reformulate) | C8 (tool) | low-confidence
        C7 ──trace(async)──> C9 ──> D3
Offline: raw docs ──> C3 ──> {D1,D2,D3,D4}
```

## Assumptions

None introduced. Architecture honors `[120]`: A-8 (single-instance; no horizontal-scaling components), NG-3 (no auth component), A-5 (C8 web-search sub-tool optional).

## References

- `leon.md` §6, §7, §8 — component and data-flow source.
- `[110]`, `[140]`, `[150]` — entities, requirements, workflows.
- `[900#ADR-0003]` — records that component decomposition mirrors `leon.md` §8 and the single-instance constraint.

## Open Questions

None blocking. Internal module structure within a component may be refined during its phase (soft portion, `[000 §9.4]`); component boundaries are hard.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (bodies/schemas/routing deferred) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (tables + diagram) — `[000 §8.1.8]`
- [x] Traceability to FRs/workflows — `[000 §8.1.9]`
- [x] Critique preserved as distinct component — `[000 §8.3]` Architecture
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` for component decomposition and boundaries (a cross-cutting contract; the hardest freeze per `[000 §3]`). Internal module structure within a component is `soft` per `[000 §1.6]` and may be refined via lightweight amendment.

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial component architecture (9 components + 4 stores). | ADR-0003 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: added 320 consumer (M6); C4 fusion detail deferred to `[240]` (M3). | — |
