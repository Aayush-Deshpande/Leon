---
id: "900"
title: "Decision Log"
status: "Approved"
freeze_class: "living"
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["000"]
outputs:
  - "000"
  - "001"
  - "005"
  - "010"
  - "020"
  - "100"
  - "110"
  - "120"
  - "130"
  - "140"
  - "150"
  - "200"
  - "210"
  - "220"
  - "230"
  - "240"
  - "300"
  - "310"
  - "320"
  - "330"
  - "340"
  - "400"
  - "41x"
  - "500"
  - "610"
  - "620"
  - "690"
category: "Governance"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: []
---

# 900 — Decision Log

> Governed by `[000]`, structured per `[001]`. Append-only record of every non-trivial engineering and documentation decision, with rationale and alternatives (`[000 §1.12]`, `[000 §3]`). It records *why* a decision was made and links to *where* it is specified; it never restates the authoritative design itself.

## Purpose

Preserve the rationale and alternatives behind every non-trivial decision so that future contributors (human or AI) do not silently reverse deliberate choices.

## Scope

Decision records (ADR-style) and change requests. Each entry carries a `scope`/`affected-docs` tag so activities can load only the decisions relevant to their Context Package (`[000 §3]`, `[000 §5.2]`).

## Owned Concepts

1. Decision history, rationale, and superseded decisions.
2. Change-request records (`[000 §9]`).

## Must Never Contain

- The authoritative statement of any design, contract, or requirement — those live in the owning document; entries link to them (`[000 §6]`).

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[000]` | Defines what constitutes a decision, the change-management procedure, and the required entry format. |

## Downstream Consumers (Outputs)

All documents and all change-management, implementation, refactoring, and audit activities consult scoped entries here (`[000 §5.1]`, `[000 §9]`).

## Decision Records

### ADR-0001 — Add explicit Functional Requirements and System Workflows documents to Core Knowledge
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[000]`, `[110]`, `[120]`, `[130]`, `[140]`, `[150]`, `[020]`
- **Context:** The Core Knowledge sprint request named `110_FUNCTIONAL_REQUIREMENTS` and `120_SYSTEM_WORKFLOWS`, which conflicted with the frozen roadmap `[000 §3]` (`110_DOMAIN_MODEL`, `120_CONSTRAINTS_AND_ASSUMPTIONS`). Repurposing 110/120 would orphan two gate-critical owned concepts: the conceptual domain model and the assumption register (referenced by Gate G4, `[000 §6]`, LLM Rule 11, and frozen `[001]`/`[010]`). Separately, the frozen `[020]` entry assumes "functional requirements … captured in the knowledge base," but no document was explicitly scoped to own them — a latent gap.
- **Decision:** Adopt **Option B**. Keep `110_DOMAIN_MODEL` and `120_CONSTRAINTS_AND_ASSUMPTIONS` unchanged, and **additively** introduce two new Core Knowledge documents: `140_FUNCTIONAL_REQUIREMENTS` (owns testable functional requirement statements) and `150_SYSTEM_WORKFLOWS` (owns end-to-end functional/user workflows). Amend `[000]` roadmap, generation order, reading order, ownership map, propagation table, Phase D, and gate wording accordingly. Re-freeze `[000]` at v1.2.
- **Alternatives considered:**
  - *Option A — keep roadmap, treat requested names as informal:* preserves ownership but leaves the functional-requirements gap unaddressed.
  - *Option C — repurpose 110/120:* highest churn; orphans the domain model and assumption register and cascades edits into frozen `[001]`/`[010]`. Rejected.
- **Consequences:** Core Knowledge tier grows from four to six documents. `[020]`'s functional-requirements source becomes concrete (`140`). No existing owner is displaced; downstream churn is limited to additive references. Ownership boundaries: `140` owns *what* the system must do; `150` owns *the ordered end-to-end flows*; control-flow mechanics remain owned by `[210]`; the domain vocabulary/entities remain with `[010]`/`[110]`; assumptions/non-goals remain with `[120]`.
- **Specified in:** `[000 §3]` (roadmap entries for 140/150), `[000 §4]`, `[000 §6]`.

### ADR-0002 — Confirm corpus scope (Indian Contract Act, 1872 + bounded case law)
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[130]`, `[120]`
- **Context:** `leon.md` §11.1 / assumption A-1 (`[120]`) left corpus scope as an assumption requiring confirmation before ingestion. It blocks Gate G4 and G6. Per the standing decision policy, confirming the scope already proposed in the seed does not change project objectives or architecture.
- **Decision:** Adopt the `leon.md`-proposed scope: the complete Indian Contract Act, 1872 (bare act) plus a bounded, curated set of leading Indian judgments interpreting its key sections; India-only; English-only. Specified in `[130]`. A-1 status set to RESOLVED.
- **Alternatives considered:** Broader multi-statute corpus (rejected — exceeds SB-2 demo scope and NG-2); pausing for human confirmation (unnecessary — no objective/architecture change, within decision policy).
- **Consequences:** A-1 closes; ingestion phase (G6) prerequisite satisfiable once `[130]` freezes. Specific case-law membership deferred to ingestion phase within the bounds set by `[130]`.
- **Specified in:** `[130]` "Corpus Scope".

### ADR-0003 — Architecture baseline: component decomposition and single-instance topology
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[200]`
- **Context:** The system needs a component decomposition. `leon.md` §6/§8 already prescribes one; A-8 (`[120]`) constrains to single-instance demo scale.
- **Decision:** Adopt the `leon.md` §8 decomposition (9 components + 4 stores) as `[200]`'s component map, with a single-instance topology (no horizontal-scaling components) and no auth component (NG-3). Generation and Critique remain distinct components.
- **Alternatives considered:** Merging Generation+Critique (rejected — violates the differentiator, FR-10); microservice-per-component (rejected — exceeds A-8 demo scope).
- **Consequences:** Establishes the boundaries all Architecture/Impl build on. Deployment topology detailed later in `[500]`.
- **Specified in:** `[200]`.

### ADR-0004 — Control-flow policy: decision procedure, thresholds, retry cap
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[210]`, `[320]`
- **Context:** `[140]` FR-11–FR-15 require a deterministic pass/fallback decision; A-3 requires a bounded retry.
- **Decision:** Pass iff `relevance ≥ T_relevance AND groundedness ≥ T_groundedness AND no unverifiable citations`. On fail: tool-verify (once) → reformulate (bounded) → low-confidence. Defaults `T_relevance=0.70`, `T_groundedness=0.80`, `MAX_REFORMULATIONS=2`, tunable via config (`[500]`). Four control-flow invariants defined for `[320]`.
- **Alternatives considered:** Single combined score (rejected — hides relevance vs. groundedness failures); unbounded retries (rejected — A-3, cost/latency).
- **Consequences:** Threshold defaults are provisional pending evaluation data.
- **Specified in:** `[210]`.

### ADR-0005 — API style: FastAPI endpoints with SSE streaming
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[220]`
- **Context:** `leon.md` §3/§9 require a streamed answer and the endpoint set; NG-3 = no auth in demo.
- **Decision:** FastAPI HTTP surface; `POST /query` streams via **Server-Sent Events** (`status`/`token`/`final`/`error` events); plus `GET /health`, MCP-exposed `POST /tools/verify_citation`, internal `GET /evaluation/summary`. Endpoints unauthenticated in demo scope (implications owned by `[310]`).
- **Alternatives considered:** WebSockets (rejected — heavier than needed for one-way token stream); non-streaming only (rejected — `leon.md` §3 streaming UX).
- **Consequences:** Frozen at Gate G3; frontend/backend build against these shapes.
- **Specified in:** `[220]`.

### ADR-0006 — Storage stack: PostgreSQL + pgvector, library BM25, filesystem raw store
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[230]`
- **Context:** `leon.md` §10 requires vector, sparse, relational, and raw-document stores; A-8 favors minimal single-instance infra.
- **Decision:** PostgreSQL with `pgvector` for dense vectors; library-backed BM25 (persisted, rebuilt at ingestion) for sparse; PostgreSQL for Traces/corpus metadata; filesystem for raw documents (S3-compatible optional later).
- **Alternatives considered:** Dedicated vector DB + OpenSearch (rejected — over-provisioned for demo, more moving parts).
- **Consequences:** Schemas are the hard contract; tech choices are revisitable defaults.
- **Specified in:** `[230]`.

### ADR-0007 — AI model roles and default models
- **Date:** 2026-07-05
- **Status:** Accepted
- **Scope / affected-docs:** `[240]`, `[230]`
- **Context:** `leon.md` §5 defines five AI stages; A-2 (critique = same family, distinct prompt) and NG-4 (no fine-tuning) constrain choices.
- **Decision:** Embedding = general English embedding model (D=768, fixing `[230]`'s vector dimension); sparse = BM25; reranker = cross-encoder; generation = instruction-following API LLM; critique = same LLM family with a distinct prompt, invoked as a separate node. All off-the-shelf/API. Separation invariant defined for `[320]`.
- **Alternatives considered:** Trained critique classifier (rejected — A-2, out of scope); shared gen+critique call (rejected — FR-10 separation).
- **Consequences:** Concrete model identifiers are deployment-config (`[500]`); roles/I-O are the contract.
- **Specified in:** `[240]`.

### ADR-0008 — Coding standards & toolchain — CLASS: SOFT
- **Date:** 2026-07-05 · **Status:** Accepted · **Scope:** `[300]`
- **Decision:** Python 3.11+ / FastAPI / Pydantic v2 / `ruff` / `mypy` strict; TypeScript + React 18 + Vite / ESLint + Prettier; module layout mirrors `leon.md` §8; exact dependency pinning with lockfiles.
- **Alternatives:** black+flake8+isort (rejected — `ruff` consolidates); loose version ranges (rejected — safety/reproducibility).
- **Consequences:** Conventions revisitable via lightweight amendment.

### ADR-0009 — Security posture & no-auth bounds — CLASS: HARD (rate-limiting sub-rule SOFT)
- **Date:** 2026-07-05 · **Status:** Accepted · **Scope:** `[310]`, `[220]`
- **Decision:** Bound the deliberate no-auth scope: never bind the unauthenticated service to a public interface (SEC-1); secrets from env only; parameterized DB access; treat model/tool/retrieved content as untrusted; disclose LLM-provider data egress (PRIV-1); enable basic rate limiting (SEC-7, SOFT).
- **Alternatives:** Add auth now (rejected — NG-3); no egress disclosure (rejected — privacy risk).
- **Consequences:** `[500]` implements the network binding under SEC-1.

### ADR-0010 — Testing strategy & correctness properties — CLASS: HARD (tooling SOFT)
- **Date:** 2026-07-05 · **Status:** Accepted · **Scope:** `[320]`
- **Decision:** Four test levels incl. property-based testing (`pytest`+`hypothesis`, `vitest`); a catalog of 10 correctness properties (P1–P10) encoding `[210]` invariants 1–4, the `[240]` separation invariant, and key FRs; each property must pass before its phase audit.
- **Alternatives:** Example-based tests only (rejected — invariants need generative coverage).
- **Consequences:** Property catalog is a hard contract; tooling is revisitable.

### ADR-0011 — Prompt standards & critique output contract — CLASS: SOFT (output-contract keys HARD)
- **Date:** 2026-07-05 · **Status:** Accepted · **Scope:** `[330]`, `[220]`
- **Decision:** Centralized, versioned templates (PT-GEN/PT-CRIT/PT-REFORM) with anti-hallucination rules; critique emits JSON `{relevance, groundedness, unverifiable}` conforming to `[220]` `CritiqueJudgment`; post-freeze prompt changes require a CR + re-evaluation.
- **Alternatives:** Prompts inline in code (rejected — undiscoverable/unversioned).
- **Consequences:** Wording tunable; output-contract keys stability-sensitive.

### ADR-0012 — Metric definitions & trace semantics — CLASS: HARD
- **Date:** 2026-07-05 · **Status:** Accepted · **Scope:** `[340]`, `[230]`, `[220]`
- **Decision:** Fix the meaning of each `traces` field and define metrics (relevance, groundedness, retrieval precision proxy = mean top-k reranker score, fallback rate, latency p50/p95); async, non-blocking logging contract.
- **Alternatives:** Single combined quality score (rejected — hides relevance vs. groundedness).
- **Consequences:** New metrics addable via CR; definition changes require a full CR.

### ADR-0013 — Embedding model is a HARD contract (dimension pinned) — CLASS: HARD
- **Date:** 2026-07-06 · **Status:** Accepted · **Scope:** `[240]`, `[230]` · **Supersedes (in part):** ADR-0007 (embedding-model class only)
- **Context (M2):** ADR-0007 treated the embedding model as a revisitable/config default, but its output dimension `D=768` is baked into the hard-frozen `chunks.embedding vector(D)` schema (`[230]`). A "config" change would force a hard schema migration.
- **Decision:** Reclassify the **embedding model choice and its dimension `D` as HARD**. Changing either requires a full CR plus a stated re-embedding/migration procedure (rebuild `chunks.embedding`, re-index). Other model choices (reranker, generation, critique) remain revisitable defaults. Provider endpoint/credentials remain config (`[500]`), but the model identity/dimension are contracts.
- **Consequences:** Removes the soft/hard contradiction; embedding swaps are explicit migrations, not config toggles.

### ADR-0014 — Retrieval fusion (RRF) and retrieval sizing — CLASS: SOFT (defaults)
- **Date:** 2026-07-06 · **Status:** Accepted · **Scope:** `[240]`, `[200]`, `[220]`
- **Context (M3):** Dense+sparse "merge" was unspecified; candidate/context sizes unowned.
- **Decision:** Fusion = **Reciprocal Rank Fusion (RRF)** over the dense and sparse candidate lists, deduplicated by `chunk_id`, then reranked. Default sizing: dense `k_dense=20`, sparse `k_sparse=20`, post-rerank context `top_n=5`. Owned by `[240]`; values tunable at deploy (`[500]`).
- **Alternatives:** Weighted score union (rejected — requires score normalization across incomparable scales); no fusion (rejected — FR-2).
- **Consequences:** Retrieval is now deterministic and reproducible; `[220]` `top_n` default defined.

### ADR-0015 — MCP transport and tool registration — CLASS: HARD
- **Date:** 2026-07-06 · **Status:** Accepted · **Scope:** `[220]`, `[200]`
- **Context (M4):** The citation-verification tool was shown only as a REST route; the MCP server/transport/registration were undefined despite MCP being a stated deliverable (`leon.md` §2.5, FR-16).
- **Decision:** Expose tools via a **dedicated MCP server over stdio transport**, registering `verify_citation` (and, if enabled, `web_search`) with declared JSON input/output schemas identical to `[220]`'s tool contract. The internal `POST /tools/verify_citation` HTTP route and the MCP tool are two transports over the **same underlying capability** (one implementation, two adapters). The MCP server is a distinct process/entrypoint in C8 (`[200]`).
- **Alternatives:** REST-only (rejected — not MCP, fails FR-16 intent); HTTP/SSE MCP transport (deferred — stdio is standard and sufficient for single-instance A-8).
- **Consequences:** MCP is now buildable from the docs; the tool capability is transport-agnostic.

### ADR-0016 — Critique calibration & threshold validation approach — CLASS: HARD
- **Date:** 2026-07-06 · **Status:** Accepted · **Scope:** `[340]`, `[320]`, `[210]`
- **Context (M5):** The pass/fail gate relies on uncalibrated LLM-judge scores with no validation that scores/thresholds are meaningful.
- **Decision:** Introduce a **critique calibration procedure** owned by `[340]`: a small labeled evaluation set (grounded vs. ungrounded answers) drawn from the corpus (`[130]`), a **critique-agreement metric** (agreement between critique verdict and labels), and a documented procedure to **set the `[210]` thresholds from this data** rather than by fiat. `[320]` adds a validation check that the gate separates labeled grounded/ungrounded cases. `[210]` thresholds are marked provisional until calibrated.
- **Alternatives:** Ship fixed thresholds unvalidated (rejected — undermines the differentiator); train a classifier (rejected — A-2, NG-4).
- **Consequences:** The differentiator gains an objective validation basis; thresholds become data-driven.

### ADR-0017 — Repository reorganization, Planning sub-range, and filename reconciliation — CLASS: SOFT (structural)
- **Date:** 2026-07-06 · **Status:** Accepted · **Scope:** `[000]`, all documents
- **Context:** Pre-freeze reorganization requested; the Planning package (`410`–`470`) is not in the frozen roadmap `[000 §3]`; the freeze list used shorthand names `300_ENGINEERING_STANDARDS`/`330_PROMPT_STANDARDS`.
- **Decision:**
  1. **Directory structure** adopted under `docs/` with category folders (`00-governance`, `10-core-knowledge`, `20-architecture`, `30-engineering-standards`, `40-planning`, `60-audits`); `leon.md` remains at repository root. Document IDs and filenames preserved; ID-based citations (`[NNN §x]`) are path-independent, so no reference rewrites are required.
  2. **Planning sub-range added** to the roadmap (`[000 §3]`, category 400–499): `410_EPIC_BREAKDOWN`, `420_PHASE_EXECUTION_PLAN`, `430_BUILD_ORDER`, `440_DEFINITION_OF_DONE`, `450_IMPLEMENTATION_CHECKLIST`, `460_RISK_REGISTER`, `470_CONFIGURATION_MATRIX`. These are planning artifacts derived from the frozen knowledge base; they introduce no new architecture.
  3. **Filename reconciliation:** the canonical frozen files are `300_CODING_STANDARDS.md` and `330_PROMPT_ENGINEERING_STANDARDS.md`; the shorthand names in the freeze request are aliases — no rename.
- **Consequences:** `[000]` amended to v1.3 (§2 layout note, §3 planning entries). No content ownership changes.

### FREEZE-0001 — Documentation Freeze (Gate G4)
- **Date:** 2026-07-06 · **Status:** Executed · **Scope:** Core Knowledge + Architecture + Engineering Standards + `010`
- **Context:** Architecture Review passed; amendment sprint closed all Major/Minor findings; verification confirmed consistency.
- **Frozen documents and classes:** `010` (living, definitions freeze-on-reference); `100` (soft), `110` (hard), `120` (soft), `130` (hard), `140` (hard), `150` (soft); `200` (hard/boundaries), `210` (hard), `220` (hard), `230` (hard), `240` (hard), `300` (soft), `310` (soft; SEC-1/PRIV-1 hard), `320` (soft; property catalog hard), `330` (soft; output-contract keys hard), `340` (hard).
- **Effect:** These documents move to `status: Frozen`. Post-freeze changes follow the change path for each freeze class (`[000 §9]`). Governance `000`/`001` were already frozen. `020` is generated post-freeze from this baseline.
- **Assumptions:** all resolved/confirmed (A-1 RESOLVED per ADR-0002; A-2–A-8 CONFIRMED).

### CR-0001 — Implementation-completeness gap closure
- **Date:** 2026-07-06 · **Status:** Approved & executed · **Trigger:** Implementation Readiness Audit (findings A1–A6, config gap, O1–O3).
- **Scope / affected-docs:** `[240]`, `[230]`, `[220]`, `[340]`, `[320]`, `[470]`, new `[500]`; index `[005]`, matrix `[020]`.
- **Summary:** Complete the under-specified contracts so implementation requires zero undocumented decisions. Hard-frozen docs unfrozen → edited → re-verified → re-frozen per `[000 §9.1]`. Discrete decisions recorded as ADR-0018…0022; RRF-`k` and pgvector index as lightweight amendments of ADR-0014/ADR-0006.
- **Post-conditions:** `500` authored; `020`/`005` updated; final readiness verification run.

### ADR-0018 — Embedding model pinned: BAAI/bge-base-en-v1.5 — CLASS: HARD
- **Scope:** `[240]`, `[230]`. **Decision:** Fix the embedding model as **`BAAI/bge-base-en-v1.5`** (768-dim, open, local via `sentence-transformers`), including its query/passage prefix convention (`"query: "` / `"passage: "` per model card). `D=768` remains the hard schema contract (`[230]`). Rationale: reproducibility, no vendor lock-in, local, stable. **Alternatives:** OpenAI `text-embedding-3-small` (rejected — vendor lock-in, 1536-dim schema change, cost); `e5-base-v2` (viable alt, not chosen). **Supersedes:** ADR-0007/ADR-0013 embedding-identity portion (now concrete).

### ADR-0019 — Citation-verification matching algorithm — CLASS: HARD
- **Scope:** `[220]`, `[130]`. **Decision:** `verify_citation` resolves `locator` to a section/paragraph span in the raw Source Document (`[230]` D4), then: if `quoted_text` present, `exists=true` iff a **normalized** (lowercase, collapse whitespace, strip punctuation) substring match is found, with a **configurable fuzzy fallback** (default ratio **0.95**, set via `[500]`) to tolerate OCR variance; if `quoted_text` absent, `exists=true` iff the locator resolves to a real span. `matched_passage` = the resolved raw span. Guards `[320]` P3. **Alternatives:** exact-only (rejected — OCR brittleness); embedding-similarity match (rejected — verification must be lexical against ground truth).

### ADR-0020 — BM25 analyzer for sparse retrieval — CLASS: HARD
- **Scope:** `[240]`, `[230]`. **Decision:** Analyzer = lowercase + Unicode NFKC normalize; tokenizer **preserves statutory references** (e.g., `s.10`, `section 10(2)`, `10(1)(a)` are not split); English stopword removal; **no stemming** (protect exact legal terminology). Applied identically at index build and query time. **Alternatives:** default Porter-stemmed analyzer (rejected — harms exact statutory matching, the reason BM25 exists here).

### ADR-0021 — Critique calibration protocol — CLASS: HARD
- **Scope:** `[340]`, `[320]`, `[210]`. **Decision:** Calibration set = **≥ 100 labeled pairs, balanced 50 grounded / 50 ungrounded** (ungrounded synthesized by injecting fabricated citations or irrelevant context), labeled by the operator (single-tenant). Critique-agreement metric = accuracy vs. labels; **P11 pass bar = agreement ≥ 0.80**. `[210]` thresholds (`T_relevance`, `T_groundedness`) are chosen to maximize agreement on this set; provisional until this runs. **Alternatives:** 60-sample set (rejected — user directive for stronger statistics).

### ADR-0022 — Generation/Critique are provider-agnostic (interface, not model) — CLASS: HARD (interface); model SOFT/config
- **Scope:** `[240]`, `[500]`. **Decision:** Do **not** pin a generation/critique model. Define a **capability interface** the provider must satisfy: instruction-following, long-context, tool-call capable (preferred), deterministic-inference support (temperature/seed controllable), and fully configurable via `[500]`. Critique uses the **same provider/model family** as generation by default (A-2), overridable. Default provider **OpenRouter**, model configurable (e.g., `qwen/qwen3-32b`, `anthropic/claude-sonnet-4`) — swappable without touching architecture. Rationale: Leon demonstrates the *architecture* (RAG + self-critique + verification + orchestration), which must hold regardless of the underlying LLM. **Alternatives:** pin a specific model (rejected — vendor coupling, weaker portability).

### CR-0001 lightweight amendments
- **ADR-0014 (amended):** RRF rank constant **`k = 60`** added as a tunable default (`[240]`/`[470]`).
- **ADR-0006 (amended):** pgvector index = **HNSW**, `vector_cosine_ops` (cosine per `leon.md` §5.1), build params **`m=16, ef_construction=64`**, tunable (`[230]`/`[470]`).

## Implementation Notes

*(Non-ADR records of implementation sequencing. These do not change architecture, contracts, or frozen documentation.)*

### IMPL-NOTE-P1-01 — BM25 scoring deferred to P2 (sequencing only)
- **Phase:** P1 (Ingestion) · **Scope:** `[230]` D2, P1/P2 build order.
- **Note:** P1 **persists the tokenized sparse corpus** required for BM25 (`data/index/sparse/<version>/bm25.json`), satisfying `[230]` D2 ("tokenized chunk text … built/rebuilt during ingestion; persisted to disk"). **BM25 scoring is intentionally implemented in P2** because scoring is query-time behavior; consequently `rank-bm25` is a P2 dependency, not P1.
- **Nature:** This is an **implementation sequencing decision only**. It does **not** modify the architecture, any contract, or the frozen documentation. **No ADR required.**

## Assumptions

None. Assumptions are owned by `[120]` (`[000 §1.7]`).

## References

- `[000]` — Engineering Manual (governing document; §9 change management, §15 amendment).
- `[001]` — Document Template.

## Open Questions

None blocking. Living document (`[000 §7]`); entries are appended and never deleted (superseded entries are marked, `[000 §10]` Rule 18).

## Review Checklist

- [x] Single Responsibility — `[000 §8.1.1]`
- [x] Ownership integrity — `[000 §8.1.2]`
- [x] No duplication (links, not restatement) — `[000 §8.1.3]`
- [x] Dependency validity — `[000 §8.1.4]`
- [x] Template conformance — `[000 §8.1.5]`
- [x] Vocabulary conformance — `[000 §8.1.6]`
- [x] Explicit assumptions in `[120]` (none here) — `[000 §8.1.7]`
- [x] Determinism — `[000 §8.1.8]`
- [x] Traceability — `[000 §8.1.9]`
- [x] Frontmatter complete and valid — `[000 §7]`

## Freeze Class

`living` — append-only; never fully frozen; individual entries are immutable once recorded (superseded, not deleted). Semantics: `[000 §7]`.

## Status

`Active` (living log). Authoritative status in frontmatter.

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | 2026-07-05 | Engineering Documentation Lead | Initialized decision log; recorded ADR-0001. | ADR-0001 |
| 0.2 | 2026-07-05 | Engineering Documentation Lead | Recorded ADR-0002 (corpus scope) and ADR-0003–0007 (Architecture sprint). | ADR-0002…0007 |
| 0.3 | 2026-07-05 | Engineering Documentation Lead | Recorded ADR-0008–0012 (Engineering Standards sprint), classified HARD/SOFT. | ADR-0008…0012 |
| 0.4 | 2026-07-06 | Engineering Documentation Lead | Amendment pass: recorded ADR-0013–0016 resolving review findings M2–M5. | ADR-0013…0016 |
| 0.5 | 2026-07-06 | Engineering Documentation Lead | Recorded ADR-0017 (reorg + Planning range) and FREEZE-0001 (Documentation Freeze). | ADR-0017, FREEZE-0001 |
| 0.6 | 2026-07-06 | Engineering Documentation Lead | CR-0001: implementation-completeness closure (ADR-0018–0022 + amendments); authored 500. | CR-0001, ADR-0018…0022 |
| 0.7 | 2026-07-06 | Lead Software Engineer | Recorded IMPL-NOTE-P1-01 (BM25 scoring deferred to P2 — sequencing only). | IMPL-NOTE-P1-01 |
