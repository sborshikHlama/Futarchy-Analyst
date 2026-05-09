'use client'

import { useState, Fragment } from 'react'
import { ChevronDown, ChevronRight, ExternalLink } from 'lucide-react'
import type { SourceWeight, SourceClass } from '@/lib/types'

const SEGMENTS = 8

function classBadge(cls: SourceClass) {
  const map: Record<SourceClass, { label: string; color: string; bg: string }> = {
    verifiable:  { label: 'VERIFIABLE',  color: 'var(--bull)',    bg: 'var(--bull-soft)' },
    partial:     { label: 'PARTIAL',     color: 'var(--fg-muted)',bg: 'var(--surface-2)' },
    manipulable: { label: 'MANIPULABLE', color: 'var(--warn)',    bg: 'var(--warn-soft)' },
  }
  return map[cls] ?? map.partial
}

function WeightBar({ weight }: { weight: number }) {
  const filled = Math.round(weight * SEGMENTS)
  return (
    <div className="flex items-center gap-1">
      <div className="flex gap-0.5">
        {Array.from({ length: SEGMENTS }).map((_, i) => (
          <div
            key={i}
            className="weight-segment"
            style={{
              background: i < filled ? 'var(--accent)' : 'var(--surface-2)',
              border: i < filled ? 'none' : '1px solid var(--border)',
              opacity: i < filled ? (0.4 + 0.6 * (i / (SEGMENTS - 1))) : 1,
            }}
          />
        ))}
      </div>
      <span
        className="mono ml-2 text-12"
        style={{ color: 'var(--fg-muted)', minWidth: 28 }}
      >
        {weight.toFixed(2)}
      </span>
    </div>
  )
}

interface Row {
  id: string
  label: string
  source: SourceWeight
}

type SortKey = 'id' | 'class_' | 'weight'

export default function SourceWeightsTable({
  sourceWeights,
  sourceIndex,
}: {
  sourceWeights: Record<string, SourceWeight>
  sourceIndex: Record<string, string>
}) {
  const [expanded, setExpanded] = useState<string | null>(null)
  const [sort, setSort] = useState<SortKey>('weight')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const rows: Row[] = Object.entries(sourceWeights).map(([id, sw]) => ({
    id,
    label: id.replace(/_/g, ' '),
    source: sw,
  }))

  const sorted = [...rows].sort((a, b) => {
    let cmp = 0
    if (sort === 'id')     cmp = (sourceIndex[a.id] ?? '').localeCompare(sourceIndex[b.id] ?? '')
    if (sort === 'class_') cmp = a.source.class_.localeCompare(b.source.class_)
    if (sort === 'weight') cmp = a.source.weight - b.source.weight
    return sortDir === 'asc' ? cmp : -cmp
  })

  function toggleSort(key: SortKey) {
    if (sort === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSort(key); setSortDir('desc') }
  }

  const ColHead = ({ label, k }: { label: string; k: SortKey }) => (
    <th
      className="mono cursor-pointer select-none pb-2 pr-6 text-left text-10 uppercase tracking-widest"
      style={{
        color: sort === k ? 'var(--fg-muted)' : 'var(--fg-faint)',
        letterSpacing: '0.08em',
        borderBottom: '1px solid var(--border)',
      }}
      onClick={() => toggleSort(k)}
    >
      {label} {sort === k ? (sortDir === 'asc' ? '↑' : '↓') : ''}
    </th>
  )

  return (
    <div>
      <table className="w-full border-collapse">
        <thead>
          <tr>
            <ColHead label="ID" k="id" />
            <th
              className="mono pb-2 pr-6 text-left text-10 uppercase tracking-widest"
              style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em', borderBottom: '1px solid var(--border)' }}
            >
              Source
            </th>
            <ColHead label="Class" k="class_" />
            <ColHead label="Weight" k="weight" />
          </tr>
        </thead>
        <tbody>
          {sorted.map((row) => {
            const badge = classBadge(row.source.class_)
            const isOpen = expanded === row.id
            return (
              <Fragment key={row.id}>
                <tr
                  id={`source-row-${row.id}`}
                  className="cursor-pointer"
                  onClick={() => setExpanded(isOpen ? null : row.id)}
                  style={{
                    borderBottom: isOpen ? 'none' : '1px solid var(--border-soft)',
                  }}
                  onMouseEnter={e => (e.currentTarget as HTMLElement).style.background = 'var(--surface-2)'}
                  onMouseLeave={e => (e.currentTarget as HTMLElement).style.background = 'transparent'}
                >
                  <td className="py-3 pr-6">
                    <div className="flex items-center gap-1.5">
                      {isOpen
                        ? <ChevronDown size={12} style={{ color: 'var(--fg-faint)' }} />
                        : <ChevronRight size={12} style={{ color: 'var(--fg-faint)' }} />}
                      <span
                        className="mono text-12 font-medium"
                        style={{ color: 'var(--accent)' }}
                      >
                        [{sourceIndex[row.id] ?? row.id}]
                      </span>
                    </div>
                  </td>
                  <td className="py-3 pr-6">
                    <div className="flex items-center gap-1.5">
                      <span className="text-13" style={{ color: 'var(--fg-muted)' }}>
                        {row.label}
                      </span>
                      {row.source.url && (
                        <a
                          href={row.source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={e => e.stopPropagation()}
                          style={{ color: 'var(--fg-faint)', lineHeight: 1 }}
                        >
                          <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                  </td>
                  <td className="py-3 pr-6">
                    <span
                      className="mono rounded px-1.5 py-0.5 text-10 font-medium uppercase"
                      style={{
                        color: badge.color,
                        background: badge.bg,
                        letterSpacing: '0.06em',
                      }}
                    >
                      {badge.label}
                    </span>
                  </td>
                  <td className="py-3">
                    <WeightBar weight={row.source.weight} />
                  </td>
                </tr>
                {isOpen && (
                  <tr
                    key={`${row.id}-detail`}
                    style={{ borderBottom: '1px solid var(--border-soft)' }}
                  >
                    <td colSpan={4} className="pb-4 pl-8 pr-4 pt-0">
                      <p
                        className="text-13 leading-relaxed"
                        style={{ color: 'var(--fg-muted)' }}
                      >
                        {row.source.reasoning}
                      </p>
                    </td>
                  </tr>
                )}
              </Fragment>
            )
          })}
        </tbody>
      </table>
      <p
        className="mt-2 text-12"
        style={{ color: 'var(--fg-faint)' }}
      >
        ↕ Click any row to see weighting rationale · Click column headers to sort
      </p>
    </div>
  )
}
