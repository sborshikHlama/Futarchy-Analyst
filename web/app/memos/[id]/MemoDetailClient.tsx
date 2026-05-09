'use client'

import { useRef } from 'react'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'
import type { Memo } from '@/lib/types'
import { buildSourceIndex } from '@/lib/utils'
import MemoHeader from '@/components/memo/MemoHeader'
import VerdictBar from '@/components/memo/VerdictBar'
import ExecutiveSummary from '@/components/memo/ExecutiveSummary'
import ManipulationFlags from '@/components/memo/ManipulationFlags'
import BullBearGrid from '@/components/memo/BullBearGrid'
import SourceWeightsTable from '@/components/memo/SourceWeightsTable'
import SelfReview from '@/components/memo/SelfReview'
import PositionRationale from '@/components/memo/PositionRationale'
import Provenance from '@/components/memo/Provenance'

function SectionDivider({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-3">
      <span
        className="mono text-11 uppercase tracking-widest"
        style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em', flexShrink: 0 }}
      >
        {label}
      </span>
      <div className="h-px flex-1" style={{ background: 'var(--border)' }} />
    </div>
  )
}

export default function MemoDetailClient({ memo }: { memo: Memo }) {
  const sourceTableRef = useRef<HTMLDivElement>(null)
  const sourceIndex = buildSourceIndex(memo.source_weights)

  function handleCitationClick(sourceId: string) {
    sourceTableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    // Highlight the row briefly
    const el = document.getElementById(`source-row-${sourceId}`)
    if (el) {
      el.style.background = 'var(--accent-soft)'
      setTimeout(() => { el.style.background = '' }, 1500)
    }
  }

  return (
    <div
      className="memo-content mx-auto space-y-8 px-6 py-8"
      style={{ maxWidth: 880 }}
    >
      {/* Back nav */}
      <Link
        href="/memos"
        className="inline-flex items-center gap-1.5 text-13 transition-opacity hover:opacity-70"
        style={{ color: 'var(--fg-muted)', textDecoration: 'none' }}
      >
        <ArrowLeft size={13} />
        All memos
      </Link>

      <MemoHeader memo={memo} />

      <VerdictBar memo={memo} />

      <ExecutiveSummary memo={memo} />

      {memo.manipulation_flags && memo.manipulation_flags.length > 0 && (
        <ManipulationFlags flags={memo.manipulation_flags} />
      )}

      <div className="space-y-3">
        <SectionDivider label="Analysis" />
        <BullBearGrid
          bull_case={memo.bull_case}
          bear_case={memo.bear_case}
          sourceIndex={sourceIndex}
          onCitationClick={handleCitationClick}
        />
      </div>

      <div className="space-y-3" ref={sourceTableRef}>
        <SectionDivider label="Source Weights" />
        <div
          className="rounded border p-5"
          style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
        >
          <SourceWeightsTable
            sourceWeights={memo.source_weights}
            sourceIndex={sourceIndex}
          />
        </div>
      </div>

      <div className="space-y-3">
        <SectionDivider label="Self-Review" />
        <SelfReview review={memo.self_review} />
      </div>

      <div className="space-y-3">
        <SectionDivider label="Position Rationale" />
        <PositionRationale position={memo.position} />
      </div>

      <Provenance memo={memo} />
    </div>
  )
}
