import { useState } from 'react'
import { postKgStage3, getKgStagePreview } from '../../../api/client'
import { useStageSSE } from '../../../hooks/useStageSSE'
import type { KgSseFrame, TriplesPreview } from '../../../types'

interface Props {
  onComplete?: () => void
}

export default function Stage3Cad({ onComplete }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [logs, setLogs] = useState<string[]>([])
  const [resultFrame, setResultFrame] = useState<KgSseFrame | null>(null)
  const [preview, setPreview] = useState<TriplesPreview | null>(null)
  const [previewOffset, setPreviewOffset] = useState(0)
  const { run, loading } = useStageSSE()

  const handleRun = async () => {
    if (!file) return
    setLogs([])
    setResultFrame(null)
    setPreview(null)
    setPreviewOffset(0)
    await run(postKgStage3(file), {
      onLog: (msg) => setLogs(prev => [...prev, msg]),
      onResult: (data) => setResultFrame(data),
      onDone: async (success) => {
        if (success) {
          const p = await getKgStagePreview('cad', 0)
          setPreview(p)
          onComplete?.()
        }
      },
      onError: (msg) => setLogs(prev => [...prev, `❌ ${msg}`]),
    })
  }

  const loadPage = async (offset: number) => {
    const p = await getKgStagePreview('cad', offset)
    setPreview(p)
    setPreviewOffset(offset)
  }

  const stats = resultFrame?.stats ?? preview?.stats ?? {}

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <input
          type="file"
          accept=".step,.stp"
          onChange={e => setFile(e.target.files?.[0] ?? null)}
          className="text-sm text-slate-600"
        />
        <button
          onClick={handleRun}
          disabled={loading || !file}
          className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 disabled:opacity-40"
        >
          {loading ? '运行中…' : '运行 CAD 解析'}
        </button>
      </div>

      {logs.length > 0 && (
        <div className="bg-slate-900 text-green-300 text-xs font-mono p-3 rounded h-48 overflow-y-auto">
          {logs.map((l, i) => <div key={i}>{l}</div>)}
        </div>
      )}

      {(resultFrame || (preview && Object.keys(stats).length > 0)) && (
        <div className="bg-blue-50 border border-blue-200 rounded p-3 text-sm flex flex-wrap gap-4">
          {resultFrame && (
            <div><span className="font-semibold text-blue-800">三元组数量：</span>
              <span className="text-blue-700">{resultFrame.triples_count ?? 0}</span></div>
          )}
          {Object.entries(stats).map(([k, v]) => (
            <div key={k}><span className="font-semibold text-slate-600">{k}：</span>
              <span className="text-slate-700">{String(v)}</span></div>
          ))}
        </div>
      )}

      {preview && (
        <div className="overflow-x-auto">
          <div className="flex items-center justify-between mb-2 text-sm text-slate-600">
            <span>第 {previewOffset + 1}–{Math.min(previewOffset + 50, preview.total)} 条 / 共 {preview.total} 条</span>
            <div className="flex gap-2">
              <button
                onClick={() => loadPage(Math.max(0, previewOffset - 50))}
                disabled={previewOffset === 0}
                className="px-2 py-1 border rounded text-xs disabled:opacity-40"
              >上一页</button>
              <button
                onClick={() => loadPage(previewOffset + 50)}
                disabled={previewOffset + 50 >= preview.total}
                className="px-2 py-1 border rounded text-xs disabled:opacity-40"
              >下一页</button>
            </div>
          </div>
          <table className="w-full text-xs border-collapse">
            <thead>
              <tr className="bg-slate-100">
                {['头实体', '关系', '尾实体', '置信度', '来源'].map(h => (
                  <th key={h} className="border border-slate-200 px-2 py-1 text-left">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {preview.triples.map((t, i) => (
                <tr key={i} className="hover:bg-slate-50">
                  <td className="border border-slate-200 px-2 py-1">{t.head}</td>
                  <td className="border border-slate-200 px-2 py-1">{t.relation}</td>
                  <td className="border border-slate-200 px-2 py-1">{t.tail}</td>
                  <td className="border border-slate-200 px-2 py-1">{t.confidence.toFixed(2)}</td>
                  <td className="border border-slate-200 px-2 py-1 text-slate-400">{t.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
