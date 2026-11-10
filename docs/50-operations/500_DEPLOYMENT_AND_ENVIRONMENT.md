---
id: "500"
title: "Deployment and Environment"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["200", "220", "230", "240", "310", "470", "130"]
outputs: ["400", "41x", "620"]
category: "Operations"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0003", "ADR-0006", "ADR-0009", "ADR-0018", "ADR-0022"]
---

# 500 — Deployment and Environment

> Governed by `[000]`, structured per `[001]`. Owns deployment topology and the configuration/environment contract (`[000 §3]`). It supplies **concrete config values** for parameters whose *semantics* are owned by `[210]`/`[240]`/`[340]`/`[310]` and indexed by `[470]`. It contains no application logic or security rationale (`[310]`).

## Purpose

Define how Leon is configured, containerized, and run as a single-instance demo (A-8), and provide the concrete provider/config values so implementation is runnable without inventing settings.

## Scope

Deployment topology, container/compose layout, the provider abstraction, the environment-variable contract, network binding (SEC-1), and default config values. Does not own parameter semantics (referenced) or security rules (`[310]`).

## Owned Concepts
1. Deployment topology and container layout.
2. The environment/configuration contract (env vars + provider abstraction) and concrete defaults.

## Must Never Contain
- Application/business logic (Implementation) or control-flow (`[210]`).
- Security *rationale/rules* — owned by `[310]` (this implements SEC-1's binding).
- Parameter *semantics* — owned by `[210]`/`[240]`/`[340]`.

## Dependencies (Inputs)

| Doc | Why |
|-----|-----|
| `[200]` | Components to deploy. |
| `[220]` | Endpoints/ports and MCP stdio entrypoint. |
| `[230]` | Stores to provision (Postgres+pgvector, BM25 dir, raw store). |
| `[240]` | AI stage models/interface (embedding HARD; generation provider-agnostic). |
| `[310]` | SEC-1 (no public binding), secrets, rate limit. |
| `[470]` | Parameter index this document assigns values to. |
| `[130]` | Corpus/version path layout. |

## Downstream Consumers (Outputs)
`[400]`/`41x` (P0 scaffold), `[620]` audits.

## Provider Abstraction (ADR-0022 / ADR-0018)

Providers are selected by configuration; the architecture is model-agnostic (`[240]` interface). Reference config:

```yaml
providers:
  embedding:
    provider: sentence-transformers
    model: BAAI/bge-base-en-v1.5     # HARD (ADR-0018) — do not change without a CR (re-embed + reindex)
    dim: 768
  reranker:
    provider: sentence-transformers
    model: BAAI/bge-reranker-base    # default, configurable
  generation:
    provider: openrouter             # default provider
    model: configurable              # e.g., qwen/qwen3-32b | anthropic/claude-sonnet-4
  critique:
    provider: same-as-generation     # A-2; overridable
    model: same-as-generation
  evaluation:
    provider: same-as-generation
```

The generation/critique provider MUST satisfy the `[240]` capability interface (instruction-following, long-context, tool-call preferred, deterministic-inference support).

## Environment Variable Contract

| Variable | Default | Owner of semantics | Notes |
|----------|---------|--------------------|-------|
| `EMBEDDING_PROVIDER` | `sentence-transformers` | `[240]` | — |
| `EMBEDDING_MODEL` | `BAAI/bge-base-en-v1.5` | `[240]` | **HARD** — CR to change |
| `RERANKER_MODEL` | `BAAI/bge-reranker-base` | `[240]` | configurable |
| `GENERATION_PROVIDER` | `openrouter` | `[240]` | configurable |
| `GENERATION_MODEL` | (configurable) | `[240]` | e.g., `qwen/qwen3-32b` |
| `CRITIQUE_MODEL` | `${GENERATION_MODEL}` | `[240]` | A-2 default |
| `T_RELEVANCE` | `0.70` | `[210]` | provisional until calibration (`[340]`) |
| `T_GROUNDEDNESS` | `0.80` | `[210]` | provisional until calibration |
| `MAX_REFORMULATIONS` | `2` | `[210]` | A-3 |
| `K_DENSE` | `20` | `[240]` | — |
| `K_SPARSE` | `20` | `[240]` | — |
| `TOP_N` | `5` | `[240]` | — |
| `K_RRF` | `60` | `[240]` | RRF constant |
| `HNSW_M` | `16` | `[230]` | — |
| `HNSW_EF_CONSTRUCTION` | `64` | `[230]` | — |
| `CITATION_FUZZY_THRESHOLD` | `0.95` | `[220]`/ADR-0019 | OCR tolerance |
| `MODEL_CALL_TIMEOUT_MS` | `30000` | `[210]` | fail-closed on timeout |
| `RATE_LIMIT_RPM` | `60` | `[310]` | SEC-7 |
| `BIND_HOST` | `127.0.0.1` | `[310]` | **SEC-1** — no public bind |
| `DATABASE_URL` | (secret) | `[500]` | Postgres+pgvector DSN |
| `OPENROUTER_API_KEY` | (secret) | `[310]` | never logged (SEC-2) |
| `CORPUS_VERSION` | (current) | `[130]` | active corpus snapshot |

## Deployment Topology (A-8 single instance)

`docker-compose` with services:
- `postgres` — PostgreSQL + `pgvector` (D1/D3).
- `backend` — FastAPI app (C2, C4–C7, C9) + the **MCP server** (C8) as a stdio entrypoint within the same image; hosts the BM25 index (D2) and raw-doc store (D4) on a mounted volume.
- `frontend` — React/Vite (C1).

All bound per `BIND_HOST` (SEC-1); no public exposure without an authenticating proxy or an auth CR (`[310]`).

## Assumptions
None beyond `[120]` (A-8 single instance; A-4 no auth).

## References
`[200]`, `[220]`, `[230]`, `[240]`, `[310]`, `[470]`, `[130]`; ADR-0018/0022/0003/0006/0009.

## Open Questions
None blocking. `GENERATION_MODEL` is intentionally operator-selected (provider-agnostic, ADR-0022).

## Review Checklist
- [x] Config values assigned; semantics referenced not restated — `[000 §8.1.3]`
- [x] SEC-1 binding implemented — `[310]`
- [x] Provider abstraction present (ADR-0022) — `[000 §8.3]`
- [x] Frontmatter valid — `[000 §7]`

## Freeze Class
`soft` — config values tunable via lightweight amendment; `EMBEDDING_MODEL` is HARD.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial deployment/env + provider abstraction + concrete config defaults. | CR-0001 |
