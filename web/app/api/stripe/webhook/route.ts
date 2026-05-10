import { NextRequest, NextResponse } from 'next/server'
import { stripe } from '@/lib/stripe'
import { prisma } from '@/lib/prisma'
import type Stripe from 'stripe'

// Disable body parsing — Stripe needs the raw body to verify signature
export const config = { api: { bodyParser: false } }

export async function POST(req: NextRequest) {
  const body      = await req.text()
  const signature = req.headers.get('stripe-signature')!

  let event: Stripe.Event
  try {
    event = stripe.webhooks.constructEvent(body, signature, process.env.STRIPE_WEBHOOK_SECRET!)
  } catch {
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 })
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed': {
        const cs  = event.data.object as Stripe.CheckoutSession
        const sub = await stripe.subscriptions.retrieve(cs.subscription as string)
        await prisma.user.update({
          where: { stripeCustomerId: cs.customer as string },
          data: {
            subscriptionId:     sub.id,
            subscriptionStatus: sub.status,
            plan:               'pro',
            currentPeriodEnd:   new Date(sub.current_period_end * 1000),
          },
        })
        break
      }
      case 'customer.subscription.updated': {
        const sub = event.data.object as Stripe.Subscription
        await prisma.user.update({
          where: { stripeCustomerId: sub.customer as string },
          data: {
            subscriptionStatus: sub.status,
            plan:               sub.status === 'active' ? 'pro' : 'free',
            currentPeriodEnd:   new Date(sub.current_period_end * 1000),
          },
        })
        break
      }
      case 'customer.subscription.deleted': {
        const sub = event.data.object as Stripe.Subscription
        await prisma.user.update({
          where: { stripeCustomerId: sub.customer as string },
          data: {
            subscriptionStatus: 'canceled',
            plan:               'free',
            subscriptionId:     null,
          },
        })
        break
      }
    }
  } catch (err) {
    console.error('Webhook handler error:', err)
    return NextResponse.json({ error: 'Webhook processing failed' }, { status: 500 })
  }

  return NextResponse.json({ received: true })
}
