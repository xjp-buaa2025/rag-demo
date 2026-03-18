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
import { postBomIngest } from '../../api/client'
import { usePostSSE } from '../../hooks/usePostSSE'

export default function BomIngest() {
  const [file, setFile] = useState<File | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { run, log, loading, clear } = usePostSSE()

  const handleIngest = async (clearFirst: boolean) => {
    clear()
    await run(postBomIngest(file, clearFirst))
  }

  return (
    <div className="border border-slate-200 rounded-lg p-4 bg-white space-y-3">
      <p className="text-xs text-slate-500">
        Excel 列要求：level_code、part_id、part_name、category（Assembly/Part/Standard）、qty、unit 等。
        不上传则使用默认 test_bom.xlsx。
      </p>

      {/* 文件选择 */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => fileInputRef.current?.click()}
          className="px-3 py-1.5 text-sm border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
        >
          📎 选择 Excel 文件
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
          accept=".xlsx"
          className="hidden"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {/* 操作按钮 */}
      <div className="flex gap-2">
        <button
          onClick={() => handleIngest(false)}
          disabled={loading}
          className="flex-1 px-3 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading ? '⏳ 入库中…' : '📥 入库（增量）'}
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
