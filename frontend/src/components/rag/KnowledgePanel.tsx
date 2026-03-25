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

import { useEffect, useRef, useState } from 'react'
import { getIngestStatus, postIngest, postIngestPipeline } from '../../api/client'
import { usePostSSE } from '../../hooks/usePostSSE'

export default function KnowledgePanel() {
  const [count, setCount] = useState<number | null>(null)
  const { run, log, loading, clear } = usePostSSE()

  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { run: runUpload, log: uploadLog, loading: uploadLoading, clear: clearUpload } = usePostSSE()

  // 组件挂载时获取当前文档块数
  useEffect(() => {
    getIngestStatus().then((r) => setCount(r.count)).catch(() => setCount(0))
  }, [])

  // 扫描 data/ 目录入库
  const handleIngest = async (clearFirst: boolean) => {
    clear()
    await run(postIngest(clearFirst))
    getIngestStatus().then((r) => setCount(r.count)).catch(() => {})
  }

  // 上传文件并通过 LangGraph 管道入库
  const handleUpload = async (clearFirst: boolean) => {
    if (!file) return
    clearUpload()
    await runUpload(postIngestPipeline(file, clearFirst))
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

      {/* 文件上传区 */}
      <div className="space-y-2">
        <div className="flex items-center gap-3">
          <button
            onClick={() => fileInputRef.current?.click()}
            className="px-3 py-1.5 text-sm border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
          >
            📎 选择文件
          </button>
          <span className="text-sm text-slate-500 truncate max-w-xs">
            {file ? file.name : '未选择文件'}
          </span>
          {file && (
            <button
              onClick={() => { setFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
              className="text-xs text-red-400 hover:text-red-600"
            >
              ✕
            </button>
          )}
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.md,.txt"
            className="hidden"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => handleUpload(false)}
            disabled={!file || uploadLoading}
            className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {uploadLoading ? '⏳ 入库中…' : '📤 上传并增量入库'}
          </button>
          <button
            onClick={() => handleUpload(true)}
            disabled={!file || uploadLoading}
            className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🗑️ 上传并清空重建
          </button>
        </div>
        {uploadLog && (
          <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
            {uploadLog}
          </pre>
        )}
      </div>

      <hr className="border-slate-200" />

      {/* 扫描 data/ 目录操作 */}
      <div className="space-y-2">
        <p className="text-xs text-slate-400">扫描 data/ 目录批量入库</p>
        <div className="flex gap-2">
          <button
            onClick={() => handleIngest(false)}
            disabled={loading}
            className="flex-1 px-3 py-2 text-sm bg-slate-600 text-white rounded-md hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '⏳ 入库中…' : '🔄 扫描并增量入库'}
          </button>
          <button
            onClick={() => handleIngest(true)}
            disabled={loading}
            className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            🗑️ 清空重建
          </button>
        </div>
        {log && (
          <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
            {log}
          </pre>
        )}
      </div>
    </div>
  )
}
