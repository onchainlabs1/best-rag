import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'RAG + Agent Knowledge Base',
  description: 'Knowledge Base system using RAG with LangGraph agents',
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
