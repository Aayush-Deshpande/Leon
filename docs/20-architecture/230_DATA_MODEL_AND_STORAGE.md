---
id: "230"
title: "Data Model and Storage"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.3"
inputs: ["110", "120", "130", "200", "220"]
outputs: ["240", "340", "400", "41x", "500", "610", "620"]
category: "Architecture"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0006", "ADR-0013", "ADR-0018", "ADR-0020"]
---

# 230 — Data Model and Storage

> Governed by `[000]`, structured per `[001]`. Owns concrete storage: vector store schema, sparse index structure, relational schema (traces + corpus metadata), and raw-document storage (`[000 §3]`). It contains no query logic (`[240]`/Impl), API shapes (`[220]`), or conceptual domain modeling (`[110]`).

## Purpose

Define how the domain entities (`[110]`) and prepared data (`[130]`) are physically stored and indexed, so ingestion, retrieval, and evaluation logging agree on one schema.

## Scope

Covers the storage stack, the dense/sparse index schemas, the relational schema for Traces and corpus metadata, the concrete Metadata field set, and raw-document storage/retention. This document does **not** cover retrieval/query algorithms (`[240]`), API shapes (`[220]`), conceptual entities (`[110]`), or metric semantics (`[340]`).

## Owned Concepts

1. The storage stack selection and its layout.
2. The vector store schema and Metadata field set.
3. The sparse (BM25) index structure.
4. The relational schema for Traces and corpus metadata.
5. Raw-document storage layout and retention.

## Must Never Contain

- Retrieval/ranking algorithms or query logic — owned by `[240]` and Implementation.
- API/tool request/response shapes — owned by `[220]`.
- Conceptual entity/relationship modeling — owned by `[110]`.
- Metric/field *meaning* — owned by `[340]` (this owns column types, not semantics).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[110]` | Entities (Chunk, Metadata, Trace, Source Document) being persisted. |
| `[130]` | Corpus/chunking spec determining what is stored and provenance. |
| `[200]` | Stores D1–D4 and which components read/write them. |
| `[220]` | Field shapes surfaced via APIs that must align with storage. |

## Downstream Consumers (Outputs)

`[240]`, `[300]`, `[320]`, `[340]`, ingestion/retrieval/evaluation phases, `[500]`, `[610]`.

## Storage Stack (ADR-0006)

Per ADR-0006 (`[900#ADR-0006]`), sized for the single-instance demo scope (A-8, `[120]`):

| Store | Technology | Rationale |
|-------|-----------|-----------|
| D1 Vector store | **PostgreSQL + `pgvector`** | Unifies vectors and relational data in one instance; adequate for demo-scale corpus. |
| D2 Sparse index | **Library-backed BM25** (persisted, rebuilt at ingestion) | Direct BM25 per `leon.md` §2.1/§5.2; no extra service. |
| D3 Relational store | **PostgreSQL** (same instance) | Traces + corpus metadata. |
| D4 Raw document store | **Filesystem** (local dir; S3-compatible optional later) | Ground truth for citation verification (`[130]`). |

Choices are revisitable defaults via lightweight amendment (`[000 §9.4]`); the *schemas* below are the hard contract.

## Vector Store Schema — `chunks` (D1)

| Column | Type | Notes |
|--------|------|-------|
| `chunk_id` | text PK | Stable chunk identifier. |
| `source_document_id` | text FK → `source_documents.doc_id` | Origin document. |
| `section_locator` | text | e.g., `Section 10`, `Section 10(2)`, `Judgment X ¶4` (citation granularity per `[130]`). |
| `doc_type` | text | `statute` \| `case_law`. |
| `jurisdiction` | text | e.g., `IN`. |
| `text` | text | Chunk text. |
| `embedding` | `vector(D)` | `D = 768`, fixed by the HARD embedding-model contract (ADR-0013, `[240]`). Changing `D` requires a CR + re-embedding migration, not a config change. |
| `corpus_version` | text | Corpus snapshot (`[130]`). |

The **Metadata field set** for a Chunk (deferred here from `[110]`) is: `source_document_id`, `section_locator`, `doc_type`, `jurisdiction`, `corpus_version`.

**Vector index (ADR-0006 amended):** HNSW on `embedding` using `vector_cosine_ops` (cosine similarity per `leon.md` §5.1), build params **`m = 16`, `ef_construction = 64`** (tunable defaults, `[470]`/`[500]`).

## Sparse Index Structure (D2)

- A BM25 index over the same chunk corpus, keyed by `chunk_id`, storing tokenized `text`.
- Tokenization/analysis per the **BM25 analyzer (ADR-0020, `[240]`)** — applied identically at build and query time.
- Built/rebuilt during ingestion for the active `corpus_version`; persisted to disk.
- Returns `(chunk_id, bm25_score)` candidates (consumed by retrieval, `[240]`).

## Relational Schema (D3)

### `source_documents`
| Column | Type | Notes |
|--------|------|-------|
| `doc_id` | text PK | |
| `title` | text | |
| `type` | text | `statute` \| `case_law`. |
| `citation_label` | text | Canonical label (e.g., "Indian Contract Act, 1872, s.10"). |
| `origin` | text | Provenance source (`[130]`). |
| `retrieved_at` | timestamptz | Provenance acquisition time. |
| `corpus_version` | text | |
| `raw_path` | text | Location in D4. |

### `traces`
Column *types* owned here; field *meaning* owned by `[340]`.
| Column | Type | Notes |
|--------|------|-------|
| `trace_id` | uuid PK | |
| `query_text` | text | |
| `created_at` | timestamptz | |
| `corpus_version` | text | |
| `retrieved_chunk_ids` | text[] | Context references (not full text). |
| `draft_answer` | text | |
| `relevance_score` | real | Meaning: `[340]`. |
| `groundedness_score` | real | Meaning: `[340]`. |
| `unverifiable_citations` | text[] | Citation locators flagged unverifiable. |
| `routing_outcome` | text | `returned`\|`reformulated`\|`tool_verified`\|`low_confidence` (`[210]`). |
| `reformulations` | int | Retry count used. |
| `reranker_topk_scores` | real[] | Reranker relevance scores of the top-k assembled candidates; supports the retrieval-precision-proxy metric (`[340]`). *(Added: review M1.)* |
| `confidence` | text | The returned confidence indicator `high`\|`low` (derivation owned by `[210]`; meaning by `[340]`). *(Added: review m2.)* |
| `latency_ms` | int | End-to-end. |

## Raw Document Store (D4)

- Original source documents stored under a version-scoped path layout: `corpus/<corpus_version>/<doc_id>.<ext>`.
- Immutable per corpus version; the citation-verification tool (`[220]`/C8) reads from here as ground truth (`[130]`).

## Retention

- Traces: retained indefinitely for the demo (no PII beyond query text; see `[310]`).
- Corpus artifacts: retained per `corpus_version`; superseded versions kept for reproducibility.

## Assumptions

None introduced. Single-instance stack follows A-8 (`[120]`).

## References

- `leon.md` §10 — storage source.
- `[110]`, `[130]`, `[200]`, `[220]` — inputs.
- `[340]` — meaning of trace fields.
- `[900#ADR-0006]` — storage stack decision.

## Open Questions

None. Embedding dimension is fixed: `D = 768` per the HARD embedding model `BAAI/bge-base-en-v1.5` (ADR-0018, `[240]`). Changing it is a CR + re-embedding migration.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (algorithms/semantics/API deferred) — `[000 §8.1.2]`
- [x] No duplication (types here; meaning in `[340]`) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (schema tables) — `[000 §8.1.8]`
- [x] Traceability to entities/corpus — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — storage schemas are a cross-boundary contract (ingestion, retrieval, evaluation build against them); changes require a full Change Request. The technology selections are revisitable defaults (`[000 §9.4]`).

## Status

`Frozen` (CR-0001 applied; re-frozen).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial storage stack + schemas (chunks, sparse, source_documents, traces, raw store). | ADR-0006 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: added `reranker_topk_scores` (M1) + `confidence` (m2) to traces; pinned `D` via ADR-0013 (M2); reconciled deps (M6). | ADR-0013 |
| 0.3 | 2026-07-06 | Engineering Documentation Lead | CR-0001: HNSW/cosine index params (ADR-0006 amend); BM25 analyzer ref (ADR-0020); pinned embedding model (ADR-0018); resolved O1. Re-frozen. | CR-0001 |
