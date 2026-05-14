import type { StageIssue } from '../../../types/hitl'

interface Props {
  issue: StageIssue
  extraSuggestion?: string
  onHighlight?: (ids: string[]) => void
}

const SEVERITY_STYLE: Record<string, { bg: string; border: string; badge: string; text: string }> = {
  critical: { bg: 'bg-red-950/30', border: 'border-red-600', badge: 'bg-red-600 text-white', text: 'text-red-400' },
  warning:  { bg: 'bg-amber-950/30', border: 'border-amber-500', badge: 'bg-amber-500 text-black', text: 'text-amber-400' },
  info:     { bg: 'bg-blue-950/30', border: 'border-blue-500', badge: 'bg-blue-500 text-white', text: 'text-blue-400' },
}

const SEVERITY_LABEL: Record<string, string> = {
  critical: '严重', warning: '警告', info: '提示',
}

export default function StageIssueCard({ issue, extraSuggestion, onHighlight }: Props) {
  const s = SEVERITY_STYLE[issue.severity] ?? SEVERITY_STYLE.info

  return (
    <div className={`rounded-lg border ${s.border} ${s.bg} p-3 mb-2`}>
      <div className="flex items-start gap-2">
        <span className={`text-xs px-2 py-0.5 rounded font-semibold shrink-0 ${s.badge}`}>
          {SEVERITY_LABEL[issue.severity]}
        </span>
        <div className="flex-1 min-w-0">
          <p className={`font-semibold text-sm ${s.text}`}>{issue.title_zh}</p>
          <p className="text-xs text-gray-400 mt-0.5">{issue.description}</p>
          <p className="text-xs text-blue-400 mt-1">
            👉 {issue.suggestion}
          </p>
          {extraSuggestion && (
            <p className="text-xs text-purple-400 mt-1 border-t border-purple-900/50 pt-1">
              🤖 {extraSuggestion}
            </p>
          )}
          {issue.affected_triple_ids.length > 0 && onHighlight && (
            <button
              onClick={() => onHighlight(issue.affected_triple_ids)}
              className="mt-1 text-xs text-gray-500 hover:text-blue-400 underline"
            >
              高亮 {issue.affected_triple_ids.length} 条相关三元组
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
