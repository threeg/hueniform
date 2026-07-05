# Hueniform — Design System

| | |
|---|---|
| **Document** | Design system (colour, typography, spacing, components) |
| **Status** | Draft for approval (Milestone 16, v0.3.0) |
| **Date** | 5 July 2026 |
| **Repository location** | `docs/06-design-system.md` |
| **Source** | The design prototype `docs/designs/Hueniform App.html`; v0.3.0 brief (`docs/10-v0.3.0-brief.md`); v0.3.0 scoping decisions, 5 July 2026 |
| **Visual reference** | `docs/designs/Hueniform App.html` (binding where this document is silent; where the two disagree, **this document wins**) |

This document is the **binding** visual specification for v0.3.0. It extracts the design system from
the prototype so that colour, type, spacing and component decisions live in the spec rather than in a
one-off HTML file. Screens are built to compose this shared vocabulary; the wireframes
(`docs/04-wireframes/`, updated in Milestone 18) describe *where* the components go, this document
describes *how they look*.

Two conventions from the scoping decisions govern the tokens below:

- **Normalised, not verbatim.** The prototype is a design-tool export at a reduced scale (12.5 px base
  type, irregular radii such as 13 px / 5 px, spacing like 6 / 11 / 26 px). The tokens here keep the
  *look* but re-express the numeric scales on a clean 4 px spacing base, a rounded `rem` type scale and
  a small radius set. Colours and font families are taken as-is.
- **Offline by construction.** The prototype loads its fonts from Google Fonts. That is a runtime fetch
  and is **not permitted** (NFR-1, NFR-8). All three families are **self-hosted and bundled at build
  time** (§4). This re-affirms the offline contract; it does not change it.

---

## 1. Principles

The look is **warm editorial**: a cream paper ground, brown ink, generous quiet space, and a small
number of saturated accents used sparingly. It should read like a well-set printed catalogue, not a
dashboard.

- **Paper, not panels.** Surfaces are warm off-whites layered by lightness, separated by hairline tan
  borders and soft shadows rather than hard lines or heavy fills.
- **Ink, not black.** Text is a warm dark brown scale; pure black is never used.
- **Accent with restraint.** Clay/terracotta is the single primary accent (actions, active state).
  Teal, orange and green are secondary/semantic and appear in small doses.
- **Let the garments be the colour.** The UI chrome is deliberately muted so that garment colours and
  the colour-family swatches (the app's actual subject) carry the visual energy. Chrome tokens (§2) are
  distinct from the data-driven garment/family colours (§2.5).
- **Serif for voice, sans for work.** A display serif (Newsreader) carries the wordmark and headings;
  a grotesque sans (Hanken Grotesk) does the interface work; a monospace (Space Mono) is reserved for
  colour codes and numeric metadata.

---

## 2. Colour

Colours are the prototype's actual values. Tokens are named by **role**, not by hue, so components
reference intent (`--color-surface-raised`) rather than a literal (`#fbf4ea`). Realised as CSS custom
properties (§4).

### 2.1 Neutrals — paper (surfaces, light → structural)

| Token | Value | Use |
|---|---|---|
| `--color-ground` | `#eae0d0` | The app background (the "paper"). |
| `--color-surface` | `#f6ebdc` | Panels, grouped sections. |
| `--color-surface-raised` | `#fbf4ea` | Cards, the primary content surface. |
| `--color-surface-highest` | `#fffdf8` | Inputs, popovers, menus — the lightest surface. |
| `--color-border-subtle` | `#ecdcc7` | Hairline dividers within a surface. |
| `--color-border` | `#e4d5be` | Default border for cards, inputs, chips. |
| `--color-border-strong` | `#d8c3a6` | Emphasised or hovered borders. |

### 2.2 Neutrals — ink (text, dark → faint)

| Token | Value | Use |
|---|---|---|
| `--color-ink` | `#3a3128` | Primary text, headings. |
| `--color-ink-secondary` | `#5f5646` | Secondary text, labels. |
| `--color-ink-muted` | `#8a7c66` | Tertiary text, captions, icons. |
| `--color-ink-faint` | `#a89b86` | Placeholder and disabled text. |

### 2.3 Accents

| Token | Value | Use |
|---|---|---|
| `--color-primary` | `#c66a4a` | **Clay** — primary actions, active/selected state, links. The signature accent. |
| `--color-primary-strong` | `#c24b38` | Hover/pressed primary; emphasis. |
| `--color-primary-deep` | `#8a3a28` | Text/icon on light clay tints; deepest clay. |
| `--color-primary-soft` | `#e0a08c` | Soft clay for subtle fills/borders. |
| `--color-primary-tint` | `#f7e6de` | Lightest clay wash — selected-row/backing tint. |
| `--color-teal` | `#2cada0` | Secondary accent — highlights, informational. |
| `--color-orange` | `#ee8225` | Secondary accent — attention, warm callouts. |
| `--color-green` | `#4f7d54` | Secondary accent — positive/confirmation. |

### 2.4 Semantic roles

Semantics map onto the accents so the palette stays small:

| Role | Token maps to | Notes |
|---|---|---|
| Action / primary | `--color-primary` (clay) | Buttons, primary controls. |
| Success / confirm | `--color-green` | Detection confirmed, saved. |
| Warning / attention | `--color-orange` | Non-blocking cautions. |
| Danger / destructive | `--color-primary-strong` → `--color-primary-deep` | Delete, irreversible actions. |
| Info / highlight | `--color-teal` | Tips, neutral emphasis. |

### 2.5 Garment & colour-family swatches (data-driven — not chrome)

The colours a garment *is*, and the colour-family swatches in the taxonomy, are **content**, not part
of this token set. They are produced by the matcher's taxonomy (`docs/02-requirements.md` §2) and
rendered from detected values. This document governs only the **chrome around** those swatches (swatch
border, selected ring, label), never the swatch fill. Keep this boundary: chrome tokens must never be
hard-coded into swatch rendering, and detected colours must never be mapped onto chrome tokens.

### 2.6 Contrast

All chrome text/background pairings shall meet the contrast floor in **NFR-11** (WCAG 2.1 AA:
≥ 4.5:1 for body text, ≥ 3:1 for large text and UI-component boundaries). `--color-ink` /
`--color-ink-secondary` on the paper surfaces clear AA; `--color-ink-muted` and `--color-ink-faint`
are for large or non-essential text only and must be checked per use. Accent-on-paper and
text-on-accent pairings are verified during implementation (see §7).

---

## 3. Typography, spacing, radius, elevation

### 3.1 Font families (self-hosted)

| Token | Stack | Role |
|---|---|---|
| `--font-display` | `'Newsreader', Georgia, 'Times New Roman', serif` | Wordmark, page/section headings. |
| `--font-sans` | `'Hanken Grotesk', system-ui, -apple-system, sans-serif` | All interface text (default). |
| `--font-mono` | `'Space Mono', ui-monospace, 'SFMono-Regular', monospace` | Colour codes (hex/HSL), numeric metadata. |

Each family is bundled as `woff2` in the repo and referenced with `font-display: swap`; the fallback
in each stack is the graceful degradation if a face fails to load. No `fonts.googleapis.com` /
`fonts.gstatic.com` reference ships (NFR-1, NFR-8).

### 3.2 Type scale (normalised, `rem` at a 16 px root)

| Token | Size | Typical use |
|---|---|---|
| `--text-xs` | `0.75rem` (12 px) | Mono labels, meta, chip text. |
| `--text-sm` | `0.8125rem` (13 px) | Secondary/supporting text. |
| `--text-base` | `0.875rem` (14 px) | **Interface default** (compact UI). |
| `--text-md` | `1rem` (16 px) | Comfortable body, dialog copy. |
| `--text-lg` | `1.125rem` (18 px) | Sub-headings. |
| `--text-xl` | `1.375rem` (22 px) | Section headings. |
| `--text-2xl` | `1.625rem` (26 px) | Page title / display. |

Weights: `--weight-regular: 400`, `--weight-medium: 500`, `--weight-semibold: 600` (the interface
default — the prototype leans semibold), `--weight-bold: 700`. Line-heights: `--leading-tight: 1.2`
(display/headings), `--leading-normal: 1.5` (body). Display headings use `--font-display` at
`--weight-regular`–`500`; the wordmark is `--font-display` italic.

### 3.3 Spacing (4 px base)

`--space-1: 4px` · `--space-2: 8px` · `--space-3: 12px` · `--space-4: 16px` · `--space-5: 24px` ·
`--space-6: 32px` · `--space-7: 48px` · `--space-8: 64px`. Component padding and gaps use these steps
(the prototype's 6/11/26 px map to 8/12/24 px). A half-step `--space-0-5: 2px` exists for hairline
insets only.

### 3.4 Radius

`--radius-sm: 6px` (inputs, small controls) · `--radius-md: 12px` (chips, buttons, small cards) ·
`--radius-lg: 16px` (cards, panels, dialogs) · `--radius-pill: 999px` (tags, toggles, avatars,
colour-swatch chips).

### 3.5 Elevation

Warm, low-contrast shadows tinted with the ink colour, never neutral grey:

- `--shadow-sm: 0 1px 2px rgba(58, 49, 40, 0.06)` — chips, inputs on focus.
- `--shadow-md: 0 2px 8px rgba(58, 49, 40, 0.08)` — cards, popovers.
- `--shadow-lg: 0 8px 24px rgba(58, 49, 40, 0.12)` — dialogs, menus.

---

## 4. Realisation in the SPA

Consistent with the committed stack (React + Vite + TypeScript, **CSS Modules**; see
`docs/03-architecture.md`), the design system is realised as **CSS custom properties** defined once at
`:root` in a global tokens stylesheet, consumed by CSS Modules. No CSS framework is introduced —
responsiveness uses native CSS (flexbox, grid, `clamp()`, media/container queries); this keeps the
existing styling convention and avoids a runtime dependency. (Should a framework ever be considered, it
is an architecture decision recorded in `docs/03-architecture.md`, not a silent divergence — see the
v0.3.0 brief.)

Fonts are vendored into the frontend (e.g. `frontend/src/assets/fonts/…woff2`), declared with local
`@font-face` rules, and bundled by Vite at build time. Nothing is fetched from the network at runtime
(NFR-1, NFR-8) — re-verified in the implementation gate.

---

## 5. Component vocabulary

Shared components and their states, drawn from the prototype. Layout and per-screen composition are the
wireframes' job (Milestone 18); this fixes appearance and interaction states.

- **Buttons.** *Primary* — clay fill (`--color-primary`), paper text, `--radius-md`, `--weight-semibold`;
  hover → `--color-primary-strong`. *Secondary* — surface fill with `--color-border`, ink text.
  *Ghost/text* — no fill, ink-secondary text, clay on hover. *Destructive* — clay-strong. All expose a
  visible focus ring (§6) and a disabled state (ink-faint on surface).
- **Cards.** `--color-surface-raised`, `--radius-lg`, `--shadow-md`, `--space-5` padding; hairline
  `--color-border`. The garment tile is a card with an image well and a caption row (name + colour
  swatches).
- **Chips / tags.** `--radius-pill`, `--text-xs`, surface or tint fill; used for categories, slots,
  filters. Selected → `--color-primary-tint` fill with `--color-primary-deep` text.
- **Colour swatches.** Pill or rounded square with a `--color-border` ring; selected state adds a
  clay ring offset. The fill is a data-driven garment/family colour (§2.5); the hex/HSL label is
  `--font-mono` `--text-xs`.
- **Form controls.** Inputs/selects on `--color-surface-highest`, `--color-border`, `--radius-sm`,
  `--text-base`; focus → clay border + `--shadow-sm` + focus ring. Checkboxes/toggles use clay for the
  on state. Labels are `--color-ink-secondary` `--text-sm`.
- **App shell.** A header carrying the **Newsreader italic wordmark** and primary navigation
  (Inventory / Add / Suggest), on `--color-ground`; content in a centred, max-width column (§6).
- **Feedback states.** *Empty* — muted illustration/icon, ink-muted copy, a primary action. *Loading* —
  calm skeleton blocks in surface tones (no spinners where a skeleton fits). *Error* — clay-strong
  heading, plain-language message, a retry action.

---

## 6. Layout & responsiveness

Content sits in a centred column with a comfortable maximum width; the app shell frames it. Layout is
**fluid** and uses grid/flex with `clamp()` for gutters and column counts (e.g. the inventory grid
reflows its columns by available width).

Per **NFR-7**, the target is **current desktop browsers (Chrome, Firefox)** and **no mobile layout is
required**. Responsiveness here therefore means *fluid across the desktop range* (roughly 1024–1920 px,
degrading gracefully to ~900 px), **not** a phone layout. Suggested breakpoints: a `wide` step for very
large screens (more inventory columns) and a `compact` step where the shell navigation condenses.

> **Open item for Milestone 18 / the requirements check:** if mobile/tablet support is actually wanted,
> that contradicts NFR-7 ("no mobile layout required") and would be a **requirement change**, not a
> styling detail — raise and amend NFR-7 first. This document currently assumes desktop-only per the
> settled spec.

---

## 7. Accessibility (NFR-11)

v0.3.0 adds a **binding** accessibility floor (`docs/02-requirements.md`, **NFR-11**):

- **Contrast** — WCAG 2.1 AA: ≥ 4.5:1 for body text, ≥ 3:1 for large text (≥ 18.66 px regular / 14 px
  bold) and for UI-component/graphical boundaries. Token pairings in §2 are chosen to meet this;
  each accent-on-paper and text-on-accent pairing is verified at implementation.
- **Visible focus** — every interactive element has a clearly visible focus indicator (a clay focus
  ring); focus is never suppressed without an equivalent replacement.
- Colour is never the **sole** carrier of meaning (pair with text/icon), which matters especially given
  the colour-centric subject matter.

How this is tested is set in the test-strategy delta (Milestone 19) — expected to combine automated
contrast checks over the token pairings with focus-visibility assertions in component/e2e tests.

---

## 8. Requirement check (Milestone 16 conclusion)

The design pass surfaced **one** requirement delta and re-affirmed two existing NFRs; nothing else in
`docs/02-requirements.md` or `docs/03-api-contract.md` changes.

- **New — NFR-11 (accessibility).** WCAG 2.1 AA contrast + visible focus, as above. This revises the
  v0.3.0 brief's initial "no requirement deltas" finding (brief §3 updated accordingly).
- **Re-affirmed — NFR-1 / NFR-8 (offline).** The prototype's Google-Fonts dependency is removed by
  self-hosting; no new requirement, but an explicit re-verification target at implementation.
- **Re-affirmed — NFR-6 / NFR-7 (responsiveness, desktop scope).** The re-laid-out inventory must hold
  NFR-6 at 500 garments; NFR-7's desktop-only scope is retained (see §6's open item).

No `FR` changes: v0.3.0 alters presentation only, not behaviour or contracts.

---

## 9. Open items (for later v0.3.0 milestones)

1. **Which screens re-lay-out vs pure restyle** — settled while updating the wireframes (Milestone 18).
2. **Mobile/tablet** — desktop-only per NFR-7 unless the spec is changed first (§6).
3. **Visual-regression tooling** — whether to adopt a snapshot/visual-diff tool, and how NFR-11 is
   tested — decided in the test-strategy delta (Milestone 19).
4. **Exact self-hosted font weights/subsets** to vendor (keep the bundle small while covering the used
   weights: 400/500/600/700 sans, display, mono) — settled at implementation.
