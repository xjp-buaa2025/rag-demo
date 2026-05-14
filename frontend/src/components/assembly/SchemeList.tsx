import { useState, useEffect } from 'react'
import { listSchemes } from '../../api/assemblyDesign'
import type { SchemeMeta } from '../../types/assemblyDesign'
import NewSchemeModal from './NewSchemeModal'

interface Props {
  selectedId: string | null
  onSelect: (id: string) => void
  refreshKey: number
}

export default function SchemeList({ selectedId, onSelect, refreshKey }: Props) {
  const [schemes, setSchemes] = useState<SchemeMeta[]>([])
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(false)

  const load = () => {
    setLoading(true)
    listSchemes()
      .then(r => setSchemes(r.schemes))
      .catch(() => {})
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [refreshKey])

  const handleCreated = (id: string) => {
    setShowModal(false)
    load()
    onSelect(id)
  }

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b border-slate-200">
        <button
          onClick={() => setShowModal(true)}
          className="w-full px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          + 新建方案
        </button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {loading && (
          <p className="text-xs text-slate-400 p-3">加载中…</p>
        )}
        {!loading && schemes.length === 0 && (
          <p className="text-xs text-slate-400 p-3">暂无方案，点击上方新建</p>
        )}
        {schemes.map(s => (
          <button
            key={s.scheme_id}
            onClick={() => onSelect(s.scheme_id)}
            className={`w-full text-left px-3 py-2.5 border-b border-slate-100 hover:bg-slate-50 transition-colors ${
              selectedId === s.scheme_id ? 'bg-blue-50 border-l-2 border-l-blue-500' : ''
            }`}
          >
            <div className="text-sm font-medium text-slate-700 truncate">
              {s.subject.system}
            </div>
            <div className="flex items-center justify-between mt-0.5">
              <span className="text-xs text-slate-400">
                {s.created_at.slice(0, 10)}
              </span>
              <span className="text-xs bg-green-100 text-green-700 px-1.5 py-0.5 rounded">
                {s.stages_done.length}/6
              </span>
            </div>
          </button>
        ))}
      </div>

      <NewSchemeModal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        onCreated={handleCreated}
      />
    </div>
  )
}
