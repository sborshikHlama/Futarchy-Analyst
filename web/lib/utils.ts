import type { SourceWeight } from './types'

export function buildSourceIndex(
  sourceWeights: Record<string, SourceWeight>
): Record<string, string> {
  const keys = Object.keys(sourceWeights)
  const index: Record<string, string> = {}
  keys.forEach((k, i) => {
    index[k] = `S${i + 1}`
  })
  return index
}
