---
id: "460"
title: "Risk Register"
status: "Approved"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["120", "210", "240", "340", "310"]
outputs: ["420", "620"]
category: "Planning"
decision_refs: ["ADR-0017"]
---

# 460 — Risk Register

> Governed by `[000]`, per `[001]`. Owns the implementation risk register. References assumptions (`[120]`); does not restate them.

## Purpose
Track implementation risks with impact, likelihood, mitigation, and owner.

## Scope
Risk entries. Does not own assumptions (`[120]`) or design.

## Owned Concepts
1. The implementation risk register.

## Must Never Contain
- Assumptions (owned by `[120]`) — referenced by ID.

## Dependencies (Inputs)
`[120]`, `[210]`, `[240]`, `[340]`, `[310]`.

## Downstream Consumers (Outputs)
`[420]`, `[620]`.

## Register

| ID | Risk | Impact | Likelihood | Mitigation | Owner |
|----|------|--------|-----------|------------|-------|
| R1 | Critique scores uncalibrated → wrong pass/fail gate | High | Med | Calibration procedure + P11 (`[340]`/ADR-0016); thresholds provisional until validated (`[210]`) | Critique/Eval |
| R2 | Retrieval quality poor (fusion/sizing) | High | Med | RRF + tunable sizing (`[240]`/ADR-0014); proxy metric monitoring (`[340]`) | Retrieval |
| R3 | LLM provider latency/outage | Med | Med | Timeouts + fail-closed to LOW_CONFIDENCE (`[210]`); 503 (`[220]`) | Orchestration |
| R4 | Embedding model change forces schema migration | Med | Low | Embedding pinned HARD (ADR-0013); CR + re-embed procedure | Data |
| R5 | Prompt drift alters behavior post-freeze | Med | Med | Prompt-change = CR + re-eval (`[330]`); versioned templates | Prompts |
| R6 | Data egress to LLM provider (privacy) | Med | High(occurs) | PRIV-1 disclosure; no other egress (`[310]`) | Security |
| R7 | Unauthenticated service exposed publicly | High | Low | SEC-1 no public binding (`[310]`); proxy/CR required | Security/Ops |
| R8 | Corpus licensing issue in case-law set | Med | Low | Primary-text only, L-1 exclusion (`[130]`) | Data |
| R9 | Cost/latency from retries + tool calls | Med | Med | Retry cap=2, tool once/turn (`[210]` inv.2/4) | Orchestration |
| R10 | Hallucinated citation passes | High | Low | P3 property + tool verification + groundedness gate | Critique |

## Assumptions
None introduced; risks reference `[120]` assumptions where relevant.

## References
`[120]`, `[210]`, `[240]`, `[340]`, `[310]`.

## Open Questions
None blocking.

## Review Checklist
- [x] Mitigations reference frozen owners — `[000 §8.1.3]`
- [x] No assumptions restated — `[000 §8.1.2]`

## Freeze Class
`soft` (living during implementation).

## Status
`Approved`.

## Version History
| Version | Date | Author | Change | Decision |
|---------|------|--------|--------|----------|
| 0.1 | 2026-07-06 | Eng Doc Lead | Initial 10-risk register. | ADR-0017 |
