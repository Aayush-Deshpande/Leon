---
id: "320"
title: "Testing Strategy"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.3"
inputs: ["130", "140", "150", "200", "210", "220", "240", "310", "340"]
outputs: ["400", "41x", "610", "620", "020"]
category: "Engineering Standards"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0010", "ADR-0016", "ADR-0021"]
---

# 320 — Testing Strategy

> Governed by `[000]`, structured per `[001]`. Owns test policy and the catalog of correctness properties the system must uphold (`[000 §3]`). It contains no test code and no feature specs (it references FRs `[140]` and invariants `[210]`/`[240]`).

## Purpose

Define how correctness is proven — the test levels, coverage expectations, test-data policy, and the executable correctness properties that guard Leon's differentiating invariants.

## Scope

Covers test levels, tooling, coverage expectations, test-data policy, and the correctness-property catalog. This document does **not** contain implemented tests, feature behavior (`[140]`), or runtime metric definitions (`[340]`; those are operational, not test-time).

## Owned Concepts

1. Test policy (levels, coverage, data).
2. The catalog of correctness properties and what each guards.

## Must Never Contain

- Actual test code — owned by Implementation.
- Feature/requirement statements — owned by `[140]`.
- Runtime metric definitions — owned by `[340]`.
- The invariants themselves — owned by `[210]`/`[240]` (referenced here).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[200]` | Components under test and their boundaries. |
| `[210]` | Control-flow invariants (1–4) to encode as properties. |
| `[220]` | Interface contracts to test against. |
| `[240]` | Generation/critique separation invariant; AI-stage behaviors. |
| `[140]` | Functional requirements the properties trace to. |
| `[150]` | Workflows exercised by end-to-end tests. |
| `[130]` | Corpus subset used for fixtures and the calibration set. |
| `[310]` | Security rules for test data (no secrets in fixtures). |

## Downstream Consumers (Outputs)

Implementation/audits, `[610]`, `[620]`, and `[020]` (properties are traceability targets).

## Test Levels & Tooling (ADR-0010)

Per ADR-0010 (`[900#ADR-0010]`; HARD for the property catalog, SOFT for tooling).

| Level | Scope | Tooling (default) |
|-------|-------|-------------------|
| Unit | Single function/module; deterministic; LLM/model calls mocked. | `pytest` (backend), `vitest` (frontend). |
| Property-based | Invariants over generated inputs. | `hypothesis` (backend). |
| Integration | Component-to-component against `[220]` contracts; real stores, mocked/staged models. | `pytest` + `httpx`. |
| End-to-end | Full `POST /query` flow incl. SSE. | `httpx`/Playwright (frontend flow optional). |

**Coverage expectations:** orchestration (`C7`), critique (`C6`), and retrieval-merge (`C4`) paths require high coverage; **every correctness property below MUST have a passing test before its phase's audit (G7/G8)**.

## Correctness Property Catalog

Each property is executable and guards a specific invariant/requirement. "Guards" cites the owner of the invariant (not restated here).

| ID | Property (must always hold) | Guards | Method |
|----|-----------------------------|--------|--------|
| P1 | No answer is returned to the user without a completed critique for that answer. | `[210]` inv.1, FR-10/FR-11 | property + integration |
| P2 | `retry_count` never exceeds `MAX_REFORMULATIONS`; every query terminates in `RETURN` or `LOW_CONFIDENCE`. | `[210]` inv.2, FR-14 | property |
| P3 | A citation flagged unverifiable and not confirmed by the tool is never presented as verified/returned as valid. | `[210]` inv.3, FR-9 | property |
| P4 | Citation-verification tool is invoked at most once per turn. | `[210]` inv.4 | property |
| P5 | Generation and critique are distinct invocations (never a shared call/prompt). | `[240]` separation, FR-10 | unit + integration |
| P6 | Given empty or irrelevant context, the system does not emit a fabricated grounded answer (it hedges/low-confidence). | FR-7 | property |
| P7 | Every `returned` answer carries ≥1 citation; otherwise the outcome is `low_confidence`. | FR-6, FR-11 | property |
| P8 | Retrieval for a query draws from both dense and sparse sources before reranking. | FR-2 | integration |
| P9 | Every query produces a complete `traces` record, and logging never blocks the user response. | FR-18, FR-19 | integration |
| P10 | Every `low_confidence` response contains the professional-consultation advisory and a stated reason. | FR-15 | unit |
| P11 | On the ≥100-sample balanced calibration set (`[340]`), the calibrated critique gate classifies grounded vs. ungrounded answers with **critique-agreement ≥ 0.80**. | `[340]` calibration (ADR-0016/ADR-0021), review M5 | calibration test |

## Test-Data Policy

- Use a small deterministic fixture subset of the corpus (drawn per `[130]`); fixed random seeds for reproducibility.
- Mock the generation/critique models in unit tests with deterministic stubs; use staged/real models in a bounded integration suite.
- No secrets in fixtures (`[310]` SEC-2); fixture legal text is public-domain per `[130]`.

## Assumptions

None introduced.

## References

- `[210]` inv.1–4; `[240]` separation; `[140]` FRs; `[220]` contracts.
- `[900#ADR-0010]`.

## Open Questions

None blocking. Exact numeric coverage thresholds are a phase-plan detail; the property catalog is mandatory regardless.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (no code/specs/metrics) — `[000 §8.1.2]`
- [x] No duplication (invariants referenced) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` (none) — `[000 §8.1.7]`
- [x] Determinism (property table) — `[000 §8.1.8]`
- [x] Includes correctness properties for routing invariants — `[000 §8.3]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — properties may be *added* via lightweight amendment; removing/weakening a property requires a CR (`[000 §3]` 320 rule).

## Status

`Frozen` (CR-0001 applied; re-frozen).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial test strategy + 10 correctness properties. | ADR-0010 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: added P11 calibration-validation (M5); reconciled deps to 130/140/150/310 (M6). | ADR-0016 |
| 0.3 | 2026-07-06 | Engineering Documentation Lead | CR-0001: P11 concrete bar (≥100 samples, agreement ≥0.80, ADR-0021). Re-frozen. | CR-0001 |
