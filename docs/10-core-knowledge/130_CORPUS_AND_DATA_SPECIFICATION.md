---
id: "130"
title: "Corpus and Data Specification"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["leon.md", "010", "100", "110", "120"]
outputs: ["140", "230", "240", "320", "400", "41x"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001", "ADR-0002"]
---

# 130 — Corpus and Data Specification

> Governed by `[000]`, structured per `[001]`. Owns *what data goes in and how it is shaped*: corpus scope, provenance/licensing, versioning, and chunking strategy (`[000 §3]`). Storage/indexing of that data is owned by `[230]`; model/embedding choices by `[240]`. Resolves blocking assumption A-1 (`[120]`).

## Purpose

Fix the corpus definition and the data-preparation decisions (segmentation/chunking, citation granularity, provenance) that determine retrieval quality and citation traceability, so ingestion is not set implicitly by whichever task runs first.

## Scope

Covers corpus scope, sources/provenance, licensing, corpus versioning, chunking strategy, citation granularity, and the ground-truth set used for citation verification. This document does **not** cover storage schemas/indexes (`[230]`), embedding/reranker/model choices (`[240]`), or retrieval/ingestion code (Implementation).

## Owned Concepts

1. Corpus scope and the concrete source set.
2. Provenance and licensing of the sources.
3. Corpus versioning scheme.
4. Chunking strategy and citation granularity.
5. The raw-document ground-truth set used for citation verification (its *definition*, not its storage — schema owned by `[230]`).

## Must Never Contain

- Storage schemas, index structures, metadata field types — owned by `[230]`.
- Embedding model, dimensions, reranker, or LLM choices — owned by `[240]`.
- Ingestion/retrieval implementation — owned by Implementation (400-series).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | Corpus-scope assumption (§11.1), data storage intent (§10). |
| `[010]` | Definitions of corpus, chunk, section, citation, jurisdiction. |
| `[100]` | Navigation into `leon.md`. |
| `[110]` | Domain entities (Corpus, Source Document, Section, Chunk, Citation) this specification instantiates. |
| `[120]` | Assumption A-1 (scope), SB-4 (English), NG-2 (single jurisdiction) constrain this spec. |

## Downstream Consumers (Outputs)

`[140]`, `[230]`, `[240]`, `[320]`, and the ingestion/retrieval phases (`[400]`/`41x`) build on this specification.

## Corpus Scope (resolves A-1)

Per ADR-0002 (`[900#ADR-0002]`), adopting the corpus scope already proposed in `leon.md` §11.1 (which does not change project objectives or architecture):

- **Primary statute:** The **Indian Contract Act, 1872** — the complete bare act (all sections, in force as amended to the corpus version date).
- **Associated case law:** A **bounded, curated set** of leading Indian judgments (Supreme Court and High Courts) that interpret key sections of the Act. The set is fixed per corpus version and small by design (demo-scale, SB-2); it is not an open-ended case-law crawl.
- **Jurisdiction:** India only (NG-2).
- **Language:** English only (SB-4).

This closes A-1: status → RESOLVED in `[120]`.

## Sources and Provenance

| Source type | Origin | Notes |
|-------------|--------|-------|
| Statute (bare act) | Official published text of the Indian Contract Act, 1872 (as maintained in the national statutory record). | Canonical section numbering preserved verbatim. |
| Case law | Full-text judgments from official/public court records. | Only the curated bounded set for the active corpus version. |

Each ingested Source Document records its origin and retrieval date as provenance (the *storage* of provenance fields is owned by `[230]`; this document mandates that provenance is captured).

## Licensing

- Indian statutory texts and court judgments are government/public works and are used here for an informational, non-commercial demo (consistent with NG-1). No third-party proprietary reporter content, headnotes, or annotations are included.
- **Constraint L-1:** If any candidate case-law source carries third-party editorial content under restrictive licensing, it is excluded from the corpus. Only primary, freely-usable text is ingested.

## Corpus Versioning

- The corpus is identified by a version string `corpus-vMAJOR.MINOR` plus an ingestion timestamp.
- MAJOR increments when the source set changes (a statute amendment is incorporated, or the curated case set changes); MINOR increments for re-ingestion without source-set change.
- Every Trace records the corpus version used (field storage owned by `[230]`, meaning owned by `[340]`).

## Chunking Strategy

Chunking is **structure-aligned** to preserve citation traceability:

| Source | Segmentation | Overlap | Rationale |
|--------|--------------|---------|-----------|
| Statute | One chunk per **Section**; long sections split at **sub-section/clause** boundaries. | None between distinct sections; boundary-aligned. | Legal citation is section/clause-precise; structure-aligned chunks make citations verifiable. |
| Case law | Split by natural paragraph/heading; group into windows of approximately **512 tokens** with about **12% overlap**. | ~12% sliding-window overlap. | Judgments lack clean atomic units; overlap avoids severing reasoning across chunk edges. |

- **Chunk size bound:** target ≤ 512 tokens per chunk; never split mid-sentence.
- Each chunk retains a stable identifier and the provenance/section metadata needed for citation (attribute *set/schema* owned by `[230]`).

## Citation Granularity

- **Statute:** citations resolve to **Section (and sub-section/clause where applicable)** of the Indian Contract Act, 1872.
- **Case law:** citations resolve to **judgment + paragraph** (or nearest cited passage).
- The **ground truth** for citation verification is the **raw Source Document** (not the chunked/embedded form), per `leon.md` §10 — the MCP citation-verification tool checks a cited section/passage against this raw text.

## Assumptions

- A-1 is **resolved** by this document (see Corpus Scope). No new assumptions introduced.
- Constraint L-1 (licensing exclusion) is recorded above and owned here.

## References

- `leon.md` §10, §11.1 — data storage and corpus-scope assumption.
- `[110]` — domain entities instantiated here.
- `[120]` — A-1, SB-4, NG-2.
- `[900#ADR-0002]` — corpus-scope confirmation decision.

## Open Questions

None blocking. The *specific membership* of the curated case-law set is an ingestion-time selection constrained by this spec (bounded, primary-text-only, interprets key sections); enumerating individual judgments is an ingestion-phase deliverable, not a Core Knowledge decision.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (data-what/why here; storage in `[230]`) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance (new terms appended to `[010]`) — `[000 §8.1.6]`
- [x] Explicit assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (tables) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — corpus scope and chunking strategy are contracts that retrieval (`[240]`), storage (`[230]`), and citation verification build against; changes require a full Change Request (`[000 §9]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial corpus/data spec; resolved A-1 (corpus scope). | ADR-0001, ADR-0002 |
