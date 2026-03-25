// ============================================================
// BomIngest — BOM Excel 文件入库面板
//
// 对应 Gradio Tab 2 的"📋 BOM 入库" Accordion。
// 功能：
//   - 文件选择（.xlsx），可选（不选则用后端默认 test_bom.xlsx）
//   - 增量入库 / 清空重建
//   - multipart/form-data POST → SSE 日志流
// ============================================================

import { useRef, useState } from 'react'
import { postBomIngest, postBomIngestPipeline } from '../../api/client'
import { usePostSSE } from '../../hooks/usePostSSE'

export default function BomIngest() {
  const [file, setFile] = useState<File | null>(null)
  const [usePipeline, setUsePipeline] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { run, log, loading, clear } = usePostSSE()

  const handleIngest = async (clearFirst: boolean) => {
    clear()
    if (usePipeline) {
      await run(postBomIngestPipeline(file, clearFirst))
    } else {
      await run(postBomIngest(file, clearFirst))
    }
  }

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">
      <p className="text-xs text-slate-500">
        支持 Excel(.xlsx/.csv)、PDF、Word(.docx) 格式。Excel/CSV 需包含标准列（level_code, part_id 等）；
        PDF/Word 将由 AI 自动识别并转换为标准 BOM 格式。不上传则使用默认 test_bom.xlsx。
      </p>

      {/* 模式切换 */}
      <div className="flex items-center gap-2 text-xs text-slate-600">
        <span>模式：</span>
        <button
          onClick={() => setUsePipeline(false)}
          className={`px-2 py-1 rounded border transition-colors ${
            !usePipeline
              ? 'bg-blue-600 text-white border-blue-600'
              : 'border-slate-300 hover:bg-slate-50'
          }`}
        >
          原生
        </button>
        <button
          onClick={() => setUsePipeline(true)}
          className={`px-2 py-1 rounded border transition-colors ${
            usePipeline
              ? 'bg-purple-600 text-white border-purple-600'
              : 'border-slate-300 hover:bg-slate-50'
          }`}
        >
          LangGraph 管道
        </button>
        {usePipeline && (
          <span className="text-purple-500">（节点化处理：提取表格 → LLM 转换 → 清洗 → Neo4j）</span>
        )}
      </div>

      {/* 文件选择 */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
        >
          📎 选择 BOM 文件
        </button>
        <span className="text-sm text-slate-500 truncate max-w-xs">
          {file ? file.name : '未选择（将使用默认 test_bom.xlsx）'}
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
          accept=".xlsx,.xls,.csv,.pdf,.docx"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <button
          onClick={() => handleIngest(false)}
          disabled={loading}
          className={`flex-1 px-3 py-2 text-sm text-white rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${
            usePipeline ? 'bg-purple-600 hover:bg-purple-700' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {loading ? '⏳ 入库中…' : usePipeline ? '🔀 管道入库（增量）' : '📥 入库（增量）'}
        </button>
        <button
          onClick={() => handleIngest(true)}
          disabled={loading}
          className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          🗑️ 清空重建
        </button>
      </div>

      {/* 日志 */}
      {log && (
        <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
          {log}
        </pre>
      )}
    </div>
  )
}
