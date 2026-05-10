import { withAuth } from 'next-auth/middleware'
import { NextResponse } from 'next/server'

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token
    const path  = req.nextUrl.pathname

    // Pro-only routes
    const proRoutes = ['/live']
    if (proRoutes.some(r => path.startsWith(r)) && (token as any)?.plan !== 'pro') {
      return NextResponse.redirect(new URL('/pricing', req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      // Live Watch requires login; memos + track are public
      authorized: ({ token, req }) => {
        const path = req.nextUrl.pathname
        if (path.startsWith('/live')) return !!token
        return true
      },
    },
  }
)

export const config = {
  matcher: ['/live/:path*'],
}
