'use client'

import Link from 'next/link'
import Image from 'next/image'
import { usePathname } from 'next/navigation'
import { useState, useEffect, useRef } from 'react'
import { useSession, signIn, signOut } from 'next-auth/react'
import { useMetaMaskAuth } from '@/hooks/useMetaMaskAuth'
import GlitchLogo from './GlitchLogo'
import { LogoBadge } from './Logo'

const LINKS = [
  { href: '/',        label: 'Home' },
  { href: '/memos',   label: 'Memos' },
  { href: '/live',    label: 'Live Watch' },
  { href: '/track',   label: 'Track Record' },
  { href: '/pricing', label: 'Pricing' },
]

function AuthButton() {
  const { data: session, status } = useSession()
  const { address, isConnected, disconnect } = useMetaMaskAuth()
  const [menuOpen, setMenuOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setMenuOpen(false)
    }
    if (menuOpen) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [menuOpen])

  if (status === 'loading') {
    return <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.06)' }} />
  }

  // Wallet connected, no NextAuth session
  if (isConnected && address && !session) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ width: 7, height: 7, borderRadius: '50%', background: '#3DE0A5', flexShrink: 0 }} />
        <span style={{ fontSize: 12, color: '#8b949e', fontFamily: 'JetBrains Mono, monospace' }}>
          {address.slice(0, 6)}…{address.slice(-4)}
        </span>
        <button
          onClick={() => disconnect()}
          style={{
            background: 'transparent', border: '1px solid #21262d',
            color: '#8b949e', padding: '5px 10px', borderRadius: 8,
            fontSize: 12, cursor: 'pointer', transition: 'color 0.15s, border-color 0.15s',
          }}
          onMouseEnter={e => {
            (e.currentTarget as HTMLElement).style.color = '#f87171'
            ;(e.currentTarget as HTMLElement).style.borderColor = 'rgba(248,113,113,0.4)'
          }}
          onMouseLeave={e => {
            (e.currentTarget as HTMLElement).style.color = '#8b949e'
            ;(e.currentTarget as HTMLElement).style.borderColor = '#21262d'
          }}
        >
          Disconnect
        </button>
      </div>
    )
  }

  // NextAuth session (Google / Twitter)
  if (session) {
    const walletLinked = session.user.walletAddress
    return (
      <div ref={ref} style={{ position: 'relative' }}>
        <button
          onClick={() => setMenuOpen(v => !v)}
          style={{ display: 'flex', alignItems: 'center', gap: 8, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
        >
          {session.user.plan === 'pro' && (
            <span style={{ fontSize: 10, padding: '2px 7px', borderRadius: 20, background: 'rgba(61,224,165,0.12)', color: '#3DE0A5', fontWeight: 600, fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.04em' }}>
              PRO
            </span>
          )}
          {walletLinked && (
            <span style={{ fontSize: 11, color: '#8b949e', fontFamily: 'JetBrains Mono, monospace' }}>
              {walletLinked.slice(0, 6)}…
            </span>
          )}
          <Image
            src={session.user.image ?? '/Mochifi_logo.png'}
            alt={session.user.name ?? 'User'}
            width={34} height={34}
            style={{ borderRadius: '50%', border: '2px solid rgba(61,224,165,0.3)' }}
          />
        </button>

        {menuOpen && (
          <div style={{ position: 'absolute', top: 44, right: 0, zIndex: 200, background: '#161b22', border: '1px solid #21262d', borderRadius: 12, padding: '8px 0', minWidth: 192, boxShadow: '0 8px 32px rgba(0,0,0,0.4)', animation: 'slideDown 0.15s ease-out' }}>
            <div style={{ padding: '10px 16px 8px', borderBottom: '1px solid #21262d' }}>
              <div style={{ color: '#ffffff', fontSize: 13, fontWeight: 500 }}>{session.user.name}</div>
              <div style={{ color: '#8b949e', fontSize: 12, marginTop: 2 }}>{session.user.email}</div>
              {walletLinked && (
                <div style={{ color: '#3DE0A5', fontSize: 11, marginTop: 4, fontFamily: 'JetBrains Mono, monospace' }}>
                  {walletLinked.slice(0, 6)}…{walletLinked.slice(-4)}
                </div>
              )}
            </div>
            {[{ label: 'Pricing', href: '/pricing' }].map(item => (
              <Link key={item.href} href={item.href} onClick={() => setMenuOpen(false)}
                style={{ display: 'block', padding: '10px 16px', color: '#8b949e', textDecoration: 'none', fontSize: 14, transition: 'color 0.15s' }}
                onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#ffffff' }}
                onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#8b949e' }}
              >
                {item.label}
              </Link>
            ))}
            <button
              onClick={() => { setMenuOpen(false); signOut() }}
              style={{ display: 'block', width: '100%', padding: '10px 16px', color: '#8b949e', background: 'none', border: 'none', textAlign: 'left', fontSize: 14, cursor: 'pointer', transition: 'color 0.15s' }}
              onMouseEnter={e => { (e.currentTarget as HTMLElement).style.color = '#f87171' }}
              onMouseLeave={e => { (e.currentTarget as HTMLElement).style.color = '#8b949e' }}
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    )
  }

  // Not signed in
  return (
    <button
      onClick={() => signIn()}
      style={{ padding: '8px 18px', borderRadius: 20, background: '#3DE0A5', color: '#0d1117', border: 'none', fontWeight: 600, fontSize: 13, cursor: 'pointer', transition: 'opacity 0.2s', fontFamily: 'Outfit, sans-serif', whiteSpace: 'nowrap' }}
      onMouseEnter={e => { (e.currentTarget as HTMLElement).style.opacity = '0.85' }}
      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.opacity = '1' }}
    >
      Sign in
    </button>
  )
}

export default function Nav() {
  const path = usePathname()
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) setOpen(false)
    }
    if (open) document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  return (
    <div ref={menuRef}>
      <nav
        className="no-print"
        style={{
          position: 'fixed', top: 0, left: 0, right: 0, zIndex: 100, height: 72,
          background: 'rgba(21, 27, 43, 0.85)',
          backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
          borderBottom: '1px solid #21262d',
        }}
      >
        <div
          className="mx-auto flex items-center justify-between h-full"
          style={{ maxWidth: 1200, padding: '0 32px' }}
        >
          {/* Logo */}
          <Link href="/" style={{ textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 8, flexShrink: 0, whiteSpace: 'nowrap' }}>
            <GlitchLogo />
            <LogoBadge />
          </Link>

          {/* Desktop nav */}
          <div className="nav-desktop flex items-center gap-1">
            {LINKS.map(l => {
              const active = l.href === '/' ? path === '/' : path === l.href || path.startsWith(l.href + '/')
              return (
                <Link
                  key={l.href}
                  href={l.href}
                  style={{
                    fontFamily: 'Inter, sans-serif',
                    fontWeight: active ? 500 : 400, fontSize: 13,
                    padding: '5px 14px', borderRadius: 9999,
                    textDecoration: 'none', transition: 'color 0.2s',
                    color: active ? '#ffffff' : '#8b949e',
                  }}
                  onMouseEnter={e => { if (!active) (e.currentTarget as HTMLElement).style.color = '#ffffff' }}
                  onMouseLeave={e => { if (!active) (e.currentTarget as HTMLElement).style.color = '#8b949e' }}
                >
                  {l.label}
                </Link>
              )
            })}
            <div style={{ marginLeft: 12 }}>
              <AuthButton />
            </div>
          </div>

          {/* Burger */}
          <button
            className="nav-burger"
            aria-label="Toggle menu"
            onClick={() => setOpen(!open)}
            style={{
              background: 'none', border: 'none', cursor: 'pointer',
              width: 44, height: 44, display: 'none',
              alignItems: 'center', justifyContent: 'center',
              marginRight: -10, color: '#ffffff',
            }}
          >
            {open ? (
              <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1={18} y1={6} x2={6} y2={18} /><line x1={6} y1={6} x2={18} y2={18} />
              </svg>
            ) : (
              <svg width={24} height={24} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <line x1={3} y1={6} x2={21} y2={6} /><line x1={3} y1={12} x2={21} y2={12} /><line x1={3} y1={18} x2={21} y2={18} />
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
            position: 'fixed', top: 72, left: 0, right: 0, zIndex: 99,
            background: '#0d1117', borderBottom: '1px solid #21262d',
            padding: '0 24px', animation: 'slideDown 0.2s ease-out',
          }}
        >
          {LINKS.map((l, i) => {
            const active = l.href === '/' ? path === '/' : path === l.href || path.startsWith(l.href + '/')
            const isLast = i === LINKS.length - 1
            return (
              <Link
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                style={{
                  display: 'flex', alignItems: 'center', height: 48,
                  textDecoration: 'none', color: active ? '#ffffff' : '#8b949e',
                  fontFamily: 'Inter, sans-serif', fontWeight: active ? 500 : 400,
                  fontSize: 14, borderBottom: isLast ? 'none' : '1px solid #21262d',
                }}
              >
                {l.label}
              </Link>
            )
          })}
          <div style={{ padding: '16px 0', borderTop: '1px solid #21262d' }}>
            <AuthButton />
          </div>
        </div>
      )}
    </div>
  )
}
