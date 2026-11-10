---
id: "010"
title: "Glossary"
status: "Frozen"
freeze_class: "living"
owner: "Engineering Documentation Lead"
version: "0.4"
inputs: ["leon.md"]
outputs:
  - "005"
  - "020"
  - "100"
  - "110"
  - "120"
  - "130"
  - "200"
  - "210"
  - "220"
  - "230"
  - "240"
  - "300"
  - "310"
  - "320"
  - "330"
  - "340"
  - "400"
  - "41x"
  - "500"
  - "610"
  - "620"
  - "690"
  - "900"
category: "Governance"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: []
---

# 010 — Glossary

> This document is governed by `[000]` and structured per `[001]`. It is the single source of truth for project vocabulary. It defines what terms *mean* — never how components behave, what values policies take, or how data is stored (those are owned by the architecture and standards documents and are pointed to under "See also").

## Purpose

Define every domain and technical term used across Project Leon exactly once, so that all documents and all activities use the same vocabulary with the same meaning.

## Scope

Covers terminology only: the canonical, concept-level definition of each term. This document does **not** cover design decisions, component behavior, policy values, storage schemas, requirements, or prompts — those are owned by their respective documents (`[110]`, `[120]`, `[130]`, `[200]`–`[240]`, `[300]`–`[340]`) and are referenced here, never restated.

## Owned Concepts

1. The canonical definition of every project term (the SSoT for vocabulary, per `[000 §6]` rule 5).

## Must Never Contain

- Design decisions or component behavior — owned by `[200]`, `[210]`, `[240]`.
- Policy values (e.g., thresholds, retry caps, top-N) — owned by `[210]` / `[240]`.
- Storage schemas or field layouts — owned by `[230]`.
- Metric semantics — owned by `[340]`.
- Requirements, assumptions, or scope — owned by `[120]` (and `leon.md`).
- Prompt text — owned by `[330]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | Source of the initial domain and technical vocabulary this glossary is seeded from. |

## Downstream Consumers (Outputs)

All project documents and all engineering activities consume this glossary; every specialized term used anywhere must be defined here and cited on first use (`[000 §8.1.6]`).

## Glossary of Terms

Terms are listed alphabetically. Definitions are concept-level only. "See also" points to the document that owns any associated design, behavior, value, or schema — consult the owner for those; do not infer them from the definition.

| Term | Definition | See also (owner) |
|------|------------|------------------|
| **Agent controller** (Orchestration controller) | The component whose role is to decide a query's routing outcome after critique. | `[200]`, `[210]` |
| **Answer** | The natural-language response returned to a user for a query, accompanied by citations. | `[220]` |
| **BM25** | A sparse, term-frequency ranking function used for exact-keyword retrieval. | `[230]`, `[240]` |
| **Case law** | Judicial decisions that may form part of the legal corpus. | `[130]` |
| **Chunk** | A discrete segment of a source document; the unit of retrieval and citation. | `[130]`, `[230]` |
| **Chunking** | The process of splitting source documents into chunks. | `[130]` |
| **Citation** | A reference within an answer to the specific source passage(s) it draws from. | `[220]` |
| **Citation marker** | An inline token in generated answer text linking a statement to a specific chunk. | `[330]` |
| **Citation verification** | Checking whether a cited section or clause actually exists in the source material. | `[220]` |
| **Confidence** | A qualitative indication of how well-grounded an answer is, derived from critique output. | `[210]`, `[340]` |
| **Corpus** | The bounded set of legal source documents the system retrieves from. | `[130]` |
| **Correctness property** | An executable, checkable statement the system must always satisfy. | `[320]` |
| **Cross-encoder** | A model type that jointly scores a query–candidate pair for relevance. | `[240]` |
| **Dense retrieval** | Retrieval by similarity between embedding vectors. | `[240]` |
| **Embedding** | A fixed-dimension vector representation of text used for semantic similarity. | `[240]` |
| **Evaluation harness** | The mechanism that records per-query metrics for later analysis. | `[340]` |
| **Fallback** (corrective action) | An alternative path taken when critique confidence is insufficient. | `[210]` |
| **Generation** | Producing a draft answer from a query and retrieved context. | `[240]`, `[330]` |
| **Groundedness** | The degree to which an answer's claims and citations are traceable to retrieved source text. | `[340]` |
| **Groundedness score** | A critique output rating how well an answer's citations are supported by source text. | `[340]` |
| **Hybrid retrieval** | Retrieval that combines dense and sparse methods before reranking. | `[240]` |
| **In-loop evaluation** | Evaluation performed as a decision node within the agent's control flow, not after the fact. | `[210]` |
| **Ingestion** | The offline pipeline that turns raw documents into indexed, searchable chunks. | `[200]`, `[130]` |
| **Jurisdiction** | The legal system a document belongs to; a metadata attribute of a chunk. | `[130]` |
| **Low-confidence response** | An answer explicitly flagged as insufficiently grounded, advising professional consultation. | `[210]` |
| **MCP** (Model Context Protocol) | The protocol by which the system exposes callable tools. | `[220]` |
| **MCP tool** | A callable capability exposed via MCP (e.g., citation verification). | `[220]` |
| **Metadata** | Descriptive fields attached to a chunk (e.g., source document, section, jurisdiction). | `[230]` |
| **Query** | A user's natural-language legal question submitted to the system. | — |
| **Query reformulation** | Rewriting a query to retry retrieval when initial results are insufficient. | `[210]` |
| **RAG** (Retrieval-Augmented Generation) | An approach that grounds generated answers in retrieved source material. | — |
| **Raw document storage** | Storage of original source documents used as ground truth for citation verification. | `[230]`, `[130]` |
| **Relevance score** | A critique output rating how relevant retrieved context is to the query. | `[340]` |
| **Reranker** | A model that reorders merged retrieval candidates by relevance. | `[240]` |
| **Retrieval** | Obtaining candidate context passages relevant to a query. | `[200]`, `[240]` |
| **Retry cap** | The maximum number of reformulation attempts before falling through to a low-confidence response. | `[210]` |
| **Self-critique** | An independent evaluation step scoring a draft answer's relevance and citation-groundedness. | `[210]`, `[240]`, `[330]` |
| **Sparse retrieval** | Keyword-based retrieval using term matching (BM25). | `[230]`, `[240]` |
| **Statute** | A written law that may form part of the corpus. | `[130]` |
| **Threshold** | The cutoff against which critique scores are compared to route the response. | `[210]` |
| **Top-N / Top-k** | The count of highest-ranked candidates carried forward from a ranking step. | `[240]` |
| **Trace object** (trace) | The accumulating record of a query's intermediate data through the pipeline. | `[230]`, `[340]` |
| **Vector store** | The store holding chunk embeddings for dense retrieval. | `[230]` |

### Addendum — Terms added in v0.2 (Core Knowledge sprint)

Appended per the living-document rule (`[000 §7]`); existing v0.1 definitions above are unchanged. These will be merged into the main alphabetical table at the next glossary maintenance revision.

| Term | Definition | See also (owner) |
|------|------------|------------------|
| **Bare act** | The complete enacted text of a statute, without commentary or annotation. | `[130]` |
| **Citation granularity** | The level (e.g., section, sub-section/clause, paragraph) at which a citation resolves. | `[130]` |
| **Context** | The top-ranked set of retrieved candidates assembled as input for generation and critique. | `[110]`, `[240]` |
| **Corpus version** | An identified snapshot of the corpus and its source set at a point in time. | `[130]` |
| **Critique judgment** | The structured evaluation output of the self-critique step (relevance, groundedness, unverifiable citations). | `[110]`, `[340]` |
| **Fallback action** | The corrective action taken when critique confidence is insufficient. | `[110]`, `[210]` |
| **Functional requirement** | A discrete, testable statement of what the system must do. | `[140]` |
| **Non-goal** | A capability or objective explicitly excluded from scope. | `[120]` |
| **Provenance** | The recorded origin and acquisition detail of a source document. | `[130]` |
| **Retrieved candidate** | A chunk returned by retrieval for a query, carrying a relevance ranking. | `[110]` |
| **Scope boundary** | An explicit limit on what the project covers. | `[120]` |
| **Section (statutory)** | A logical division of a statute; a primary unit of citation. | `[110]`, `[130]` |
| **Sliding-window chunking** | Chunking that produces overlapping text windows to avoid severing content at edges. | `[130]` |
| **Sub-section / Clause** | A subdivision of a statutory section. | `[110]`, `[130]` |
| **System workflow** | An ordered, end-to-end functional sequence composing multiple requirements. | `[150]` |

### Addendum — Terms added in v0.3 (Architecture sprint)

| Term | Definition | See also (owner) |
|------|------------|------------------|
| **Confidence indicator** | A user-facing signal of an answer's confidence level (e.g., high/low). | `[210]`, `[220]` |
| **Routing metadata** | Data describing which control-flow outcome/path produced a response. | `[210]`, `[220]` |
| **Server-Sent Events (SSE)** | A unidirectional server-to-client streaming protocol over HTTP. | `[220]` |

### Addendum — Terms added in v0.4 (Engineering Standards sprint)

| Term | Definition | See also (owner) |
|------|------------|------------------|
| **Property-based testing** | Testing that verifies properties hold over many generated inputs, rather than fixed examples. | `[320]` |
| **Retrieval precision proxy** | A proxy metric for retrieval quality: the mean reranker relevance score of the top-k candidates. | `[340]` |
| **Fallback rate** | The fraction of queries whose routing outcome is not a direct return. | `[340]` |

## Assumptions

None. This glossary introduces no assumptions. Any assumption belongs in `[120]` per `[000 §1.7]`.

## References

- `[000]` — Engineering Manual (governing document; ownership and lifecycle rules).
- `[001]` — Document Template (structure this document conforms to).
- `leon.md` — Seed specification; source of the initial vocabulary.

## Open Questions

None blocking. This is a living document (`[000 §7]`): new terms are appended as later documents introduce them, and each definition freezes once referenced.

## Review Checklist

- [ ] Single Responsibility — `[000 §8.1.1]`
- [ ] Ownership integrity: Owned Concepts + Must Never Contain honored — `[000 §8.1.2]`
- [ ] No duplication; definitions do not restate design/behavior/values — `[000 §8.1.3]`
- [ ] Dependency validity: `inputs`/`outputs` accurate — `[000 §8.1.4]`, `[000 §8.5]`
- [ ] Template conformance: skeleton + citation format followed — `[000 §8.1.5]`
- [ ] Vocabulary conformance: definitions are self-consistent — `[000 §8.1.6]`
- [ ] Explicit assumptions in `[120]` (none here) — `[000 §8.1.7]`
- [ ] Determinism: terms in a structured table — `[000 §8.1.8]`
- [ ] Traceability: terms trace to `leon.md` / owning documents — `[000 §8.1.9]`
- [ ] Frontmatter complete and valid; `status` reflects reality — `[000 §7]`

## Freeze Class

`living` — semantics owned by `[000 §1.6]` / `[000 §7]`; fixed by the roadmap entry `[000 §3]`. New terms may be appended at any time; a definition freezes once another document references it.

## Status

`Frozen` (living; definitions freeze on first reference). Authoritative status is the `status` frontmatter field. Semantics: `[000 §7]`.

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | (pending) | Engineering Documentation Lead | Initial seed of 42 terms drawn from `leon.md`. | — |
| 0.2 | 2026-07-05 | Engineering Documentation Lead | Appended 15 terms from the Core Knowledge sprint (addendum). | ADR-0001 |
| 0.3 | 2026-07-05 | Engineering Documentation Lead | Appended 3 terms from the Architecture sprint (addendum). | — |
| 0.4 | 2026-07-05 | Engineering Documentation Lead | Appended 3 terms from the Engineering Standards sprint (addendum). | — |
