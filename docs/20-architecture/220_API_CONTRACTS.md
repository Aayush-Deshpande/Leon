---
id: "220"
title: "API Contracts"
status: "Frozen"
freeze_class: "hard"
owner: "Engineering Documentation Lead"
version: "0.3"
inputs: ["200", "110", "120", "140", "210"]
outputs: ["230", "240", "300", "310", "320", "330", "340", "400", "41x", "500", "610"]
category: "Architecture"
reviewers: []
last_reviewed: "2026-07-06"
supersedes: null
superseded_by: null
decision_refs: ["ADR-0005", "ADR-0015", "ADR-0019"]
---

# 220 — API Contracts

> Governed by `[000]`, structured per `[001]`. Owns every interface contract: external HTTP endpoints, request/response schemas, status/error shapes, streaming behavior, MCP tool interfaces, and internal component interfaces (`[000 §3]`). It is the hard-frozen boundary both sides build against. It contains no implementation logic (200-series/Impl), prompts (`[330]`), or storage schemas (`[230]`).

## Purpose

Fix the shapes of every interface so frontend, backend, tools, and components can be built independently and correctly, and so "Interfaces Frozen" (Gate G3) has a concrete subject.

## Scope

Covers external endpoints, their request/response/error schemas and status codes, the streaming protocol, MCP tool signatures, and internal service interface contracts. This document does **not** cover how endpoints are implemented, routing logic (`[210]`), stored data shapes (`[230]`), or prompts (`[330]`).

## Owned Concepts

1. External HTTP endpoint contracts (paths, methods, request/response/error schemas, status codes).
2. The streaming protocol for `POST /query`.
3. MCP tool interface signatures.
4. Internal component interface contracts.

## Must Never Contain

- Implementation logic — owned by Implementation (400-series).
- Control-flow/routing decisions — owned by `[210]` (this owns only the *shape* of the routing metadata field).
- Storage schemas — owned by `[230]`.
- Prompt text/output formats — owned by `[330]`.

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[200]` | Components and their interaction points. |
| `[110]` | Entities (Answer, Citation, Trace) shaped by these contracts. |
| `[120]` | NG-3 (no auth), A-5 (optional tool). |
| `[140]` | FR-16/FR-20/FR-21/FR-22 endpoint requirements. |
| `[210]` | The routing-metadata and confidence values surfaced in responses. |

## Downstream Consumers (Outputs)

Frontend + backend implementation, MCP tool impl, `[230]`, `[240]`, `[300]`, `[310]`, `[320]`, `[500]`, `[610]`.

## Security Note (deferred to `[310]`)

Per NG-3 (`[120]`), these endpoints are **unauthenticated** in the initial single-tenant demo scope. This is a deliberate, documented choice; its security implications and any network-exposure mitigations are owned by `[310]`. Implementers must not add auth without a CR, and must not expose the service publicly without consulting `[310]`.

## External Endpoints

### `POST /query` (realizes FR-1, FR-21)
Request:
```json
{ "query": "string (required, 1..2000 chars)" }
```
Response (non-streaming form / final payload): `application/json`
```json
{
  "answer": "string",
  "citations": [
    { "id": "string (citation id, unique within this answer)",
      "chunk_id": "string (the referenced chunk in [230])",
      "source_document": "string",
      "locator": "string (e.g., 'Section 10' | 'Judgment X ¶4')", "passage": "string" }
  ],
  "confidence": "high | low",
  "routing": { "outcome": "returned | reformulated | tool_verified | low_confidence",
               "reformulations": 0 },
  "reason": "string | null"
}
```
- `confidence` and `routing.outcome` values are produced by `[210]`; this fixes only their shape.
- Streaming form: see Streaming Protocol below.
- Status: `200` success; `422` invalid request body; `503` dependency unavailable; error shape below.

### `GET /health` (realizes FR-22)
Response `200`:
```json
{ "status": "ok", "version": "string" }
```

### `POST /tools/verify_citation` (internal HTTP adapter; realizes FR-16)
Request:
```json
{ "locator": "string", "quoted_text": "string | null" }
```
Response `200`:
```json
{ "exists": true, "source_document": "string | null", "matched_passage": "string | null" }
```
- Checks against the raw document store (D4, ground truth per `[130]`).

**Matching algorithm (ADR-0019):**
1. Resolve `locator` to a section/paragraph span in the raw Source Document (via stored structure/`raw_path`, `[230]`).
2. If the locator does not resolve to a real span → `{ "exists": false }`.
3. If `quoted_text` is null → `exists=true`, `matched_passage` = the resolved span.
4. If `quoted_text` is present → normalize both sides (lowercase, collapse whitespace, strip punctuation) and test substring containment; if not found, apply a **fuzzy ratio** with a **configurable threshold (default `0.95`, `CITATION_FUZZY_THRESHOLD` in `[500]`)** to tolerate OCR variance. `exists=true` iff matched; `matched_passage` = the matched raw span.
- The comparison is **lexical against ground truth** — never embedding similarity — so it cannot be fooled by paraphrase. Guards `[320]` P3.

### `GET /evaluation/summary` (internal/admin; realizes FR-20)
Response `200`:
```json
{ "avg_groundedness": 0.0, "avg_relevance": 0.0, "fallback_rate": 0.0,
  "latency_ms": { "p50": 0, "p95": 0 }, "count": 0 }
```
- Metric *definitions* owned by `[340]`; this fixes the response shape only.

## Streaming Protocol (`POST /query`)

**Selection (resolves review m5):** the client selects the form via the `Accept` header — `Accept: text/event-stream` → SSE stream; otherwise (`application/json`) → the single JSON payload above. Default is JSON when `Accept` is absent.

Per ADR-0005 (`[900#ADR-0005]`): **Server-Sent Events (SSE)**, `Content-Type: text/event-stream`. Event sequence:

| Event | Data | When |
|-------|------|------|
| `status` | `{ "state": "retrieving | generating | checking" }` | On state changes (mirrors `[210]` states, coarse-grained). |
| `token` | `{ "text": "string" }` | Incremental tokens of the **final, post-critique** answer (see note). |
| `final` | The full JSON response object above. | Terminal success. |
| `error` | The error object below. | Terminal failure. |

**Streaming vs. in-loop critique (review O3):** because the critique gate runs *before* return (`[210]` inv.1), `token` events stream the **already-critique-passed final answer** (a post-critique replay), never a live draft. On a fallback/low-confidence outcome, no `token` events are emitted — the terminal `final` (or `error`) event carries the low-confidence response.

## Error Shape

All non-2xx responses use:
```json
{ "error": { "code": "string", "message": "string", "detail": "string | null" } }
```
Status codes: `422` validation, `429` rate limit (if enabled by `[310]`), `503` upstream/model/store unavailable, `500` unexpected. The **timeout/failure-handling policy** (when a model/store call fails or times out) is owned by `[210]`; `503` is surfaced only when no response can be produced (review m7).

## MCP Transport & Tool Registration (ADR-0015, resolves review M4)

The MCP capability is exposed by a **dedicated MCP server over stdio transport**, distinct from the FastAPI HTTP app but backed by the **same underlying tool implementation** (one capability, two adapters — the internal `POST /tools/verify_citation` route and the MCP tool).

| Aspect | Contract |
|--------|----------|
| Transport | MCP over **stdio** (single-instance, A-8). |
| Registered tools | `verify_citation` (always); `web_search` (only if enabled per A-5 — deferred). |
| `verify_citation` MCP schema | Input `{ "locator": string, "quoted_text": string\|null }`; Output `{ "exists": bool, "source_document": string\|null, "matched_passage": string\|null }` — identical to the HTTP contract above. |
| Registration | Tools are registered with the MCP server at startup with the JSON schemas above; the server runs as a separate entrypoint within component C8 (`[200]`). |

The HTTP route and the MCP tool MUST stay schema-identical; changing one changes both (single capability).

## Internal Component Interface Contracts

Contracts between components (`[200]`); shapes only, no implementation. Entity types per `[110]`. **This document is the single owner of the `CritiqueJudgment` field set** (resolves review m3); `[330]` references it and `[340]` defines its field semantics.

| Interface | Input | Output |
|-----------|-------|--------|
| `Retrieval.retrieve` | `query`, `top_n` (default from `[240]` ADR-0014 sizing) | `RankedContext` (ordered `RetrievedCandidate[]` with metadata) |
| `Generation.generate` | `query`, `RankedContext` | `DraftAnswer` (text + `Citation[]` markers) |
| `Critique.evaluate` | `query`, `RankedContext`, `DraftAnswer` | `CritiqueJudgment` (`relevance`, `groundedness`, `unverifiable[]`) |
| `Orchestration.handle` | `query` | `QueryResponse` (the `/query` payload) + `Trace` handle |
| `Tools.verify_citation` | `locator`, `quoted_text?` | verification result (see endpoint) |
| `Evaluation.log` | `Trace` | ack (async, non-blocking) |

Field *semantics* of `CritiqueJudgment`/`Trace` are owned by `[340]`; storage by `[230]`.

## Assumptions

None introduced. NG-3 and A-5 (`[120]`) shape the security note and optional tool.

## References

- `leon.md` §9 — API source.
- `[200]`, `[210]`, `[110]`, `[140]` — inputs.
- `[900#ADR-0005]` — API/streaming decision.

## Open Questions

None blocking. Rate limiting (`429`) is conditional on `[310]`'s decision; the shape is reserved here.

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity (logic/schema/prompts deferred) — `[000 §8.1.2]`
- [x] No duplication — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Assumptions tracked in `[120]` — `[000 §8.1.7]`
- [x] Determinism (schemas + tables) — `[000 §8.1.8]`
- [x] Traceability to FRs — `[000 §8.1.9]`
- [x] Security implication of no-auth flagged and deferred to `[310]` — `[000]` security
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`hard` — interface contracts are the parallel-development boundary; frozen at Gate G3; changes require a full Change Request (`[000 §9]`).

## Status

`Frozen` (CR-0001 applied; re-frozen).

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initial API, streaming, MCP, and internal interface contracts. | ADR-0005 |
| 0.2 | 2026-07-06 | Engineering Documentation Lead | Amendment: MCP transport/registration (M4); streaming negotiation + citation id (m5); top_n default ref (M3); CritiqueJudgment ownership (m3); timeout policy note (m7); reconciled deps (M6). | ADR-0015 |
| 0.3 | 2026-07-06 | Engineering Documentation Lead | CR-0001: citation-verification matching algorithm (ADR-0019); streaming/critique clarification (O3). Re-frozen. | CR-0001 |
