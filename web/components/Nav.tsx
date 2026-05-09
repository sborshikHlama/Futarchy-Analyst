'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import clsx from 'clsx'

const LINKS = [
  { href: '/',       label: 'Home' },
  { href: '/memos',  label: 'Memos' },
  { href: '/live',   label: 'Live Watch' },
  { href: '/track',  label: 'Track Record' },
]

export default function Nav() {
  const path = usePathname()

  return (
    <nav
      className="no-print sticky top-0 z-50 border-b"
      style={{ background: 'var(--bg)', borderColor: 'var(--border)' }}
    >
      <div className="mx-auto flex h-12 max-w-[1200px] items-center justify-between px-6">
        <Link
          href="/"
          className="flex items-center gap-2"
          style={{ textDecoration: 'none' }}
        >
          <span
            className="font-semibold tracking-tight"
            style={{ color: 'var(--fg)', fontSize: 14 }}
          >
            Umia Analyst
          </span>
          <span
            className="mono rounded px-1.5 py-0.5 text-10"
            style={{
              background: 'var(--accent-soft)',
              color: 'var(--accent)',
              letterSpacing: '0.02em',
            }}
          >
            v1.0
          </span>
        </Link>

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
                className={clsx(
                  'rounded px-3 py-1.5 text-13 transition-colors',
                  active
                    ? 'font-medium'
                    : 'hover:opacity-80'
                )}
                style={{
                  color: active ? 'var(--fg)' : 'var(--fg-muted)',
                  background: active ? 'var(--surface)' : 'transparent',
                  textDecoration: 'none',
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
