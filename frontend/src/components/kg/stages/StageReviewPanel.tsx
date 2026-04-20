import React, { useState, useEffect, useCallback } from 'react'
import { StageReport } from '../../../types'
import {
  getStageReport, approveStage, diagnoseStage,
} from '../../../api/client'
import StageIssueCard from './StageIssueCard'
import TriplesEditor from './TriplesEditor'
import ExpertKnowledgeInput from './ExpertKnowledgeInput'
import ParamTuner, { RerunParams } from './ParamTuner'
import KgViewer from '../KgViewer'

interface Props {
  stageN: 1 | 2
  onApproved: () => void
  onRerun: (params: RerunParams) => void
  rerunning: boolean
}

type ActiveTab = 'issues' | 'graph' | 'triples' | 'knowledge' | 'params'

export default function StageReviewPanel({ stageN, onApproved, onRerun, rerunning }: Props) {
  const [report, setReport] = useState<StageReport | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<ActiveTab>('issues')
  const [diagnosing, setDiagnosing] = useState(false)
  const [diagnosisByIndex, setDiagnosisByIndex] = useState<Record<number, string>>({})
  const [approving, setApproving] = useState(false)
  const [highlightIds, setHighlightIds] = useState<string[]>([])

  const loadReport = useCallback(async () => {
    setLoading(true)
    try {
      const r = await getStageReport(stageN)
      setReport(r)
    } finally {
      setLoading(false)
    }
  }, [stageN])

  useEffect(() => { loadReport() }, [loadReport])

  const handleDiagnose = async () => {
    if (!report) return
    setDiagnosing(true)
    setDiagnosisByIndex({})
    try {
      for await (const frame of diagnoseStage(stageN)) {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const f = frame as any
        if (f.type === 'diagnosis_chunk') {
          const idx = f.issue_index as number
          setDiagnosisByIndex(prev => ({
            ...prev,
            [idx]: (prev[idx] ?? '') + (f.content as string),
          }))
        }
      }
    } finally {
      setDiagnosing(false)
    }
  }

  const handleApprove = async () => {
    setApproving(true)
    try {
      await approveStage(stageN)
      onApproved()
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return <div className="py-4 text-center text-gray-500 text-sm">加载审阅报告...</div>
  }
  if (!report) {
    return <div className="py-4 text-center text-red-500 text-sm">报告加载失败</div>
  }

  const { stats, issues, diff } = report
  const criticalCount = issues.filter(i => i.severity === 'critical').length
  const warningCount = issues.filter(i => i.severity === 'warning').length

  const TABS: { key: ActiveTab; label: string }[] = [
    { key: 'issues', label: `问题清单 (${issues.length})` },
    { key: 'graph', label: 'KG 快照' },
    { key: 'triples', label: '三元组编辑' },
    { key: 'knowledge', label: '领域知识' },
    { key: 'params', label: '参数调整' },
  ]

  return (
    <div className="border border-purple-700/50 rounded-lg bg-gray-900/50 p-4 mt-2">
      {/* 统计卡片行 */}
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="bg-blue-950/40 border border-blue-700/50 rounded px-3 py-1.5 text-xs">
          <span className="text-gray-400">实体</span>
          <span className="ml-2 text-blue-400 font-semibold">{stats.entities_count}</span>
        </div>
        <div className="bg-blue-950/40 border border-blue-700/50 rounded px-3 py-1.5 text-xs">
          <span className="text-gray-400">三元组</span>
          <span className="ml-2 text-blue-400 font-semibold">{stats.triples_count}</span>
        </div>
        {stats.bom_coverage_ratio !== null && (
          <div className={`border rounded px-3 py-1.5 text-xs ${stats.bom_coverage_ratio < 0.4 ? 'bg-red-950/40 border-red-700/50' : 'bg-green-950/40 border-green-700/50'}`}>
            <span className="text-gray-400">BOM覆盖率</span>
            <span className={`ml-2 font-semibold ${stats.bom_coverage_ratio < 0.4 ? 'text-red-400' : 'text-green-400'}`}>
              {(stats.bom_coverage_ratio * 100).toFixed(0)}%
            </span>
          </div>
        )}
        <div className={`border rounded px-3 py-1.5 text-xs ${criticalCount > 0 ? 'bg-red-950/40 border-red-700/50' : 'bg-gray-800 border-gray-700'}`}>
          <span className="text-gray-400">严重</span>
          <span className={`ml-2 font-semibold ${criticalCount > 0 ? 'text-red-400' : 'text-gray-500'}`}>{criticalCount}</span>
        </div>
        <div className={`border rounded px-3 py-1.5 text-xs ${warningCount > 0 ? 'bg-amber-950/40 border-amber-700/50' : 'bg-gray-800 border-gray-700'}`}>
          <span className="text-gray-400">警告</span>
          <span className={`ml-2 font-semibold ${warningCount > 0 ? 'text-amber-400' : 'text-gray-500'}`}>{warningCount}</span>
        </div>
        {diff && (
          <div className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-xs">
            <span className="text-green-400">+{diff.added_triples.length}</span>
            <span className="text-gray-600 mx-1">/</span>
            <span className="text-red-400">-{diff.removed_triples.length}</span>
            <span className="text-gray-500 ml-1">（与上次对比）</span>
          </div>
        )}
      </div>

      {/* Tab 导航 */}
      <div className="flex gap-1 border-b border-gray-700 mb-3">
        {TABS.map(t => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-3 py-1 text-xs rounded-t border-b-2 transition-colors ${
              activeTab === t.key
                ? 'border-purple-500 text-purple-300'
                : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Tab 内容 */}
      <div className="min-h-40">
        {activeTab === 'issues' && (
          <div>
            {issues.length === 0 && (
              <p className="text-green-400 text-sm">✓ 未检测到明显问题，质量良好</p>
            )}
            {issues.map((issue, i) => (
              <StageIssueCard
                key={i}
                issue={issue}
                extraSuggestion={diagnosisByIndex[i]}
                onHighlight={ids => { setHighlightIds(ids); setActiveTab('triples') }}
              />
            ))}
            {issues.length > 0 && (
              <button
                onClick={handleDiagnose}
                disabled={diagnosing}
                className="mt-2 px-3 py-1 text-xs border border-purple-600 text-purple-400 rounded hover:bg-purple-950/30 disabled:opacity-40"
              >
                {diagnosing ? '🤖 LLM 诊断中...' : '🤖 生成 LLM 深度诊断'}
              </button>
            )}
          </div>
        )}

        {activeTab === 'graph' && (
          <div className="h-64 rounded border border-gray-700 overflow-hidden">
            <KgViewer stageFilter={stageN === 1 ? 'BOM' : 'Manual'} />
          </div>
        )}

        {activeTab === 'triples' && (
          <TriplesEditor
            stageN={stageN}
            highlightIds={highlightIds}
          />
        )}

        {activeTab === 'knowledge' && (
          <ExpertKnowledgeInput
            stageN={stageN}
            onConfirmed={() => { loadReport() }}
          />
        )}

        {activeTab === 'params' && (
          <ParamTuner
            stageN={stageN}
            onRerun={onRerun}
            running={rerunning}
          />
        )}
      </div>

      {/* 确认放行按钮 */}
      <div className="mt-4 pt-3 border-t border-gray-700 flex items-center gap-3">
        <button
          onClick={handleApprove}
          disabled={approving}
          className="px-4 py-1.5 bg-green-800 text-white rounded font-semibold hover:bg-green-700 disabled:opacity-40 text-sm"
        >
          {approving ? '处理中...' : `✅ 确认放行 → Stage ${stageN === 1 ? '2' : '完成'}`}
        </button>
        <p className="text-gray-500 text-xs">确认后将解锁下一阶段</p>
      </div>
    </div>
  )
}
