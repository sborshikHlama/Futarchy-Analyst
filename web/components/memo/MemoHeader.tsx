import type { Memo } from '@/lib/types'

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  })
}

export default function MemoHeader({ memo }: { memo: Memo }) {
  const meta = memo.market_metadata
  return (
    <div
      className="rounded border p-6"
      style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
    >
      <div
        className="mono mb-3 text-11 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)' }}
      >
        Research Memo · {memo.market_id.toUpperCase()}
      </div>

      <h1
        className="mb-4 text-15 font-semibold leading-tight"
        style={{ color: 'var(--fg)' }}
      >
        {meta.title}
      </h1>

      <p className="mb-4 text-13 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>
        {meta.proposal}
      </p>

      <div
        className="mono flex flex-wrap gap-x-4 gap-y-1 text-11"
        style={{ color: 'var(--fg-faint)' }}
      >
        {[
          ['VENUE', meta.venue],
          ['OPENS', fmt(meta.opens_at)],
          ['CLOSES', fmt(meta.closes_at)],
          ['GENERATED', fmt(memo.generated_at)],
          ...(memo.model ? [['MODEL', memo.model]] : []),
          ...(memo.prompt_version ? [['PROMPT', memo.prompt_version]] : []),
        ].map(([label, value], i) => (
          <span key={i} className="flex items-center gap-1.5">
            <span style={{ color: 'var(--fg-faint)' }}>{label}</span>
            <span style={{ color: 'var(--fg-muted)' }}>{value}</span>
          </span>
        ))}
      </div>
    </div>
  )
}
