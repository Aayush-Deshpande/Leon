---
id: "340"
title: "Observability and Evaluation"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.3"
inputs: ["210", "220", "230", "240"]
outputs: ["320", "330", "400", "41x", "610", "620"]
category: "Engineering Standards"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0012", "ADR-0016", "ADR-0021"]
---

# 340 — Observability and Evaluation

> Governed by `[000]`, structured per `[001]`. Owns metric definitions and the trace-logging contract — the *meaning* of each logged field and metric (`[000 §3]`). It contains no storage schema/types (`[230]` owns those) and no control-flow logic (`[210]`).

## Purpose

Precisely define Leon's evaluation metrics and the meaning of each trace field, so metrics are computed consistently and the system's real-world groundedness is measurable rather than assumed.

## Scope

Covers trace-field semantics, metric definitions, evaluation-summary semantics, and async logging behavior. This document does **not** cover storage column types/indexes (`[230]`), control-flow routing (`[210]`), API response shapes (`[220]`), or how scores are produced (`[240]`/`[330]`).

## Owned Concepts

1. The meaning of each `traces` field.
2. Metric definitions (relevance, groundedness, retrieval precision proxy, fallback rate, latency).
3. Evaluation-summary semantics.
4. The async trace-logging contract (what a complete trace is; non-blocking requirement meaning).

## Must Never Contain

- Storage column types/indexes — owned by `[230]` (referenced).
- Control-flow routing/thresholds — owned by `[210]`.
- API response shapes — owned by `[220]`.
- How scores are computed (model/prompt) — owned by `[240]`/`[330]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[210]` | Routing outcomes and retry counts whose meaning is logged. |
| `[230]` | The `traces` columns whose *meaning* this document defines. |
| `[240]` | The AI stages that produce the scores/latency being interpreted. |

## Downstream Consumers (Outputs)

`[320]` (P9), Implementation of `C9`/`GET /evaluation/summary`, `[610]`, `[620]`.

## Trace-Field Semantics (ADR-0012)

Per ADR-0012 (`[900#ADR-0012]`; HARD). Column types owned by `[230]`; meanings below.

| `traces` field | Meaning |
|----------------|---------|
| `query_text` | The user's submitted question (verbatim). |
| `corpus_version` | The corpus snapshot used to answer (`[130]`). |
| `retrieved_chunk_ids` | The chunk IDs in the assembled context (references, not text). |
| `draft_answer` | The generated answer prior to the return decision. |
| `relevance_score` | Critique's assessment ∈ [0,1] of how relevant the retrieved context is to the query. |
| `groundedness_score` | Critique's assessment ∈ [0,1] of how well the answer's citations are supported by the context. |
| `unverifiable_citations` | Citations the critique/tool could not support against context/ground truth. |
| `routing_outcome` | Which `[210]` terminal/branch outcome occurred (`returned`/`reformulated`/`tool_verified`/`low_confidence`). |
| `reformulations` | Count of reformulation attempts used (0..`MAX_REFORMULATIONS`). |
| `reranker_topk_scores` | The reranker relevance scores of the top-k assembled candidates; the basis of the retrieval precision proxy. |
| `confidence` | The returned confidence indicator (`high`/`low`); derivation owned by `[210]`. |
| `latency_ms` | End-to-end wall-clock time from query receipt to user-facing response. |

## Metric Definitions

| Metric | Definition |
|--------|------------|
| Relevance (avg) | Mean `relevance_score` over the query set. |
| Groundedness (avg) | Mean `groundedness_score` over the query set. |
| **Retrieval precision proxy** | Mean of the stored `reranker_topk_scores` (`[230]`) over the top-k assembled candidates (`leon.md` §2.6); a proxy for retrieval quality when no labeled relevance exists. Computed from persisted trace data (resolves review M1). |
| **Fallback rate** | Fraction of queries with `routing_outcome ≠ returned`. |
| Latency distribution | `p50` and `p95` of `latency_ms` over the query set. |
| Query count | Number of queries in the aggregation window. |

These definitions back the `GET /evaluation/summary` fields (shape owned by `[220]`).

> **Score-aggregation caveat (review O4):** `reranker_topk_scores` must be on a comparable scale before averaging. If the reranker emits unbounded logits, they are min-max/logistic-normalized to [0,1] at logging time so the proxy is meaningful across queries.

## Critique Calibration & Threshold Validation (ADR-0016, resolves review M5)

The pass/fail gate in `[210]` compares critique scores against thresholds. Those scores are LLM-judge outputs and are **not assumed calibrated**; this section defines how their validity is established. This is owned here; `[210]` thresholds are **provisional until calibrated**.

- **Calibration set (ADR-0021):** **≥ 100 labeled (query, answer) pairs, balanced 50 grounded / 50 ungrounded**, drawn from the corpus (`[130]`). Ungrounded cases are synthesized by injecting fabricated citations or pairing answers with irrelevant context. Labeling is performed by the operator (single-tenant demo, `[120]` A-4).
- **Critique-agreement metric:** accuracy of the critique verdict (grounded vs. ungrounded, using candidate thresholds) against the labels. Measures whether the critique + thresholds actually separate grounded from ungrounded answers.
- **Threshold-setting procedure:** `T_relevance` and `T_groundedness` (`[210]`) are chosen to **maximize agreement** on the calibration set, not by fiat. Re-run when the generation/critique model or prompts (`[330]`) change.
- **Gate:** `[320]` P11 requires **critique-agreement ≥ 0.80** on the calibration set before the thresholds are considered validated.

## Async Logging Contract

- A **complete trace** contains all fields above for one query.
- The trace is assembled and persisted **after** the user-facing response is sent and **must not block** it (FR-19; verified by `[320]` P9).
- Every `[210]` `DECIDE` outcome is recorded via `routing_outcome` (+ `reformulations`).

## Assumptions

None introduced.

## References

- `[210]`, `[230]`, `[240]` — inputs.
- `[220]` — summary response shape; `leon.md` §2.6 — metric intent.
- `[900#ADR-0012]`.

## Open Questions

None blocking. Aggregation window/granularity for the summary is an implementation detail; definitions here are window-agnostic.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (meaning here; types in `[230]`) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` (none) — `[000 §8.1.7]`
- [x] Determinism (definition tables) — `[000 §8.1.8]`
- [x] Metrics precisely defined — `[000 §3]` 340 intent
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — metric definitions and trace-field semantics are contracts consumed by `[320]` tests and the `[220]` summary; new metrics may be *added* via CR, but changing a definition requires a full Change Request (`[000 §3]` 340 rule).

## Status

`Frozen` (CR-0001 applied; re-frozen).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial trace-field semantics + metric definitions + async logging contract. | ADR-0012 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: proxy computable from stored scores (M1); confidence semantics (m2); calibration approach (M5); score-normalization caveat (O4); reconciled deps (M6). | ADR-0016 |
| 0.3 | 2026-07-06 | Engineering Documentation Lead | CR-0001: concrete calibration protocol — ≥100 balanced samples, agreement ≥0.80 (ADR-0021). Re-frozen. | CR-0001 |
