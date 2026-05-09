'use client'

import Link from 'next/link'
import type { Memo } from '@/lib/types'

function Countdown({ closesAt }: { closesAt: string }) {
  const ms = new Date(closesAt).getTime() - Date.now()
  if (ms <= 0) return <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>Closed</span>
  const d = Math.floor(ms / 86400000)
  const h = Math.floor((ms % 86400000) / 3600000)
  const m = Math.floor((ms % 3600000) / 60000)
  return (
    <span className="mono text-12" style={{ color: 'var(--fg-muted)' }}>
      {d > 0 && `${d}d `}{h}h {m}m
    </span>
  )
}

export default function LiveTable({ memos }: { memos: Memo[] }) {
  if (memos.length === 0) {
    return <p className="text-13" style={{ color: 'var(--fg-muted)' }}>No memos yet.</p>
  }

  return (
    <table className="w-full border-collapse">
      <thead>
        <tr style={{ borderBottom: '1px solid var(--border)' }}>
          {['MARKET', 'VENUE', 'STATUS', 'CLOSES IN', 'POSITION', 'MEMO'].map((h) => (
            <th
              key={h}
              className="mono pb-3 pr-6 text-left text-10 uppercase tracking-widest"
              style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
            >
              {h}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {memos.map((m) => {
          const isOpen = !m.outcome
          const sideColor =
            m.position.side === 'YES'
              ? 'var(--bull)'
              : m.position.side === 'NO'
              ? 'var(--bear)'
              : 'var(--neutral)'
          return (
            <tr
              key={m.market_id}
              style={{ borderBottom: '1px solid var(--border-soft)' }}
              onMouseEnter={(e) =>
                ((e.currentTarget as HTMLElement).style.background = 'var(--surface-2)')
              }
              onMouseLeave={(e) =>
                ((e.currentTarget as HTMLElement).style.background = 'transparent')
              }
            >
              <td className="py-3 pr-6">
                <div className="text-13" style={{ color: 'var(--fg)' }}>
                  <span className="mono text-12" style={{ color: 'var(--accent)' }}>
                    {m.market_id}
                  </span>
                </div>
                <div className="mt-0.5 text-12" style={{ color: 'var(--fg-muted)', maxWidth: 260 }}>
                  {m.market_metadata.title.replace(/^MetaDAO Proposal \d+: /, '')}
                </div>
              </td>
              <td className="py-3 pr-6">
                <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>
                  {m.market_metadata.venue}
                </span>
              </td>
              <td className="py-3 pr-6">
                {isOpen ? (
                  <span className="inline-flex items-center gap-1.5">
                    <span
                      className="live-dot h-1.5 w-1.5 flex-shrink-0 rounded-full"
                      style={{ background: 'var(--bull)' }}
                    />
                    <span className="mono text-11 uppercase" style={{ color: 'var(--bull)' }}>
                      MONITORING
                    </span>
                  </span>
                ) : (
                  <span className="mono text-11 uppercase" style={{ color: 'var(--fg-faint)' }}>
                    RESOLVED
                  </span>
                )}
              </td>
              <td className="py-3 pr-6">
                {isOpen ? (
                  <Countdown closesAt={m.market_metadata.closes_at} />
                ) : (
                  <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>—</span>
                )}
              </td>
              <td className="py-3 pr-6">
                <span className="mono text-12 font-medium" style={{ color: sideColor }}>
                  {m.position.side}
                </span>
              </td>
              <td className="py-3">
                <Link
                  href={`/memos/${m.market_id}`}
                  className="mono text-12 transition-opacity hover:opacity-70"
                  style={{ color: 'var(--accent)', textDecoration: 'none' }}
                >
                  View →
                </Link>
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
