import { notFound } from 'next/navigation'
import { getMemo } from '@/lib/memos'
import MemoDetailClient from './MemoDetailClient'

export async function generateStaticParams() {
  const { getAllMemos } = await import('@/lib/memos')
  return getAllMemos().map((m) => ({ id: m.market_id }))
}

export default async function MemoDetailPage({
  params,
}: {
  params: { id: string }
}) {
  const memo = getMemo(params.id)
  if (!memo) notFound()

  return <MemoDetailClient memo={memo} />
}
