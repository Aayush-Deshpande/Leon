---
id: "420"
title: "Phase Execution Plan"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["400", "410", "320", "440"]
outputs: ["430", "450", "41x"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 420 — Phase Execution Plan

> Governed by `[000]`, per `[001]`. Owns the per-phase execution schedule: the Context Package (`[000 §5.2]`) and exit criteria for each phase. No design.

## Purpose
Give each phase a precise, minimal reading set and exit gate so execution is deterministic.

## Scope
Per-phase Context Package + exit criteria. No task-level design; `41x` phase plans hold task detail.

## Owned Concepts
1. Each phase's Context Package and exit criteria.

## Must Never Contain
- Design or new requirements.

## Dependencies (Inputs)
`[400]`, `[410]`, `[320]` (properties as exits), `[440]` (DoD).

## Downstream Consumers (Outputs)
`[430]`, `[450]`, `41x`.

## Per-Phase Plan

| Phase | Context Package (read-only refs in brackets) | Exit criteria (gate) |
|-------|----------------------------------------------|----------------------|
| P0 | 300, 310, 470 [200,500] | Scaffold builds; CI green; lint/type pass (G6/G7) |
| P1 | 130, 230 [110,200,240] | Corpus ingested & indexed; provenance recorded; P8 fixture ready |
| P2 | 240, 230 [130,200] | Retrieval returns RRF+reranked top_n; P8 passes |
| P3 | 240(S4), 330 [220,110] | Cited draft generated; P6, P7 pass |
| P4 | 240(S5), 330, 340 [210,320] | Critique emits CritiqueJudgment; calibration set built; P5, P11 pass |
| P5 | 210, 220 [240,320] | Control flow routes correctly; P1,P2,P3,P4 pass |
| P6 | 220, 230(D4), 130 [200,240] | MCP verify_citation over stdio; P3 (tool path) passes |
| P7 | 340, 230 [210] | Traces logged non-blocking; /summary metrics; P9 passes |
| P8 | 220, 100 [300] | Chat UI renders answer/citations/confidence (FR-1,21,23,15) |
| P9 | 320, 150, 340 [all] | Full e2e green; calibration validates thresholds; audit (G8) |

Each phase also loads its `41x` plan + scoped `900` entries per `[000 §5.2]`.

## Assumptions
None beyond `[120]`.

## References
`[400]`, `[410]`, `[320]`, `[440]`.

## Open Questions
None blocking.

## Review Checklist
- [x] Minimal sufficient package per phase — `[000 §1.10]`
- [x] Exit criteria reference `[320]`/`[440]` — `[000 §8.1.9]`
- [x] No design — `[000 §8.3]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial per-phase execution plan. | ADR-0017 |
