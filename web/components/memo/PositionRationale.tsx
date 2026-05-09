import type { Position } from '@/lib/types'

function sideColor(side: string) {
  if (side === 'YES') return 'var(--bull)'
  if (side === 'NO')  return 'var(--bear)'
  return 'var(--neutral)'
}

export default function PositionRationale({ position }: { position: Position }) {
  return (
    <div
      className="rounded border-l p-5"
      style={{
        background: 'var(--surface)',
        borderColor: 'var(--border)',
        borderLeftWidth: 3,
        borderLeftStyle: 'solid',
        borderLeftColor: sideColor(position.side),
      }}
    >
      <div
        className="mono mb-3 text-11 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        Position Rationale ·{' '}
        <span style={{ color: sideColor(position.side) }}>
          {position.side} @ {position.size_pct.toFixed(1)}%
        </span>
      </div>
      <p className="text-13 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>
        {position.rationale}
      </p>
    </div>
  )
}
