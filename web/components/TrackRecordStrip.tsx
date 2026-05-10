import type { TrackRecord } from '@/lib/types'

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <div
        className="mono text-10 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        {label}
      </div>
      <div
        className="mono text-24 font-semibold"
        style={{ color: color ?? 'var(--fg)' }}
      >
        {value}
      </div>
    </div>
  )
}

export default function TrackRecordStrip({ tr }: { tr: TrackRecord }) {
  const pnlColor = tr.aggregate_pnl >= 0 ? 'var(--bull)' : 'var(--bear)'
  const pnlSign = tr.aggregate_pnl >= 0 ? '+' : ''
  const winRate =
    tr.resolved > 0 ? ((tr.wins / (tr.wins + tr.losses)) * 100).toFixed(0) : '—'

  return (
    <div
      className="track-strip flex flex-wrap gap-8 rounded border p-6"
      style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
    >
      <Stat label="Total Memos" value={String(tr.total)} />
      <Stat label="Resolved" value={String(tr.resolved)} />
      <Stat label="Open" value={String(tr.open)} />
      <Stat label="Win Rate" value={`${winRate}%`} />
      <Stat
        label="Aggregate PnL"
        value={`${pnlSign}${tr.aggregate_pnl.toFixed(2)}%`}
        color={pnlColor}
      />
      <Stat label="Wins / Losses" value={`${tr.wins} / ${tr.losses}`} />
    </div>
  )
}
