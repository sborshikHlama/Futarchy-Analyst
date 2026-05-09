import Link from 'next/link'
import { getAllMemos } from '@/lib/memos'
import VerdictBar from '@/components/memo/VerdictBar'
import LiveTable from './LiveTable'

export default function LiveWatchPage() {
  const allMemos = getAllMemos()
  const open = allMemos.filter((m) => !m.outcome)
  const latestOpen = open.length > 0 ? open[0] : null

  return (
    <div className="mx-auto space-y-8 px-6 py-8" style={{ maxWidth: 1100 }}>
      <div className="flex items-center gap-3">
        <span
          className="live-dot h-2.5 w-2.5 rounded-full"
          style={{ background: 'var(--bull)' }}
        />
        <h1
          className="mono text-11 font-semibold uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          Live Watch
        </h1>
      </div>

      {latestOpen ? (
        <div>
          <div
            className="mono mb-3 text-10 uppercase tracking-widest"
            style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
          >
            Active Position · {latestOpen.market_metadata.title}
          </div>
          <VerdictBar memo={latestOpen} />
          <div className="mt-3 text-right">
            <Link
              href={`/memos/${latestOpen.market_id}`}
              className="mono text-12 transition-opacity hover:opacity-70"
              style={{ color: 'var(--accent)', textDecoration: 'none' }}
            >
              Read full memo →
            </Link>
          </div>
        </div>
      ) : (
        <div
          className="rounded border p-8 text-center"
          style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
        >
          <p className="text-14" style={{ color: 'var(--fg-muted)' }}>
            No open markets currently under monitoring.
          </p>
        </div>
      )}

      <div
        className="rounded border p-5"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        <div
          className="mono mb-4 text-11 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          All Monitored Markets
        </div>
        <LiveTable memos={allMemos} />
      </div>
    </div>
  )
}
