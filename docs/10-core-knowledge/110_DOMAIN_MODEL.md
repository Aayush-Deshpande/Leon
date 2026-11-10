---
id: "110"
title: "Domain Model"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["leon.md", "010", "100"]
outputs: ["130", "140", "150", "200", "210", "220", "230", "240", "330"]
category: "Core Knowledge"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0001"]
---

# 110 — Domain Model

> Governed by `[000]`, structured per `[001]`. Owns the **conceptual** domain entities and their relationships. Term *definitions* are owned by `[010]`; storage *schemas* by `[230]`; interface *shapes* by `[220]`. This document adds the relationships/cardinality between entities, not their definitions or persistence.

## Purpose

Establish one shared conceptual model of Leon's domain entities and how they relate, so every subsystem models "chunk", "citation", "trace", etc. consistently.

## Scope

Covers domain entities and their relationships as a conceptual model. This document does **not** cover storage schemas or indexes (`[230]`), API/tool shapes (`[220]`), control-flow behavior (`[210]`), model choices (`[240]`), or term definitions (`[010]`).

## Owned Concepts

1. The set of conceptual domain entities.
2. The relationships and cardinalities between those entities.

## Must Never Contain

- Term definitions — owned by `[010]` (referenced here).
- Physical storage schemas, field types, indexes — owned by `[230]`.
- API/MCP request/response shapes — owned by `[220]`.
- Control flow, routing, thresholds — owned by `[210]`.
- Model/algorithm choices — owned by `[240]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `leon.md` | Source of the domain (legal corpus, RAG entities, trace). |
| `[010]` | Canonical definitions of the terms named here. |
| `[100]` | Orientation into the relevant `leon.md` sections. |

## Downstream Consumers (Outputs)

`[130]`, `[140]`, `[150]`, `[200]`, `[210]`, `[230]`, `[240]`, `[300]` build on these entities and relationships.

## Domain Entities

Each entity is defined in `[010]`; this table records its role in the model and its key relationships (not its definition or storage).

| Entity | Role in the model | Key relationships |
|--------|-------------------|-------------------|
| **Corpus** | The bounded body of source material. | contains 1..* Source Document. |
| **Source Document** | A single legal document (statute or case-law item). | belongs to 1 Corpus; composed of 1..* Section; is-ground-truth-for Citation verification. |
| **Section** | A logical division of a Source Document (e.g., a statutory section/clause). | part-of 1 Source Document; source-of 0..* Chunk. |
| **Chunk** | The unit of retrieval and citation. | derived-from 1 Section (of 1 Source Document); carries 1 Metadata; embedded-as 1 Embedding; referenced-by 0..* Citation. |
| **Metadata** | The descriptive attributes attached to a Chunk (e.g., source document, section identifier, jurisdiction, document type). | attached-to 1 Chunk. (Concrete field set/schema owned by `[230]`.) |
| **Embedding** | The vector representation of a Chunk or Query. | of exactly 1 Chunk **or** 1 Query. |
| **Query** | A user's natural-language legal question. | initiates 1 Retrieval; embedded-as 1 Embedding; answered-by 0..1 Answer. |
| **Retrieved Candidate** | A Chunk returned by retrieval for a Query, with a relevance ranking. | references 1 Chunk; produced-for 1 Query; ranked-by Reranker. |
| **Context** | The top-ranked set of Retrieved Candidates assembled for generation. | composed-of 1..* Retrieved Candidate; input-to Generation and Self-Critique. |
| **Answer** | The draft/final response to a Query. | answers 1 Query; grounded-in 1 Context; contains 0..* Citation; evaluated-by 1 Critique Judgment. |
| **Citation** | A reference within an Answer to specific source material. | part-of 1 Answer; points-to 1 Chunk (and thereby its Section/Source Document); verifiable-against Source Document. |
| **Critique Judgment** | The structured evaluation of an Answer against its Context. | evaluates 1 Answer; yields relevance and groundedness assessments and a list of unverifiable Citations. |
| **Fallback Action** | A corrective action taken when a Critique Judgment is insufficient. | triggered-by 1 Critique Judgment; may re-initiate Retrieval or invoke an MCP Tool or produce a low-confidence Answer. (Selection logic owned by `[210]`.) |
| **MCP Tool** | An externally callable capability (e.g., citation verification). | invoked-by Fallback Action; operates-on Citation and/or Source Document. (Contract owned by `[220]`.) |
| **Trace** | The accumulating record of one Query's journey. | spans 1 Query → Context → Answer → Critique Judgment → Fallback Action(s); persisted for evaluation. (Field semantics owned by `[340]`, schema by `[230]`.) |

## Entity Relationship Overview

```
Corpus 1─* Source Document 1─* Section 1─* Chunk 1─1 Embedding
                                   Chunk 1─1 Metadata
Query 1─1 Embedding
Query 1─* Retrieved Candidate *─1 Chunk
Retrieved Candidate *─1 Context (top-ranked subset)
Context 1─1 Answer *─* Citation *─1 Chunk
Answer 1─1 Critique Judgment 1─0..* Fallback Action
Fallback Action 0..* MCP Tool
Trace 1─1 Query (spans the whole chain above)
```

## Assumptions

None introduced here. Assumptions affecting the domain (e.g., corpus scope) are owned by `[120]` and elaborated in `[130]`.

## References

- `leon.md` §1–§10 — domain source.
- `[010]` — term definitions.
- `[100]` — navigation index.
- `[000]` — Engineering Manual.

## Open Questions

None blocking. Metadata's concrete attribute set is intentionally deferred to `[230]`; this document fixes only that Metadata attaches to a Chunk.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity — `[000 §8.1.2]`
- [x] No duplication (definitions deferred to `[010]`, schema to `[230]`) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Explicit assumptions in `[120]` — `[000 §8.1.7]`
- [x] Determinism (entity + relationship tables) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — a foundational conceptual contract that `[130]`, `[140]`, `[150]`, and all Architecture documents build on; changes cascade widely and therefore require a full Change Request (`[000 §9]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial conceptual domain model (14 entities + relationships). | ADR-0001 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: reconciled `outputs` (M6) — added 220/330, removed spurious 300. | — |
