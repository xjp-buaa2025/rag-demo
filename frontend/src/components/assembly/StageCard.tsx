import { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import type { StageKey } from '../../types/assemblyDesign'

interface Props {
  stageKey: StageKey
  title: string
  isDone: boolean
  stageData?: Record<string, unknown>
  prerequisiteDone: boolean
  prerequisiteLabel: string | null  // e.g. "S1" or null
  loading: boolean
  onGenerate: () => void
}

export default function StageCard({
  stageKey,
  title,
  isDone,
  stageData,
  prerequisiteDone,
  prerequisiteLabel,
  loading,
  onGenerate,
}: Props) {
  const [expanded, setExpanded] = useState(false)
  const [showRaw, setShowRaw] = useState(false)

  const canGenerate = prerequisiteDone && !loading

  return (
    <div className={`border rounded-lg overflow-hidden ${isDone ? 'border-green-200' : 'border-slate-200'}`}>
      {/* Header row */}
      <div className={`flex items-center justify-between px-4 py-3 ${isDone ? 'bg-green-50' : 'bg-slate-50'}`}>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-mono px-1.5 py-0.5 rounded ${isDone ? 'bg-green-200 text-green-800' : 'bg-slate-200 text-slate-600'}`}>
            {isDone ? '✓' : '○'}
          </span>
          <span className="text-sm font-medium text-slate-700">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {isDone && (
            <button
              onClick={() => setExpanded(v => !v)}
              className="text-xs text-blue-600 hover:underline"
            >
              {expanded ? '▲ 收起' : '▶ 展开产物'}
            </button>
          )}
          <button
            onClick={onGenerate}
            disabled={!canGenerate}
            title={!prerequisiteDone && prerequisiteLabel ? `请先完成 ${prerequisiteLabel}` : undefined}
            className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {loading ? '生成中…' : isDone ? '重新生成' : '生成'}
          </button>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && isDone && stageData && (
        <div className="px-4 py-3 bg-white border-t border-slate-100 space-y-2">
          {/* S1: show task_card_md as Markdown */}
          {stageKey === '1' && typeof stageData.task_card_md === 'string' && (
            <div className="prose prose-sm max-w-none text-slate-700">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {stageData.task_card_md}
              </ReactMarkdown>
            </div>
          )}

          {/* S5: show recommendation + overall_score */}
          {stageKey === '5' && (
            <div className="flex gap-4 text-sm">
              <span className="text-slate-600">评审结论：
                <span className={`ml-1 font-semibold ${
                  stageData.recommendation === 'approved' ? 'text-green-600' :
                  stageData.recommendation === 'rejected' ? 'text-red-600' : 'text-amber-600'
                }`}>
                  {String(stageData.recommendation)}
                </span>
              </span>
              {typeof stageData.overall_score === 'number' && (
                <span className="text-slate-600">综合评分：
                  <span className="ml-1 font-semibold text-blue-600">
                    {stageData.overall_score.toFixed(1)} / 5
                  </span>
                </span>
              )}
            </div>
          )}

          {/* Raw JSON toggle */}
          <div>
            <button
              onClick={() => setShowRaw(v => !v)}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              {showRaw ? '▲ 隐藏 JSON' : '▶ 原始 JSON'}
            </button>
            {showRaw && (
              <pre className="mt-2 text-xs bg-slate-900 text-green-300 p-3 rounded overflow-x-auto max-h-64 overflow-y-auto">
                {JSON.stringify(stageData, null, 2)}
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
