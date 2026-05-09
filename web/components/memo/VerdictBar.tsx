import type { Memo } from '@/lib/types'
import ConfidenceMeter from './ConfidenceMeter'

function sideColor(side: string) {
  if (side === 'YES') return 'var(--bull)'
  if (side === 'NO')  return 'var(--bear)'
  return 'var(--neutral)'
}

function sideBg(side: string) {
  if (side === 'YES') return 'var(--bull-soft)'
  if (side === 'NO')  return 'var(--bear-soft)'
  return 'transparent'
}

function fmtPnl(pnl: number) {
  const sign = pnl >= 0 ? '+' : ''
  return `${sign}${pnl.toFixed(2)}%`
}

export default function VerdictBar({ memo }: { memo: Memo }) {
  const { position, confidence, outcome } = memo
  const isResolved = outcome != null
  const pnlPositive = isResolved && outcome!.pnl_pct >= 0

  return (
    <div
      className="flex w-full rounded border"
      style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
    >
      {/* POSITION */}
      <div className="verdict-cell">
        <div
          className="mono mb-2 text-10 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          POSITION
        </div>
        <div className="flex items-center gap-2">
          <span
            className="h-2.5 w-2.5 flex-shrink-0 rounded-full"
            style={{ background: sideColor(position.side) }}
          />
          <span
            className="mono text-24 font-semibold"
            style={{
              color: sideColor(position.side),
              background: sideBg(position.side),
              padding: '0 6px',
              borderRadius: 4,
            }}
          >
            {position.side}
          </span>
        </div>
      </div>

      {/* CONFIDENCE */}
      <div className="verdict-cell">
        <ConfidenceMeter confidence={confidence} />
      </div>

      {/* SIZE */}
      <div className="verdict-cell">
        <div
          className="mono mb-2 text-10 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          SIZE
        </div>
        <div
          className="mono text-24 font-semibold"
          style={{ color: 'var(--fg)' }}
        >
          {position.size_pct.toFixed(1)}%
        </div>
        <div className="mono text-11 mt-1" style={{ color: 'var(--fg-faint)' }}>
          of treasury
        </div>
      </div>

      {/* STATUS / PNL */}
      <div className="verdict-cell">
        <div
          className="mono mb-2 text-10 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          STATUS
        </div>
        {isResolved ? (
          <div>
            <div className="mb-1 flex items-center gap-2">
              <span
                className="mono rounded px-1.5 py-0.5 text-10 font-semibold uppercase"
                style={{
                  background: 'var(--surface-2)',
                  color: 'var(--fg-muted)',
                  letterSpacing: '0.05em',
                }}
              >
                RESOLVED
              </span>
            </div>
            <div
              className="mono text-24 font-semibold"
              style={{ color: pnlPositive ? 'var(--bull)' : 'var(--bear)' }}
            >
              {fmtPnl(outcome!.pnl_pct)}
            </div>
            <div className="mono text-11 mt-1" style={{ color: 'var(--fg-faint)' }}>
              {outcome!.resolved_side} outcome
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-2">
            <span
              className="live-dot h-2 w-2 flex-shrink-0 rounded-full"
              style={{ background: 'var(--bull)' }}
            />
            <span
              className="mono text-14 font-semibold uppercase"
              style={{ color: 'var(--bull)', letterSpacing: '0.04em' }}
            >
              LIVE
            </span>
          </div>
        )}
      </div>
    </div>
  )
}
