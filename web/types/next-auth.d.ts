import NextAuth from 'next-auth'

declare module 'next-auth' {
  interface Session {
    user: {
      id:                 string
      name?:              string | null
      email?:             string | null
      image?:             string | null
      plan:               string
      subscriptionStatus: string | null
      stripeCustomerId:   string | null
      walletAddress?:     string | null
    }
  }
  interface User {
    plan:               string
    subscriptionStatus: string | null
    stripeCustomerId:   string | null
    walletAddress?:     string | null
  }
}
