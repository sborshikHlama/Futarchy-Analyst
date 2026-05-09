export type SourceClass = 'verifiable' | 'partial' | 'manipulable'

export interface SourceWeight {
  class_: SourceClass
  weight: number
  reasoning: string
}

export interface Position {
  side: 'YES' | 'NO' | 'ABSTAIN'
  size_pct: number
  rationale: string
}

export interface SelfReview {
  weaknesses: string[]
  counter_arguments: string[]
}

export interface Outcome {
  resolved_side: 'YES' | 'NO'
  pnl_pct: number
}

export interface MarketMetadata {
  title: string
  proposal: string
  venue: string
  opens_at: string
  closes_at: string
  resolved_outcome?: string
}

export interface SentimentResult {
  score: number
  label: 'bullish' | 'neutral' | 'bearish'
  confidence: number
  sample_size: number
  model: string
}

export interface Sentiment {
  telegram?: SentimentResult
  news?: SentimentResult
}

export interface Memo {
  market_id: string
  request_id?: string
  generated_at: string
  published_at?: string
  market_metadata: MarketMetadata
  source_weights: Record<string, SourceWeight>
  bull_case: string
  bear_case: string
  manipulation_flags: string[]
  confidence: number
  position: Position
  self_review: SelfReview
  sentiment?: Sentiment
  outcome?: Outcome
  prompt_version?: string
  model?: string
  status?: string
  audit_events?: number
  position_iteration?: number
  reviewer_verdict?: string
}

export interface TrackRecord {
  total: number
  resolved: number
  open: number
  wins: number
  losses: number
  abstains: number
  aggregate_pnl: number
  memos: MemoSummary[]
}

export interface MemoSummary {
  market_id: string
  title: string
  venue: string
  generated_at: string
  side: 'YES' | 'NO' | 'ABSTAIN'
  confidence: number
  size_pct: number
  pnl_pct: number | null
  resolved: boolean
}
