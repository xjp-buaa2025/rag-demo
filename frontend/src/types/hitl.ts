import type { FlatTriple } from './index'

export interface StageStats {
  entities_count: number
  triples_count: number
  relation_breakdown: Record<string, number>
  confidence_histogram: number[]
  bom_coverage_ratio: number | null
  isolated_entities_count: number
  low_confidence_count: number
}

export interface StageIssue {
  severity: 'critical' | 'warning' | 'info'
  title: string
  title_zh: string
  description: string
  suggestion: string
  affected_triple_ids: string[]
}

export interface StageDiff {
  added_triples: FlatTriple[]
  removed_triples: FlatTriple[]
  modified_triples: [FlatTriple, FlatTriple][]
}

export interface StageReport {
  stage: string
  generated_at: string
  stats: StageStats
  issues: StageIssue[]
  diff: StageDiff | null
}

export interface StageStateInfo {
  stage: string
  status: 'idle' | 'running' | 'awaiting_review' | 'approved'
  approved_at?: string
}

export interface BilingualTriple extends FlatTriple {
  head_zh: string
  relation_zh: string
  tail_zh: string
}

export interface ExpertDiff {
  added: FlatTriple[]
  removed_indices: number[]
  modified: { index: number; triple: FlatTriple }[]
}

export interface RerunParams {
  confidence_threshold: number
  gleaning_rounds: number
}
