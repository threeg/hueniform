/**
 * Design-token contrast test — test strategy §10.3, design system §2.6.
 *
 * Parses src/tokens.css and asserts that documented ink/paper and
 * text-on-accent pairings meet WCAG 2.1 AA:
 *   - ≥ 4.5:1 for body text (normal text, < 18.66 px regular / 14 px bold)
 *   - ≥ 3.0:1 for large text and UI-component boundaries
 *
 * This file is the single source of truth for token-level contrast; a token
 * value change that breaks a ratio fails here before any component test.
 *
 * Notes on omitted pairings:
 *   --color-ink-faint (#a89b86) is for disabled/placeholder text which is
 *   explicitly exempt from WCAG 1.4.3 contrast requirements.
 *
 *   --color-surface-highest on --color-primary (#c66a4a) gives ≈ 3.78:1,
 *   which clears the UI-component boundary threshold (≥ 3:1 per WCAG 1.4.11)
 *   but not the body-text threshold (≥ 4.5:1). Primary button labels must
 *   therefore use --text-lg / --text-xl or heavier weight to qualify as
 *   large text, OR use --color-primary-deep as the text colour instead.
 *   That constraint is enforced in the button component (HUE-096), not here.
 */

import { readFileSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'

const __dirname = dirname(fileURLToPath(import.meta.url))
const tokensRaw = readFileSync(join(__dirname, '..', 'tokens.css'), 'utf8')

// ── WCAG contrast utilities ──────────────────────────────────────────────────

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '')
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ]
}

function toLinear(c8: number): number {
  const c = c8 / 255
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4
}

function relativeLuminance(hex: string): number {
  const [r, g, b] = hexToRgb(hex)
  return 0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b)
}

function contrastRatio(fg: string, bg: string): number {
  const l1 = relativeLuminance(fg)
  const l2 = relativeLuminance(bg)
  const [light, dark] = l1 > l2 ? [l1, l2] : [l2, l1]
  return (light + 0.05) / (dark + 0.05)
}

// ── Parse token values from the CSS source ───────────────────────────────────

function parseTokens(css: string): Map<string, string> {
  const map = new Map<string, string>()
  for (const match of css.matchAll(/--([a-z0-9-]+):\s*(#[0-9a-fA-F]{6})/g)) {
    map.set(`--${match[1]}`, match[2])
  }
  return map
}

const tokens = parseTokens(tokensRaw)

function token(name: string): string {
  const val = tokens.get(name)
  if (!val) throw new Error(`Token ${name} not found in tokens.css`)
  return val
}

// ── Contrast assertions ──────────────────────────────────────────────────────

describe('design-token contrast (WCAG 2.1 AA)', () => {
  const BODY_AA   = 4.5  // normal text
  const LARGE_AA  = 3.0  // large text / UI-component boundaries

  const paperSurfaces = [
    '--color-ground',
    '--color-surface',
    '--color-surface-raised',
    '--color-surface-highest',
  ] as const

  describe('--color-ink on paper surfaces (body text ≥ 4.5:1)', () => {
    for (const surface of paperSurfaces) {
      it(`${surface}`, () => {
        const ratio = contrastRatio(token('--color-ink'), token(surface))
        expect(ratio).toBeGreaterThanOrEqual(BODY_AA)
      })
    }
  })

  describe('--color-ink-secondary on paper surfaces (body text ≥ 4.5:1)', () => {
    for (const surface of paperSurfaces) {
      it(`${surface}`, () => {
        const ratio = contrastRatio(token('--color-ink-secondary'), token(surface))
        expect(ratio).toBeGreaterThanOrEqual(BODY_AA)
      })
    }
  })

  describe('--color-ink-muted on surfaces (large / non-essential text ≥ 3:1)', () => {
    const largeSurfaces = ['--color-surface', '--color-surface-raised', '--color-surface-highest'] as const
    for (const surface of largeSurfaces) {
      it(`${surface}`, () => {
        const ratio = contrastRatio(token('--color-ink-muted'), token(surface))
        expect(ratio).toBeGreaterThanOrEqual(LARGE_AA)
      })
    }
  })

  describe('accent pairings', () => {
    it('--color-primary-deep on --color-primary-tint (chip/selected text ≥ 4.5:1)', () => {
      const ratio = contrastRatio(token('--color-primary-deep'), token('--color-primary-tint'))
      expect(ratio).toBeGreaterThanOrEqual(BODY_AA)
    })

    it('--color-primary-deep on --color-surface-raised (text-on-light ≥ 4.5:1)', () => {
      const ratio = contrastRatio(token('--color-primary-deep'), token('--color-surface-raised'))
      expect(ratio).toBeGreaterThanOrEqual(BODY_AA)
    })

    it('--color-surface-highest on --color-primary (button/UI boundary ≥ 3:1)', () => {
      // Primary button label text clears the UI-component boundary threshold.
      // Full body-text AA (4.5:1) requires large/bold label text — see module docstring.
      const ratio = contrastRatio(token('--color-surface-highest'), token('--color-primary'))
      expect(ratio).toBeGreaterThanOrEqual(LARGE_AA)
    })

    it('--color-ink on --color-primary-tint (ink text on tint backing ≥ 4.5:1)', () => {
      const ratio = contrastRatio(token('--color-ink'), token('--color-primary-tint'))
      expect(ratio).toBeGreaterThanOrEqual(BODY_AA)
    })
  })
})
