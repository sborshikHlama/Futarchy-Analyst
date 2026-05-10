import { NextRequest, NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { stripe } from '@/lib/stripe'
import { prisma } from '@/lib/prisma'

export async function POST(req: NextRequest) {
  const session = await getServerSession(authOptions)
  if (!session?.user?.email) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const { interval } = await req.json() as { interval: 'month' | 'year' }

  let customerId = session.user.stripeCustomerId
  if (!customerId) {
    const customer = await stripe.customers.create({
      email:    session.user.email,
      name:     session.user.name ?? undefined,
      metadata: { userId: session.user.id },
    })
    customerId = customer.id
    await prisma.user.update({
      where: { id: session.user.id },
      data:  { stripeCustomerId: customerId },
    })
  }

  const priceId = interval === 'year'
    ? process.env.STRIPE_PRICE_YEARLY!
    : process.env.STRIPE_PRICE_MONTHLY!

  const checkoutSession = await stripe.checkout.sessions.create({
    customer:             customerId,
    mode:                 'subscription',
    payment_method_types: ['card'],
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${process.env.NEXTAUTH_URL}/settings?success=true`,
    cancel_url:  `${process.env.NEXTAUTH_URL}/pricing?canceled=true`,
    metadata:    { userId: session.user.id },
  })

  return NextResponse.json({ url: checkoutSession.url })
}
