---
id: "330"
title: "Prompt Engineering Standards"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["110", "120", "210", "220", "240", "340"]
outputs: ["400", "41x", "610", "620"]
category: "Engineering Standards"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0011"]
---

# 330 — Prompt Engineering Standards

> Governed by `[000]`, structured per `[001]`. Owns all prompt templates and their output-formatting contracts, plus prompt versioning/change policy (`[000 §3]`). It contains no model architecture (`[240]`), control-flow routing (`[210]`), or code. It references which model runs a prompt (`[240]`) and when it runs (`[210]`).

## Purpose

Centralize the load-bearing prompt logic of the RAG pipeline so prompts are discoverable, versioned, testable, and consistent — not scattered across code.

## Scope

Covers the generation, critique, and reformulation prompt templates; the critique structured-output contract; anti-hallucination instruction patterns; and prompt versioning/change policy. This document does **not** cover model choice/behavior (`[240]`), routing/thresholds (`[210]`), storage (`[230]`), or code.

## Owned Concepts

1. Prompt templates (generation, critique, reformulation).
2. The critique prompt's structured-output format contract.
3. Prompt versioning and change policy.
4. Anti-hallucination instruction patterns.

## Must Never Contain

- Which model performs a step / model behavior — owned by `[240]`.
- Routing, thresholds, retry logic — owned by `[210]`.
- The *meaning* of relevance/groundedness scores — owned by `[340]`.
- The *service* `CritiqueJudgment` shape — owned by `[220]` (this owns the prompt output that must conform to it).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[110]` | Entities referenced in prompts (chunk, citation, context). |
| `[210]` | The nodes (generate, critique, reformulate) these prompts serve. |
| `[240]` | Stage roles/expected behaviors the prompts must elicit (esp. S4/S5 separation). |

## Downstream Consumers (Outputs)

`[320]` (P5/P6/P7 test these prompts' effects), Implementation, `[610]`, `[620]`.

## Prompt Standards (ADR-0011)

Per ADR-0011 (`[900#ADR-0011]`; SOFT — prompts are tunable; the critique output contract is stability-sensitive).

### Common rules (anti-hallucination)
- Every generation/critique prompt MUST instruct: *answer only from the provided context; do not use outside knowledge; if the context is insufficient, say so explicitly.*
- Citations MUST reference provided chunk identifiers only; the model must not invent identifiers.
- Prompts are parameterized templates; runtime values are injected, never concatenated ad hoc.

### PT-GEN — Generation prompt (serves `[210]` GENERATE / `[240]` S4)
```
System: You answer legal questions using ONLY the provided context passages.
Cite every claim with the passage's [chunk_id]. If the context does not
contain the answer, respond that the provided sources are insufficient —
do not use outside knowledge.
User: Question: {query}
Context:
{for each candidate}: [{chunk_id}] ({section_locator}) {text}
Output: A grounded answer with inline [chunk_id] citations.
```

### PT-CRIT — Critique prompt (serves `[210]` CRITIQUE / `[240]` S5; distinct from PT-GEN)
```
System: You are an independent reviewer. Given a question, the context, and a
draft answer, assess (1) whether the context is relevant to the question and
(2) whether every citation in the draft is supported by the context.
List any citation not supported by the context.
User: Question: {query}
Context: {context passages with [chunk_id]}
Draft answer: {draft_with_citations}
Output: JSON only, per the Critique Output Contract below.
```

### PT-REFORM — Reformulation prompt (serves `[210]` REFORMULATE)
```
System: Rewrite the question to improve retrieval of relevant legal passages,
preserving the user's intent. Return only the rewritten query.
User: Original question: {query}
Prior retrieval was insufficient.
```

## Critique Output Contract

The **field set is owned by `[220]`** (`CritiqueJudgment`) and its semantics by `[340]` (resolves review m3); this document owns only the requirement that PT-CRIT *emit* that structure as parseable JSON. The PT-CRIT prompt MUST return JSON conforming exactly to `[220]`'s `CritiqueJudgment` — keys and value ranges as defined there — with no prose outside the JSON. (Illustrative serialization only; the authoritative keys/types live in `[220]`.)

## Versioning & Change Policy

- Each prompt has an ID (`PT-GEN`, `PT-CRIT`, `PT-REFORM`) and a version.
- Prompts are `soft`-frozen: editable until Documentation Freeze; **after freeze, any prompt change requires a CR and re-running the affected `[320]` properties (P5/P6/P7) and evaluation**, because prompts materially alter behavior (`[000 §3]` 330 rule).
- The Critique Output Contract keys are stability-sensitive: changing them is a `[220]`-affecting change (full CR).

## Assumptions

None introduced. Relies on A-2 (`[120]`): critique uses the same model family with this distinct prompt.

## References

- `[110]`, `[210]`, `[240]` — inputs.
- `[220]` — `CritiqueJudgment` shape; `[340]` — score meaning.
- `[900#ADR-0011]`.

## Open Questions

None blocking. Final prompt wording will be tuned during implementation within these templates and rules.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (no model/routing/meaning) — `[000 §8.1.2]`
- [x] No duplication (references `[220]`/`[240]`/`[340]`) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (explicit templates + output contract) — `[000 §8.1.8]`
- [x] Prompts centralized and versioned — `[000 §3]` 330 intent
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — prompt wording is tunable via lightweight amendment pre-freeze; post-freeze prompt changes require a CR + re-evaluation. The Critique Output Contract keys are hard (shared with `[220]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial prompt templates (gen/critique/reform) + critique output contract. | ADR-0011 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: critique field set ownership deferred to `[220]` (m3); reconciled deps (M6, added 120/220 inputs). | — |
