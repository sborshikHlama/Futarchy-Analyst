import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { getTrackRecord, getLatestMemo } from '@/lib/memos'
import TrackRecordStrip from '@/components/TrackRecordStrip'
import MemoTable from '@/components/MemoTable'
import VerdictBar from '@/components/memo/VerdictBar'
import { HeroLogo } from '@/components/Logo'

const PROBLEM = `Futarchic governance markets produce a flood of signal — on-chain transactions, developer commits, founder communications, community sentiment — but no structured analysis. Voters and traders have no institutional-quality research to anchor their positions. The result is thin markets, manipulation, and decisions that don't price information efficiently.

The Umia Analyst Agent reads every available signal for a decision market, classifies sources by manipulability, synthesizes a thesis, takes a verifiable on-chain position from the treasury, and publishes a timestamped, auditable memo. Its track record is its reputation.

This is not a dashboard. It is an autonomous analyst with a P&L.`

const HOW_IT_WORKS = [
  ['01 INGEST',    'Pulls GitHub commits, on-chain transactions, Telegram channels, and Twitter for every signal relevant to the proposal.'],
  ['02 CLASSIFY',  'Each source is classified: verifiable, partial, or manipulable. Hard caps prevent manipulable sources from dominating the analysis.'],
  ['03 SYNTHESIZE','A versioned AI skill synthesizes bull and bear cases, flags manipulation, and assigns a confidence score. Every claim must cite a source.'],
  ['04 POSITION',  'A position agent takes a YES, NO, or ABSTAIN position with size proportional to confidence. A self-reviewer checks citations. An audit log is appended.'],
]

const ROADMAP = [
  ['Q2 2026', 'Phase 1 — MetaDAO Backtest', 'Three resolved MetaDAO proposals, full audit trail, track record published.'],
  ['Q3 2026', 'Phase 2 — Live Production', 'Real-time Apify and on-chain ingestion, production position-taking against live markets.'],
  ['Q4 2026', 'Phase 3 — Multi-Protocol', 'Polymarket, Umia Protocol native markets. Cross-protocol track record.'],
  ['Q1 2027', 'Phase 4 — Treasury Autonomy', 'DAO-governed treasury allocation. Analyst earns protocol revenue on correct predictions.'],
]

export default function LandingPage() {
  const tr = getTrackRecord()
  const latest = getLatestMemo()

  return (
    <div>
      {/* Hero */}
      <section className="px-6 py-24" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="mx-auto" style={{ maxWidth: 780 }}>
          {/* Hero logo */}
          <div className="mb-8">
            <HeroLogo />
          </div>

          {/* Label */}
          <div
            className="mono mb-5 inline-flex items-center gap-2 rounded-full px-3 py-1 text-11 uppercase tracking-widest"
            style={{
              background: 'var(--accent-soft)',
              color: 'var(--accent)',
              border: '1px solid rgba(61,224,165,0.2)',
              letterSpacing: '0.08em',
            }}
          >
            <span
              style={{
                width: 6, height: 6, borderRadius: '50%',
                background: 'var(--accent)', flexShrink: 0,
                display: 'inline-block',
              }}
              className="live-dot"
            />
            Mochifi · Research Memo System
          </div>

          {/* Headline */}
          <h1
            className="mb-5 leading-tight"
            style={{ fontSize: 44, lineHeight: 1.1, letterSpacing: '-0.03em' }}
          >
            <span
              style={{
                backgroundImage: 'linear-gradient(90deg, #3DE0A5 0%, #60A5FA 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              Bloomberg Terminal
            </span>
            <br />
            <span style={{ color: 'var(--fg)' }}>for futarchic governance.</span>
          </h1>

          <p className="mb-8 text-15 leading-relaxed" style={{ color: 'var(--fg-muted)', maxWidth: '58ch' }}>
            An autonomous research analyst that reads every signal in a decision
            market, publishes its memo, and bets its own treasury on the outcome.
          </p>

          <div className="flex flex-wrap gap-3">
            <Link href="/memos" className="btn-primary">
              View Track Record
              <ArrowRight size={14} />
            </Link>
            <Link
              href={latest ? `/memos/${latest.market_id}` : '/memos'}
              className="btn-ghost"
            >
              Read latest memo
            </Link>
          </div>
        </div>
      </section>

      {/* Latest verdict bar — product as hero */}
      {latest && (
        <section
          className="border-b px-6 py-8"
          style={{ borderColor: 'var(--border)', background: 'var(--surface)' }}
        >
          <div className="mx-auto" style={{ maxWidth: 880 }}>
            <div
              className="mono mb-3 text-10 uppercase tracking-widest"
              style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
            >
              Latest Memo · {latest.market_metadata.title}
            </div>
            <VerdictBar memo={latest} />
            <div className="mt-3 text-right">
              <Link
                href={`/memos/${latest.market_id}`}
                className="mono text-12 transition-opacity hover:opacity-70"
                style={{ color: 'var(--accent)', textDecoration: 'none' }}
              >
                Read full memo →
              </Link>
            </div>
          </div>
        </section>
      )}

      {/* The Problem */}
      <section
        className="border-b px-6 py-16"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="mx-auto" style={{ maxWidth: 660 }}>
          <div
            className="mono mb-6 text-11 uppercase tracking-widest"
            style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
          >
            The Problem
          </div>
          {PROBLEM.split('\n\n').map((para, i) => (
            <p
              key={i}
              className="mb-5 text-14 leading-relaxed"
              style={{ color: 'var(--fg-muted)' }}
            >
              {para}
            </p>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section className="px-6 py-16" style={{ borderBottom: '1px solid var(--border)' }}>
        <div className="mx-auto" style={{ maxWidth: 960 }}>
          <div className="mono mb-8 text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>
            How It Works
          </div>
          <div className="grid grid-cols-4 gap-5">
            {HOW_IT_WORKS.map(([step, desc], i) => (
              <div key={i} className="how-card">
                <div
                  className="mono text-11 font-semibold"
                  style={{
                    color: 'var(--accent)',
                    background: 'var(--accent-soft)',
                    borderRadius: 99,
                    padding: '2px 10px',
                    display: 'inline-block',
                    letterSpacing: '0.04em',
                  }}
                >
                  {step}
                </div>
                <p className="text-13 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>
                  {desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Track record preview */}
      <section
        className="border-b px-6 py-16"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="mx-auto" style={{ maxWidth: 1100 }}>
          <div className="mb-6 flex items-center justify-between">
            <div
              className="mono text-11 uppercase tracking-widest"
              style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
            >
              Track Record
            </div>
            <Link
              href="/memos"
              className="mono text-12 transition-opacity hover:opacity-70"
              style={{ color: 'var(--accent)', textDecoration: 'none' }}
            >
              View all →
            </Link>
          </div>
          <div className="mb-6">
            <TrackRecordStrip tr={tr} />
          </div>
          <div
            className="rounded border p-5"
            style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}
          >
            <MemoTable memos={tr.memos} limit={5} />
          </div>
        </div>
      </section>

      {/* Why this is a venture */}
      <section
        className="border-b px-6 py-16"
        style={{ borderColor: 'var(--border)', background: 'var(--surface)' }}
      >
        <div className="mx-auto" style={{ maxWidth: 660 }}>
          <div
            className="mono mb-6 text-11 uppercase tracking-widest"
            style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
          >
            Why This Is a Venture
          </div>
          {[
            `The Umia Analyst Agent earns protocol revenue when its positions are correct. A portion of every winning P&L accrues to a DAO-governed treasury. Token holders vote on capital allocation, risk parameters, and which markets the agent covers. The analyst's track record is the product's moat.`,
            `Unlike AI advisory products that sell subscriptions, this system puts its money where its output is. Every memo carries a verifiable on-chain position. The audit trail is public. Incorrect analysis costs the treasury — correct analysis builds it. This alignment between model output and financial consequence is the core incentive design.`,
            `As futarchic governance scales across DeFi protocols, the demand for professional-quality market analysis scales with it. The Umia Analyst is the first institutional-grade analyst purpose-built for this market structure.`,
          ].map((p, i) => (
            <p
              key={i}
              className="mb-5 text-14 leading-relaxed"
              style={{ color: 'var(--fg-muted)' }}
            >
              {p}
            </p>
          ))}
        </div>
      </section>

      {/* Roadmap */}
      <section
        className="border-b px-6 py-16"
        style={{ borderColor: 'var(--border)' }}
      >
        <div className="mx-auto" style={{ maxWidth: 760 }}>
          <div
            className="mono mb-8 text-11 uppercase tracking-widest"
            style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}
          >
            Roadmap
          </div>
          <div className="space-y-5">
            {ROADMAP.map(([date, phase, desc], i) => (
              <div
                key={i}
                className="flex gap-6 border-b pb-5"
                style={{ borderColor: 'var(--border-soft)' }}
              >
                <div className="w-20 flex-shrink-0">
                  <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>
                    {date}
                  </span>
                </div>
                <div>
                  <div
                    className="mb-1 text-13 font-semibold"
                    style={{ color: 'var(--fg)' }}
                  >
                    {phase}
                  </div>
                  <div className="text-13" style={{ color: 'var(--fg-muted)' }}>
                    {desc}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        className="px-6 py-8"
        style={{ borderTop: '1px solid var(--border)' }}
      >
        <div
          className="mono mx-auto flex flex-wrap gap-6 text-12"
          style={{ maxWidth: 880, color: 'var(--fg-faint)' }}
        >
          <span>Mochifi · v1.0</span>
          <span>Built for Umia Protocol Hackathon 2026</span>
          <Link
            href="/memos"
            style={{ color: 'var(--fg-faint)', textDecoration: 'none' }}
          >
            Memo Archive
          </Link>
          <Link
            href="/live"
            style={{ color: 'var(--fg-faint)', textDecoration: 'none' }}
          >
            Live Watch
          </Link>
        </div>
      </footer>
    </div>
  )
}
