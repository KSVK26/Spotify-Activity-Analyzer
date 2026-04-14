import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Spotify Activity Analyzer',
  description: 'Analyze your Spotify listening habits and share your story',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}