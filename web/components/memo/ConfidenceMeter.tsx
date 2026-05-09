'use client'

const SEGMENTS = 8

function segmentColor(index: number, total: number): string {
  // Gradient: low (red) → mid (amber) → high (green)
  // index is 0-based from left
  const t = index / (total - 1) // 0..1
  if (t < 0.4) {
    // red → amber
    const p = t / 0.4
    const r = Math.round(229 + (245 - 229) * p)
    const g = Math.round(72  + (165 - 72)  * p)
    const b = Math.round(77  + (36  - 77)  * p)
    return `rgb(${r},${g},${b})`
  } else {
    // amber → green
    const p = (t - 0.4) / 0.6
    const r = Math.round(245 + (46  - 245) * p)
    const g = Math.round(165 + (189 - 165) * p)
    const b = Math.round(36  + (133 - 36)  * p)
    return `rgb(${r},${g},${b})`
  }
}

export default function ConfidenceMeter({ confidence }: { confidence: number }) {
  const filled = Math.round(confidence * SEGMENTS)

  return (
    <div className="flex flex-col gap-1.5">
      <div
        className="mono text-10 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        CONFIDENCE
      </div>

      <div className="flex items-center gap-1">
        {Array.from({ length: SEGMENTS }).map((_, i) => (
          <div
            key={i}
            className="conf-segment"
            style={{
              background: i < filled
                ? segmentColor(i, SEGMENTS)
                : 'var(--surface-2)',
              border: i < filled ? 'none' : '1px solid var(--border)',
            }}
          />
        ))}
      </div>

      <div
        className="mono text-11"
        style={{ color: 'var(--fg-muted)' }}
      >
        {confidence.toFixed(2)}
      </div>
    </div>
  )
}
