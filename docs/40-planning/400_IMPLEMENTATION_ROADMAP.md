---
id: "400"
title: "Implementation Roadmap"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["100", "110", "120", "130", "140", "150", "200", "210", "220", "230", "240", "300", "310", "320", "330", "340", "020"]
outputs: ["410", "420", "430", "440", "450", "460", "470", "41x"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 400 — Implementation Roadmap

> Governed by `[000]`, structured per `[001]`. Owns build sequencing into ordered, dependency-aware phases mapped to the frozen knowledge base and gates. Introduces no design; every phase references frozen owners.

## Purpose

Sequence the entire build into phases whose inputs are fully specified by the frozen knowledge base, so implementation is deterministic execution, not design.

## Scope

Phase list, dependencies, per-phase document mapping, and gate placement. Does not contain component design (`[200]`–`[240]`) or task-level detail (phase plans `41x`).

## Owned Concepts
1. The phase list and phase dependency graph.
2. The mapping of phases to frozen documents and gates.

## Must Never Contain
- Design decisions (Architecture) or new requirements (`[140]`).

## Dependencies (Inputs)
All frozen Core Knowledge, Architecture, and Standards docs, plus `[020]`.

## Downstream Consumers (Outputs)
`[410]`–`[470]`, `41x` phase plans, implementation.

## Phases

| Phase | Name | Builds (components) | Primary docs (Context Package) | Depends on |
|-------|------|---------------------|-------------------------------|------------|
| P0 | Project scaffold & tooling | repo, config, docker, CI | 300, 310, 500(env), 470 | — |
| P1 | Ingestion & corpus | C3, D1–D4 population | 130, 230, 240(S1/S2), 200 | P0 |
| P2 | Retrieval | C4 (dense, sparse, RRF, rerank) | 240, 230, 130, 200 | P1 |
| P3 | Generation | C5, PT-GEN | 240(S4), 330, 220, 110 | P2 |
| P4 | Critique + calibration | C6, PT-CRIT, calibration set | 240(S5), 330, 210, 340, 320 | P3 |
| P5 | Orchestration | C7 control flow | 210, 220, 320 | P3, P4 |
| P6 | MCP tools | C8 verify_citation (MCP) | 220, 230(D4), 130 | P2 |
| P7 | Evaluation & logging | C9, /evaluation/summary | 340, 230, 210 | P5 |
| P8 | Frontend | C1 | 220, 100, 300 | P5 |
| P9 | Integration, e2e, calibration, audit | full flow | 320, 150, 340, all | P5–P8 |

## Gates (per `[000 §12]`)
G5 (this roadmap approved) → per-phase G6/G7/G8 → G9/G10 at completion.

## Assumptions
None beyond `[120]`.

## References
`[000 §11]` workflow; `[020]`; all frozen docs.

## Open Questions
None blocking.

## Review Checklist
- [x] Ownership integrity — `[000 §8.1.2]`
- [x] No new design — `[000 §8.3]`
- [x] Dependency graph acyclic — `[000 §8.1.4]`
- [x] Traceable to `[020]` — `[000 §8.1.9]`

## Freeze Class
`soft` — phase scope stabilizes at G5; status updates as phases complete.

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial 10-phase roadmap. | ADR-0017 |
