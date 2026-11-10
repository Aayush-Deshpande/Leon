---
id: "001"
title: "Document Template"
status: "Frozen"            # Draft until approved, then Frozen — see [000 §7]
freeze_class: "hard"       # per the roadmap entry [000 §3]
owner: "Engineering Documentation Lead"
version: "0.1"
inputs: ["000"]
outputs:
  - "005"
  - "010"
  - "020"
  - "100"
  - "110"
  - "120"
  - "130"
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
  - "900"
category: "Governance"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: []
---

# 001 — Document Template

> This document is governed by the Engineering Manual `[000]`. It owns the mandatory structure, the frontmatter schema, and the cross-reference citation format for every project document. It defines *how documents are shaped* — never *what the project builds* (that is project content) and never *how the process runs* (that is owned by `[000]`).

---

## Purpose

Define the single, mandatory structure that every knowledge-base document in Project Leon must follow, so that documents are uniform, machine-parseable, reviewable, and cheap to load into an AI assistant's context. See the philosophy this serves in `[000 §1.2]`, `[000 §1.10]`, and `[000 §1.11]`.

---

## Scope

This document covers:
- The **YAML frontmatter schema** (required and optional fields, allowed values).
- The **canonical section skeleton** every document must contain.
- The **cross-reference / citation format** used throughout the project.
- **Authoring guidance** for each section.

This document does **not** cover the meaning of lifecycle states, freeze classes, review criteria, gates, or any other process rule — those are owned by `[000]` and are only *referenced* here.

---

## Owned Concepts

This document is the Single Source of Truth for:
1. The document frontmatter schema (field names, types, allowed values).
2. The canonical section order and required sections of a document.
3. The citation/cross-reference syntax (defined in [§ Citation Format](#citation-format-owned-here)).
4. The Version History table format.

---

## Must Never Contain

Per `[000 §8.1.2]`, this document must never contain:
- Any project/domain content (product intent, architecture, APIs, prompts, data — owned by the 100–500 documents).
- Any process rules (lifecycle semantics, review process, gates, change management, freeze semantics — all owned by `[000]`). Where those are needed, this template **references** them.
- Definitions of terms (owned by `[010]`).

---

## Dependencies (Inputs)

| Doc | Why depended upon |
|-----|-------------------|
| `[000]` | Defines the frontmatter field requirements, lifecycle states, freeze classes, review criteria, and ownership discipline that this template operationalizes. |

*(Mirror this list in the `inputs` frontmatter field as doc IDs.)*

---

## Downstream Consumers (Outputs)

Every authored knowledge-base document (`005`, `010`, `020`, `100`–`130`, `200`–`240`, `300`–`340`, `400`/`41x`, `500`, `610`/`620`/`690`, `900`) copies this template. Generated artifacts (`005`, `020`) carry the frontmatter block but are produced mechanically — see `[000 §3]`.

*(Mirror this list in the `outputs` frontmatter field as doc IDs.)*

---

## Assumptions

None. This template introduces no assumptions. Any document that does must label, number, and register each one in `[120]` per `[000 §1.7]`, and list them in its own **Assumptions** section as references to the `[120]` entry (never as a second copy).

---

## References

- `[000]` — Engineering Manual (governing document).
- `[000 §3]` — Roadmap entry that specifies this document's required frontmatter fields.
- `[000 §7]` — Document lifecycle and freeze classes.
- `[000 §8]` — Review process and checklists.

---

## Open Questions

None. *(A document may not enter **Frozen** with blocking open questions — see `[000 §7]`. Non-blocking questions must be explicitly marked as such.)*

---

## Review Checklist

Confirm each item before requesting approval. Items reference the authoritative criteria in `[000 §8]` rather than restating them.

- [ ] Single Responsibility — `[000 §8.1.1]`
- [ ] Ownership integrity: Owned Concepts + Must Never Contain honored — `[000 §8.1.2]`
- [ ] No duplication; all borrowed facts are citations — `[000 §8.1.3]`
- [ ] Dependency validity: `inputs`/`outputs` accurate and Approved — `[000 §8.1.4]`, `[000 §8.5]`
- [ ] Template conformance: this skeleton + citation format followed — `[000 §8.1.5]`
- [ ] Vocabulary conformance: specialized terms defined in `[010]` — `[000 §8.1.6]`
- [ ] Explicit assumptions registered in `[120]` — `[000 §8.1.7]`
- [ ] Determinism: tables/schemas used where applicable — `[000 §8.1.8]`
- [ ] Traceability preserved — `[000 §8.1.9]`
- [ ] Category-specific checklist applied, if any — `[000 §8.3]`
- [ ] Frontmatter complete and valid; `status` reflects reality — `[000 §7]`

---

## Freeze Class

`hard`. Allowed values and their meaning are owned by `[000 §1.6]` and `[000 §7]`; each document's class is fixed by its roadmap entry in `[000 §3]`. Set the `freeze_class` frontmatter field accordingly: `hard` | `soft` | `living` | `generated` | `none`.

---

## Status

`Frozen` (approved and frozen). The authoritative status lives in the `status` frontmatter field, not in prose — see `[000 §7]`.

---

## Version History

| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | (pending) | Engineering Documentation Lead | Initial draft of the document template. | — |

---

# The Template (copy this for every new document)

Everything below this line is the **mandatory, reusable structure**. To create any new project document: copy the frontmatter block and the section skeleton, then fill them in following the authoring guidance. Do not remove required sections. Specialized document types may **add** sections (e.g., phase plans add *Context Package* and *Progress / Resume State* per `[000 §3]` and `[000 §5.2]`) but may never drop the required ones.

---

## Frontmatter Schema (owned here)

Every document — including generated artifacts — MUST begin with a YAML frontmatter block. The following fields are the schema. Required fields are mandated by `[000 §3]`.

| Field | Required | Type | Allowed values / format | Notes |
|-------|----------|------|-------------------------|-------|
| `id` | ✅ | string | Document number as string, e.g., `"210"`; phase plans use their concrete number, e.g., `"410"` | Matches the roadmap in `[000 §3]`. |
| `title` | ✅ | string | Free text | Human-readable name, no ID prefix. |
| `status` | ✅ | enum | `Draft` \| `Review` \| `Approved` \| `Frozen` \| `Deprecated` | Authoritative here, not in prose. Semantics: `[000 §7]`. |
| `freeze_class` | ✅ | enum | `hard` \| `soft` \| `living` \| `generated` \| `none` | Fixed by roadmap entry `[000 §3]`. Semantics: `[000 §1.6]`, `[000 §7]`. |
| `owner` | ✅ | string | Role or team | The accountable owner. |
| `version` | ✅ | string | `MAJOR.MINOR`, e.g., `"1.0"` | Bump MINOR for non-breaking edits, MAJOR for contract-changing edits. Matches the style used by `[000]`. |
| `inputs` | ✅ | list of strings | Doc IDs, e.g., `["200","110"]` | Documents this one depends on. Must be Approved/Frozen before this enters Review — `[000 §7]`. |
| `outputs` | ✅ | list of strings | Doc IDs | Downstream consumers. Keep in sync with the **Downstream Consumers** section. |
| `category` | ⬚ optional | string | `Governance` \| `Core Knowledge` \| `Architecture` \| `Engineering Standards` \| `Implementation` \| `Operations` \| `Audits & Reviews` | Mirrors the hierarchy in `[000 §2]`. |
| `reviewers` | ⬚ optional | list of strings | Names/roles | Populated at sign-off — `[000 §8.2]`. |
| `last_reviewed` | ⬚ optional | date | `YYYY-MM-DD` or `null` | Date of last approval/review. |
| `supersedes` | ⬚ optional | string | Doc ID or `null` | For replacements. |
| `superseded_by` | ⬚ optional | string | Doc ID or `null` | Set when `Deprecated` — `[000 §7]`. |
| `decision_refs` | ⬚ optional | list of strings | `900` entry IDs | Decisions that shaped this document — `[000 §1.12]`. |

Documents whose `freeze_class` is `generated` (`005`, `020`) carry this frontmatter but are produced mechanically and never hand-edited — `[000 §10.7]` Rule 21.

---

## Section Skeleton (required order)

Every document contains these sections, in this order:

1. **Title** (`# <id> — <title>`) and a one-line governing note.
2. **Purpose** — one paragraph: what this document is for.
3. **Scope** — what it covers and, explicitly, what it does not.
4. **Owned Concepts** — the facts this document is SSoT for.
5. **Must Never Contain** — content that belongs to other owners (with pointers).
6. **Dependencies (Inputs)** — table of upstream docs + why.
7. **Downstream Consumers (Outputs)** — who depends on this.
8. **Assumptions** — labeled, each referencing its `[120]` entry.
9. **References** — cited documents and external sources.
10. **Open Questions** — unresolved items (must be non-blocking before Frozen).
11. **Review Checklist** — the `[000 §8]` criteria as confirmable items.
12. **Freeze Class** — the value and a pointer to `[000]`.
13. **Status** — current lifecycle state (authoritative in frontmatter).
14. **Version History** — the change table.

Body content specific to the document's responsibility goes **between Scope and Owned Concepts is not permitted**; instead place domain content in clearly-headed sections after **Owned Concepts** and before **Assumptions**, or in document-type-specific sections. Keep the fixed sections above present regardless.

---

## Citation Format (owned here)

Use these forms consistently; they are the project's only reference syntax.

| Target | Syntax | Example |
|--------|--------|---------|
| A document | `[<id>]` | `[240]` |
| A document section | `[<id> §<section>]` | `[200 §3.2]` |
| The seed spec | `` `leon.md` §<section> `` | `leon.md §5.5` |
| A glossary term | bold on first use; defined in `[010]` | **groundedness** (`[010]`) |
| A decision record | `[900#<decision-id>]` | `[900#D-014]` |
| An assumption | `[120#<assumption-id>]` | `[120#A-3]` |

Rules:
- **Reference, never restate.** To use another document's owned concept, cite it — do not paraphrase it (`[000 §1.3]`, `[000 §6]`).
- Every citation must resolve to a real document/section (`[000 §8.4]`).
- First use of a specialized term links to `[010]`; do not redefine it locally.

---

## Copy-Paste Block

```markdown
---
id: "<NNN>"
title: "<Human Readable Title>"
status: "Draft"
freeze_class: "<hard|soft|living|generated|none>"
owner: "<role or team>"
version: "0.1"
inputs: ["<id>", "<id>"]
outputs: ["<id>", "<id>"]
category: "<Governance|Core Knowledge|Architecture|Engineering Standards|Implementation|Operations|Audits & Reviews>"
reviewers: []
last_reviewed: null
supersedes: null
superseded_by: null
decision_refs: []
---

# <NNN> — <Human Readable Title>

> One-line note: what this document governs and its relationship to its owner(s).

## Purpose
<One paragraph. What this document is for.>

## Scope
<What it covers. Then an explicit line: "This document does not cover … (owned by [<id>]).">

## Owned Concepts
<Numbered list of the facts this document is the single source of truth for.>

## Must Never Contain
<Bulleted list of content that belongs to other owners, each with a pointer, e.g., "Storage schema — owned by [230]".>

## Dependencies (Inputs)
| Doc | Why depended upon |
|-----|-------------------|
| [<id>] | <reason> |

## Downstream Consumers (Outputs)
<List of documents/activities that consume this one. Keep in sync with `outputs`.>

## Assumptions
<Each assumption as: "A-x: <statement> — registered as [120#A-x]." If none, write "None.">

## References
<Cited documents and external sources, using the citation format.>

## Open Questions
<Unresolved items. Mark each blocking / non-blocking. Must be non-blocking before Frozen. If none, "None.">

## Review Checklist
- [ ] Single Responsibility — [000 §8.1.1]
- [ ] Ownership integrity — [000 §8.1.2]
- [ ] No duplication — [000 §8.1.3]
- [ ] Dependency validity — [000 §8.1.4], [000 §8.5]
- [ ] Template conformance — [000 §8.1.5]
- [ ] Vocabulary conformance — [000 §8.1.6]
- [ ] Explicit assumptions in [120] — [000 §8.1.7]
- [ ] Determinism — [000 §8.1.8]
- [ ] Traceability — [000 §8.1.9]
- [ ] Category-specific checklist — [000 §8.3]
- [ ] Frontmatter complete and valid — [000 §7]

## Freeze Class
<value> — semantics owned by [000 §1.6] / [000 §7]; fixed by [000 §3].

## Status
<state> — authoritative in the `status` frontmatter field. Semantics: [000 §7].

## Version History
| Version | Date | Author | Change summary | Decision |
|---------|------|--------|----------------|----------|
| 0.1 | <YYYY-MM-DD> | <author> | Initial draft. | — |
```

---

## Authoring Guidance (per section)

- **Purpose** — one paragraph, no lists. If you need two paragraphs, the document may be doing two jobs (`[000 §1.2]`).
- **Scope** — always include the negative boundary ("does not cover … owned by `[<id>]`"). This is the first line of defense against duplication.
- **Owned Concepts** — if a concept here is already owned elsewhere, remove it and cite the owner instead. Two owners is a blocking defect (`[000 §6]`).
- **Must Never Contain** — list the *neighboring* concepts most likely to leak in, each with the correct owner. This makes review mechanical.
- **Dependencies / Consumers** — must exactly match the `inputs` / `outputs` frontmatter. Mismatch is a blocking finding (`[000 §8.5]`).
- **Assumptions** — never state an assumption only here; it must live in `[120]`. This section holds references, so gates can find and resolve them (`[000 §1.7]`).
- **Open Questions** — a document with blocking open questions cannot be Frozen. Resolve or downgrade them first (`[000 §7]`).
- **Version History** — add a row for every change; link the `[900]` decision when one exists (`[000 §1.12]`). Bump `version` in frontmatter to match.
- **Generated artifacts** (`005`, `020`) — do not hand-write body content; the generator populates it from sources. Only the schema and section headers are prescribed here.

---

*End of Document Template. Every project document must conform to this structure. Structural changes require an amendment recorded per `[000 §15]`.*
