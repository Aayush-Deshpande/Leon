---
id: "410"
title: "Epic Breakdown"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["400", "200", "140", "020"]
outputs: ["420", "430", "450"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 410 — Epic Breakdown

> Governed by `[000]`, per `[001]`. Owns the decomposition of the build into epics mapped to components and FRs. No design.

## Purpose
Group implementation work into epics with clear scope and FR coverage.

## Scope
Epic list, each mapped to component(s), FRs, and phase. No design or task detail.

## Owned Concepts
1. The epic list and epic→component→FR mapping.

## Must Never Contain
- Design (Architecture) or new requirements.

## Dependencies (Inputs)
`[400]` phases, `[200]` components, `[140]` FRs, `[020]`.

## Downstream Consumers (Outputs)
`[420]`, `[430]`, `[450]`.

## Epics

| Epic | Scope | Components | FRs | Phase |
|------|-------|-----------|-----|-------|
| E0 | Project scaffold, config, CI, Docker | — | — | P0 |
| E1 | Corpus ingestion & indexing | C3, D1–D4 | (2,4,16 enablement) | P1 |
| E2 | Hybrid retrieval + rerank | C4 | 2,3,4 | P2 |
| E3 | Grounded generation | C5 | 5,6,7 | P3 |
| E4 | Self-critique + calibration | C6 | 8,9,10 | P4 |
| E5 | Orchestration / control flow | C7 | 11–15 | P5 |
| E6 | MCP citation-verification tool | C8 | 16 (17 deferred) | P6 |
| E7 | Evaluation logging & summary | C9 | 18,19,20 | P7 |
| E8 | Frontend chat UI | C1 | 1,21,23,15 | P8 |
| E9 | Integration, e2e, calibration run, audit | all | all | P9 |

**Coverage:** every FR (1–25) is covered by exactly one primary epic; every component maps to one epic.

## Assumptions
None beyond `[120]`.

## References
`[400]`, `[200]`, `[140]`, `[020]`.

## Open Questions
None blocking.

## Review Checklist
- [x] Every FR covered by an epic — `[000 §8.1.9]`
- [x] No design — `[000 §8.3]`
- [x] Ownership integrity — `[000 §8.1.2]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial 10 epics. | ADR-0017 |
