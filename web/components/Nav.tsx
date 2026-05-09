'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { NavLogo, LogoBadge } from './Logo'

const LINKS = [
  { href: '/',      label: 'Home' },
  { href: '/memos', label: 'Memos' },
  { href: '/live',  label: 'Live Watch' },
  { href: '/track', label: 'Track Record' },
]

export default function Nav() {
  const path = usePathname()

  return (
    <nav
      className="no-print sticky top-0 z-50"
      style={{
        background: 'rgba(21, 27, 43, 0.72)',
        backdropFilter: 'blur(12px)',
        WebkitBackdropFilter: 'blur(12px)',
        borderBottom: '1px solid rgba(255,255,255,0.06)',
      }}
    >
      <div
        className="mx-auto flex h-14 items-center justify-between px-6"
        style={{ maxWidth: 1200 }}
      >
        {/* Logo */}
        <Link href="/" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8, flexShrink: 0, whiteSpace: 'nowrap' }}>
          <NavLogo />
          <LogoBadge />
        </Link>

        {/* Nav links */}
        <div className="flex items-center gap-1">
          {LINKS.map((l) => {
            const active =
              l.href === '/'
                ? path === '/'
                : path === l.href || path.startsWith(l.href + '/')
            return (
              <Link
                key={l.href}
                href={l.href}
                style={{
                  fontFamily: active ? 'Outfit, sans-serif' : 'Inter, sans-serif',
                  fontWeight: active ? 600 : 400,
                  fontSize: 13,
                  padding: '5px 14px',
                  borderRadius: 9999,
                  textDecoration: 'none',
                  transition: 'all 0.18s',
                  color: active ? '#151B2B' : 'var(--fg-muted)',
                  background: active ? 'var(--accent)' : 'transparent',
                  border: active ? 'none' : '1px solid transparent',
                  letterSpacing: active ? '-0.01em' : 0,
                }}
                onMouseEnter={e => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = 'var(--accent)'
                    ;(e.currentTarget as HTMLElement).style.borderColor = 'rgba(61,224,165,0.25)'
                  }
                }}
                onMouseLeave={e => {
                  if (!active) {
                    (e.currentTarget as HTMLElement).style.color = 'var(--fg-muted)'
                    ;(e.currentTarget as HTMLElement).style.borderColor = 'transparent'
                  }
                }}
              >
                {l.label}
              </Link>
            )
          })}
        </div>
      </div>
    </nav>
  )
}
