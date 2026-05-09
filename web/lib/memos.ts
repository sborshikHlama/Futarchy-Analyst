import fs from 'fs'
import path from 'path'
import type { Memo, TrackRecord, MemoSummary } from './types'

const MARKETS_DIR = path.join(process.cwd(), '..', 'data', 'markets')

function readMemoFile(marketId: string): Memo | null {
  try {
    const filePath = path.join(MARKETS_DIR, marketId, 'memo.json')
    const raw = fs.readFileSync(filePath, 'utf-8')
    return JSON.parse(raw) as Memo
  } catch {
    return null
  }
}

function getMarketIds(): string[] {
  try {
    return fs
      .readdirSync(MARKETS_DIR)
      .filter((d) => {
        const full = path.join(MARKETS_DIR, d)
        return (
          fs.statSync(full).isDirectory() &&
          fs.existsSync(path.join(full, 'memo.json'))
        )
      })
      .sort()
  } catch {
    return []
  }
}

export function getMemo(id: string): Memo | null {
  return readMemoFile(id)
}

export function getAllMemos(): Memo[] {
  return getMarketIds()
    .map(readMemoFile)
    .filter((m): m is Memo => m !== null)
    .sort(
      (a, b) =>
        new Date(b.generated_at).getTime() - new Date(a.generated_at).getTime()
    )
}

export function getTrackRecord(): TrackRecord {
  const memos = getAllMemos()
  const resolved = memos.filter((m) => m.outcome !== undefined)
  const open = memos.filter((m) => m.outcome === undefined)

  const wins = resolved.filter((m) => m.outcome!.pnl_pct > 0).length
  const losses = resolved.filter(
    (m) => m.position.side !== 'ABSTAIN' && m.outcome!.pnl_pct < 0
  ).length
  const abstains = resolved.filter((m) => m.position.side === 'ABSTAIN').length

  const aggregate_pnl = resolved.reduce(
    (sum, m) => sum + (m.outcome?.pnl_pct ?? 0),
    0
  )

  const summaries: MemoSummary[] = memos.map((m) => ({
    market_id: m.market_id,
    title: m.market_metadata.title,
    venue: m.market_metadata.venue,
    generated_at: m.generated_at,
    side: m.position.side,
    confidence: m.confidence,
    size_pct: m.position.size_pct,
    pnl_pct: m.outcome?.pnl_pct ?? null,
    resolved: m.outcome !== undefined,
  }))

  return {
    total: memos.length,
    resolved: resolved.length,
    open: open.length,
    wins,
    losses,
    abstains,
    aggregate_pnl,
    memos: summaries,
  }
}

export function getOpenMemos(): Memo[] {
  return getAllMemos().filter((m) => m.outcome === undefined)
}

export function getLatestMemo(): Memo | null {
  const all = getAllMemos()
  return all.length > 0 ? all[0] : null
}

// Convert [CITATION:source_id] to [S{n}] and return the index map
