import type { Metadata } from 'next'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import './globals.css'
import Nav from '@/components/Nav'
import Footer from '@/components/Footer'
import Providers from '@/components/Providers'

export const metadata: Metadata = {
  title: 'Mochifi',
  description: 'Bloomberg Terminal for futarchic governance',
  themeColor: '#0d1117',
  icons: { icon: '/Mochifi_logo.png' },
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const session = await getServerSession(authOptions)

  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
          rel="stylesheet"
        />
        <link rel="icon" href="/Mochifi_logo.png" type="image/png" />
      </head>
      <body>
        <Providers session={session}>
          <Nav />
          <main className="fade-in main-content">{children}</main>
          <Footer />
        </Providers>
      </body>
    </html>
  )
}
