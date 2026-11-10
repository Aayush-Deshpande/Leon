# Project Leon — Engineering Specification

**Status:** Design specification (pre-implementation). This document is the canonical source of truth for the project. No code has been written yet; this defines what is to be built.

---

## 1. Project Overview

### What it is
Leon is a full-stack Retrieval-Augmented Generation (RAG) system that answers natural-language legal questions by retrieving relevant passages from a corpus of legal documents (statutes, case law) and generating grounded, cited answers. Its defining characteristic is a **self-evaluating retrieval layer**: before the system commits to an answer, it scores its own retrieval quality and citation-groundedness, and takes a corrective action if that score is low, rather than answering regardless of confidence.

### Problem it solves
Standard RAG systems retrieve context, stuff it into a prompt, and generate an answer unconditionally — even when retrieval quality is poor or the model's claimed citations don't actually exist in the source material. In legal contexts, this failure mode (a confidently stated but fabricated citation) is a well-documented and specifically damaging problem. Leon addresses this by making evaluation a **control-flow decision inside the agent loop**, not an offline metric computed after the fact.

### Core objective
Given an arbitrary legal question, return an answer that is either (a) well-grounded in retrieved source material with verifiable citations, or (b) explicitly flagged as low-confidence with a stated reason, rather than a fluent but ungrounded guess.

### High-level workflow
1. User submits a natural-language legal question via a chat interface.
2. The system retrieves candidate passages using hybrid search (dense + BM25) over an indexed legal corpus.
3. Retrieved passages are reranked for relevance.
4. A generation step drafts an answer grounded in the retrieved context, with citations to specific source passages.
5. A self-critique step scores (a) retrieval relevance and (b) whether the citations in the draft answer actually exist in the retrieved source text.
6. If the score is above threshold, the answer is returned to the user with citations.
7. If below threshold, the system takes a fallback action: reformulate the query and re-retrieve, invoke an MCP tool (e.g., citation verification or web search), or return an explicit low-confidence response instructing the user to consult a professional.
8. Every query is logged with evaluation metrics (retrieval precision proxy, groundedness score, fallback trigger) for offline analysis.

### Key innovations
- **In-loop evaluation**: the critique step is a decision node in the agent's control flow, not a post-hoc measurement. This is the project's core differentiator from typical RAG demos.
- **Citation-groundedness as a first-class check**: rather than only scoring "is this relevant," the system explicitly checks whether cited sections/clauses are traceable to retrieved text.
- **Generalized semantic retrieval**: the system is not built around a fixed set of FAQ patterns; it is designed to handle arbitrary phrasings against the same retrieval and evaluation pipeline.

### Project scope
Leon is scoped as a **single-domain, single-jurisdiction, demo-to-production-quality system** — not a general-purpose legal AI platform. It is meant to be a complete, working, defensible system on a bounded corpus, not a broad product.

**Assumption (labeled):** Given no jurisdiction was specified, this document assumes the corpus is scoped to a **single Indian statute or a small, well-defined set of related statutes** (e.g., the Indian Contract Act, 1872, plus a limited set of associated case law), rather than "all of law." This keeps the project buildable in a realistic timeframe while preserving technical depth. This should be confirmed/changed before implementation begins, as it affects ingestion scope.

### Explicit non-goals
- Leon is **not** a substitute for legal advice and does not claim to be. All outputs are informational.
- Leon does not attempt multi-jurisdictional coverage.
- Leon does not implement user authentication/authorization in its initial scope (see Section 16 for rationale and future extension).
- Leon does not fine-tune any models; it uses retrieval + prompting + off-the-shelf or API-based LLMs.
- Leon does not implement a document-upload feature for arbitrary user-supplied legal documents in its initial scope (corpus is pre-ingested and fixed); this is listed as a future improvement.

---

## 2. Core Features

### 2.1 Hybrid Retrieval
Combines dense vector similarity search with BM25 sparse keyword search over the legal corpus, then reranks combined candidates. This exists because legal text relies heavily on exact term matching (section numbers, defined terms, specific phrasing) that pure embedding similarity often misses, while dense retrieval captures semantic paraphrase queries that BM25 misses. Neither alone is sufficient for legal text.

### 2.2 Grounded Answer Generation
Given reranked context, an LLM generates an answer that must cite the specific source passage(s) it draws from. This exists to make the system's claims auditable rather than opaque.

### 2.3 Self-Critique Layer
A separate evaluation step (can be a second LLM call with a distinct prompt, or a smaller/cheaper model) scores two things: (a) whether the retrieved context is actually relevant to the query, and (b) whether the citations in the generated answer can be verified against the retrieved source text. This exists to prevent the system from confidently returning ungrounded or hallucinated legal claims. It interacts directly with the Agent Workflow (Section — see Fallback Logic) by determining whether the draft answer is returned as-is or triggers a corrective action.

### 2.4 Fallback / Corrective Actions
When the self-critique score is below threshold, the system does not simply return the low-confidence answer. It instead: (a) reformulates the query and re-retrieves, (b) invokes an MCP tool for citation verification or supplementary retrieval, or (c) returns an explicit "low confidence" response to the user. This exists because silently returning a bad answer is worse than surfacing uncertainty.

### 2.5 MCP Tool Integration
At least one tool is exposed via MCP: a citation-verification tool that checks whether a cited section/clause exists in the indexed source documents (as opposed to being fabricated by the generation step). This reuses prior MCP server experience and demonstrates tool-calling/agentic behavior, which is directly relevant to the target use case (product roles involving agents and integrations).

**Assumption (labeled):** A second MCP tool for general web search fallback is included in scope as a "nice-to-have," used only when the internal corpus genuinely lacks coverage for a query (e.g., a question about a law outside the ingested corpus). This is marked optional and can be deferred without affecting the core system.

### 2.6 Evaluation Harness (In-Loop Logging)
Every query is logged with: retrieval precision proxy (e.g., reranker relevance scores of top-k), the self-critique groundedness score, whether a fallback was triggered and which type, and end-to-end latency. This exists to make the system's real-world failure rate visible and analyzable, rather than assumed.

---

## 3. Complete User Flow

1. User opens the chat interface (React frontend).
2. User types a natural-language legal question and submits it.
3. Frontend sends the query to the backend API (FastAPI) via a POST request.
4. Backend embeds the query and performs hybrid retrieval against the vector store + BM25 index.
5. Reranker reorders retrieved candidates by relevance.
6. Generation LLM call produces a draft answer with inline citations, using the reranked context.
7. Self-critique LLM call evaluates the draft answer against the retrieved context for relevance and citation-groundedness.
8. **If confidence is sufficient:** the answer, with citations, is streamed back to the frontend and displayed with source references (clickable/expandable to show the original passage).
9. **If confidence is insufficient:** the backend either (a) silently retries with a reformulated query (transparent to the user, possibly shown as a brief "still checking..." state), (b) calls the MCP tool for citation verification or supplementary retrieval, or (c) returns a response explicitly stating low confidence, along with whatever partial information is available and a note to consult a professional.
10. The frontend displays the final answer, its citations (with the ability to view the underlying source passage), and — optionally, for transparency — an indicator of confidence level.
11. The query, retrieved context, generated answer, critique score, and any fallback action taken are logged to the evaluation store in the background (non-blocking to the user-facing response).

---

## 4. System Workflow

**Stage 1 — Ingestion (offline, pre-deployment):**
Raw legal documents → text extraction/cleaning → chunking → embedding → indexing into vector store, with parallel indexing into a BM25 sparse index. Metadata (source document, section number, jurisdiction, document type) is attached to each chunk at this stage.

**Stage 2 — Query-time retrieval:**
User query → query embedding → parallel dense search (vector store) and sparse search (BM25) → merge candidate sets → rerank (cross-encoder or LLM-based reranker) → top-N context assembled with citations metadata attached.

**Stage 3 — Generation:**
Assembled context + query → prompt template → LLM generates answer with inline citation markers referencing specific chunks.

**Stage 4 — Self-critique:**
Draft answer + retrieved context + query → critique prompt → LLM (or smaller model) returns a structured judgment: relevance score, groundedness score, list of any citations that could not be verified against source text.

**Stage 5 — Decision / fallback:**
Critique output → threshold check → route to (a) direct return, (b) query reformulation and loop back to Stage 2, (c) MCP tool invocation, or (d) explicit low-confidence response.

**Stage 6 — Logging:**
All of the above (query, retrieved chunks, draft answer, critique scores, routing decision, latency) written to the evaluation data store asynchronously.

---

## 5. AI Workflow

### 5.1 Embedding Model
- **Purpose:** Convert query and document chunks into dense vector representations for semantic search.
- **Input:** Raw text chunk or query string.
- **Output:** Fixed-dimension embedding vector.
- **Processing:** Batch-embed all corpus chunks at ingestion time; embed each incoming query at request time.
- **Expected behaviour:** Semantically similar legal concepts should have high cosine similarity even with different surface phrasing.

### 5.2 Sparse Retrieval (BM25)
- **Purpose:** Capture exact-term matches (section numbers, defined legal terms) that dense embeddings may under-weight.
- **Input:** Query string, indexed corpus.
- **Output:** Ranked list of candidate chunks by BM25 score.
- **Processing:** Standard inverted-index term-frequency scoring.
- **Expected behaviour:** Queries containing exact statutory references should surface the correct section reliably.

### 5.3 Reranker
- **Purpose:** Reorder the merged dense + sparse candidate set by true query-relevance, since neither retrieval method alone produces optimal ordering.
- **Input:** Query + candidate chunk set (merged from 5.1/5.2).
- **Output:** Reordered, scored candidate list.
- **Processing:** Cross-encoder model or LLM-based pairwise/listwise scoring.
- **Expected behaviour:** Highest-ranked chunks should be the most directly relevant to answering the query.

### 5.4 Generation LLM
- **Purpose:** Produce a natural-language answer grounded in retrieved context, with explicit citations.
- **Input:** User query + top-N reranked context chunks (with metadata).
- **Output:** Answer text with inline citation markers tied to specific chunk IDs.
- **Processing:** Prompted with instructions to answer only from provided context and to cite explicitly; no unguided generation.
- **Expected behaviour:** Should refuse or hedge when context is insufficient, rather than filling gaps from parametric knowledge.

### 5.5 Self-Critique LLM (or smaller model)
- **Purpose:** Independently evaluate the draft answer's grounding before it's returned to the user.
- **Input:** Query, retrieved context, draft answer with citations.
- **Output:** Structured judgment — relevance score, groundedness score, list of unverifiable citations.
- **Processing:** Separate prompt/model from generation, to avoid the same model rubber-stamping its own output. A distinct prompt framing (or smaller/different model) is used to reduce self-confirmation bias.
- **Expected behaviour:** Should flag citations that don't appear in the provided context, and score relevance conservatively.

**Assumption (labeled):** The critique step uses the same LLM family but a distinct system prompt, rather than a separately trained classifier, since training a custom classifier is out of scope for this project's timeline. This can be revisited in Future Improvements.

### 5.6 Interaction Between AI Components
Retrieval (5.1/5.2) feeds the Reranker (5.3), whose output feeds both Generation (5.4) and the Self-Critique step (5.5) — the critique step re-examines the same context Generation used, so it can independently verify grounding rather than trusting Generation's self-report.

---

## 6. Component Breakdown

- **Ingestion Service:** Responsibility: transform raw legal documents into indexed, searchable chunks. Input: raw document files. Output: populated vector store + BM25 index with metadata. Internal behaviour: extraction → cleaning → chunking → embedding → dual indexing.
- **Retrieval Service:** Responsibility: given a query, return ranked candidate context. Input: query string. Output: ranked, reranked chunk list with metadata. Internal behaviour: parallel dense/sparse search, merge, rerank.
- **Generation Service:** Responsibility: produce a cited draft answer. Input: query + ranked context. Output: draft answer with citation markers. Internal behaviour: prompt construction, LLM call, citation-marker parsing.
- **Critique Service:** Responsibility: evaluate draft answer grounding. Input: query, context, draft answer. Output: structured score + flagged issues. Internal behaviour: separate prompt/model call, structured output parsing.
- **Orchestration/Agent Controller:** Responsibility: route between direct return, reformulation, MCP tool call, or low-confidence response based on critique output. Input: critique result. Output: final response payload + routing decision (for logging). Internal behaviour: threshold-based branching logic (see Section 7).
- **MCP Tool Layer:** Responsibility: expose citation-verification (and optionally web-search fallback) as callable tools. Input: tool-specific parameters (e.g., a citation string to verify). Output: verification result or supplementary retrieved content.
- **Evaluation Logging Service:** Responsibility: persist per-query metrics asynchronously. Input: full query trace. Output: written records in the evaluation data store.
- **Frontend (React):** Responsibility: chat interface, citation display, confidence indication. Input: user text. Output: rendered conversation with sources.
- **Backend API (FastAPI):** Responsibility: orchestrate the above services behind a request/response (or streaming) interface for the frontend.

---

## 7. Data Flow

User input (text) → Backend API receives request → Query embedded → Retrieval Service queries vector store + BM25 index in parallel → merged candidates passed to Reranker → top-N reranked context returned → Generation Service constructs prompt from context + query → LLM returns draft answer with citations → Critique Service receives (query, context, draft answer) → returns structured judgment → Orchestration Controller branches based on judgment:
  - **Pass:** response formatted with citations → returned to frontend.
  - **Fail → Reformulate:** query rewritten → loop back to Retrieval Service (bounded retry count — see Assumption below).
  - **Fail → Tool call:** MCP Tool Layer invoked → result incorporated → re-evaluated or returned directly depending on tool type.
  - **Fail → Explicit low-confidence:** formatted low-confidence response returned directly.
Throughout, a trace object accumulates all intermediate data and is written to the Evaluation Logging Service asynchronously after the user-facing response is sent (non-blocking).

**Assumption (labeled):** Query reformulation retry is capped at a small fixed number of attempts (e.g., 2) before falling through to an explicit low-confidence response, to prevent unbounded latency/cost from repeated re-retrieval loops.

---

## 8. Project Structure

```
leon/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app entrypoint
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── query.py       # POST /query endpoint
│   │   │       └── health.py      # health check endpoint
│   │   ├── retrieval/
│   │   │   ├── dense.py           # vector store query logic
│   │   │   ├── sparse.py          # BM25 query logic
│   │   │   └── reranker.py        # reranking logic
│   │   ├── generation/
│   │   │   └── generator.py       # generation LLM call + citation parsing
│   │   ├── critique/
│   │   │   └── critic.py          # self-critique LLM call + scoring
│   │   ├── orchestration/
│   │   │   └── controller.py      # routing/fallback decision logic
│   │   ├── tools/
│   │   │   ├── citation_verify.py # MCP tool: citation verification
│   │   │   └── web_fallback.py    # MCP tool: optional web search fallback
│   │   ├── ingestion/
│   │   │   ├── extract.py         # document text extraction
│   │   │   ├── chunk.py           # chunking logic
│   │   │   └── index.py           # embedding + indexing pipeline
│   │   ├── evaluation/
│   │   │   └── logger.py          # async logging to evaluation store
│   │   ├── models/                # request/response schemas (Pydantic)
│   │   └── config.py              # environment/config management
│   ├── tests/
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/            # chat UI, citation display, confidence indicator
│   │   ├── pages/
│   │   ├── api/                   # backend API client
│   │   └── state/                 # frontend state management
│   ├── public/
│   └── Dockerfile
├── data/
│   └── corpus/                    # raw legal source documents (pre-ingestion)
├── docker-compose.yml
├── .env.example
└── README.md
```

Each folder exists to keep retrieval, generation, critique, and orchestration logic separable and independently testable — this separation directly mirrors the system's core design principle (evaluation as a distinct, inspectable step, not folded into generation).

---

## 9. API Overview

- `POST /query` — Accepts a user question, returns the final answer, citations, confidence indicator, and routing metadata (which fallback path, if any, was taken).
- `GET /health` — Basic liveness/readiness check.
- `POST /tools/verify_citation` (internal, MCP-exposed) — Given a citation string, checks whether it exists in the indexed corpus.
- `GET /evaluation/summary` (optional, internal/admin use) — Returns aggregate evaluation metrics (average groundedness score, fallback rate, latency distribution) for monitoring the system's real-world behavior.

---

## 10. Data Storage

- **Vector store:** Stores dense embeddings of document chunks plus metadata (source document, section, chunk text, document type). Used for semantic similarity search.
- **BM25 / sparse index:** Stores tokenized chunk text for exact-term retrieval.
- **Relational store (for evaluation logs and metadata):** Stores per-query traces — query text, retrieved chunk IDs, critique scores, routing decision, latency, timestamp. Also stores corpus metadata (document versions, ingestion timestamps).
- **Raw document storage:** The original source legal documents, kept as the ground truth for citation verification (the MCP citation-verification tool checks against this, not against the chunked/embedded representation, to avoid verifying a citation against a potentially lossy intermediate form).

---

## 11. Assumptions

1. Corpus is scoped to a single statute or small related set (e.g., Indian Contract Act, 1872, plus limited case law), not all of law — needs explicit confirmation before ingestion begins.
2. The self-critique step uses the same LLM family with a distinct prompt, not a separately trained classifier.
3. Query reformulation retries are capped at a small fixed number (e.g., 2) before falling to an explicit low-confidence response.
4. No user authentication/authorization is in initial scope; the system is treated as a single-tenant demo/portfolio deployment.
5. A second MCP tool (general web search fallback) is optional/deferrable and not required for the core system to function.
6. English-only queries and corpus in the initial scope; multilingual support is a future improvement.
7. Single-turn Q&A is in scope; multi-turn conversational memory is not, unless explicitly added later.
8. Deployment target is a single-instance Docker/AWS setup appropriate for a demo-scale system, not a horizontally scaled production service.

---

## 12. Future Improvements

**Near-term:**
- User-uploaded document ingestion (arbitrary legal documents, not just the fixed corpus).
- Confidence indicator surfaced visually in the frontend (not just internally logged).
- Expanded MCP tool set (e.g., a tool to fetch the full text of a cited case).

**Medium-term:**
- Multi-turn conversational memory with context carried across a session.
- Multi-jurisdiction corpus support with jurisdiction-aware retrieval filtering.
- Authentication/authorization layer if the system moves beyond single-tenant demo use.

**Long-term:**
- Multilingual query and corpus support (relevant given an Indian legal context).
- A generalized version of the self-evaluating retrieval framework applied to other high-precision domains (medical, financial) as a reusable pattern rather than a legal-specific system.
- Fine-tuned or distilled smaller critique model to reduce latency/cost of the self-critique step at scale.