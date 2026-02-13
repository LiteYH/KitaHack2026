import type { Metadata } from 'next'
import { Space_Grotesk } from 'next/font/google'

import './globals.css'

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
  weight: ['300', '400', '500', '600', '700'],
})

export const metadata: Metadata = {
  title: 'BossolutionAI - AI Marketing Assistant',
  description: 'AI-Powered Marketing and Advertisement Platform for SMEs. Automate content creation, competitor analysis, and campaign optimization.',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${spaceGrotesk.variable} font-sans antialiased`}>{children}</body>
    </html>
  )
}
