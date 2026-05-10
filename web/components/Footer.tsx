'use client'

import Link from 'next/link'
import Image from 'next/image'

const NAV_LINKS = [
  { href: '/', label: 'Home' },
  { href: '/memos', label: 'Memos' },
  { href: '/live', label: 'Live Watch' },
  { href: '/track', label: 'Track Record' },
]

const SOCIAL = [
  {
    label: 'Twitter',
    href: 'https://x.com/mochifi',
    icon: (
      <svg width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
        <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-4.714-6.231-5.401 6.231H2.742l7.733-8.835L1.254 2.25H8.08l4.254 5.622L18.244 2.25zm-1.161 17.52h1.833L7.084 4.126H5.117L17.083 19.77z" />
      </svg>
    ),
  },
  {
    label: 'GitHub',
    href: 'https://github.com/sborshikHlama/Futarchy-Analyst',
    icon: (
      <svg width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
      </svg>
    ),
  },
  {
    label: 'Telegram',
    href: 'https://t.me/mochifi',
    icon: (
      <svg width={16} height={16} viewBox="0 0 24 24" fill="currentColor">
        <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
      </svg>
    ),
  },
]

export default function Footer() {
  return (
    <footer
      style={{
        background: '#0d1117',
        borderTop: '1px solid #21262d',
        padding: '48px 24px 32px',
      }}
    >
      <div
        className="footer-inner"
        style={{ maxWidth: 1200, margin: '0 auto' }}
      >
        {/* Left */}
        <div className="footer-col">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
            <Image
              src="/Mochifi_logo.png"
              alt="Mochifi"
              width={28}
              height={28}
              style={{ borderRadius: 8, objectFit: 'contain' }}
            />
            <span
              style={{
                fontFamily: 'Outfit, sans-serif',
                fontWeight: 700,
                fontSize: 15,
                color: '#ffffff',
              }}
            >
              Mochifi
            </span>
          </div>
          <p
            style={{
              fontFamily: 'Inter, sans-serif',
              fontSize: 13,
              color: '#8b949e',
              lineHeight: 1.6,
              marginBottom: 16,
              maxWidth: 260,
            }}
          >
            Bloomberg Terminal for futarchic governance.
          </p>
          <p style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11, color: '#8b949e' }}>
            © 2026 Mochifi · Built at ETH Prague
          </p>
        </div>

        {/* Center */}
        <div className="footer-col">
          <div
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              color: '#8b949e',
              marginBottom: 16,
            }}
          >
            Navigation
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {NAV_LINKS.map((l) => (
              <Link
                key={l.href}
                href={l.href}
                style={{
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  color: '#8b949e',
                  textDecoration: 'none',
                  transition: 'color 0.2s',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#ffffff' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#8b949e' }}
              >
                {l.label}
              </Link>
            ))}
          </div>
        </div>

        {/* Right */}
        <div className="footer-col">
          <div
            style={{
              fontFamily: 'JetBrains Mono, monospace',
              fontSize: 12,
              textTransform: 'uppercase',
              letterSpacing: '0.1em',
              color: '#8b949e',
              marginBottom: 16,
            }}
          >
            Community
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {SOCIAL.map((s) => (
              <a
                key={s.label}
                href={s.href}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 8,
                  fontFamily: 'Inter, sans-serif',
                  fontSize: 13,
                  color: '#8b949e',
                  textDecoration: 'none',
                  transition: 'color 0.2s',
                  cursor: 'pointer',
                }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#ffffff' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#8b949e' }}
              >
                {s.icon}
                {s.label}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  )
}
