import type { Metadata } from 'next'
import './globals.css'
import Nav from '@/components/Nav'

export const metadata: Metadata = {
  title: 'Umia Analyst Agent',
  description: 'Autonomous research analyst for futarchic decision markets',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Nav />
        <main className="fade-in">{children}</main>
      </body>
    </html>
  )
}
