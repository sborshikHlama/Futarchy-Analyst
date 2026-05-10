'use client'

import { signIn } from 'next-auth/react'
import { useMetaMaskAuth } from '@/hooks/useMetaMaskAuth'
import Image from 'next/image'
import { useState } from 'react'

const btnBase: React.CSSProperties = {
  width: '100%',
  padding: '14px 24px',
  border: 'none',
  borderRadius: 10,
  fontSize: 15,
  fontWeight: 600,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: 12,
  transition: 'opacity 0.2s',
  marginBottom: 12,
  fontFamily: 'Inter, sans-serif',
}

export default function SignInPage() {
  const { connectAndSign, loading: walletLoading, error: walletError } = useMetaMaskAuth()
  const [twitterLoading, setTwitterLoading] = useState(false)

  async function handleMetaMask() {
    const result = await connectAndSign()
    if (result?.success) window.location.href = '/'
  }

  return (
    <div style={{
      minHeight: '100vh', background: '#0d1117',
      display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: 24,
    }}>
      <div style={{
        background: '#161b22', border: '1px solid #21262d',
        borderRadius: 16, padding: '48px 40px',
        width: '100%', maxWidth: 400, textAlign: 'center',
      }}>
        {/* Logo */}
        <div style={{ marginBottom: 36 }}>
          <Image src="/Mochifi_logo.png" alt="Mochifi" width={56} height={56}
                 style={{ borderRadius: 14, marginBottom: 16 }} />
          <h1 style={{ color: '#fff', fontSize: 22, fontWeight: 700,
                       margin: 0, fontFamily: 'Outfit, sans-serif',
                       letterSpacing: '-0.02em' }}>
            Sign in to Mochifi
          </h1>
          <p style={{ color: '#8b949e', fontSize: 14, marginTop: 8 }}>
            Bloomberg Terminal for futarchic governance
          </p>
        </div>

        {/* MetaMask */}
        <button
          onClick={handleMetaMask}
          disabled={walletLoading}
          style={{ ...btnBase, background: '#F6851B', color: '#fff',
                   opacity: walletLoading ? 0.7 : 1 }}
          onMouseEnter={e => { if (!walletLoading) e.currentTarget.style.opacity = '0.85' }}
          onMouseLeave={e => { e.currentTarget.style.opacity = walletLoading ? '0.7' : '1' }}
        >
          {/* MetaMask fox outline */}
          <svg width="22" height="20" viewBox="0 0 212 189" fill="none">
            <polygon points="204,0 114,66 130,28" fill="#E2761B"/>
            <polygon points="8,0 97,67 82,28" fill="#E4761B"/>
            <polygon points="174,136 150,172 199,185 212,137" fill="#E4761B"/>
            <polygon points="0,137 13,185 62,172 38,136" fill="#E4761B"/>
            <polygon points="59,82 46,101 95,103 93,50" fill="#E4761B"/>
            <polygon points="153,82 119,50 117,103 166,101" fill="#E4761B"/>
            <polygon points="62,172 91,158 66,138" fill="#E4761B"/>
            <polygon points="121,158 150,172 146,138" fill="#E4761B"/>
          </svg>
          {walletLoading ? 'Connecting…' : 'Connect MetaMask'}
        </button>

        {walletError && (
          <p style={{ color: '#f87171', fontSize: 12, marginBottom: 12,
                      textAlign: 'left', lineHeight: 1.5 }}>
            ⚠ {walletError}
          </p>
        )}

        {/* Twitter / X */}
        <button
          onClick={() => { setTwitterLoading(true); signIn('twitter', { callbackUrl: '/' }) }}
          disabled={twitterLoading}
          style={{ ...btnBase, background: '#000', color: '#fff',
                   border: '1px solid #333',
                   opacity: twitterLoading ? 0.7 : 1 }}
          onMouseEnter={e => { if (!twitterLoading) e.currentTarget.style.opacity = '0.8' }}
          onMouseLeave={e => { e.currentTarget.style.opacity = twitterLoading ? '0.7' : '1' }}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
            <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.748l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
          </svg>
          {twitterLoading ? 'Redirecting…' : 'Continue with X (Twitter)'}
        </button>

        {/* Divider */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, margin: '8px 0 20px' }}>
          <div style={{ flex: 1, height: 1, background: '#21262d' }} />
          <span style={{ color: '#8b949e', fontSize: 12 }}>or</span>
          <div style={{ flex: 1, height: 1, background: '#21262d' }} />
        </div>

        {/* Google */}
        <button
          onClick={() => signIn('google', { callbackUrl: '/' })}
          style={{ ...btnBase, background: '#fff', color: '#0d1117', marginBottom: 0 }}
          onMouseEnter={e => { e.currentTarget.style.opacity = '0.9' }}
          onMouseLeave={e => { e.currentTarget.style.opacity = '1' }}
        >
          <svg width="18" height="18" viewBox="0 0 18 18">
            <path fill="#4285F4" d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 002.38-5.88c0-.57-.05-.66-.15-1.18z"/>
            <path fill="#34A853" d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2a4.8 4.8 0 01-7.18-2.54H1.83v2.07A8 8 0 008.98 17z"/>
            <path fill="#FBBC05" d="M4.5 10.52a4.8 4.8 0 010-3.04V5.41H1.83a8 8 0 000 7.18l2.67-2.07z"/>
            <path fill="#EA4335" d="M8.98 4.18c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 001.83 5.4L4.5 7.49a4.77 4.77 0 014.48-3.3z"/>
          </svg>
          Continue with Google
        </button>

        <p style={{ color: '#8b949e', fontSize: 12, marginTop: 24, lineHeight: 1.6 }}>
          MetaMask login creates a wallet-linked account.
          <br />Free plan includes 3 memos/month.
        </p>
      </div>
    </div>
  )
}
