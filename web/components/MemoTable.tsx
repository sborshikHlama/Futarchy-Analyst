'use client'

import Link from 'next/link'
import type { MemoSummary } from '@/lib/types'

function fmtDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

function fmtPnl(pnl: number | null, resolved: boolean) {
  if (!resolved || pnl === null) return { text: '—', color: 'var(--fg-faint)' }
  const sign = pnl >= 0 ? '+' : ''
  return {
    text: `${sign}${pnl.toFixed(2)}%`,
    color: pnl >= 0 ? 'var(--bull)' : 'var(--bear)',
  }
}

function SideDot({ side }: { side: string }) {
  const color =
    side === 'YES' ? 'var(--bull)' : side === 'NO' ? 'var(--bear)' : 'var(--neutral)'
  return (
    <span className="inline-flex items-center gap-1.5">
      <span
        className="inline-block h-2 w-2 flex-shrink-0 rounded-full"
        style={{ background: color }}
      />
      <span className="mono font-medium" style={{ color }}>
        {side}
      </span>
    </span>
  )
}

export default function MemoTable({
  memos,
  limit,
}: {
  memos: MemoSummary[]
  limit?: number
}) {
  const rows = limit ? memos.slice(0, limit) : memos

  return (
    <table className="w-full border-collapse">
      <thead>
        <tr style={{ borderBottom: '1px solid var(--border)' }}>
          {['DATE', 'MARKET', 'VENUE', 'POSITION', 'CONF', 'SIZE', 'PNL'].map(
            (h) => (
              <th
                key={h}
                className="mono pb-3 pr-6 text-left text-10 uppercase tracking-widest"
                style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
              >
                {h}
              </th>
            )
          )}
        </tr>
      </thead>
      <tbody>
        {rows.map((m) => {
          const pnl = fmtPnl(m.pnl_pct, m.resolved)
          return (
            <tr
              key={m.market_id}
              className="group transition-colors"
              style={{ borderBottom: '1px solid var(--border-soft)' }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLElement).style.background =
                  'var(--surface-2)')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLElement).style.background = 'transparent')
              }
            >
              <td className="py-3 pr-6">
                <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>
                  {fmtDate(m.generated_at)}
                </span>
              </td>
              <td className="py-3 pr-6" style={{ maxWidth: 300 }}>
                <Link
                  href={`/memos/${m.market_id}`}
                  className="text-13 transition-colors hover:underline"
                  style={{ color: 'var(--fg)', textDecoration: 'none' }}
                >
                  <span style={{ color: 'var(--accent)' }}>{m.market_id}</span>
                  {' · '}
                  <span>{m.title.replace(/^MetaDAO Proposal \d+: /, '')}</span>
                </Link>
              </td>
              <td className="py-3 pr-6">
                <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>
                  {m.venue}
                </span>
              </td>
              <td className="py-3 pr-6">
                <SideDot side={m.side} />
              </td>
              <td className="py-3 pr-6">
                <span className="mono text-12" style={{ color: 'var(--fg-muted)' }}>
                  {m.confidence.toFixed(2)}
                </span>
              </td>
              <td className="py-3 pr-6">
                <span className="mono text-12" style={{ color: 'var(--fg-muted)' }}>
                  {m.size_pct.toFixed(1)}%
                </span>
              </td>
              <td className="py-3">
                <span
                  className="mono text-12 font-medium"
                  style={{ color: pnl.color }}
                >
                  {pnl.text}
                </span>
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
