/**
 * Offline-fonts asset test — test strategy §10.3, NFR-1, NFR-8.
 *
 * Parses src/fonts.css to assert:
 *   1. No fonts.googleapis.com / fonts.gstatic.com reference exists.
 *   2. @font-face blocks are declared for all three required families.
 *   3. Every @font-face src: url(…) is a relative local path, not a
 *      network URL — re-verifying that no runtime web-font fetch is needed.
 *   4. Each referenced woff2 file physically exists in src/assets/fonts/.
 *
 * This test catches a re-introduction of CDN references or a missing font
 * file without requiring a full Vite build.
 */

import { readFileSync, existsSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, it, expect } from 'vitest'

const __dirname = dirname(fileURLToPath(import.meta.url))
const srcDir    = join(__dirname, '..')
const fontsDir  = join(srcDir, 'assets', 'fonts')
const fontsCss  = readFileSync(join(srcDir, 'fonts.css'), 'utf8')

describe('offline-fonts (NFR-1, NFR-8)', () => {
  it('contains no url() pointing to fonts.googleapis.com', () => {
    expect(fontsCss).not.toMatch(/url\(['"]?https?:\/\/fonts\.googleapis\.com/)
  })

  it('contains no url() pointing to fonts.gstatic.com', () => {
    expect(fontsCss).not.toMatch(/url\(['"]?https?:\/\/fonts\.gstatic\.com/)
  })

  it('declares @font-face for Hanken Grotesk', () => {
    expect(fontsCss).toContain("font-family: 'Hanken Grotesk'")
  })

  it('declares @font-face for Newsreader', () => {
    expect(fontsCss).toContain("font-family: 'Newsreader'")
  })

  it('declares @font-face for Space Mono', () => {
    expect(fontsCss).toContain("font-family: 'Space Mono'")
  })

  it('all @font-face src: url() values are local relative paths (no http/https)', () => {
    const urlPattern = /src:\s*url\((['"]?)(.+?)\1\)/g
    const urls: string[] = []
    for (const m of fontsCss.matchAll(urlPattern)) {
      urls.push(m[2])
    }
    expect(urls.length).toBeGreaterThan(0)
    for (const u of urls) {
      expect(u).not.toMatch(/^https?:\/\//)
    }
  })

  it('all referenced woff2 files exist on disk', () => {
    const urlPattern = /src:\s*url\((['"]?)(.+?)\1\)/g
    for (const m of fontsCss.matchAll(urlPattern)) {
      const relativePath = m[2].replace('./assets/fonts/', '')
      const fullPath = join(fontsDir, relativePath)
      expect(existsSync(fullPath), `missing font file: ${relativePath}`).toBe(true)
    }
  })

  it('Hanken Grotesk covers all four required weights (400/500/600/700)', () => {
    const hkBlocks = fontsCss.split('@font-face').filter(b => b.includes("'Hanken Grotesk'"))
    const weights = hkBlocks.map(b => {
      const m = b.match(/font-weight:\s*(\d+)/)
      return m ? m[1] : null
    })
    expect(weights).toContain('400')
    expect(weights).toContain('500')
    expect(weights).toContain('600')
    expect(weights).toContain('700')
  })

  it('Newsreader has italic variant (required for the wordmark)', () => {
    const nrBlocks = fontsCss.split('@font-face').filter(b => b.includes("'Newsreader'"))
    const hasItalic = nrBlocks.some(b => /font-style:\s*italic/.test(b))
    expect(hasItalic).toBe(true)
  })

  it('all font-display values are swap', () => {
    const faceBlocks = fontsCss.split('@font-face').slice(1)
    for (const block of faceBlocks) {
      if (block.trim().startsWith('{')) {
        const m = block.match(/font-display:\s*(\w+)/)
        if (m) expect(m[1]).toBe('swap')
      }
    }
  })
})
