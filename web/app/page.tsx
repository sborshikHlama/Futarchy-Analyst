import { getTrackRecord, getLatestMemo } from '@/lib/memos'
import HomeClient from './HomeClient'

export default function LandingPage() {
  const tr = getTrackRecord()
  const latest = getLatestMemo()
  return <HomeClient tr={tr} latest={latest} />
}
