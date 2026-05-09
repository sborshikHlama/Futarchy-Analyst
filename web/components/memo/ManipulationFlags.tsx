import { AlertTriangle } from 'lucide-react'

export default function ManipulationFlags({ flags }: { flags: string[] }) {
  if (!flags || flags.length === 0) return null

  return (
    <div
      className="rounded border-l-3 p-4"
      style={{
        background: 'var(--warn-soft)',
        borderColor: 'var(--warn)',
        borderLeftWidth: 3,
        borderLeftStyle: 'solid',
      }}
    >
      <div className="mb-3 flex items-center gap-2">
        <AlertTriangle
          size={14}
          style={{ color: 'var(--warn)', flexShrink: 0 }}
        />
        <span
          className="mono text-11 font-semibold uppercase tracking-widest"
          style={{ color: 'var(--warn)', letterSpacing: '0.08em' }}
        >
          Manipulation Flags
        </span>
        <span
          className="mono rounded px-1.5 py-0.5 text-10"
          style={{
            background: 'rgba(245,165,36,0.15)',
            color: 'var(--warn)',
          }}
        >
          {flags.length}
        </span>
      </div>
      <ul className="space-y-2">
        {flags.map((flag, i) => (
          <li key={i} className="flex items-start gap-2 text-13">
            <span
              className="mono mt-0.5 flex-shrink-0 text-11"
              style={{ color: 'var(--warn)' }}
            >
              ·
            </span>
            <span style={{ color: 'var(--fg-muted)' }}>{flag}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
