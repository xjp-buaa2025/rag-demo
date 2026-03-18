// ============================================================
// KnowledgePanel — 知识库管理面板
//
// 对应 Gradio 中 Tab 1 的"📂 知识库管理" Accordion。
// 功能：
//   - 显示当前知识库文档块数量
//   - 增量入库（POST /ingest?clear_first=false）
//   - 清空重建（POST /ingest?clear_first=true）
//   - 实时日志输出（SSE 覆盖式）
// ============================================================

import { useEffect, useState } from 'react'
import { getIngestStatus, postIngest } from '../../api/client'
import { usePostSSE } from '../../hooks/usePostSSE'

export default function KnowledgePanel() {
  const [count, setCount] = useState<number | null>(null)
  const { run, log, loading, clear } = usePostSSE()

  // 组件挂载时获取当前文档块数
  useEffect(() => {
    getIngestStatus().then((r) => setCount(r.count)).catch(() => setCount(0))
  }, [])

  // 入库完成后刷新数量
  const handleIngest = async (clearFirst: boolean) => {
    clear()
    await run(postIngest(clearFirst))
    getIngestStatus().then((r) => setCount(r.count)).catch(() => {})
  }

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">
      {/* 状态行 */}
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-600">📚 知识库文档块</span>
        <span className="text-sm font-bold text-blue-600">
          {count === null ? '…' : `${count} 条`}
        </span>
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <button
          onClick={() => handleIngest(false)}
          disabled={loading}
          className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '⏳ 入库中…' : '🔄 扫描 data/ 并入库（增量）'}
        </button>
        <button
          onClick={() => handleIngest(true)}
          disabled={loading}
          className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          🗑️ 清空重建
        </button>
      </div>

      {/* 日志输出框 */}
      {log && (
        <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
          {log}
        </pre>
      )}
    </div>
  )
}
