import type { Memo } from '@/lib/types'

function buildSummary(memo: Memo): string {
  const { position, confidence, market_metadata, outcome } = memo
  const side = position.side
  const size = position.size_pct.toFixed(1)
  const conf = (confidence * 100).toFixed(0)
  const title = market_metadata.title

  const verdict =
    side === 'ABSTAIN'
      ? `The agent abstains on ${title} — confidence at ${conf}% is below the threshold to commit capital.`
      : `The agent takes a ${side} position at ${size}% treasury size on ${title}, with ${conf}% confidence.`

  const basis = position.rationale.split('.')[0] + '.'

  const result = outcome
    ? `Resolved ${outcome.resolved_side} — position ${outcome.pnl_pct >= 0 ? 'returned' : 'lost'} ${Math.abs(outcome.pnl_pct).toFixed(2)}% against treasury.`
    : `Market is live and unresolved.`

  return `${verdict} ${basis} ${result}`
}

export default function ExecutiveSummary({ memo }: { memo: Memo }) {
  const summary = buildSummary(memo)

  return (
    <div
      className="rounded p-5"
      style={{
        background: 'var(--accent-soft)',
        borderLeft: '3px solid var(--accent)',
      }}
    >
      <div
        className="mono mb-3 text-10 uppercase tracking-widest"
        style={{ color: 'var(--accent)', letterSpacing: '0.08em' }}
      >
        Executive Summary
      </div>
      <p
        className="text-14 leading-relaxed"
        style={{ color: 'var(--fg)', maxWidth: '65ch' }}
      >
        {summary}
      </p>
    </div>
  )
}
