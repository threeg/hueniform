/** Convert HSL (h: 0–360, s: 0–100, l: 0–100) to a CSS hex colour string. */
export function hslToHex(h: number, s: number, l: number): string {
  const sl = s / 100
  const ll = l / 100
  const c = (1 - Math.abs(2 * ll - 1)) * sl
  const x = c * (1 - Math.abs(((h / 60) % 2) - 1))
  const m = ll - c / 2
  let r = 0, g = 0, b = 0
  if      (h < 60)  { r = c; g = x; b = 0 }
  else if (h < 120) { r = x; g = c; b = 0 }
  else if (h < 180) { r = 0; g = c; b = x }
  else if (h < 240) { r = 0; g = x; b = c }
  else if (h < 300) { r = x; g = 0; b = c }
  else              { r = c; g = 0; b = x }
  const hex = (n: number) => Math.round((n + m) * 255).toString(16).padStart(2, '0')
  return `#${hex(r)}${hex(g)}${hex(b)}`
}

/**
 * Scale an array of proportions so they sum to exactly 100.
 * Rounding errors are absorbed by the largest bucket.
 */
export function normaliseProportions(proportions: number[]): number[] {
  const total = proportions.reduce((a, b) => a + b, 0)
  if (total === 0) {
    const each = Math.floor(100 / proportions.length)
    return proportions.map((_, i) =>
      i === 0 ? 100 - each * (proportions.length - 1) : each,
    )
  }
  const scaled = proportions.map(p => Math.round((p * 100) / total))
  const diff = 100 - scaled.reduce((a, b) => a + b, 0)
  const maxIdx = scaled.reduce((mi, v, i, a) => (v > a[mi] ? i : mi), 0)
  scaled[maxIdx] += diff
  return scaled
}
