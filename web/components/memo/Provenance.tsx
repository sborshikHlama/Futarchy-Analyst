import { ExternalLink, Lock } from 'lucide-react'
import type { Memo } from '@/lib/types'

function fmtUtc(iso: string) {
  return new Date(iso).toUTCString().replace(' GMT', ' UTC')
}

export default function Provenance({ memo }: { memo: Memo }) {
  return (
    <div
      className="rounded border p-5"
      style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
    >
      <div className="mb-3 flex items-center gap-2">
        <Lock size={12} style={{ color: 'var(--fg-faint)' }} />
        <span
          className="mono text-10 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          Provenance
        </span>
      </div>

      <div
        className="mono space-y-1 text-12"
        style={{ color: 'var(--fg-faint)' }}
      >
        <div>
          <span style={{ color: 'var(--fg-faint)' }}>Generated </span>
          <span style={{ color: 'var(--fg-muted)' }}>{fmtUtc(memo.generated_at)}</span>
        </div>

        {memo.published_at && (
          <div>
            <span style={{ color: 'var(--fg-faint)' }}>Published </span>
            <span style={{ color: 'var(--fg-muted)' }}>{fmtUtc(memo.published_at)}</span>
          </div>
        )}

        {memo.model && (
          <div>
            <span style={{ color: 'var(--fg-faint)' }}>Model </span>
            <span style={{ color: 'var(--fg-muted)' }}>{memo.model}</span>
          </div>
        )}

        {memo.prompt_version && (
          <div>
            <span style={{ color: 'var(--fg-faint)' }}>Synthesizer prompt </span>
            <span style={{ color: 'var(--fg-muted)' }}>v.{memo.prompt_version.slice(0, 10)}</span>
          </div>
        )}

        {memo.audit_events !== undefined && (
          <div>
            <span style={{ color: 'var(--fg-faint)' }}>Audit events </span>
            <span style={{ color: 'var(--fg-muted)' }}>{memo.audit_events}</span>
          </div>
        )}

        {memo.reviewer_verdict && (
          <div>
            <span style={{ color: 'var(--fg-faint)' }}>Reviewer verdict </span>
            <span
              style={{
                color: memo.reviewer_verdict === 'APPROVE' ? 'var(--bull)' : 'var(--bear)',
              }}
            >
              {memo.reviewer_verdict}
            </span>
          </div>
        )}

        <div className="mt-3 pt-3" style={{ borderTop: '1px solid var(--border-soft)' }}>
          <span style={{ color: 'var(--fg-faint)' }}>
            This memo is immutable. Its content will not be edited after publication.
            Outcome is appended on resolution.
          </span>
        </div>
      </div>
    </div>
  )
}
