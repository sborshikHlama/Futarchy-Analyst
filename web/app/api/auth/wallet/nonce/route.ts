import { NextResponse } from 'next/server'
import { generateNonce } from 'siwe'

// In-memory nonce store — fine for hackathon demo
export const nonces = new Map<string, { nonce: string; expires: number }>()

export async function GET() {
  // Prune expired nonces
  const now = Date.now()
  for (const [key, val] of nonces) {
    if (now > val.expires) nonces.delete(key)
  }

  const nonce   = generateNonce()
  const expires = now + 5 * 60 * 1000 // 5 min TTL
  nonces.set(nonce, { nonce, expires })
  return NextResponse.json({ nonce })
}
