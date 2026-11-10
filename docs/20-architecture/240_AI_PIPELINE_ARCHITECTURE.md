---
id: "240"
title: "AI Pipeline Architecture"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.3"
inputs: ["110", "120", "130", "200", "210", "230"]
outputs: ["310", "320", "330", "340", "400", "41x", "500", "610"]
category: "Architecture"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0007", "ADR-0013", "ADR-0014", "ADR-0018", "ADR-0020", "ADR-0022"]
---

# 240 — AI Pipeline Architecture

> Governed by `[000]`, structured per `[001]`. Owns the AI/ML pipeline: which model performs each role, its expected behavior, the I/O contract between AI stages, and the generation/critique separation (`[000 §3]`). It contains no prompt text (`[330]`), control-flow routing (`[210]`), or storage detail (`[230]`).

## Purpose

Define the roles, expected behaviors, and inter-stage I/O contracts of Leon's AI components, and protect the architectural separation between generation and self-critique.

## Scope

Covers the embedding, sparse-retrieval, reranker, generation, and self-critique stages: role, expected behavior, model selection (defaults), and the data each stage consumes/produces at the model level. This document does **not** cover prompt text (`[330]`), routing/thresholds (`[210]`), storage schemas (`[230]`), or the software service signatures (`[220]`).

## Owned Concepts

1. The role and expected behavior of each AI stage.
2. Model-selection decisions (defaults) for each stage.
3. The model-level I/O contract between AI stages.
4. The architectural separation between generation and critique.

## Must Never Contain

- Prompt text or prompt-output schemas — owned by `[330]`.
- Control-flow routing, thresholds, retry policy — owned by `[210]`.
- Storage schemas/index structures — owned by `[230]`.
- Software/service interface signatures — owned by `[220]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[200]` | Retrieval/Generation/Critique components hosting these stages. |
| `[210]` | The control flow that invokes generation and critique as distinct nodes. |
| `[110]` | Entities (Context, Draft Answer, Critique Judgment). |
| `[120]` | A-2 (critique = same family, distinct prompt), NG-4 (no fine-tuning). |
| `[130]` | Corpus/chunking that embedding and retrieval operate over. |
| `[230]` | Storage/index schemas that retrieval reads and embeddings populate. |

## Downstream Consumers (Outputs)

`[230]` (embedding dimension), `[320]` (behavioral tests), `[330]` (prompts per stage), `[340]` (score meaning), Implementation, `[610]`.

## Boundary vs. `[220]`

`[220]` owns the *software* interface signatures (e.g., `Generation.generate(query, context) → DraftAnswer`). This document owns the *model-level* I/O (what the model consumes/produces and how it behaves). The two align but do not duplicate: `[220]` = service shape, `[240]` = model role/behavior.

## AI Stages (ADR-0007)

Per ADR-0007 (`[900#ADR-0007]`); all off-the-shelf/API, no fine-tuning (NG-4). Model choices are revisitable defaults (`[000 §9.4]`); roles and I/O contracts are the hard contract.

| Stage | Role | Model (default, revisitable) | Model-level I/O | Expected behavior |
|-------|------|------------------------------|-----------------|-------------------|
| S1 Embedding | Encode text for dense similarity. | **`BAAI/bge-base-en-v1.5`** (HARD, ADR-0018), dim **D = 768**, via `sentence-transformers`. | `text → vector(768)` | Similar legal concepts → high cosine similarity across paraphrase. Same model at ingestion and query time. Uses the model's prefix convention (`"query: "` for queries, `"passage: "` for chunks). |
| S2 Sparse retrieval | Exact-term matching. | BM25 (algorithmic; index in `[230]`; analyzer per ADR-0020 below). | `query → (chunk_id, score)[]` | Statutory references surface the correct section reliably. |
| S3 Reranker | Reorder merged candidates by true relevance. | Cross-encoder; default **`BAAI/bge-reranker-base`** (config via `[500]`). | `(query, candidate[]) → scored/ordered candidate[]` | Top-ranked chunks are the most directly relevant. |
| S4 Generation | Produce grounded, cited draft answer. | **Provider-agnostic LLM (interface, not model — ADR-0022)**; config via `[500]`. | `(query, ranked context) → draft answer + citation markers` | Answers only from provided context; hedges/refuses when insufficient (FR-7). Prompt owned by `[330]`. |
| S5 Self-critique | Independently score grounding of the draft. | **Same provider/model family as S4 by default** (A-2, ADR-0022), distinct prompt; config via `[500]`. | `(query, context, draft) → {relevance, groundedness, unverifiable[]}` | Conservative scoring; flags citations absent from context. Prompt owned by `[330]`; score meaning by `[340]`. |

### Generation/Critique LLM Capability Interface (ADR-0022)
Generation and critique are defined by a **capability interface**, not a pinned model — Leon demonstrates the architecture (RAG + self-critique + verification + orchestration), which must hold across LLMs. The configured provider/model (via `[500]`) MUST satisfy:
- **Instruction-following** (reliably obeys system/format instructions).
- **Long-context** (accommodates `top_n` context chunks + prompts).
- **Tool-call capable** (preferred, for agentic/MCP paths).
- **Deterministic-inference support** (controllable temperature/seed for reproducible tests).
- **Fully configurable** via `[500]` (`GENERATION_PROVIDER`, `GENERATION_MODEL`, `CRITIQUE_MODEL`). Default provider **OpenRouter**; default model configurable. Critique defaults to the generation model family, overridable.

`D = 768` fixes the `embedding vector(D)` column in `[230]`.

**Embedding model is a HARD contract (ADR-0013, resolves review M2):** unlike the other stages' revisitable defaults, the **embedding model identity and its dimension `D` are hard-frozen** because `D` is baked into the `[230]` schema. Changing the embedding model requires a full CR plus a stated re-embedding/re-index migration — it is *not* a mere `[500]` config change. (Provider endpoint/credentials remain config.)

## Retrieval Sizing & Fusion (ADR-0014, resolves review M3)

Owned here (algorithmic); values are tunable defaults at deploy (`[500]`). Consumed by `[200]` (C4) and `[220]` (`top_n`).

| Parameter | Meaning | Default |
|-----------|---------|---------|
| `k_dense` | Dense candidates retrieved (S1). | 20 |
| `k_sparse` | Sparse/BM25 candidates retrieved (S2). | 20 |
| `top_n` | Reranked candidates assembled into context (S3 → S4/S5). | 5 |

**Fusion method:** the dense and sparse candidate lists are merged by **Reciprocal Rank Fusion (RRF)** with rank constant **`k_rrf = 60`** (tunable default, ADR-0014), deduplicated by `chunk_id`, and the fused set is passed to the reranker (S3). RRF is chosen because dense cosine scores and BM25 scores are not on a comparable scale; rank-based fusion avoids score normalization. The reranker then produces the final `top_n` ordering.

### BM25 Analyzer (ADR-0020)
Applied identically at index build (`[230]`) and query time:
- Lowercase; Unicode **NFKC** normalize.
- Tokenizer **preserves statutory references** — `s.10`, `section 10(2)`, `10(1)(a)` are single tokens, not split on `.`/`(`/`)`.
- Remove standard English stopwords.
- **No stemming** (protect exact legal terminology; stemming would harm the exact-match role BM25 exists to serve).

## Stage Interaction

```
S1(query) ─┐
S2 ────────┤─> merge ─> S3(rerank) ─> ranked context ─┬─> S4 (generate)
S1(chunks, at ingestion) into store                   └─> S5 (critique)
S4 draft ──────────────────────────────────────────────> S5 (critique re-examines the SAME context)
```

**Separation invariant (protects the differentiator):** S5 is a distinct invocation from S4 — it re-examines the same context to independently verify grounding, never trusting S4's self-report (`leon.md` §5.5/§5.6, FR-10). S4 and S5 must not share a single call or prompt. Enforced as a correctness property in `[320]`; invoked as distinct nodes by `[210]`.

## Assumptions

None introduced. A-2 (critique model strategy) and NG-4 (no fine-tuning) owned by `[120]`.

## References

- `leon.md` §5 — AI workflow source.
- `[200]`, `[210]`, `[110]`, `[130]` — inputs.
- `[230]` — embedding dimension consumer; `[330]` — prompts; `[340]` — score meaning.
- `[900#ADR-0007]` — AI model roles & defaults decision.

## Open Questions

None blocking. Concrete model identifiers/providers are deployment-configurable (`[500]`); this document fixes roles, behavior, and the default class of model per stage.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (prompts/routing/storage/service-shape deferred) — `[000 §8.1.2]`
- [x] No duplication (model role here; service shape in `[220]`) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (stage tables) — `[000 §8.1.8]`
- [x] Traceability to `leon.md` §5 / FRs — `[000 §8.1.9]`
- [x] Generation/critique separation preserved — `[000 §8.3]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — AI-stage roles and I/O contracts are cross-boundary contracts; changes require a full Change Request. Concrete reranker/generation/critique model identifiers are revisitable defaults (`[000 §9.4]`); the **embedding model and its dimension `D` are HARD** (ADR-0013) because `[230]`'s schema depends on `D`. Retrieval sizing values are tunable defaults.

## Status

`Frozen` (CR-0001 applied; re-frozen).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial AI pipeline (5 stages), I/O contracts, separation invariant. | ADR-0007 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: embedding model HARD (M2); added RRF fusion + sizing (M3); reconciled deps (M6). | ADR-0013, ADR-0014 |
| 0.3 | 2026-07-06 | Engineering Documentation Lead | CR-0001: pinned embedding (ADR-0018); generation/critique interface (ADR-0022); BM25 analyzer (ADR-0020); RRF k=60. Re-frozen. | CR-0001 |
