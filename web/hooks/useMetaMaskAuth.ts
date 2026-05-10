'use client'

import { useState, useEffect } from 'react'
import { SiweMessage } from 'siwe'

declare global {
  interface Window {
    ethereum?: {
      request: (args: { method: string; params?: unknown[] }) => Promise<unknown>
      on: (event: string, handler: (...args: unknown[]) => void) => void
      removeListener: (event: string, handler: (...args: unknown[]) => void) => void
      isMetaMask?: boolean
    }
  }
}

export function useMetaMaskAuth() {
  const [address, setAddress]       = useState<string | null>(null)
  const [isConnected, setConnected] = useState(false)
  const [loading, setLoading]       = useState(false)
  const [error, setError]           = useState<string | null>(null)

  // Restore connected address on mount
  useEffect(() => {
    if (!window.ethereum) return
    window.ethereum
      .request({ method: 'eth_accounts' })
      .then((accounts) => {
        const list = accounts as string[]
        if (list.length > 0) { setAddress(list[0]); setConnected(true) }
      })
      .catch(() => {})

    const handleAccountsChanged = (accounts: unknown) => {
      const list = accounts as string[]
      if (list.length === 0) { setAddress(null); setConnected(false) }
      else { setAddress(list[0]); setConnected(true) }
    }
    window.ethereum.on('accountsChanged', handleAccountsChanged)
    return () => window.ethereum?.removeListener('accountsChanged', handleAccountsChanged)
  }, [])

  async function connectAndSign() {
    setLoading(true)
    setError(null)

    try {
      if (!window.ethereum) throw new Error('MetaMask is not installed')

      // 1. Request accounts
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' }) as string[]
      const addr = accounts[0]

      // 2. Get chain id
      const chainIdHex = await window.ethereum.request({ method: 'eth_chainId' }) as string
      const chainId = parseInt(chainIdHex, 16)

      // 3. Get nonce from server
      const nonceRes = await fetch('/api/auth/wallet/nonce')
      const { nonce } = await nonceRes.json()

      // 4. Build SIWE message
      const message = new SiweMessage({
        domain:    window.location.host,
        address:   addr,
        statement: 'Sign in to Mochifi — Bloomberg Terminal for futarchic governance.',
        uri:       window.location.origin,
        version:   '1',
        chainId,
        nonce,
      })
      const prepared = message.prepareMessage()

      // 5. Sign with MetaMask (personal_sign)
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [prepared, addr],
      }) as string

      // 6. Verify on server
      const verifyRes = await fetch('/api/auth/wallet/verify', {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify({ message, signature }),
      })
      const data = await verifyRes.json()
      if (!data.success) throw new Error(data.error ?? 'Verification failed')

      setAddress(addr)
      setConnected(true)
      return data
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Connection failed'
      // Suppress user-rejected errors
      if (!msg.toLowerCase().includes('rejected') && !msg.toLowerCase().includes('denied') && !msg.includes('4001')) {
        setError(msg)
      }
      return null
    } finally {
      setLoading(false)
    }
  }

  function disconnect() {
    setAddress(null)
    setConnected(false)
  }

  return { address, isConnected, loading, error, connectAndSign, disconnect }
}
