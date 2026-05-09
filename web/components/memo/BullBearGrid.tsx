'use client'

import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { Components } from 'react-markdown'
import { useMemo } from 'react'

interface BullBearGridProps {
  bull_case: string
  bear_case: string
  sourceIndex: Record<string, string>  // source_id -> "S1", "S2", etc.
  onCitationClick: (sourceId: string) => void
}

function renderCitations(
  text: string,
  sourceIndex: Record<string, string>,
  onCitationClick: (sourceId: string) => void
): React.ReactNode[] {
  // Replace [CITATION:source_id] with clickable badges
  const parts = text.split(/\[CITATION:([^\]]+)\]/)
  return parts.map((part, i) => {
    if (i % 2 === 0) return part
    const sourceId = part
    const label = sourceIndex[sourceId] ?? sourceId
    return (
      <button
        key={i}
        className="citation-link"
        onClick={() => onCitationClick(sourceId)}
        title={`Go to source: ${sourceId}`}
      >
        [{label}]
      </button>
    )
  })
}

function CaseSection({
  title,
  content,
  sourceIndex,
  onCitationClick,
  side,
}: {
  title: string
  content: string
  sourceIndex: Record<string, string>
  onCitationClick: (sourceId: string) => void
  side: 'bull' | 'bear'
}) {
  const color = side === 'bull' ? 'var(--bull)' : 'var(--bear)'
  const bg    = side === 'bull' ? 'var(--bull-soft)' : 'var(--bear-soft)'

  const components: Components = {
    p: ({ children }) => (
      <p className="mb-3 text-13 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>
        {typeof children === 'string'
          ? renderCitations(children, sourceIndex, onCitationClick)
          : children}
      </p>
    ),
    li: ({ children }) => (
      <li className="mb-1.5 text-13" style={{ color: 'var(--fg-muted)' }}>
        {typeof children === 'string'
          ? renderCitations(children, sourceIndex, onCitationClick)
          : children}
      </li>
    ),
  }

  // Pre-process text to replace citation markers before markdown parsing
  // We'll handle them post-render by splitting paragraphs
  const processedContent = content

  return (
    <div
      className="rounded border p-5"
      style={{
        background: 'var(--surface)',
        borderColor: 'var(--border)',
        borderTop: `3px solid ${color}`,
      }}
    >
      <div
        className="mono mb-4 text-11 font-semibold uppercase tracking-widest"
        style={{ color, letterSpacing: '0.08em' }}
      >
        {title}
      </div>

      <div className="prose-memo">
        {processedContent.split('\n\n').map((para, idx) => {
          const trimmed = para.trim()
          if (!trimmed) return null
          return (
            <p
              key={idx}
              className="mb-3 text-13 leading-relaxed"
              style={{ color: 'var(--fg-muted)' }}
            >
              {renderCitations(trimmed, sourceIndex, onCitationClick)}
            </p>
          )
        })}
      </div>
    </div>
  )
}

export default function BullBearGrid({
  bull_case,
  bear_case,
  sourceIndex,
  onCitationClick,
}: BullBearGridProps) {
  return (
    <div className="grid grid-cols-2 gap-6">
      <CaseSection
        title="Bull Case"
        content={bull_case}
        sourceIndex={sourceIndex}
        onCitationClick={onCitationClick}
        side="bull"
      />
      <CaseSection
        title="Bear Case"
        content={bear_case}
        sourceIndex={sourceIndex}
        onCitationClick={onCitationClick}
        side="bear"
      />
    </div>
  )
}
