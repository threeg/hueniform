---
id: HUE-095
title: Self-hosted fonts (offline)
type: task
status: done
milestone: 20
batch: design-system
layer: frontend
depends_on: [HUE-094]
implements: [NFR-1, NFR-8]
tests_required: true
estimate: 2
---

## In plain English
Ships the app's three fonts inside the app itself so it never has to download them from the internet — keeping it fully offline.

## Background
The prototype loads Hanken Grotesk, Newsreader and Space Mono from Google Fonts — a runtime fetch that breaks NFR-1/NFR-8. The fonts must be vendored and bundled at build time (design system §3.1, architecture §2.5).

## Technical requirements
- Vendor the three families (only the used weights/subsets — 400/500/600/700 sans, display, mono) as `woff2` into the frontend (e.g. `frontend/src/assets/fonts/`).
- Declare local `@font-face` rules with `font-display: swap`; wire the families to the `--font-*` tokens (HUE-094).
- Remove any `fonts.googleapis.com` / `fonts.gstatic.com` / `preconnect` references. Vite bundles the fonts.

## Definition of done (acceptance criteria)
- [ ] Three families vendored and declared with local `@font-face`; wired to the font tokens
- [ ] No web-font network reference remains
- [ ] An **offline-fonts asset test** asserts the built output contains no `fonts.g*` reference and `@font-face` sources resolve to bundled files (test strategy §10.3)
- [ ] Tests added/updated and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
- Asset/build test (§10.3) over the Vite build output; `cd frontend && npm run test -- fonts --run` (or the build-assertion target). Re-verifies NFR-1/NFR-8.

## Notes

- 2026-07-05 — done. Installed @fontsource packages to extract the woff2 files, then removed the packages (fonts are committed directly). Nine woff2 files vendored into `src/assets/fonts/` (Hanken Grotesk 400/500/600/700 normal; Newsreader 400/500 normal+italic; Space Mono 400 normal; ~163 KB total, all OFL-licensed). Added `src/fonts.css` with nine `@font-face` declarations (font-display: swap); imported in `main.tsx` before tokens.css. Added `src/test/fonts.test.ts` (10 tests, §10.3): asserts no CDN url() references, all three families declared, all woff2 files present on disk, Hanken Grotesk covers all four weights, Newsreader has italic, all font-display: swap. `make test` (1120+213, zero warnings). Sanity test: `cd frontend && npm run test -- fonts --run`.
