import { getTrackRecord } from '@/lib/memos'
import TrackRecordStrip from '@/components/TrackRecordStrip'
import MemoTable from '@/components/MemoTable'

export default function TrackRecordPage() {
  const tr = getTrackRecord()

  return (
    <div className="mx-auto space-y-8 px-6 py-8" style={{ maxWidth: 1100 }}>
      <div>
        <div
          className="mono mb-1 text-11 uppercase tracking-widest"
          style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
        >
          Umia Analyst · Performance
        </div>
        <h1 className="text-24 font-semibold" style={{ color: 'var(--fg)' }}>
          Track Record
        </h1>
      </div>

      <TrackRecordStrip tr={tr} />

      <div
        className="rounded border p-5"
        style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
      >
        <MemoTable memos={tr.memos} />
      </div>
    </div>
  )
}
