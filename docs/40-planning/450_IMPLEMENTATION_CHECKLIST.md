---
id: "450"
title: "Implementation Checklist"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["400", "410", "420", "430", "440"]
outputs: ["41x", "620"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 450 — Implementation Checklist

> Governed by `[000]`, per `[001]`. Owns the executable per-phase implementation checklist. Aggregates `[420]`/`[430]`/`[440]`; introduces no design.

## Purpose
A single actionable checklist an implementer/AI follows per phase.

## Scope
Ordered, checkable steps per wave/phase. No design.

## Owned Concepts
1. The per-phase executable checklist.

## Must Never Contain
- Design or new requirements.

## Dependencies (Inputs)
`[400]`, `[410]`, `[420]`, `[430]`, `[440]`.

## Downstream Consumers (Outputs)
`41x`, `[620]`.

## Checklist

**P0 Scaffold (W0)**
- [ ] Create backend/frontend skeleton per `[300]` layout; wire `config.py` to `[470]` params; Docker + compose; CI (lint/type/test).

**P1 Ingestion (W1–W2)**
- [ ] Provision Postgres+pgvector, BM25 index dir, raw-doc store (`[230]`).
- [ ] Implement extract→clean→chunk (per `[130]`)→embed (S1, D=768)→dual-index; record provenance/corpus_version.

**P2 Retrieval (W3)**
- [ ] Dense + sparse search; RRF merge (dedup by chunk_id); cross-encoder rerank to top_n (`[240]` sizing); log reranker_topk_scores. Verify P8.

**P3 Generation (W4)**
- [ ] PT-GEN (`[330]`); context-only answering + citations; parse markers. Verify P6, P7.

**P4 Critique (W5)**
- [ ] PT-CRIT (`[330]`) emitting `CritiqueJudgment` (`[220]`); build labeled calibration set (`[340]`). Verify P1, P3, P5.

**P5 Orchestration (W7)**
- [ ] Implement `[210]` state machine, decision procedure, timeout/failure fail-closed, retry cap, confidence derivation. Verify P1–P4.

**P6 MCP tool (W6)**
- [ ] Implement verify_citation against raw store; expose over MCP stdio + HTTP (schema-identical, ADR-0015). Verify P3 tool path.

**P7 Evaluation (W8)**
- [ ] Async trace logging (all `[230]`/`[340]` fields); /evaluation/summary metrics. Verify P9.

**P8 Frontend (W9)**
- [ ] Chat UI, streaming (SSE), citation view, confidence indicator; handle error shapes (`[220]`).

**P9 Integration & release (W10)**
- [ ] e2e over `[150]` W-2/W-3; run calibration → set `[210]` thresholds; verify P11; complete `[620]` audit; update `[020]`.

## Assumptions
None beyond `[120]`.

## References
`[400]`,`[410]`,`[420]`,`[430]`,`[440]`.

## Open Questions
None blocking.

## Review Checklist
- [x] Every step traces to a frozen doc — `[000 §8.1.9]`
- [x] No design — `[000 §8.3]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial per-phase checklist. | ADR-0017 |
