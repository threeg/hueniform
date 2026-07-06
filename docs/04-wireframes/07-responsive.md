# Hueniform — Wireframes: Responsive Layouts (mobile / tablet / desktop)

| | |
|---|---|
| **Document** | Responsive layout specification (Milestone 18, v0.3.0) |
| **Status** | Draft for approval |
| **Date** | 5 July 2026 |
| **Source** | The design prototype `docs/designs/Hueniform App.html` (its `MOBILE` and `TABLET` sections); the per-screen wireframes (`01`–`06`); design system (`docs/06-design-system.md` §6); NFR-7 (amended, v0.3.0) |
| **Repository location** | `docs/04-wireframes/07-responsive.md` |

This document specifies how the existing screens **reflow by viewport**. It complements — does not
replace — the per-screen wireframes (`01`–`06`), which remain the source of record for each screen's
content, states and contract-bound fields. Nothing here changes behaviour, data or the API contract:
the same routes and components render at every tier (NFR-7, amended v0.3.0; architecture §2.5). As with
the other wireframes, this is **low-to-mid fidelity** — visual styling (colour, type, spacing) is the
design system's job (`docs/06-design-system.md`); only structure and reflow are specified here.

---

## 1. Tiers and breakpoints

Breakpoints are **guides** — layout is fluid between them and components reflow rather than snapping.

| Tier | Width (guide) | Reference device | Primary navigation | Main grid |
|---|---|---|---|---|
| **Mobile** | `< 640px` | phone (~360–430 px) | **Bottom tab bar** | 2 columns |
| **Tablet** | `640–1023px` | tablet portrait (~834 px) | condensed sidebar → top bar | 3–4 columns (up to 6 for compact swatch rows) |
| **Desktop** | `≥ 1024px` | laptop/desktop (≥ 1024 px) | fixed left **sidebar** | reflows by width (existing) |

Minimum touch target on mobile/tablet is **44 × 44 px**. The desktop layout is exactly the one in the
`01`–`06` wireframes and `00-overview.md` §3; only mobile and tablet are new.

---

## 2. Navigation by tier

**Desktop** — the fixed left sidebar (wordmark + Wardrobe / Add garment / Suggest outfit), unchanged
(`00-overview.md` §2, §3).

**Tablet** — the sidebar condenses (icons + short labels) or moves to a top bar to reclaim width; the
three destinations and all routing rules are identical.

**Mobile** — the sidebar is replaced by a **fixed bottom tab bar** with the three destinations; the
wordmark moves to a slim top bar. Routing, deep-links and the "Build around this" flow (overview §2)
are unchanged — only the navigation *chrome* differs.

```
 Mobile ( <640px )                 Tablet ( 640–1023px )            Desktop ( ≥1024px )
┌───────────────────┐            ┌──┬───────────────────────┐     ┌────────┬──────────────────────┐
│ ˹Hueniform˺  title│            │≡ │ Page title            │     │Hueniform│ Page title          │
│                   │            │Wa│                       │     │        │                      │
│  page content     │            │Ad│  page content         │     │Wardrobe│  page content        │
│  (single column)  │            │Su│  (3–4 col grids)       │     │Add     │                      │
│                   │            │  │                       │     │Suggest │                      │
├───────────────────┤            └──┴───────────────────────┘     └────────┴──────────────────────┘
│ Wardrobe Add Suggest│  ← bottom tab bar
└───────────────────┘
```

---

## 3. Global reflow rules

1. **Stacking.** Multi-column desktop panels stack to a single column on mobile, top-to-bottom in
   reading order; on tablet, side-by-side pairs may remain if width allows, otherwise stack.
2. **Grids.** The garment grid is **2 columns** on mobile, **3–4** on tablet, and width-driven on
   desktop. Dense swatch/colour rows may use up to **6** columns on tablet.
3. **Sticky actions.** Primary actions that sit in a sidebar/side panel on desktop (e.g. Generate,
   Save) become a **full-width button**, sticky to the bottom above the tab bar, on mobile.
4. **Horizontal scroll for chip rows.** Region/slot chip rows and filter pills scroll horizontally on
   mobile rather than wrapping into tall blocks.
5. **Images.** Garment thumbnails keep their aspect ratio and scale to the column width.
6. **States unchanged.** Every state in the per-screen wireframes (empty / loading / error / variants)
   exists at every tier; only its arrangement reflows. The state-coverage matrix (`00-overview.md` §5)
   is orthogonal to tier.

---

## 4. Per-screen reflow

Grounded in the prototype's `MOBILE` and `TABLET` sections. Desktop is per the numbered wireframes.

### Screen 1 — Upload & detect
Mobile/tablet: the drop zone becomes a full-width tap target ("Choose photo" / camera on mobile);
detecting and rejection states stack full-width. Single column throughout.

### Screen 2 — Confirm-and-correct
Desktop's two panes (image preview | proportion editor) **stack** on mobile: preview on top, editor
below, the colour rows full-width with the numeric steppers and live total beneath; the region-grouped
category picker becomes a horizontally scrollable / wrapped chip set. Save is a sticky full-width
action on mobile. On tablet the two panes may sit side-by-side if width allows, else stack.

### Screen 3 — Inventory (Wardrobe)
The grouped-by-category grid is **2 columns** on mobile, **3–4** on tablet, width-driven on desktop.
Per-category group headers + counts persist; the Hue / Date order toggle and filters move into a
compact bar (filters may collapse behind a "Filters" control on mobile). Empty / loading / load-failure
states as per screen 3, full-width.

### Screen 4 — Garment detail
Single column on mobile: enlarged image, then palette strip, then category (with the inline edit →
`PATCH`), then Regenerate / Delete actions. Delete-confirmation and regenerate-pending states as per
screen 4. Tablet keeps image + details side-by-side where width allows.

### Screen 5 — Outfit request
The slot selector's four regions (Head / Upper body / Lower body / Feet) **stack** on mobile, each a
full-width group; category-constraint checklists and the colour/scheme anchor collapse into
expandable sections; the count stepper and Generate are a sticky full-width footer above the tab bar.
Tablet shows two regions per row where width allows.

### Screen 6 — Suggestion results
Results are already stacked full-width cards, so they carry across tiers directly; on mobile each
outfit card's slot items reflow to a 2-column mini-grid. The count header, first-class-neutral and
neutral-fallback labels, and zero-results hint are unchanged. On the combined request/results page,
the request panel collapses above the results on mobile (a "Refine" affordance re-opens it).

---

## 5. Decisions log (Milestone 18, 5 July 2026)

| Decision | Outcome |
|---|---|
| Responsive scope | App is responsive across **mobile / tablet / desktop** (NFR-7 amended); the prototype's mobile + tablet layouts are in scope for v0.3.0. |
| Mobile navigation | The left sidebar is replaced by a **bottom tab bar** (Wardrobe / Add / Suggest); wordmark to a slim top bar. |
| Tablet navigation | Condensed sidebar or top bar; same three destinations. |
| Grids | Garment grid 2 (mobile) / 3–4 (tablet) / width-driven (desktop); dense swatch rows up to 6 on tablet. |
| Primary actions on mobile | Sticky full-width footer button above the tab bar (Generate, Save). |
| Behaviour/contract | Unchanged — responsive is a viewport-only reflow of the same screens (no new routes, data or `FR`). |

---

*This document is a v0.3.0 addition to the wireframe set. Its approval is part of Milestone 18
sign-off; it realises the amended NFR-7 and is referenced by `docs/06-design-system.md` §6 and
`docs/03-architecture.md` §2.5.*
