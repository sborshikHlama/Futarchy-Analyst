import type { SelfReview as SelfReviewType } from '@/lib/types'

function SubSection({ title, items }: { title: string; items: string[] }) {
  if (!items || items.length === 0) return null
  return (
    <div>
      <div
        className="mono mb-2 text-11 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        {title}
      </div>
      <ul className="space-y-1.5">
        {items.map((item, i) => (
          <li key={i} className="flex items-start gap-2 text-13">
            <span
              className="mono mt-0.5 flex-shrink-0"
              style={{ color: 'var(--fg-faint)' }}
            >
              ·
            </span>
            <span style={{ color: 'var(--fg-muted)' }}>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function SelfReview({ review }: { review: SelfReviewType }) {
  return (
    <div
      className="rounded border p-5"
      style={{
        background: 'var(--surface)',
        borderColor: 'var(--border)',
        opacity: 0.88,
      }}
    >
      <div
        className="mono mb-4 text-11 font-semibold uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
      >
        Agent Self-Review
      </div>
      <div className="space-y-5">
        <SubSection title="Weaknesses" items={review.weaknesses} />
        <SubSection title="Counter-Arguments" items={review.counter_arguments} />
      </div>
    </div>
  )
}
