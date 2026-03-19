// ============================================================
// EvalPanel — 性能评估面板（三阶段）
//
// 阶段一：检索阶段（POST /eval/retrieval）
//   上下文精确率 / Recall@K / MRR / NDCG@K
//   ~1-3 分钟，LLM 自动标注 Ground Truth
//
// 阶段二：生成阶段（POST /eval/generation）
//   忠实度 / 相关性 / 可回答性
//   ~3-8 分钟，LLM 生成答案并评估
//
// 阶段三：RAGAS（POST /eval/ragas）
//   Context Relevance / Faithfulness / Answer Relevance
//   ~5-15 分钟，业界标准框架
// ============================================================

import { useState } from 'react'
import { usePostSSE } from '../../hooks/usePostSSE'
import { postEvalRetrieval, postEvalGeneration, postEvalRagas } from '../../api/client'

type EvalType = 'retrieval' | 'generation' | 'ragas' | null

const METRIC_SECTIONS = [
  {
    stage: '🔍 检索阶段',
    time: '~1-3 分钟',
    color: 'blue',
    desc: '评估检索器能否找得对、找得全',
    metrics: [
      { name: '上下文精确率', desc: '检索结果中有多少是真正相关的文档，反映检索的信噪比（Precision@K）' },
      { name: 'Recall@K', desc: '前 K 个结果中召回了多少比例的相关文档，反映检索的覆盖率' },
      { name: 'MRR', desc: '第一个相关文档出现在第几位的倒数均值，衡量排名质量' },
      { name: 'NDCG@K', desc: '综合考虑排名位置与相关性的归一化折损累计增益' },
    ],
  },
  {
    stage: '💬 生成阶段',
    time: '~3-8 分钟',
    color: 'green',
    desc: '评估 LLM 能否基于上下文生成忠实、准确、有用的答案',
    metrics: [
      { name: '忠实度', desc: '答案中的事实声明有多少能在检索内容中找到支撑，衡量幻觉程度（0-1）' },
      { name: '相关性', desc: '生成的答案是否真正针对了用户的问题，通过反向生成问题的余弦相似度计算（0-1）' },
      { name: '可回答性', desc: 'LLM 根据检索内容能否给出令人满意的答案，综合判断上下文充分性（0-5 分）' },
    ],
  },
  {
    stage: '🧪 RAGAS',
    time: '~5-15 分钟',
    color: 'purple',
    desc: '业界标准的端到端 RAG 评估框架（最全面）',
    metrics: [
      { name: 'Context Relevance', desc: '上下文中与问题直接相关的句子占比' },
      { name: 'Faithfulness', desc: '答案声明被上下文支撑的比例（与生成阶段忠实度同源）' },
      { name: 'Answer Relevance', desc: '答案与原问题的语义匹配度' },
    ],
  },
]

const COLOR_MAP: Record<string, string> = {
  blue:   'border-blue-200 bg-blue-50',
  green:  'border-green-200 bg-green-50',
  purple: 'border-purple-200 bg-purple-50',
}

const TAG_COLOR_MAP: Record<string, string> = {
  blue:   'bg-blue-100 text-blue-700',
  green:  'bg-green-100 text-green-700',
  purple: 'bg-purple-100 text-purple-700',
}

const BTN_ACTIVE: Record<string, string> = {
  retrieval:  'bg-blue-700 text-white',
  generation: 'bg-green-700 text-white',
  ragas:      'bg-purple-700 text-white',
}

const BTN_IDLE: Record<string, string> = {
  retrieval:  'bg-blue-600 text-white hover:bg-blue-700',
  generation: 'bg-green-600 text-white hover:bg-green-700',
  ragas:      'bg-purple-600 text-white hover:bg-purple-700',
}

export default function EvalPanel() {
  const { run, log, loading, clear } = usePostSSE()
  const [active, setActive] = useState<EvalType>(null)
  const [showDocs, setShowDocs] = useState(true)

  const handleEval = async (type: EvalType) => {
    clear()
    setActive(type)
    const genMap = {
      retrieval:  postEvalRetrieval,
      generation: postEvalGeneration,
      ragas:      postEvalRagas,
    }
    if (!type) return
    await run(genMap[type]())
    setActive(null)
  }

  const btnClass = (type: NonNullable<EvalType>) =>
    `flex-1 px-3 py-2 text-sm rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed
     ${active === type ? BTN_ACTIVE[type] : BTN_IDLE[type]}`

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">

      {/* 指标说明区 */}
      <div className="border border-slate-100 rounded-md bg-slate-50">
        <button
          onClick={() => setShowDocs(v => !v)}
          className="w-full flex items-center justify-between px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-md transition-colors"
        >
          <span>📖 评估指标说明</span>
          <span className="text-slate-400 text-xs">{showDocs ? '▲ 收起' : '▼ 展开'}</span>
        </button>

        {showDocs && (
          <div className="px-3 pb-3 space-y-2">
            {METRIC_SECTIONS.map(section => (
              <div key={section.stage} className={`border rounded-md p-3 ${COLOR_MAP[section.color]}`}>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="font-medium text-sm text-slate-800">{section.stage}</span>
                  <span className={`text-xs px-1.5 py-0.5 rounded ${TAG_COLOR_MAP[section.color]}`}>{section.time}</span>
                  <span className="text-xs text-slate-500">{section.desc}</span>
                </div>
                <div className="space-y-1">
                  {section.metrics.map(m => (
                    <div key={m.name} className="flex gap-2 text-xs">
                      <span className="font-medium text-slate-700 shrink-0 w-28">{m.name}</span>
                      <span className="text-slate-500">{m.desc}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 评估按钮区 */}
      <div className="flex gap-2">
        <button onClick={() => handleEval('retrieval')} disabled={loading} className={btnClass('retrieval')}>
          {loading && active === 'retrieval' ? '⏳ 评估中…' : '🔍 检索阶段评估'}
        </button>
        <button onClick={() => handleEval('generation')} disabled={loading} className={btnClass('generation')}>
          {loading && active === 'generation' ? '⏳ 评估中…' : '💬 生成阶段评估'}
        </button>
        <button onClick={() => handleEval('ragas')} disabled={loading} className={btnClass('ragas')}>
          {loading && active === 'ragas' ? '⏳ 评估中…' : '🧪 RAGAS 评估'}
        </button>
      </div>

      {/* 日志输出区 */}
      {log && (
        <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-96 overflow-y-auto whitespace-pre-wrap leading-relaxed">
          {log}
        </pre>
      )}
    </div>
  )
}
