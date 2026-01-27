import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Academic RAG Assistant',
  description: 'Research paper sentiment analysis tool',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
