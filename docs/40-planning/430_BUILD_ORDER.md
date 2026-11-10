---
id: "430"
title: "Build Order"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["400", "410", "200"]
outputs: ["450", "41x"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 430 — Build Order

> Governed by `[000]`, per `[001]`. Owns the concrete dependency-ordered build sequence. Derives dependencies from `[200]`/`[400]`; introduces none.

## Purpose
Give a single linear (wave-based) build order so components are built only after their dependencies exist.

## Scope
Ordered build steps with dependency rationale. No design.

## Owned Concepts
1. The dependency-ordered build sequence (waves).

## Must Never Contain
- New dependencies (must derive from `[200]`/`[400]`).

## Dependencies (Inputs)
`[400]` phases, `[410]` epics, `[200]` component boundaries.

## Downstream Consumers (Outputs)
`[450]`, `41x`.

## Build Order (waves)

| Wave | Build | Rationale (dependency) |
|------|-------|------------------------|
| W0 | Repo scaffold, config (`config.py`/env), Docker, CI, `470` params wiring | nothing precedes |
| W1 | Data stores provisioning (Postgres+pgvector, BM25 index dir, raw-doc store) | needed by ingestion/retrieval |
| W2 | Ingestion pipeline (extract→chunk→embed→index) | needs W1 + `[130]` |
| W3 | Retrieval (dense, sparse, RRF merge, reranker) | needs W2 index |
| W4 | Generation service + PT-GEN | needs W3 context |
| W5 | Critique service + PT-CRIT; build calibration set | needs W4 draft |
| W6 | MCP tool (verify_citation) | needs W2 raw store; parallel with W4/W5 |
| W7 | Orchestration controller (control flow, thresholds) | needs W3,W4,W5,W6 |
| W8 | Evaluation logging + /summary | needs W7 trace |
| W9 | Frontend | needs W7 API |
| W10 | Integration, e2e, calibration run, threshold setting, audit | needs W7–W9 |

Waves W4/W6 and W8/W9 may proceed in parallel where dependencies allow.

## Assumptions
None beyond `[120]`.

## References
`[400]`, `[410]`, `[200]`.

## Open Questions
None blocking.

## Review Checklist
- [x] Acyclic; each build after its deps — `[000 §8.1.4]`
- [x] No new dependencies — `[000 §8.3]`

## Freeze Class
`soft`.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial 11-wave build order. | ADR-0017 |
