---
id: "140"
title: "Functional Requirements"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["leon.md", "010", "100", "110", "120", "130"]
outputs: ["150", "200", "210", "220", "320", "020"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001"]
---

# 140 — Functional Requirements

> Governed by `[000]`, structured per `[001]`. Owns the discrete, testable statements of *what* Leon must do (`[900#ADR-0001]`). It states observable behavior only; *how* each requirement is met is owned by Architecture (`[200]`–`[240]`), and workflow ordering by `[150]`.

## Purpose

Provide a numbered, individually testable set of functional requirements that design must satisfy, tests must cover, and the traceability matrix (`[020]`) maps against.

## Scope

Covers functional requirements (`FR-n`) as observable "the system shall …" statements. This document does **not** cover implementation mechanism (200-series), interface shapes (`[220]`), data schemas (`[230]`), control-flow routing (`[210]`), non-goals/assumptions (`[120]`), or workflow ordering (`[150]`).

## Owned Concepts

1. The authoritative set of functional requirement statements and their `FR-n` identifiers.

## Must Never Contain

- *How* a requirement is realized — owned by `[200]`/`[210]`/`[240]`.
- Interface shapes and status codes — owned by `[220]`.
- Data schemas — owned by `[230]`.
- Workflow step ordering — owned by `[150]` (references FRs).
- Non-goals/assumptions — owned by `[120]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | Source of features (§2), user flow (§3), API intent (§9). |
| `[010]` | Terms used in requirement statements. |
| `[100]` | Navigation into `leon.md`. |
| `[110]` | Entities referenced by requirements. |
| `[120]` | Scope boundaries, non-goals, assumptions that bound requirements. |
| `[130]` | Corpus/ground-truth referenced by FR-16 (citation verification). |

## Downstream Consumers (Outputs)

`[150]` sequences these FRs; `[200]`–`[240]` must satisfy each; `[320]` tests trace to them; `[020]` records the mapping.

## Functional Requirements

Each requirement is observable and verifiable. "Traces to" cites the seed; mechanism is deferred to the owner noted where relevant.

| ID | The system shall … | Traces to | Verified by (acceptance) |
|----|---------------------|-----------|--------------------------|
| FR-1 | Accept a natural-language legal question as input. | `leon.md` §3 | A submitted question is accepted and processed. |
| FR-2 | Retrieve candidate passages from the corpus using hybrid retrieval (dense + sparse/BM25). | `leon.md` §2.1 | Trace shows both dense and sparse candidates contributed. |
| FR-3 | Rerank the merged candidate set before use. | `leon.md` §2.1, §5.3 | Trace shows a reranked ordering distinct from raw retrieval. |
| FR-4 | Assemble a top-N context with citation metadata for each included passage. | `leon.md` §4 (Stage 2) | Context carries per-passage source metadata. |
| FR-5 | Generate an answer grounded in the assembled retrieved context. | `leon.md` §2.2 | Answer content is attributable to context passages. |
| FR-6 | Include, in each answer, citations to the specific source passage(s) used. | `leon.md` §2.2 | Every substantive claim carries a citation marker. |
| FR-7 | Refuse or hedge when context is insufficient, rather than answering from parametric knowledge. | `leon.md` §5.4 | With empty/irrelevant context, the system does not fabricate an answer. |
| FR-8 | Evaluate, before returning, both (a) retrieval relevance and (b) citation-groundedness of the draft answer against the retrieved context. | `leon.md` §2.3, §5.5 | Trace contains a relevance score and a groundedness score. |
| FR-9 | Identify any citations in the draft answer that cannot be verified against the retrieved source text. | `leon.md` §5.5 | Unverifiable citations are listed in the critique output. |
| FR-10 | Perform the critique as an evaluation distinct from generation, before the return decision. | `leon.md` §5.5, §5.6 | Trace records a separate critique step preceding routing. |
| FR-11 | Return the answer with its citations when critique confidence is sufficient. | `leon.md` §3 (step 8) | Sufficient-confidence queries return an answer + citations. |
| FR-12 | Take a corrective action rather than returning the answer when critique confidence is insufficient. | `leon.md` §2.4, §3 (step 9) | Insufficient-confidence queries never return the draft unconditionally. |
| FR-13 | Support corrective actions including query reformulation + re-retrieval, MCP tool invocation, and an explicit low-confidence response. | `leon.md` §2.4 | Each corrective action type is exercisable and recorded in routing metadata. |
| FR-14 | Bound the number of reformulation retries and, when exhausted, return an explicit low-confidence response. | `leon.md` §7 (retry bound, A-3) | Beyond the bound, the system returns a low-confidence response (bound value owned by `[210]`). |
| FR-15 | Make a low-confidence response clearly indicate low confidence and advise consulting a professional. | `leon.md` §1 NG-1, §3 (step 9) | Low-confidence responses contain the advisory and a stated reason. |
| FR-16 | Expose a citation-verification capability via MCP that checks whether a cited section/clause exists in the source documents. | `leon.md` §2.5, §9 | The tool returns exists/not-found against raw source text (`[130]`). |
| FR-17 | Optionally expose a web-search fallback tool, used only when the corpus lacks coverage. **Deferred** (A-5): not present in the `[210]` control flow until enabled by a future ADR. | `leon.md` §2.5 (A-5) | If enabled, invoked only on corpus-miss; system functions fully without it (review m4). |
| FR-18 | Log every query with retrieved-context reference, draft answer, critique scores, **reranker top-k scores**, routing/fallback decision, confidence, and end-to-end latency. | `leon.md` §2.6, §4 (Stage 6) | A per-query trace record contains all listed fields (incl. reranker scores — review M1). |
| FR-19 | Perform evaluation logging without blocking the user-facing response. | `leon.md` §3 (step 11), §7 | User response latency is unaffected by logging. |
| FR-20 | Expose aggregate evaluation metrics (e.g., average groundedness, fallback rate, latency distribution) for monitoring. | `leon.md` §9 | An internal summary reports the aggregate metrics. |
| FR-21 | Provide a query interface that returns the final answer, its citations, a confidence indicator, and routing metadata. | `leon.md` §9 | The query response includes all four elements (shape owned by `[220]`). |
| FR-22 | Provide a health/readiness check. | `leon.md` §9 | A liveness/readiness signal is available. |
| FR-23 | Present each citation such that the user can view the underlying source passage. | `leon.md` §3 (step 10) | Each citation exposes/links its source passage. |
| FR-24 | Operate on single-turn queries, without multi-turn conversational memory. | `[120]` SB-3 | No cross-query session state is used to answer. |
| FR-25 | Process English queries against the English corpus. | `[120]` SB-4 | Non-English support is absent by design. |

## Assumptions

None introduced. FR-14 depends on assumption A-3 (retry bound) and FR-17 on A-5, both owned by `[120]`.

## References

- `leon.md` §2, §3, §4, §5, §9 — feature and flow source.
- `[110]` — entities; `[120]` — scope/non-goals/assumptions; `[130]` — corpus ground truth for FR-16.
- `[000]` — Engineering Manual.

## Open Questions

None blocking. Threshold values (FR-11/FR-12) and the retry bound (FR-14) are intentionally deferred to `[210]`; this document fixes only the observable behavior.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (behavior here; mechanism deferred) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (FR table) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` — `[000 §8.1.9]`
- [x] Each FR individually testable — `[000 §8.3]` Core Knowledge
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — the set of functional requirements is a contract for design, tests, and traceability; changes require a full Change Request (`[000 §9]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial 25 functional requirements derived from `leon.md`. | ADR-0001 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: FR-18 adds reranker scores/confidence (M1); FR-17 marked deferred (m4); added `[130]` input (M6). | — |
