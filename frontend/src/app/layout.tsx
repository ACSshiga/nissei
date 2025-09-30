import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Nissei 工数管理システム',
  description: '工数管理と請求処理のためのシステム',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  )
}