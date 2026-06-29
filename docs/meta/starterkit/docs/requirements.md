# <PROJECT> — Requirements

| | |
|---|---|
| **Document** | Functional and non-functional requirements |
| **Repository location** | `docs/requirements.md` |
| **Status** | Binding specification |

> **Purpose.** This document turns the brief's goals into **numbered, testable rules**. It is the
> contract the implementation is held to and the source the test strategy traces against. Every
> functional requirement gets an `FR-n`; every non-functional one an `NFR-n`. Numeric thresholds
> stated here are **contractual** (§1.4) — code and tests must use the exact values, and changing one
> is a documented spec change, not a silent reinterpretation.
>
> Write requirements so a fresh agent session could implement and test them from this document
> alone. Prefer "the system MUST return at most N results, ordered by X" over "results should be
> reasonable".

---

## 1. Conventions

1. **Identifiers.** Functional requirements are `FR-n`; non-functional are `NFR-n`. Numbers are
   permanent once allocated — never reused or renumbered. New requirements take the next free
   number; superseded ones are amended in place and annotated (e.g. *“rewritten — vX.Y”*).
2. **Modal verbs.** MUST / MUST NOT are binding; SHOULD is a strong default that may be overridden
   with a recorded reason; MAY is optional.
3. **Traceability.** Every `FR`/`NFR` is realised by at least one ticket (its `implements` field)
   and covered by at least one test (test strategy §14).
4. **Numeric thresholds are contractual.** Any number in this document (limits, tolerances,
   timeouts, counts) is binding. Implementation references it as a named constant; tests assert it.
   Changing one means editing this document first.

---

## 2. <Core domain definitions / taxonomy>

> If the project depends on a precise vocabulary or classification (categories, states, families,
> tiers), define it here as tables with exact boundaries. This is the most common source of subtle
> bugs, so make the boundaries unambiguous (closed vs open intervals, tie-breaks, the catch-all
> case). Rename/extend this section to fit the domain; delete if not needed.

### 2.1 <Sub-table>

| <Name> | <Definition / exact boundary> |
|--------|-------------------------------|
| <…>    | <…>                           |

---

## 3. <Domain rules>

> The substantive rules of the domain — the logic the core layer implements. State each as a
> testable proposition. Group related rules under sub-headings. These are where test-first pays off
> most, so be exact: inputs, outputs, ordering, tie-breaking, and the boundary conditions.

---

## 4. Functional requirements by capability

> Group requirements under the capability they serve (mirroring the brief's goals). Each entry is a
> single MUST/SHOULD statement with an id. Example shape:

### 4.1 <Capability A>

- **FR-1** The system MUST <observable behaviour, with exact limits/ordering>.
- **FR-2** The system MUST <…>.
- **FR-3** When <condition>, the system SHOULD <…>; otherwise it MUST <…>.

### 4.2 <Capability B>

- **FR-4** <…>
- **FR-5** <…>

<!-- Continue grouping by capability. Keep statements atomic — one assertion per FR so a single
     test can target it and traceability stays clean. -->

---

## 5. <Behaviour / flow rules>

> Cross-cutting behavioural rules that span capabilities (e.g. how results are ranked, what the
> fallback ladder is when no result qualifies, how errors surface). State the precedence/order
> explicitly where one rule can override another.

- **FR-n** <…>

---

## 6. Non-functional requirements

> Performance, reliability, security, portability, accessibility, and any hard constraints from the
> brief (e.g. offline operation). Make them measurable: "responds in ≤ N ms at M records", not
> "fast". The architecture's dependency rule is often encoded as an NFR here so it can be cited by
> the ticket that enforces it.

- **NFR-1** <e.g. The application MUST make no network calls at runtime.>
- **NFR-2** <e.g. The application MUST start with a single command.>
- **NFR-3** <e.g. A request over <N> records MUST return within <T>.>
- **NFR-n** <e.g. The innermost layer MUST import only the standard library; enforced by tooling.>

---

## 7. Decisions log

> A dated record of decisions taken during requirement interviews — especially where a default was
> chosen among alternatives, or a threshold was set to a specific value. This is where future-you
> learns *why* FR-12 says 25 and not 50. Append, never rewrite.

- **<DATE>** — <decision, the options considered, and the rationale>.

<!-- For later versions, add a dated sub-section per version delta, e.g.:
### 7.1 vX.Y.0 decisions (Milestone NN, <DATE>)
- <decision> ...
-->
