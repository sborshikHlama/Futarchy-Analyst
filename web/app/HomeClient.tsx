'use client'

import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import { useEffect, useState, useRef } from 'react'
import { motion } from 'framer-motion'
import TrackRecordStrip from '@/components/TrackRecordStrip'
import MemoTable from '@/components/MemoTable'
import VerdictBar from '@/components/memo/VerdictBar'
import { HeroLogo } from '@/components/Logo'
import type { Memo, TrackRecord } from '@/lib/types'

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

const TYPING_TEXT = 'Bloomberg Terminal'

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease: 'easeOut' as const } },
}

function CountUp({ target, decimals = 0, prefix = '', suffix = '' }: { target: number; decimals?: number; prefix?: string; suffix?: string }) {
  const [value, setValue] = useState(0)
  const ref = useRef<HTMLSpanElement>(null)
  const started = useRef(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting && !started.current) {
        started.current = true
        const steps = 40
        const increment = target / steps
        let current = 0
        const t = setInterval(() => {
          current = Math.min(current + increment, target)
          setValue(parseFloat(current.toFixed(decimals)))
          if (current >= target) clearInterval(t)
        }, 1000 / steps)
      }
    }, { threshold: 0.3 })
    obs.observe(el)
    return () => obs.disconnect()
  }, [target, decimals])

  return (
    <span ref={ref} className="mono" style={{ fontSize: 36, fontWeight: 700, color: 'var(--accent)' }}>
      {prefix}{value.toFixed(decimals)}{suffix}
    </span>
  )
}

export default function HomeClient({ tr, latest }: { tr: TrackRecord; latest: Memo | null }) {
  const [displayed, setDisplayed] = useState('')
  const [doneTyping, setDoneTyping] = useState(false)

  useEffect(() => {
    let i = 0
    const t = setInterval(() => {
      setDisplayed(TYPING_TEXT.slice(0, ++i))
      if (i === TYPING_TEXT.length) { clearInterval(t); setDoneTyping(true) }
    }, 50)
    return () => clearInterval(t)
  }, [])

  return (
    <div>
      {/* Hero */}
      <section
        className="px-6 py-24"
        style={{ borderBottom: '1px solid var(--border)', position: 'relative', overflow: 'hidden' }}
      >
        <div className="hero-bg" />
        <div className="mx-auto" style={{ maxWidth: 780, position: 'relative', zIndex: 1 }}>
          <div className="hero-logo-wrap mb-8"><HeroLogo /></div>

          <div
            className="mono mb-5 inline-flex items-center gap-2 rounded-full px-3 py-1 text-11 uppercase tracking-widest"
            style={{ background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid rgba(61,224,165,0.2)', letterSpacing: '0.08em' }}
          >
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--accent)', flexShrink: 0, display: 'inline-block' }} className="live-dot" />
            Mochifi · Research Memo System
          </div>

          <h1 className="mb-5 leading-tight" style={{ fontSize: 44, lineHeight: 1.1, letterSpacing: '-0.03em' }}>
            <span
              className={doneTyping ? 'typing-cursor' : ''}
              style={{
                backgroundImage: 'linear-gradient(90deg, #3DE0A5 0%, #60A5FA 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              {displayed}
            </span>
            <br />
            <span style={{ color: 'var(--fg)' }}>for futarchic governance.</span>
          </h1>

          <p className="mb-8 text-15 leading-relaxed" style={{ color: 'var(--fg-muted)', maxWidth: '58ch' }}>
            An autonomous research analyst that reads every signal in a decision market, publishes its memo, and bets its own treasury on the outcome.
          </p>

          <div className="hero-cta-group flex flex-wrap gap-3">
            <Link href="/memos" className="btn-primary">
              View Track Record <ArrowRight size={14} />
            </Link>
            <Link href={latest ? `/memos/${latest.market_id}` : '/memos'} className="btn-ghost">
              Read latest memo
            </Link>
          </div>
        </div>
      </section>

      {/* Latest verdict */}
      {latest && (
        <motion.section
          className="border-b px-6 py-8"
          style={{ borderColor: 'var(--border)', background: 'var(--surface)' }}
          initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}
        >
          <div className="mx-auto" style={{ maxWidth: 880 }}>
            <div className="mono mb-3 text-10 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>
              Latest Memo · {latest.market_metadata.title}
            </div>
            <VerdictBar memo={latest} />
            <div className="mt-3 text-right">
              <Link href={`/memos/${latest.market_id}`} className="mono text-12 transition-opacity hover:opacity-70" style={{ color: 'var(--accent)', textDecoration: 'none' }}>
                Read full memo →
              </Link>
            </div>
          </div>
        </motion.section>
      )}

      {/* Stats */}
      <motion.section
        className="border-b px-6 py-12"
        style={{ borderColor: 'var(--border)' }}
        initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}
      >
        <div className="mx-auto" style={{ maxWidth: 880 }}>
          <div className="stats-grid">
            {[
              { target: 60, suffix: '%', label: 'Avg Confidence' },
              { target: 3.33, decimals: 2, prefix: '+', suffix: '%', label: 'P3 PnL (resolved YES)' },
              { target: 3.0, decimals: 1, prefix: '+', suffix: '%', label: 'P6 PnL (resolved NO)' },
            ].map((s, i) => (
              <div key={i} className="stat-card">
                <CountUp target={s.target} decimals={s.decimals ?? 0} prefix={s.prefix ?? ''} suffix={s.suffix ?? ''} />
                <span style={{ fontSize: 12, color: 'var(--fg-faint)', marginTop: 4 }}>{s.label}</span>
              </div>
            ))}
            <div className="stat-card">
              <span className="mono" style={{ fontSize: 36, fontWeight: 700, color: 'var(--accent)' }}>2/2</span>
              <span style={{ fontSize: 12, color: 'var(--fg-faint)', marginTop: 4 }}>Resolved Correct</span>
            </div>
          </div>
        </div>
      </motion.section>

      {/* The Problem */}
      <motion.section className="border-b px-6 py-16" style={{ borderColor: 'var(--border)' }} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
        <div className="mx-auto" style={{ maxWidth: 660 }}>
          <div className="mono mb-6 text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>The Problem</div>
          {PROBLEM.split('\n\n').map((para, i) => (
            <p key={i} className="mb-5 text-14 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>{para}</p>
          ))}
        </div>
      </motion.section>

      {/* How It Works */}
      <motion.section className="px-6 py-16" style={{ borderBottom: '1px solid var(--border)' }} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
        <div className="mx-auto" style={{ maxWidth: 960 }}>
          <div className="mono mb-8 text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>How It Works</div>
          <div className="grid grid-cols-4 gap-5">
            {HOW_IT_WORKS.map(([step, desc], i) => (
              <div key={i} className="how-card">
                <div className="mono text-11 font-semibold" style={{ color: 'var(--accent)', background: 'var(--accent-soft)', borderRadius: 99, padding: '2px 10px', display: 'inline-block', letterSpacing: '0.04em' }}>
                  {step}
                </div>
                <p className="text-13 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Track Record */}
      <motion.section className="border-b px-6 py-16" style={{ borderColor: 'var(--border)' }} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
        <div className="mx-auto" style={{ maxWidth: 1100 }}>
          <div className="mb-6 flex items-center justify-between">
            <div className="mono text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>Track Record</div>
            <Link href="/memos" className="mono text-12 transition-opacity hover:opacity-70" style={{ color: 'var(--accent)', textDecoration: 'none' }}>View all →</Link>
          </div>
          <div className="mb-6"><TrackRecordStrip tr={tr} /></div>
          <div className="rounded border p-5" style={{ background: 'var(--surface)', borderColor: 'var(--border)' }}>
            <MemoTable memos={tr.memos} limit={5} />
          </div>
        </div>
      </motion.section>

      {/* Why This Is a Venture */}
      <motion.section className="border-b px-6 py-16" style={{ borderColor: 'var(--border)', background: 'var(--surface)' }} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
        <div className="mx-auto" style={{ maxWidth: 660 }}>
          <div className="mono mb-6 text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>Why This Is a Venture</div>
          {[
            `The Umia Analyst Agent earns protocol revenue when its positions are correct. A portion of every winning P&L accrues to a DAO-governed treasury. Token holders vote on capital allocation, risk parameters, and which markets the agent covers. The analyst's track record is the product's moat.`,
            `Unlike AI advisory products that sell subscriptions, this system puts its money where its output is. Every memo carries a verifiable on-chain position. The audit trail is public. Incorrect analysis costs the treasury — correct analysis builds it. This alignment between model output and financial consequence is the core incentive design.`,
            `As futarchic governance scales across DeFi protocols, the demand for professional-quality market analysis scales with it. The Umia Analyst is the first institutional-grade analyst purpose-built for this market structure.`,
          ].map((p, i) => (
            <p key={i} className="mb-5 text-14 leading-relaxed" style={{ color: 'var(--fg-muted)' }}>{p}</p>
          ))}
        </div>
      </motion.section>

      {/* Roadmap */}
      <motion.section className="border-b px-6 py-16" style={{ borderColor: 'var(--border)' }} initial="hidden" whileInView="visible" viewport={{ once: true }} variants={fadeUp}>
        <div className="mx-auto" style={{ maxWidth: 760 }}>
          <div className="mono mb-8 text-11 uppercase tracking-widest" style={{ color: 'var(--fg-faint)', letterSpacing: '0.08em' }}>Roadmap</div>
          <div className="space-y-5">
            {ROADMAP.map(([date, phase, desc], i) => (
              <div key={i} className="flex gap-6 border-b pb-5" style={{ borderColor: 'var(--border-soft)' }}>
                <div className="w-20 flex-shrink-0">
                  <span className="mono text-12" style={{ color: 'var(--fg-faint)' }}>{date}</span>
                </div>
                <div>
                  <div className="mb-1 text-13 font-semibold" style={{ color: 'var(--fg)' }}>{phase}</div>
                  <div className="text-13" style={{ color: 'var(--fg-muted)' }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </motion.section>
    </div>
  )
}
