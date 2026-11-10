---
id: "310"
title: "Security and Privacy"
status: "Frozen"
freeze_class: "soft"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["120", "200", "220", "240"]
outputs: ["320", "400", "41x", "500", "610", "620"]
category: "Engineering Standards"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: ["ADR-0009"]
---

# 310 — Security and Privacy

> Governed by `[000]`, structured per `[001]`. Owns security posture, secret handling, input validation, privacy/data-egress rules, and the bounds of the no-auth demo scope (`[000 §3]`). It contains no coding style (`[300]`) or deployment mechanics (`[500]`) — it states security *requirements*; `[500]` implements them.

## Purpose

Define the security and privacy rules Leon must follow, and precisely bound what the deliberate "no authentication" scope permits and forbids, so no assistant either adds unrequested auth or exposes the system unsafely.

## Scope

Covers secret/config handling, input validation, injection/tool safety, data egress/privacy, dependency safety, network-exposure posture, and the no-auth boundary. This document does **not** cover coding conventions (`[300]`), deployment tooling (`[500]`), or the legal-advice disclaimer (product behavior, FR-15/NG-1).

## Owned Concepts

1. Security rules and posture for the system.
2. The permitted/forbidden bounds of the no-auth demo scope.
3. Privacy and data-egress rules.

## Must Never Contain

- Coding style — owned by `[300]`.
- Deployment/infra mechanics — owned by `[500]` (this states requirements, not how to deploy).
- Wire error shapes — owned by `[220]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[120]` | NG-3/A-4 (no auth), SB-2 (demo scope). |
| `[200]` | Components and their trust boundaries. |
| `[220]` | The unauthenticated endpoint surface and the reserved `429`. |
| `[240]` | The external LLM provider stage that creates the data-egress surface (PRIV-1). |

## Downstream Consumers (Outputs)

`[300]`, Implementation, `[500]`, `[610]`, `[620]`.

## No-Auth Boundary (bounds NG-3 / A-4) — ADR-0009 (HARD)

| Permitted | Forbidden |
|-----------|-----------|
| Single-tenant, single-operator demo/portfolio use. | Public internet exposure of the unauthenticated API. |
| Running behind a trusted network boundary (localhost, private network, or an authenticating reverse proxy). | Adding auth/roles in code without a CR (NG-3 is deliberate). |
| Treating all callers as one trusted principal. | Storing end-user identity or acting as multi-tenant. |

**SEC-1 (HARD):** The unauthenticated service **must not be bound to a public interface**. Public exposure requires either an authenticating proxy or an auth CR amending NG-3. (`[220]` flagged this; `[310]` owns the rule; `[500]` implements the binding.)

## Security Rules

| ID | Rule | Class |
|----|------|-------|
| SEC-2 | Read all secrets/credentials from environment/config; never hard-code, never log, never write to `traces`. | HARD |
| SEC-3 | Validate `POST /query` input: enforce the `1..2000` char bound (`[220]`), reject oversized/empty; treat query text as untrusted. | HARD |
| SEC-4 | Use parameterized queries / an ORM for all DB access; never string-interpolate untrusted input into SQL. | HARD |
| SEC-5 | Treat model output, retrieved text, and tool inputs/outputs as **untrusted data**, never as instructions that alter control flow; the citation-verification tool performs a bounded lookup only (no code execution, no arbitrary path access). | HARD |
| SEC-6 | Pin dependencies (per `[300]`) and run vulnerability scanning in CI; flag typosquat-suspect packages. | SOFT |
| SEC-7 | Enable basic per-client rate limiting on `POST /query` (maps to `[220]` `429`) as an abuse/cost safeguard. | SOFT |

## Privacy & Data Egress

| ID | Rule | Class |
|----|------|-------|
| PRIV-1 | **Data egress disclosure (HARD):** user queries and retrieved corpus passages are sent to the external generation/critique LLM provider (`[240]`). This egress must be documented to the operator; no other third-party egress is permitted. | HARD |
| PRIV-2 | The `traces` store may contain user query text; treat it as sensitive, restrict access to the operator, and exclude secrets (SEC-2). | HARD |
| PRIV-3 | No end-user PII is deliberately collected (single-tenant demo); do not add analytics that transmit user content to third parties. | HARD |

## Assumptions

None introduced. Bounds NG-3, A-4 (`[120]`).

## References

- `[120]` — NG-3, A-4, SB-2.
- `[200]`, `[220]`, `[240]` — trust boundaries, endpoints, egress source.
- `[900#ADR-0009]`.

## Open Questions

None blocking. The concrete network binding and proxy choice are implemented by `[500]` under SEC-1.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (no style/deploy) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (rule tables) — `[000 §8.1.8]`
- [x] No-auth scope explicitly bounded — `[000 §3]` 310 intent
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`soft` — rules may be tightened via lightweight amendment; SEC-1/PRIV-1 are hard security constraints within it (weakening them is a scope/security change requiring escalation).

## Status

`Frozen` (Documentation Freeze, FREEZE-0001).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial security/privacy rules; bounded no-auth scope; data-egress disclosure. | ADR-0009 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: reconciled dependency graph (M6) — added `[240]` input (egress source), corrected outputs. | — |
