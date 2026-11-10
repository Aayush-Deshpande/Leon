---
id: "440"
title: "Definition of Done"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["320", "300", "310", "340", "020"]
outputs: ["420", "450", "620"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 440 — Definition of Done

> Governed by `[000]`, per `[001]`. Owns the global Definition of Done and per-artifact acceptance gates. References the correctness properties (`[320]`); does not restate them.

## Purpose
Define, unambiguously, when a task/phase is complete, so completion is objective.

## Scope
Global DoD + per-artifact gates. Does not own the properties (`[320]`) or metrics (`[340]`).

## Owned Concepts
1. The Definition of Done and per-artifact acceptance gates.

## Must Never Contain
- The correctness properties themselves (`[320]`) or metric definitions (`[340]`) — referenced.

## Dependencies (Inputs)
`[320]`, `[300]`, `[310]`, `[340]`, `[020]`.

## Downstream Consumers (Outputs)
`[420]`, `[450]`, `[620]`.

## Global Definition of Done (every task)
- [ ] Traces to a frozen requirement/design element (`[020]`); no undocumented behavior.
- [ ] Conforms to the frozen contracts it touches (`[220]`/`[230]`/`[210]`/`[240]`).
- [ ] Meets coding standards (`[300]`) — lint, types, structure.
- [ ] Meets security rules (`[310]`) — secrets, validation, no public no-auth binding.
- [ ] Unit tests written and green.
- [ ] Applicable correctness properties (`[320]` P1–P11) pass.
- [ ] Documentation status/`020` updated; decisions logged in `[900]`.

## Per-Artifact Gates
| Artifact | Done when |
|----------|-----------|
| Ingestion | Corpus indexed; provenance + corpus_version recorded; chunking matches `[130]`. |
| Retrieval | RRF+rerank returns top_n; P8 green; reranker scores logged. |
| Generation | Cited draft only from context; P6/P7 green. |
| Critique | Emits `CritiqueJudgment` per `[220]`; P1/P3/P5 green; calibration set exists. |
| Orchestration | Routing per `[210]`; P1–P4 green; thresholds sourced from calibration. |
| MCP tool | verify_citation over MCP+HTTP, schema-identical; P3 green. |
| Evaluation | Complete non-blocking trace; /summary metrics per `[340]`; P9 green. |
| Frontend | FR-1/21/23/15 rendered; error shapes handled. |
| Release | Full e2e green; P11 threshold validation passed; audit G8 clean. |

## Assumptions
None beyond `[120]`.

## References
`[320]`, `[300]`, `[310]`, `[340]`, `[020]`.

## Open Questions
None blocking.

## Review Checklist
- [x] References properties, not restated — `[000 §8.1.3]`
- [x] Objective/checkable — `[000 §8.3]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial global DoD + per-artifact gates. | ADR-0017 |
