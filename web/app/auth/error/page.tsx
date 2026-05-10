'use client'

import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

const ERRORS: Record<string, string> = {
  Configuration:  'Server configuration error. Please contact support.',
  AccessDenied:   'Access was denied. Please try a different account.',
  Verification:   'The sign-in link has expired. Please request a new one.',
  Default:        'An unexpected error occurred. Please try again.',
}

export default function AuthErrorPage() {
  const params = useSearchParams()
  const error  = params.get('error') ?? 'Default'
  const message = ERRORS[error] ?? ERRORS.Default

  return (
    <div
      style={{
        minHeight: '100vh',
        background: '#0d1117',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: 24,
      }}
    >
      <div
        style={{
          background: '#161b22',
          border: '1px solid #21262d',
          borderRadius: 16,
          padding: '48px 40px',
          width: '100%',
          maxWidth: 400,
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: 40, marginBottom: 16 }}>⚠️</div>
        <h1 style={{ color: '#ffffff', fontSize: 20, fontWeight: 700, marginBottom: 12, fontFamily: 'Outfit, sans-serif' }}>
          Authentication Error
        </h1>
        <p style={{ color: '#8b949e', fontSize: 14, marginBottom: 32, lineHeight: 1.6 }}>
          {message}
        </p>
        <Link
          href="/auth/signin"
          style={{
            display: 'inline-block',
            padding: '12px 28px',
            background: '#3DE0A5',
            color: '#0d1117',
            borderRadius: 10,
            fontWeight: 600,
            fontSize: 14,
            textDecoration: 'none',
            fontFamily: 'Outfit, sans-serif',
          }}
        >
          Try again
        </Link>
      </div>
    </div>
  )
}
