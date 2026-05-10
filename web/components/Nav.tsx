'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useEffect, useRef } from 'react'
import GlitchLogo from './GlitchLogo'
import { LogoBadge } from './Logo'

const LINKS = [
  { href: '/',      label: 'Home' },
  { href: '/memos', label: 'Memos' },
  { href: '/live',  label: 'Live Watch' },
  { href: '/track', label: 'Track Record' },
]

export default function Nav() {
  const path = usePathname()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    if (open) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div ref={menuRef}>
      <nav
        className="no-print"
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 100,
          height: 64,
          background: 'rgba(21, 27, 43, 0.85)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid #21262d',
        }}
      >
        <div
          className="mx-auto flex items-center justify-between h-full px-6"
          style={{ maxWidth: 1200 }}
        >
          {/* Logo */}
          <Link
            href="/"
            style={{
              textDecoration: 'none',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 8,
              flexShrink: 0,
              whiteSpace: 'nowrap',
            }}
          >
            <GlitchLogo />
            <LogoBadge />
          </Link>

          {/* Desktop nav */}
          <div className="nav-desktop flex items-center gap-1">
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
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: active ? 500 : 400,
                    fontSize: 13,
                    padding: '5px 14px',
                    borderRadius: 9999,
                    textDecoration: 'none',
                    transition: 'color 0.2s',
                    color: active ? '#ffffff' : '#8b949e',
                  }}
                  onMouseEnter={e => {
                    if (!active) (e.currentTarget as HTMLElement).style.color = '#ffffff'
                  }}
                  onMouseLeave={e => {
                    if (!active) (e.currentTarget as HTMLElement).style.color = '#8b949e'
                  }}
                >
                  {l.label}
                </Link>
              )
            })}
            <Link
              href="/track"
              className="nav-cta"
              style={{
                marginLeft: 8,
                background: '#3DE0A5',
                color: '#0d1117',
                fontFamily: 'Outfit, sans-serif',
                fontWeight: 600,
                fontSize: 13,
                padding: '8px 20px',
                borderRadius: 20,
                textDecoration: 'none',
                transition: 'opacity 0.2s',
                whiteSpace: 'nowrap',
              }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.opacity = '0.9' }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.opacity = '1' }}
            >
              View Track Record →
            </Link>
          </div>

          {/* Burger */}
          <button
            className="nav-burger"
            aria-label="Toggle menu"
            onClick={() => setOpen(!open)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: 4,
              color: '#ffffff',
              display: 'none',
            }}
          >
            {open ? (
              <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1={18} y1={6} x2={6} y2={18} />
                <line x1={6} y1={6} x2={18} y2={18} />
              </svg>
            ) : (
              <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1={3} y1={6} x2={21} y2={6} />
                <line x1={3} y1={12} x2={21} y2={12} />
                <line x1={3} y1={18} x2={21} y2={18} />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile drawer */}
      {open && (
        <div
          className="nav-mobile-drawer"
          style={{
            position: 'fixed',
            top: 64,
            left: 0,
            right: 0,
            zIndex: 99,
            background: '#0d1117',
            borderBottom: '1px solid #21262d',
            padding: '0 24px',
            animation: 'slideDown 0.2s ease-out',
          }}
        >
          {LINKS.map((l, i) => {
            const active =
              l.href === '/'
                ? path === '/'
                : path === l.href || path.startsWith(l.href + '/')
            const isLast = i === LINKS.length - 1
            return (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  height: 48,
                  textDecoration: 'none',
                  color: active ? '#ffffff' : '#8b949e',
                  fontFamily: 'Inter, sans-serif',
                  fontWeight: active ? 500 : 400,
                  fontSize: 14,
                  borderBottom: isLast ? 'none' : '1px solid #21262d',
                  transition: 'color 0.2s',
                }}
              >
                {l.label}
              </Link>
            )
          })}
          <div style={{ padding: '12px 0' }}>
            <Link
              href="/track"
              onClick={() => setOpen(false)}
              style={{
                display: 'inline-block',
                background: '#3DE0A5',
                color: '#0d1117',
                fontFamily: 'Outfit, sans-serif',
                fontWeight: 600,
                fontSize: 13,
                padding: '8px 20px',
                borderRadius: 20,
                textDecoration: 'none',
              }}
            >
              View Track Record →
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}
