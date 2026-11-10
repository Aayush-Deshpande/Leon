---
id: "470"
title: "Configuration Matrix"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["210", "240", "340", "310", "130", "230"]
outputs: ["500", "420", "450"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 470 — Configuration Matrix

> Governed by `[000]`, per `[001]`. Owns the consolidated index of tunable configuration parameters and their defaults referenced by the frozen docs. It **indexes** parameters for `[500]`; the *semantics* remain owned by `[210]`/`[240]`/`[340]`.

## Purpose
Give one place listing every tunable parameter, its default, its owner, and whether it is tunable vs. contract.

## Scope
Parameter index. Does not own semantics (referenced) or deployment mechanics (`[500]`).

## Owned Concepts
1. The consolidated tunable-parameter index.

## Must Never Contain
- Parameter *semantics* (owned by `[210]`/`[240]`/`[340]`) — referenced.
- Deployment/env wiring (owned by `[500]`).

## Dependencies (Inputs)
`[210]`, `[240]`, `[340]`, `[310]`, `[130]`, `[230]`.

## Downstream Consumers (Outputs)
`[500]`, `[420]`, `[450]`.

## Parameter Matrix

| Parameter | Default | Tunable? | Semantics owner |
|-----------|---------|----------|-----------------|
| `T_relevance` | 0.70 | tunable (provisional until calibrated) | `[210]` |
| `T_groundedness` | 0.80 | tunable (provisional) | `[210]` |
| `MAX_REFORMULATIONS` | 2 | tunable | `[210]` |
| `k_dense` | 20 | tunable | `[240]` |
| `k_sparse` | 20 | tunable | `[240]` |
| `top_n` | 5 | tunable | `[240]` |
| `k_rrf` | 60 | tunable | `[240]` (ADR-0014) |
| `hnsw_m` | 16 | tunable | `[230]` (ADR-0006) |
| `hnsw_ef_construction` | 64 | tunable | `[230]` (ADR-0006) |
| `embedding_model` / `D` | `BAAI/bge-base-en-v1.5` / 768 | **HARD — not config** (ADR-0018) | `[240]` |
| `reranker_model` | `BAAI/bge-reranker-base` | config | `[240]`/`[500]` |
| `generation_provider` | `openrouter` (default) | config | `[240]`/`[500]` (ADR-0022) |
| `generation_model` | operator-selected | config (provider-agnostic) | `[240]`/`[500]` (ADR-0022) |
| `critique_model` | `${generation_model}` | config (A-2 default) | `[240]`/`[500]` |
| `citation_fuzzy_threshold` | 0.95 | tunable | `[220]` (ADR-0019) |
| `llm_provider_endpoint`/creds | — | config (secret) | `[310]`/`[500]` |
| `model_call_timeout_ms` | 30000 | tunable | `[210]` |
| `rate_limit_rpm` | 60 | tunable | `[310]` |
| `bind_host` | 127.0.0.1 | config (SEC-1) | `[310]`/`[500]` |
| `corpus_version` | current | contract per ingest | `[130]` |
| `db_connection` | — | config (secret) | `[500]` |

## Assumptions
None beyond `[120]`.

## References
`[210]`, `[240]`, `[340]`, `[310]`, `[130]`.

## Open Questions
None. Concrete values are now assigned in `[500]` (CR-0001); `generation_model` is intentionally operator-selected (provider-agnostic, ADR-0022).

## Review Checklist
- [x] Indexes only; semantics referenced — `[000 §8.1.3]`
- [x] HARD vs tunable distinguished — `[000 §8.3]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial configuration index. | ADR-0017 |
| 0.2 | 2026-07-06 | Eng Doc Lead | CR-0001: added k_rrf, HNSW params, citation threshold, bind_host; concrete model defaults; values assigned in 500. | CR-0001 |
