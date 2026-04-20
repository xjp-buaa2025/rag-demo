import React, { useState } from 'react'
import { ExpertDiff } from '../../../types'
import { submitExpertKnowledge, confirmExpertKnowledge } from '../../../api/client'

interface Props {
  stageN: 1 | 2
  onConfirmed: () => void
}

export default function ExpertKnowledgeInput({ stageN, onConfirmed }: Props) {
  const [text, setText] = useState('')
  const [diff, setDiff] = useState<ExpertDiff | null>(null)
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError('')
    setDiff(null)
    try {
      const res = await submitExpertKnowledge(stageN, text)
      setDiff(res.diff)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const handleConfirm = async () => {
    if (!diff) return
    setConfirming(true)
    try {
      await confirmExpertKnowledge(stageN, diff)
      setDiff(null)
      setText('')
      onConfirmed()
    } finally {
      setConfirming(false)
    }
  }

  return (
    <div className="text-xs">
      <p className="text-gray-400 mb-1">输入您的领域知识，系统将自动分析并修改对应的三元组：</p>
      <textarea
        rows={3}
        value={text}
        onChange={e => setText(e.target.value)}
        placeholder="例如：压气机第一级叶片和盘是榫槽配合，不是螺栓连接..."
        className="w-full bg-gray-900 border border-gray-600 rounded px-2 py-1 text-white text-xs resize-none focus:border-purple-500 outline-none"
      />
      <button
        onClick={handleSubmit}
        disabled={loading || !text.trim()}
        className="mt-1 px-3 py-1 bg-purple-800 text-white rounded disabled:opacity-40 hover:bg-purple-700"
      >
        {loading ? '分析中...' : '提交领域知识'}
      </button>

      {error && <p className="mt-1 text-red-400">{error}</p>}

      {diff && (
        <div className="mt-3 border border-purple-700 rounded p-2 bg-purple-950/20">
          <p className="text-purple-400 font-semibold mb-2">变更预览</p>

          {diff.added.length > 0 && (
            <div className="mb-2">
              <p className="text-green-400 mb-1">+ 新增 {diff.added.length} 条</p>
              {diff.added.map((t, i) => (
                <div key={i} className="text-green-300 bg-green-950/30 rounded px-1 py-0.5 mb-0.5">
                  {t.head} → <span className="text-purple-300">{t.relation}</span> → {t.tail}
                </div>
              ))}
            </div>
          )}

          {diff.removed_indices.length > 0 && (
            <div className="mb-2">
              <p className="text-red-400 mb-1">- 删除 {diff.removed_indices.length} 条（索引：{diff.removed_indices.join(', ')}）</p>
            </div>
          )}

          {diff.modified.length > 0 && (
            <div className="mb-2">
              <p className="text-amber-400 mb-1">~ 修改 {diff.modified.length} 条</p>
              {diff.modified.map((m, i) => (
                <div key={i} className="text-amber-300 bg-amber-950/30 rounded px-1 py-0.5 mb-0.5">
                  #{m.index}: {m.triple.head} → <span className="text-purple-300">{m.triple.relation}</span> → {m.triple.tail}
                </div>
              ))}
            </div>
          )}

          <div className="flex gap-2 mt-2">
            <button
              onClick={handleConfirm}
              disabled={confirming}
              className="px-3 py-1 bg-green-800 text-white rounded hover:bg-green-700 disabled:opacity-40"
            >
              {confirming ? '应用中...' : '确认应用'}
            </button>
            <button
              onClick={() => setDiff(null)}
              className="px-3 py-1 bg-gray-700 text-white rounded hover:bg-gray-600"
            >
              取消
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
