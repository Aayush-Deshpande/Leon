---
id: "210"
title: "Agent Control Flow"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["200", "110", "120", "140", "150"]
outputs: ["220", "240", "320", "330", "340", "400", "41x", "610"]
category: "Architecture"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0004", "ADR-0016"]
---

# 210 — Agent Control Flow

> Governed by `[000]`, structured per `[001]`. Owns the in-loop evaluation control flow: the state machine, routing conditions, threshold semantics, and retry-cap policy (`[000 §3]`). This is Leon's core differentiator. It references (never defines) prompts (`[330]`), model choices (`[240]`), the trace schema (`[230]`) and its field semantics (`[340]`).

## Purpose

Define the decision logic that turns critique output into a routing decision, so evaluation is a control-flow node — not a post-hoc metric — and so no implementation can bypass or "simplify away" the critique step.

## Scope

Covers the query-processing state machine, the pass/fail decision, the fallback routing procedure, threshold parameters (semantics + defaults), and the reformulation retry bound. This document does **not** cover prompt text (`[330]`), which models perform each step (`[240]`), score computation internals, the trace schema (`[230]`), or metric definitions (`[340]`).

## Owned Concepts

1. The agent control-flow state machine and transitions.
2. Routing conditions and the fallback decision procedure.
3. Threshold parameters and their semantics (with default values, tunable at deploy).
4. The reformulation retry-cap policy.

## Must Never Contain

- Prompt text or output formats — owned by `[330]`.
- Which model runs a step — owned by `[240]`.
- Trace schema/fields — owned by `[230]`; metric/field semantics — owned by `[340]`.
- Component boundaries — owned by `[200]`.
- Interface shapes — owned by `[220]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[200]` | Components (C4–C9) this flow orchestrates. |
| `[110]` | Entities (Critique Judgment, Fallback Action, Trace) in the flow. |
| `[120]` | A-3 (retry bound), A-5 (optional tool). |
| `[140]` | FR-8–FR-15 this flow realizes. |
| `[150]` | W-2/W-3 functional ordering this flow makes precise. |

## Downstream Consumers (Outputs)

`[220]` (routing metadata in responses), `[240]` (which models serve each node), `[320]` (correctness properties), `[330]` (prompts per node), `[340]` (which decisions get logged), Implementation, and `[610]`.

## State Machine

Per ADR-0004 (`[900#ADR-0004]`).

| State | Entry | Action | Exit transition |
|-------|-------|--------|-----------------|
| `RETRIEVE` | Query received or reformulated | Obtain ranked context (C4). | → `GENERATE` |
| `GENERATE` | Context ready | Produce draft answer + citations (C5). | → `CRITIQUE` |
| `CRITIQUE` | Draft ready | Score relevance + groundedness; list unverifiable citations (C6). | → `DECIDE` |
| `DECIDE` | Critique available | Apply the decision procedure below. | → `RETURN` \| `REFORMULATE` \| `TOOL` \| `LOW_CONFIDENCE` |
| `REFORMULATE` | Fail + retries remain | Rewrite query; increment retry counter. | → `RETRIEVE` |
| `TOOL` | Fail due to unverifiable citation(s) | Invoke citation-verification tool (C8). | → `DECIDE` (re-evaluate) |
| `RETURN` | Pass | Emit answer + citations + confidence + routing metadata. | → terminal (+ async trace) |
| `LOW_CONFIDENCE` | Fail + no path remains | Emit explicit low-confidence response with reason + advisory. | → terminal (+ async trace) |

## Decision Procedure (`DECIDE`)

Inputs (meaning owned by `[340]`): `relevance` score, `groundedness` score, `unverifiable[]` citation list, `retry_count`.

```
PASS  ⇔  relevance ≥ T_relevance
     AND groundedness ≥ T_groundedness
     AND unverifiable is empty
```

- **If PASS →** `RETURN`.
- **Else if `unverifiable` is non-empty AND the citation-verification tool has not yet been tried this turn →** `TOOL` (verify against raw ground truth `[130]`/C8), then re-`DECIDE`.
  - After `TOOL`: any citation the tool confirms absent is treated as permanently unverifiable (never returned as verified — correctness property, `[320]`).
- **Else if `relevance` below threshold AND `retry_count` < `MAX_REFORMULATIONS` →** `REFORMULATE`.
- **Else →** `LOW_CONFIDENCE`.

Routing order is deterministic: tool-verify (once) → reformulate (bounded) → low-confidence. Every `DECIDE` outcome is recorded as routing metadata (logged per `[340]`).

## Threshold Parameters

Semantics owned here; values are tunable at deploy (configuration storage owned by `[500]`).

| Parameter | Meaning | Default |
|-----------|---------|---------|
| `T_relevance` | Minimum acceptable retrieval-relevance score to pass. | 0.70 |
| `T_groundedness` | Minimum acceptable citation-groundedness score to pass. | 0.80 |
| `MAX_REFORMULATIONS` | Max query-reformulation attempts before low-confidence (realizes A-3). | 2 |

Defaults are a starting policy, revisitable via lightweight amendment (`[000 §9.4]`) as evaluation data (`[340]`) informs tuning; changing the *semantics* requires a CR.

**Thresholds are provisional until calibrated (review M5).** The default values above are unvalidated. They MUST be set from the critique-calibration procedure owned by `[340]` (ADR-0016) before they are relied upon; until then they are placeholders.

## Confidence Indicator Derivation (resolves review m1)

The `confidence` value surfaced in `[220]` responses is derived here:
- `high` ⇔ the outcome is `RETURN` (a PASS) — i.e., relevance and groundedness both met threshold and no unverifiable citations remain.
- `low` ⇔ the outcome is `LOW_CONFIDENCE`.
- `reformulated`/`tool_verified` are intermediate; the final `confidence` reflects the terminal outcome (`high` if it ultimately RETURNs, else `low`).

## Model-Call Failure & Timeout Handling (resolves review m7)

- Each retrieval/generation/critique/tool call has a bounded timeout (value tunable via `[500]` config).
- On timeout or provider error of **generation or critique**: the turn fails closed → `LOW_CONFIDENCE` (never a silent unchecked answer; upholds invariant 1). The API surfaces `503` per `[220]` only if no response can be produced.
- On **retrieval** failure: one bounded retry, then `LOW_CONFIDENCE`.
- Failures never bypass critique and never loop unbounded (upholds invariants 1–2).

## Notes on Routing Choices

- **Low groundedness with good retrieval (resolves review m8):** when relevance passes but groundedness fails with no unverifiable citations, the outcome is `LOW_CONFIDENCE` by design — the system does **not** regenerate. Rationale: a poorly-grounded answer over adequate context indicates a generation-faithfulness problem that re-generation is unlikely to fix cheaply within latency/cost bounds; surfacing low confidence is safer than looping. Revisitable if evaluation data (`[340]`) shows regeneration helps.
- **Web-search fallback tool (FR-17) is not in this control flow (resolves review m4):** it is optional (A-5, `[120]`) and **deferred** — no `[210]` state invokes it. Enabling it (a corpus-miss branch) requires a future ADR amending this flow. The `TOOL` state covers citation-verification only.

## Control-Flow Invariants (to be enforced as correctness properties in `[320]`)

1. No `RETURN` occurs without a completed `CRITIQUE` for that answer (critique cannot be bypassed).
2. `retry_count` never exceeds `MAX_REFORMULATIONS`; the loop always terminates in `RETURN` or `LOW_CONFIDENCE`.
3. A citation flagged unverifiable and not subsequently confirmed by the tool is never presented as verified.
4. `TOOL` verification is attempted at most once per turn (no tool-call loops).

## Assumptions

None introduced. Depends on A-3 and A-5 (`[120]`).

## References

- `[200]`, `[110]`, `[140]`, `[150]` — inputs.
- `[130]` — raw ground truth used by `TOOL`.
- `[340]` — meaning of the scores consumed here.
- `[900#ADR-0004]` — control-flow policy decision.

## Open Questions

None blocking. Default threshold values are provisional pending evaluation data; the mechanism to tune them (config) is owned by `[500]`.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (prompts/models/schema/metrics deferred) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (state table + explicit procedure) — `[000 §8.1.8]`
- [x] Traceability to FR-8–FR-15 — `[000 §8.1.9]`
- [x] In-loop critique preserved as a decision node — `[000 §8.3]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — the control flow is the project's central contract; changes require a full Change Request and architecture re-review (`[000 §9]`).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial control-flow state machine, decision procedure, thresholds, invariants. | ADR-0004 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: confidence derivation (m1), failure/timeout handling (m7), low-groundedness rationale (m8), web-tool scope (m4), provisional-threshold note (M5). | ADR-0016 |
