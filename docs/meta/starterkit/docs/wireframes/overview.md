# <PROJECT> — Wireframes: Overview, Navigation and Conventions

| | |
|---|---|
| **Document** | Wireframes overview |
| **Repository location** | `docs/wireframes/00-overview.md` |
| **Status** | Binding specification (for UI) |

> **Purpose.** For projects with a user interface, this folder is the binding description of the
> screens, their states, and the navigation between them. The overview (this file) indexes the
> screens and fixes shared conventions; one file per screen (`01-<screen>.md`, `02-<screen>.md`, …)
> describes each in detail, optionally alongside an HTML mockup of the same name.
>
> **Non-UI projects:** skip this milestone entirely and remove `docs/wireframes/`.

---

## 1. Screen index

| # | Screen | File | Purpose |
|---|--------|------|---------|
| 1 | <Screen A> | `01-<slug>.md` | <one line> |
| 2 | <Screen B> | `02-<slug>.md` | <one line> |

---

## 2. Navigation structure

> How the user moves between screens — the routes, the entry point, the back/cancel behaviour. A
> small diagram or indented tree works well.

```
<entry> ─▶ <Screen A> ─▶ <Screen B>
                └▶ <Screen C>
```

---

## 3. Shared layout

> The frame every screen sits in: header, navigation, primary actions, where errors and loading
> appear. Define shared components once here so each screen file can reference them.

### Shared components

- <Component — e.g. banner, card, toolbar> — <where used, what it does>

### <Shared vocabulary / labels>

> Any domain labels that must read identically across screens (category names, status words). List
> them once so wording stays consistent.

---

## 4. Mockup conventions

> The fidelity and notation used: grey-box vs styled, how interactive vs static elements are shown,
> how annotations are written. State whether a visual-design pass is expected or deferred (e.g.
> "styling to emerge in implementation against these wireframes").

---

## 5. State coverage matrix

> Every screen, every state. A screen is not specified until its empty / loading / populated /
> error states are all described. This matrix is the checklist.

| Screen | Empty | Loading | Populated | Error |
|--------|:-----:|:-------:|:---------:|:-----:|
| <Screen A> | ☐ | ☐ | ☐ | ☐ |
| <Screen B> | ☐ | ☐ | ☐ | ☐ |

---

## 6. Decisions log

> Dated record of UI decisions from the wireframe interview — layout choices, what was deliberately
> left out, ordering/grouping decisions. Append per version.

- **<DATE>** — <decision and rationale>.
