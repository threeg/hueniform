# <PROJECT> — System Architecture

| | |
|---|---|
| **Document** | System architecture |
| **Repository location** | `process/architecture/architecture.md` |
| **Status** | Binding specification |

> **Purpose.** This document fixes the module layout, the **dependency rule**, the data model, and
> the key flows. Where code and this document disagree on structure, this document wins (where code
> and the *interface contract* disagree on shapes, the contract wins — see `api-contract.md`).
> The dependency rule defined here is enforced by tooling in the scaffolding step.
>
> **Supporting context.** Drop reference material for this milestone — integration specs, vendor API
> docs, diagrams — into `process/architecture/` beside this file. It informs the design but is *not*
> binding; only this master file and `api-contract.md` are.

---

## 1. Architectural overview

> A short prose description plus, ideally, one diagram. Cover: the overall shape (monolith / client
> + server / pipeline), the process topology (how many processes, what serves what), and the
> single most important structural decision and why it was made.

---

## 2. Component breakdown

### 2.1 Module layout and the dependency rule

> List the layers from innermost to outermost and state, for each, **what it may import**. The
> innermost layer should depend on nothing but the language runtime / standard library. Then state
> the rule as a single line and note that it is enforced.

Proposed layering (rename layers to fit the project):

```
core → domain → services → interface,   with  storage  beneath  services
```

| Layer | May import | Notes |
|-------|-----------|-------|
| `core` | standard library only | Pure logic. No I/O, no framework, no mutable global state. |
| `domain` | `core` | <…> |
| `storage` | (nothing in the app graph) | Persistence only; imports no business layer. |
| `services` | `core`, `domain`, `storage` | Orchestration. |
| `interface` | `services` and its own schemas | The HTTP/CLI/UI edge. **Nothing imports `interface`.** |

> **The dependency rule (enforced, not aspirational).** `<state the one-line rule>`. This is checked
> by `<import-linter contract / module-boundary tool / dependency cruiser>` and a
> standard-library-only allowlist test for the core; a violation **fails the build**. The ticket
> `depends_on` graph must respect the same ordering (see `process/tickets/CONVENTIONS.md`).

### 2.2 The core (pure module)

> Describe the innermost layer in more detail: it is pure, deterministic, framework-free, and (by
> convention) held to the highest coverage gate. Note any constraints (e.g. immutable inputs and
> outputs, constants centralised in one module).

### 2.3 <Pipeline / processing layer>

> If there is a processing pipeline (parsing, detection, transformation), describe its stages and
> the seams where tests inject fakes. Delete if not applicable.

### 2.4 Services and interface layer

> How orchestration is structured, how the interface layer maps requests to services, and where
> validation lives.

### 2.5 <Frontend / client>

> If there is a UI/client, summarise its structure (routing, state management, data fetching) and
> how it talks to the interface layer. Delete for non-UI projects.

---

## 3. Data model

### 3.1 Entities

> Each persistent entity: its fields, types, constraints, and relationships. Note which fields are
> user-editable vs derived/regenerate-only. Keep this in step with the storage schema — drift here
> causes the worst bugs.

| Entity | Field | Type | Notes |
|--------|-------|------|-------|
| `<Entity>` | `<field>` | `<type>` | <constraints, default, editability> |

### 3.2 Disk / storage layout

> Where data physically lives (tables, files, directories) and why. Relevant to portability and
> offline NFRs.

### 3.3 <Transient / staging state>

> Any intermediate state not yet committed to the main store (uploads pending confirmation, draft
> records). Delete if not applicable.

---

## 4. Key flows

> For each important end-to-end flow, give a numbered step list naming the layers and the FR/NFR
> ids it realises. These are the backbone the tickets and integration tests are organised around.

### 4.1 <Flow A — e.g. create → process → confirm → save>  (FR-n…FR-m)

1. <step, naming the layer responsible>
2. <…>

### 4.2 <Flow B>  (FR-…)

1. <…>

---

## 5. Startup and runtime topology

> What runs when the app starts, in what order; how the single run command (NFR) is satisfied; what
> serves the interface and any static assets.

---

## 6. Technology choices

> The binding stack decisions and the rationale for each. This is where the brief's directional
> "technical direction" becomes contractual. Note pinned major versions and any deliberately
> excluded technologies.
