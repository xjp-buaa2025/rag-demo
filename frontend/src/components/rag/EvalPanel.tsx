// ============================================================
// EvalPanel — 性能评估面板
//
// 对应 Gradio 中 Tab 1 的"📊 性能评估" Accordion。
// 三种评估：
//   - 召回诊断（POST /eval/diagnose）：秒级，纯统计
//   - LLM 打分（POST /eval/judge）：~1-2 分钟
//   - RAGAS 评估（POST /eval/ragas）：~5-15 分钟
// 均为 SSE 日志流，覆盖式显示报告。
// ============================================================

import { usePostSSE } from '../../hooks/usePostSSE'
import { postEvalDiagnose, postEvalJudge, postEvalRagas } from '../../api/client'

type EvalType = 'diagnose' | 'judge' | 'ragas' | null

export default function EvalPanel() {
  const { run, log, loading, clear } = usePostSSE()
  // 记录当前正在运行哪种评估，用于按钮高亮
  const [active, setActive] = useState<EvalType>(null)

  const handleEval = async (type: EvalType) => {
    clear()
    setActive(type)
    const genMap = {
      diagnose: postEvalDiagnose,
      judge: postEvalJudge,
      ragas: postEvalRagas,
    }
    if (!type) return
    await run(genMap[type]())
    setActive(null)
  }

  const btnClass = (type: EvalType) =>
    `flex-1 px-3 py-2 text-sm rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed
     ${active === type
      ? 'bg-indigo-700 text-white'
      : 'bg-indigo-600 text-white hover:bg-indigo-700'}`

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">
      <p className="text-xs text-slate-500">
        诊断（秒级）→ LLM 打分（~1-2 分钟）→ RAGAS（~5-15 分钟，最全面）
      </p>

      <div className="flex gap-2">
        <button onClick={() => handleEval('diagnose')} disabled={loading} className={btnClass('diagnose')}>
          {loading && active === 'diagnose' ? '⏳ 诊断中…' : '🔍 召回诊断'}
        </button>
        <button onClick={() => handleEval('judge')} disabled={loading} className={btnClass('judge')}>
          {loading && active === 'judge' ? '⏳ 打分中…' : '⚖️ LLM 打分'}
        </button>
        <button onClick={() => handleEval('ragas')} disabled={loading} className={btnClass('ragas')}>
          {loading && active === 'ragas' ? '⏳ 评估中…' : '🧪 RAGAS 评估'}
        </button>
      </div>

      {log && (
        <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
          {log}
        </pre>
      )}
    </div>
  )
}

// 需要手动 import useState（React 17 以下需要显式导入，18+ JSX transform 不需要，但 useState 仍需）
import { useState } from 'react'
