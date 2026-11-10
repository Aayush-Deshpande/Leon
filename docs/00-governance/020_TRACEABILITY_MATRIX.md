---
id: "020"
title: "Traceability Matrix"
status: "Frozen"
freeze_class: "generated"
owner: "Engineering Documentation Lead"
version: "0.2"
inputs: ["100", "110", "120", "130", "140", "150", "200", "210", "220", "230", "240", "300", "310", "320", "330", "340", "470", "500"]
outputs: ["610", "620", "690"]
category: "Governance"
---

# 020 — Traceability Matrix

> Generated artifact (`[000 §3]`, ADR-0016/deferred generation), produced from the frozen knowledge base. Establishes bidirectional traceability: every functional requirement maps forward to design, prompt, data, test, and metric; every design element maps back to a need. No orphans.

## 1. Functional Requirement → Design → Test → Metric

| FR | Realized by (component/design) | Contract/Data | Test property | Metric/ADR |
|----|-------------------------------|---------------|---------------|-----------|
| FR-1 | C2, C7 | `[220]` /query | P-e2e | — |
| FR-2 | C4 (dense+sparse+RRF) `[240]` | `[230]` chunks, sparse | P8 | retrieval precision proxy `[340]` |
| FR-3 | C4c reranker `[240]` S3 | — | P8 | retrieval precision proxy |
| FR-4 | C4 `[240]` sizing top_n | `[230]` metadata | P8 | — |
| FR-5 | C5 `[240]` S4 | PT-GEN `[330]` | P6 | groundedness `[340]` |
| FR-6 | C5 | `[220]` citations, PT-GEN | P7 | — |
| FR-7 | C5 `[240]` S4 | PT-GEN | P6 | — |
| FR-8 | C6 `[240]` S5, `[210]` CRITIQUE | PT-CRIT `[330]` | P1, P11 | relevance/groundedness `[340]` |
| FR-9 | C6 | PT-CRIT, `[220]` CritiqueJudgment | P3 | — |
| FR-10 | C6 distinct `[240]` sep. invariant | — | P1, P5 | — |
| FR-11 | C7 `[210]` DECIDE/RETURN | `[220]` response | P1, P7 | — |
| FR-12 | C7 `[210]` fallback | — | P1, P2 | fallback rate `[340]` |
| FR-13 | C7 `[210]` TOOL/REFORMULATE/LOW_CONF | `[220]` routing | P2, P3 | fallback rate |
| FR-14 | C7 `[210]` retry cap | — | P2 | — |
| FR-15 | C7 `[210]` LOW_CONFIDENCE | `[220]` response | P10 | — |
| FR-16 | C8 `[220]` MCP verify_citation (ADR-0015) | `[230]` D4 raw store, `[130]` | P3 | — |
| FR-17 | C8 (deferred, A-5) | `[220]` optional tool | — | — |
| FR-18 | C9 `[340]` | `[230]` traces (incl. reranker_topk_scores, confidence) | P9 | all metrics |
| FR-19 | C9 async | — | P9 | latency `[340]` |
| FR-20 | C9 `[220]` /evaluation/summary | `[230]` traces | P9 | summary metrics `[340]` |
| FR-21 | C1, C2 | `[220]` /query fields | P7 | — |
| FR-22 | C2 | `[220]` /health | — | — |
| FR-23 | C1 | `[220]` citations.passage | — | — |
| FR-24 | C7 (single-turn) | — | — | — |
| FR-25 | C3/C4 (English) `[130]` | — | — | — |

**No orphan FRs:** all FR-1…FR-25 map to at least one component. **No orphan components:** C1–C9 each realize ≥1 FR (see §4).

## 2. Assumptions → Resolution

| Assumption | Status | Resolved/owned by |
|-----------|--------|-------------------|
| A-1 corpus scope | RESOLVED | `[130]` / ADR-0002 |
| A-2 critique same family | CONFIRMED | `[240]` S5 |
| A-3 retry cap | CONFIRMED | `[210]` MAX_REFORMULATIONS / ADR-0004 |
| A-4 no auth | CONFIRMED | `[310]` / ADR-0009 |
| A-5 optional web tool | CONFIRMED | `[220]`/`[210]` (deferred) |
| A-6 English-only | CONFIRMED | `[130]` |
| A-7 single-turn | CONFIRMED | FR-24 `[140]` |
| A-8 single instance | CONFIRMED | `[200]`,`[230]` / ADR-0003,0006 |

## 3. Workflows → FRs

| Workflow | Steps realize |
|----------|---------------|
| W-1 Ingestion | corpus for FR-2/4/16 (`[130]`,`[230]`,`[240]`) |
| W-2 Query→Answer | FR-1..FR-11, FR-18/19, FR-21/23 |
| W-3 Fallback | FR-12..FR-16 |
| W-4 Logging | FR-18/19/20 |

## 4. Domain Entities & Components → Owner/Usage

| Entity `[110]` | Persisted `[230]` | Used by |
|----------------|-------------------|---------|
| Corpus/Source Doc/Section | source_documents, D4 | C3, C8 |
| Chunk/Metadata/Embedding | chunks | C3, C4 |
| Query/RetrievedCandidate/Context | (transient) | C4, C5, C6 |
| Answer/Citation | /query payload | C5, C1 |
| Critique Judgment | traces fields | C6, C7 |
| Fallback Action | routing_outcome | C7 |
| Trace | traces | C9 |

| Component | FRs | Docs |
|-----------|-----|------|
| C1 Frontend | 1,21,23,15 | 200,220 |
| C2 Backend API | 1,21,22 | 200,220 |
| C3 Ingestion | (2,4,16) | 200,130,230,240 |
| C4 Retrieval | 2,3,4 | 200,240,230 |
| C5 Generation | 5,6,7 | 200,240,330 |
| C6 Critique | 8,9,10 | 200,240,330,210 |
| C7 Orchestration | 11–15 | 200,210 |
| C8 MCP Tools | 16,17 | 200,220,130 |
| C9 Evaluation | 18,19,20 | 200,340,230 |

## 5. AI Stages / Prompts / Metrics / Properties → Source

| Item | Owner | Consumed by |
|------|-------|-------------|
| S1 Embedding (D=768, HARD) | `[240]`/ADR-0013 | `[230]` |
| S2 Sparse BM25 | `[240]`,`[230]` | C4 |
| S3 Reranker (cross-encoder) | `[240]` | C4, `[340]` proxy |
| S4 Generation | `[240]`, PT-GEN `[330]` | C5 |
| S5 Critique | `[240]`, PT-CRIT `[330]` | C6 |
| PT-GEN/PT-CRIT/PT-REFORM | `[330]` | C5/C6/C7 |
| Metrics (relevance, groundedness, precision proxy, fallback rate, latency) | `[340]` | `[220]` summary, `[320]` |
| P1–P11 | `[320]` | audits `[620]` |

## 6. ADR Coverage

| ADR | Class | Specified in |
|-----|-------|--------------|
| 0001 | — | `[000]`,`[140]`,`[150]` |
| 0002 | — | `[130]` |
| 0003 | HARD | `[200]` |
| 0004 | HARD | `[210]` |
| 0005 | HARD | `[220]` |
| 0006 | HARD | `[230]` |
| 0007 | SOFT | `[240]` |
| 0008 | SOFT | `[300]` |
| 0009 | HARD | `[310]` |
| 0010 | HARD | `[320]` |
| 0011 | SOFT | `[330]` |
| 0012 | HARD | `[340]` |
| 0013 | HARD | `[240]`,`[230]` |
| 0014 | SOFT | `[240]` |
| 0015 | HARD | `[220]` |
| 0016 | HARD | `[340]`,`[320]`,`[210]` |
| 0017 | SOFT | `[000]` |
| 0018 | HARD | `[240]`,`[230]`,`[500]` (embedding pinned) |
| 0019 | HARD | `[220]`,`[130]` (verification matching) |
| 0020 | HARD | `[240]`,`[230]` (BM25 analyzer) |
| 0021 | HARD | `[340]`,`[320]`,`[210]` (calibration) |
| 0022 | HARD/SOFT | `[240]`,`[500]` (provider-agnostic gen/critique) |

## 6b. Implementation-Completeness Closures (CR-0001)

| Item | Resolution | Owner |
|------|-----------|-------|
| Embedding model | `BAAI/bge-base-en-v1.5`, D=768 (HARD) | `[240]`/`[230]`/`[500]` |
| Reranker model | `BAAI/bge-reranker-base` (config) | `[240]`/`[500]` |
| Generation/critique | Provider-agnostic interface; OpenRouter default; config | `[240]`/`[500]` |
| Citation verification | Lexical normalized + fuzzy (0.95 default, config) | `[220]`/`[500]` |
| BM25 analyzer | lowercase/NFKC, preserve statutory refs, stopwords, no stemming | `[240]`/`[230]` |
| RRF constant | `k_rrf=60` | `[240]`/`[470]` |
| pgvector index | HNSW cosine, m=16, ef_construction=64 | `[230]`/`[470]` |
| Calibration | ≥100 balanced samples, agreement ≥0.80 (P11) | `[340]`/`[320]` |
| Config values | Concrete env contract + provider abstraction | `[500]`/`[470]` |

## 7. Orphan Check

- **Unimplemented requirements:** none — every FR (1–25) maps to a component and (where testable) a property.
- **Undocumented implementations:** none exist yet (pre-implementation); the matrix will be extended with code/test IDs per phase at each audit (G8).
- **Uncovered invariants:** `[210]` inv.1–4 → P1–P4; `[240]` separation → P5; calibration → P11.
