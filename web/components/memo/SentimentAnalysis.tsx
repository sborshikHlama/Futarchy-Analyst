import type { Sentiment, SentimentResult } from '@/lib/types'

function scoreColor(label: string) {
  if (label === 'bullish') return 'var(--bull)'
  if (label === 'bearish') return 'var(--bear)'
  return 'var(--fg-muted)'
}

function fmtScore(score: number) {
  const sign = score > 0 ? '+' : ''
  return `${sign}${score.toFixed(2)}`
}

function SourceRow({ label, result }: { label: string; result: SentimentResult }) {
  if (result.sample_size === 0) return null
  return (
    <div className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border-soft)' }}>
      <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>{label}</span>
      <div className="flex items-center gap-3">
        <span className="mono text-12 font-semibold" style={{ color: scoreColor(result.label) }}>
          {fmtScore(result.score)}
        </span>
        <span
          className="mono rounded px-1.5 py-0.5 text-10 uppercase"
          style={{ color: scoreColor(result.label), background: 'var(--surface-2)', letterSpacing: '0.06em' }}
        >
          {result.label}
        </span>
        <span className="mono text-11" style={{ color: 'var(--fg-faint)' }}>
          {result.sample_size} texts
        </span>
      </div>
    </div>
  )
}

export default function SentimentAnalysis({ sentiment }: { sentiment: Sentiment }) {
  const sources = [
    { label: 'telegram', result: sentiment.telegram },
    { label: 'news', result: sentiment.news },
  ].filter((s): s is { label: string; result: SentimentResult } => !!s.result && s.result.sample_size > 0)

  if (sources.length === 0) return null

  const scores = sources.map(s => s.result.score)
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length
  const avgLabel = avg > 0.15 ? 'bullish' : avg < -0.15 ? 'bearish' : 'neutral'
  const totalTexts = sources.reduce((a, s) => a + s.result.sample_size, 0)

  return (
    <div
      className="rounded border p-5"
      style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
    >
      <div className="mb-4 flex items-start justify-between">
        <div>
          <div
            className="mono text-10 uppercase tracking-widest"
            style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
          >
            Community Sentiment
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span className="mono text-28 font-semibold" style={{ color: scoreColor(avgLabel) }}>
              {fmtScore(avg)}
            </span>
            <span
              className="mono text-12 uppercase font-semibold"
              style={{ color: scoreColor(avgLabel) }}
            >
              {avgLabel}
            </span>
          </div>
          <div className="mono text-11 mt-1" style={{ color: 'var(--fg-faint)' }}>
            {totalTexts} texts · HuggingFace Inference API
          </div>
        </div>
      </div>

      <div
        className="mono mb-2 text-10 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        By Source
      </div>
      {sources.map(s => (
        <SourceRow key={s.label} label={s.label} result={s.result} />
      ))}

      <div className="mt-3 text-11" style={{ color: 'var(--fg-faint)' }}>
        Models: {sources.map(s => s.result.model).join(' · ')}
      </div>
    </div>
  )
}
