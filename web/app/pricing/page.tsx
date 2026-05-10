'use client'

import { useState } from 'react'
import { useSession, signIn } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { PLANS } from '@/lib/plans'

export default function PricingPage() {
  const { data: session } = useSession()
  const router = useRouter()
  const [interval, setIntervalVal] = useState<'month' | 'year'>('month')
  const [loading, setLoading] = useState(false)

  async function handleUpgrade() {
    if (!session) { signIn('google'); return }
    setLoading(true)
    try {
      const res  = await fetch('/api/stripe/checkout', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ interval }),
      })
      const { url, error } = await res.json()
      if (error) throw new Error(error)
      window.location.href = url
    } catch (err) {
      console.error(err)
      setLoading(false)
    }
  }

  const isPro  = session?.user?.plan === 'pro'
  const price  = interval === 'month' ? '$9/mo' : '$79/yr'

  return (
    <div style={{ minHeight: '100vh', background: '#0d1117', padding: '80px 24px 64px' }}>
      <div style={{ maxWidth: 860, margin: '0 auto' }}>

        <h1 style={{
          color: '#ffffff', fontSize: 36, fontWeight: 700,
          textAlign: 'center', marginBottom: 8,
          fontFamily: 'Outfit, sans-serif', letterSpacing: '-0.02em',
        }}>
          Simple pricing
        </h1>
        <p style={{ color: '#8b949e', textAlign: 'center', marginBottom: 40, fontSize: 15 }}>
          Start free. Upgrade when you need real-time signals.
        </p>

        {/* Interval toggle */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 8, marginBottom: 48 }}>
          {(['month', 'year'] as const).map(i => (
            <button
              key={i}
              onClick={() => setIntervalVal(i)}
              style={{
                padding: '8px 20px', borderRadius: 20, cursor: 'pointer',
                background: interval === i ? '#3DE0A5' : 'transparent',
                color:      interval === i ? '#0d1117'  : '#8b949e',
                border:     interval === i ? 'none'     : '1px solid #21262d',
                fontWeight: 600, fontSize: 14, transition: 'all 0.2s',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {i === 'month' ? 'Monthly' : 'Yearly · Save 27%'}
            </button>
          ))}
        </div>

        {/* Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>

          {/* Free */}
          <div style={{
            background: '#161b22', border: '1px solid #21262d',
            borderRadius: 16, padding: '32px 28px',
          }}>
            <div style={{ color: '#8b949e', fontSize: 13, fontWeight: 600,
                          letterSpacing: '0.08em', marginBottom: 16,
                          fontFamily: 'JetBrains Mono, monospace' }}>FREE</div>
            <div style={{ color: '#ffffff', fontSize: 40, fontWeight: 700,
                          marginBottom: 4, fontFamily: 'Outfit, sans-serif' }}>$0</div>
            <div style={{ color: '#8b949e', fontSize: 14, marginBottom: 32 }}>forever</div>
            {PLANS.free.features.map(f => (
              <div key={f} style={{ display: 'flex', alignItems: 'center',
                                    gap: 10, marginBottom: 12 }}>
                <span style={{ color: '#8b949e', fontSize: 14 }}>○</span>
                <span style={{ color: '#8b949e', fontSize: 14, fontFamily: 'Inter, sans-serif' }}>{f}</span>
              </div>
            ))}
            <div style={{ marginTop: 32, padding: '14px', borderRadius: 10,
                          background: 'transparent', border: '1px solid #21262d',
                          color: '#8b949e', fontSize: 15, textAlign: 'center',
                          fontFamily: 'Inter, sans-serif' }}>
              {session ? (isPro ? 'Downgrade' : 'Current plan') : 'Get started free'}
            </div>
          </div>

          {/* Pro */}
          <div style={{
            background: '#161b22',
            border: '1px solid #3DE0A5',
            borderRadius: 16, padding: '32px 28px',
            boxShadow: '0 0 32px rgba(61,224,165,0.06)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center',
                          justifyContent: 'space-between', marginBottom: 16 }}>
              <span style={{ color: '#3DE0A5', fontSize: 13, fontWeight: 600,
                             letterSpacing: '0.08em', fontFamily: 'JetBrains Mono, monospace' }}>PRO</span>
              <span style={{ background: 'rgba(61,224,165,0.1)', color: '#3DE0A5',
                             fontSize: 11, padding: '3px 8px', borderRadius: 20,
                             fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>
                MOST POPULAR
              </span>
            </div>
            <div style={{ color: '#ffffff', fontSize: 40, fontWeight: 700,
                          marginBottom: 4, fontFamily: 'Outfit, sans-serif' }}>{price}</div>
            <div style={{ color: '#8b949e', fontSize: 14, marginBottom: 32 }}>
              billed {interval === 'month' ? 'monthly' : 'annually'}
            </div>
            {PLANS.pro.features.map(f => (
              <div key={f} style={{ display: 'flex', alignItems: 'center',
                                    gap: 10, marginBottom: 12 }}>
                <span style={{ color: '#3DE0A5', fontSize: 14 }}>✓</span>
                <span style={{ color: '#ffffff', fontSize: 14, fontFamily: 'Inter, sans-serif' }}>{f}</span>
              </div>
            ))}
            <button
              onClick={handleUpgrade}
              disabled={loading || isPro}
              style={{
                width: '100%', padding: 14, marginTop: 32, borderRadius: 10,
                background: isPro ? 'rgba(61,224,165,0.15)' : '#3DE0A5',
                border: isPro ? '1px solid #3DE0A5' : 'none',
                color: isPro ? '#3DE0A5' : '#0d1117',
                fontSize: 15, fontWeight: 700,
                cursor: loading || isPro ? 'default' : 'pointer',
                opacity: loading ? 0.8 : 1,
                transition: 'opacity 0.2s',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {isPro ? '✓ Current plan' : loading ? 'Redirecting...' : `Upgrade to Pro →`}
            </button>
          </div>
        </div>

        {/* Mobile grid collapse */}
        <style>{`@media (max-width: 640px) { .pricing-grid { grid-template-columns: 1fr !important; } }`}</style>
      </div>
    </div>
  )
}
