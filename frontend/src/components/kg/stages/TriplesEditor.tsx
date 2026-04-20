import React, { useState, useEffect, useCallback } from 'react'
import { BilingualTriple } from '../../../types'
import {
  listTriplesBilingual, updateTriple, deleteTriple, addTriple,
} from '../../../api/client'

interface Props {
  stageN: 1 | 2
  highlightIds?: string[]
}

type DisplayMode = 'en' | 'zh' | 'both'

const EMPTY_TRIPLE = { head: '', relation: '', tail: '', confidence: 1.0, source: 'expert', head_type: '', tail_type: '' }

export default function TriplesEditor({ stageN, highlightIds = [] }: Props) {
  const [triples, setTriples] = useState<BilingualTriple[]>([])
  const [total, setTotal] = useState(0)
  const [offset, setOffset] = useState(0)
  const [mode, setMode] = useState<DisplayMode>('both')
  const [editIdx, setEditIdx] = useState<number | null>(null)
  const [editBuf, setEditBuf] = useState<Partial<BilingualTriple>>({})
  const [adding, setAdding] = useState(false)
  const [newTriple, setNewTriple] = useState({ ...EMPTY_TRIPLE })
  const [loading, setLoading] = useState(false)
  const LIMIT = 50

  const load = useCallback(async (off: number) => {
    setLoading(true)
    try {
      const res = await listTriplesBilingual(stageN, off, LIMIT)
      setTriples(res.triples)
      setTotal(res.total)
      setOffset(off)
    } finally {
      setLoading(false)
    }
  }, [stageN])

  useEffect(() => { load(0) }, [load])

  const handleSave = async (idx: number) => {
    await updateTriple(stageN, offset + idx, editBuf)
    setEditIdx(null)
    load(offset)
  }

  const handleDelete = async (idx: number) => {
    if (!confirm('确认删除这条三元组？')) return
    await deleteTriple(stageN, offset + idx)
    load(offset)
  }

  const handleAdd = async () => {
    await addTriple(stageN, newTriple)
    setAdding(false)
    setNewTriple({ ...EMPTY_TRIPLE })
    load(offset)
  }

  const isHighlighted = (t: BilingualTriple) =>
    highlightIds.includes(t.head) || highlightIds.includes(t.tail)

  const showEn = mode === 'en' || mode === 'both'
  const showZh = mode === 'zh' || mode === 'both'

  return (
    <div className="text-xs">
      {/* 工具栏 */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-gray-400">显示模式：</span>
        {(['en', 'zh', 'both'] as DisplayMode[]).map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`px-2 py-0.5 rounded text-xs border ${mode === m ? 'border-blue-500 text-blue-400' : 'border-gray-600 text-gray-500'}`}
          >
            {{ en: '仅英文', zh: '仅中文', both: '中英对照' }[m]}
          </button>
        ))}
        <button
          onClick={() => setAdding(true)}
          className="ml-auto px-2 py-0.5 rounded border border-green-600 text-green-400"
        >
          + 新增三元组
        </button>
      </div>

      {/* 新增行 */}
      {adding && (
        <div className="mb-2 p-2 bg-green-950/30 border border-green-700 rounded flex gap-1 flex-wrap">
          {(['head', 'relation', 'tail'] as const).map(f => (
            <input
              key={f}
              placeholder={f}
              value={newTriple[f]}
              onChange={e => setNewTriple(p => ({ ...p, [f]: e.target.value }))}
              className="flex-1 min-w-20 bg-gray-900 border border-gray-600 rounded px-1 py-0.5 text-white"
            />
          ))}
          <input
            type="number" min={0} max={1} step={0.1}
            value={newTriple.confidence}
            onChange={e => setNewTriple(p => ({ ...p, confidence: parseFloat(e.target.value) }))}
            className="w-16 bg-gray-900 border border-gray-600 rounded px-1 py-0.5 text-white"
          />
          <button onClick={handleAdd} className="px-2 py-0.5 bg-green-700 text-white rounded">确认</button>
          <button onClick={() => setAdding(false)} className="px-2 py-0.5 bg-gray-700 text-white rounded">取消</button>
        </div>
      )}

      {/* 表格 */}
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="text-gray-500 border-b border-gray-700">
              {showEn && <th className="text-left p-1">Head</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">主体</th>}
              {showEn && <th className="text-left p-1">Relation</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">关系</th>}
              {showEn && <th className="text-left p-1">Tail</th>}
              {showZh && <th className="text-left p-1 text-blue-400/70">客体</th>}
              <th className="text-left p-1">置信度</th>
              <th className="p-1"></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan={8} className="text-center py-4 text-gray-500">加载中...</td></tr>
            )}
            {triples.map((t, i) => {
              const hi = isHighlighted(t)
              if (editIdx === i) {
                return (
                  <tr key={i} className="bg-blue-950/40 border-b border-gray-800">
                    <td colSpan={showZh ? 6 : 3} className="p-1">
                      <div className="flex gap-1">
                        {(['head', 'relation', 'tail'] as const).map(f => (
                          <input
                            key={f}
                            value={String(editBuf[f] ?? t[f] ?? '')}
                            onChange={e => setEditBuf(p => ({ ...p, [f]: e.target.value }))}
                            className="flex-1 bg-gray-900 border border-blue-600 rounded px-1 py-0.5 text-white text-xs"
                          />
                        ))}
                      </div>
                    </td>
                    <td className="p-1">
                      <input
                        type="number" min={0} max={1} step={0.1}
                        value={Number(editBuf.confidence ?? t.confidence)}
                        onChange={e => setEditBuf(p => ({ ...p, confidence: parseFloat(e.target.value) }))}
                        className="w-14 bg-gray-900 border border-blue-600 rounded px-1 py-0.5 text-white text-xs"
                      />
                    </td>
                    <td className="p-1 flex gap-1">
                      <button onClick={() => handleSave(i)} className="px-1 py-0.5 bg-blue-700 text-white rounded">保存</button>
                      <button onClick={() => setEditIdx(null)} className="px-1 py-0.5 bg-gray-700 text-white rounded">取消</button>
                    </td>
                  </tr>
                )
              }
              return (
                <tr
                  key={i}
                  className={`border-b border-gray-800 ${hi ? 'bg-amber-950/20' : 'hover:bg-gray-800/30'}`}
                >
                  {showEn && <td className="p-1 text-gray-300 truncate max-w-32">{t.head}</td>}
                  {showZh && <td className="p-1 text-blue-300 truncate max-w-24">{t.head_zh}</td>}
                  {showEn && <td className="p-1 text-purple-400 truncate max-w-24">{t.relation}</td>}
                  {showZh && <td className="p-1 text-purple-300 truncate max-w-20">{t.relation_zh}</td>}
                  {showEn && <td className="p-1 text-gray-300 truncate max-w-32">{t.tail}</td>}
                  {showZh && <td className="p-1 text-blue-300 truncate max-w-24">{t.tail_zh}</td>}
                  <td className="p-1 text-gray-400">{t.confidence.toFixed(2)}</td>
                  <td className="p-1 flex gap-1 shrink-0">
                    <button onClick={() => { setEditIdx(i); setEditBuf({}) }} className="text-blue-500 hover:text-blue-300">编辑</button>
                    <button onClick={() => handleDelete(i)} className="text-red-500 hover:text-red-300">删除</button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* 分页 */}
      <div className="flex items-center gap-2 mt-2 text-gray-500">
        <span>共 {total} 条</span>
        <button
          disabled={offset === 0}
          onClick={() => load(Math.max(0, offset - LIMIT))}
          className="px-2 py-0.5 border border-gray-700 rounded disabled:opacity-30"
        >上页</button>
        <span>{Math.floor(offset / LIMIT) + 1} / {Math.ceil(total / LIMIT)}</span>
        <button
          disabled={offset + LIMIT >= total}
          onClick={() => load(offset + LIMIT)}
          className="px-2 py-0.5 border border-gray-700 rounded disabled:opacity-30"
        >下页</button>
      </div>
    </div>
  )
}
