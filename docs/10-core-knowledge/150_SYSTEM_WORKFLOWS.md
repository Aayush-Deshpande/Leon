---
id: "150"
title: "System Workflows"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["leon.md", "010", "100", "110", "120", "140"]
outputs: ["200", "210", "320", "400", "41x"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001"]
---

# 150 — System Workflows

> Governed by `[000]`, structured per `[001]`. Owns the **end-to-end functional workflows** — the ordered, observable sequences that compose functional requirements into complete flows (`[900#ADR-0001]`). It references FRs by ID and defers the agent control-flow state machine, routing conditions, thresholds, and retry policy to `[210]`.

## Purpose

Show how Leon's functional requirements compose into complete, ordered flows, giving a shared behavioral picture without pre-empting the architectural control-flow contract.

## Scope

Covers ordered functional workflows and their behavioral decision points. This document does **not** cover the control-flow state machine, routing logic, threshold semantics, or retry policy (`[210]`), component boundaries (`[200]`), interface shapes (`[220]`), or restated FR text (`[140]`).

## Owned Concepts

1. The end-to-end functional workflow descriptions and their step ordering.

## Must Never Contain

- Routing/threshold/retry mechanics — owned by `[210]` (referenced).
- Component decomposition — owned by `[200]`.
- Interface shapes — owned by `[220]`.
- Restated functional requirements — owned by `[140]` (referenced by ID).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | User flow (§3), system workflow (§4), data flow (§7). |
| `[010]` | Terms used in the flows. |
| `[100]` | Navigation into `leon.md`. |
| `[110]` | Entities moved through the flows. |
| `[140]` | The FRs these workflows sequence. |

## Downstream Consumers (Outputs)

`[200]` (data-flow architecture), `[210]` (control flow), `[320]` (end-to-end tests), and `41x` phase plans build on these workflows.

## W-1 — Ingestion Workflow (offline, pre-deployment)

Prepares the corpus so query-time retrieval is possible. Realizes the data availability behind FR-2, FR-4, FR-16.

| Step | Action | Notes / owner |
|------|--------|---------------|
| 1 | Acquire raw Source Documents for the active corpus version. | Corpus scope owned by `[130]`. |
| 2 | Extract and clean text. | — |
| 3 | Segment into Chunks. | Chunking strategy owned by `[130]`. |
| 4 | Produce embeddings for each Chunk. | Model owned by `[240]`. |
| 5 | Index chunks into the dense store and the sparse (BM25) index, with metadata. | Schema/index owned by `[230]`. |

Exit: a populated, versioned corpus ready for retrieval.

## W-2 — Query → Answer Workflow (online)

The primary flow. Each step notes the FR(s) it realizes.

| Step | Action | Realizes | Notes / owner |
|------|--------|----------|---------------|
| 1 | Receive a natural-language query. | FR-1, FR-21 | Interface shape owned by `[220]`. |
| 2 | Embed the query. | FR-2 | Model owned by `[240]`. |
| 3 | Retrieve dense + sparse candidates and merge. | FR-2 | Hybrid retrieval. |
| 4 | Rerank merged candidates. | FR-3 | — |
| 5 | Assemble top-N context with citation metadata. | FR-4 | — |
| 6 | Generate a draft answer with citations. | FR-5, FR-6, FR-7 | Prompt owned by `[330]`. |
| 7 | Critique the draft (relevance + groundedness; flag unverifiable citations). | FR-8, FR-9, FR-10 | Distinct from generation. |
| 8 | **Decision point:** sufficient vs. insufficient confidence. | FR-11, FR-12 | **Routing logic and threshold owned by `[210]`.** |
| 8a | If sufficient → return answer + citations + confidence + routing metadata. | FR-11, FR-15, FR-21, FR-23 | Response shape owned by `[220]`. |
| 8b | If insufficient → enter the Fallback Workflow (W-3). | FR-12 | See W-3. |
| 9 | Emit the trace to the Evaluation Logging Workflow (W-4), non-blocking. | FR-18, FR-19 | — |

## W-3 — Fallback Workflow (corrective actions)

Entered from W-2 step 8b. This document specifies the **available ordered outcomes**; the **selection logic, thresholds, and retry bound are owned by `[210]`**.

| Step | Action | Realizes | Notes / owner |
|------|--------|----------|---------------|
| 1 | Choose a corrective action. | FR-12, FR-13 | **Selection logic owned by `[210]`.** |
| 2a | Reformulate the query and re-enter retrieval (W-2 step 3), within the retry bound. | FR-13, FR-14 | Retry bound value owned by `[210]` (A-3, `[120]`). |
| 2b | Invoke an MCP tool (e.g., citation verification) and incorporate/act on the result. | FR-13, FR-16, FR-17 | Tool contract owned by `[220]`. |
| 2c | Produce an explicit low-confidence response. | FR-13, FR-15 | Advises professional consultation. |
| 3 | On retry-bound exhaustion, produce a low-confidence response (2c). | FR-14, FR-15 | Terminal outcome. |
| 4 | Return the resulting response with routing metadata; emit trace (W-4). | FR-18, FR-21 | — |

## W-4 — Evaluation Logging Workflow (asynchronous)

Runs after the user-facing response is sent. Realizes FR-18, FR-19, FR-20.

| Step | Action | Realizes | Notes / owner |
|------|--------|----------|---------------|
| 1 | Assemble the Trace (query, context ref, draft answer, critique scores, routing decision, latency, corpus version). | FR-18 | Field semantics owned by `[340]`; schema by `[230]`. |
| 2 | Persist the Trace without blocking the response. | FR-19 | — |
| 3 | Serve aggregate metrics on request. | FR-20 | Metric definitions owned by `[340]`. |

## Workflow Overview

```
W-1 Ingestion (offline) ──> populated corpus
                                   │
User query ─> W-2 [embed→retrieve→rerank→assemble→generate→critique→decision]
                                   │
                sufficient ────────┴──────── insufficient
                    │                             │
             return answer                  W-3 Fallback
                    │                             │
                    └────────────> W-4 Logging <──┘  (async, non-blocking)
```

## Assumptions

None introduced. W-3 depends on A-3 (retry bound) and FR-17/A-5 (optional tool), owned by `[120]`.

## References

- `leon.md` §3, §4, §7 — flow source.
- `[110]` — entities; `[140]` — FRs realized; `[130]` — corpus/chunking.
- `[210]` — control-flow owner (forward reference).
- `[000]` — Engineering Manual.

## Open Questions

None blocking. Decision-point mechanics (step 8 / W-3 step 1) are intentionally deferred to `[210]`; if `[210]` refines step ordering, this document updates via lightweight amendment (`[000 §9.4]`).

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (flows here; routing deferred to `[210]`) — `[000 §8.1.2]`
- [x] No duplication (FRs referenced by ID) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (workflow tables) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` and FRs — `[000 §8.1.9]`
- [x] Workflows reference FRs and defer control flow to `[210]` — `[000 §8.3]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — the functional sequence is stable but may be refined as `[200]`/`[210]` detail lands, via lightweight amendment (`[000 §9.4]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial four workflows (ingestion, query→answer, fallback, logging). | ADR-0001 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: added `[120]` input (A-3/A-5 referenced) — dependency reconciliation (M6). | — |
