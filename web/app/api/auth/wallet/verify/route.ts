import { NextRequest, NextResponse } from 'next/server'
import { SiweMessage } from 'siwe'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'
import { nonces } from '../nonce/route'

export async function POST(req: NextRequest) {
  const { message, signature } = await req.json()

  // 1. Verify SIWE signature
  const siweMessage = new SiweMessage(message)
  let verification: Awaited<ReturnType<typeof siweMessage.verify>>
  try {
    verification = await siweMessage.verify({ signature })
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  if (!verification.success) {
    return NextResponse.json({ error: 'Signature verification failed' }, { status: 400 })
  }

  // 2. Validate nonce
  const stored = nonces.get(siweMessage.nonce)
  if (!stored || Date.now() > stored.expires) {
    return NextResponse.json({ error: 'Nonce expired or invalid' }, { status: 400 })
  }
  nonces.delete(siweMessage.nonce)

  const walletAddress = siweMessage.address.toLowerCase()

  // 3. Logged-in user → link wallet to existing account
  const session = await getServerSession(authOptions)
  if (session?.user?.id) {
    await prisma.user.update({
      where: { id: session.user.id },
      data:  { walletAddress, walletLinkedAt: new Date() },
    })
    return NextResponse.json({ success: true, action: 'linked', address: walletAddress })
  }

  // 4. No session → find or create wallet-only user
  let user = await prisma.user.findUnique({ where: { walletAddress } })
  if (!user) {
    user = await prisma.user.create({
      data: {
        walletAddress,
        walletLinkedAt: new Date(),
        name: `${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)}`,
        plan: 'free',
      },
    })
  }

  return NextResponse.json({
    success: true,
    action:  'signin',
    address: walletAddress,
    userId:  user.id,
  })
}
