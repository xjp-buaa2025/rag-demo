import { useState } from 'react'
import { createScheme } from '../../api/assemblyDesign'

interface Props {
  isOpen: boolean
  onClose: () => void
  onCreated: (schemeId: string) => void
}

export default function NewSchemeModal({ isOpen, onClose, onCreated }: Props) {
  const [system, setSystem] = useState('')
  const [systemEn, setSystemEn] = useState('')
  const [scope, setScope] = useState('')
  const [intent, setIntent] = useState('工艺优化')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!system.trim()) { setError('子系统名称不能为空'); return }
    const scopeArr = scope.split(/[,，]/).map(s => s.trim()).filter(Boolean)
    if (scopeArr.length === 0) { setError('范围不能为空'); return }
    setLoading(true)
    setError(null)
    try {
      const res = await createScheme({
        subject_system: system.trim(),
        subject_system_en: systemEn.trim() || undefined,
        subject_scope: scopeArr,
        design_intent: intent.trim() || '工艺优化',
      })
      onCreated(res.scheme_id)
      // reset
      setSystem(''); setSystemEn(''); setScope(''); setIntent('工艺优化')
    } catch (err) {
      setError(err instanceof Error ? err.message : '创建失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <h2 className="text-base font-semibold text-slate-800 mb-4">新建装配方案</h2>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <label className="text-xs text-slate-600 block mb-1">子系统名称（中文）*</label>
            <input
              value={system}
              onChange={e => setSystem(e.target.value)}
              placeholder="例：PT6A 高压压气机"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">子系统名称（英文，可选）</label>
            <input
              value={systemEn}
              onChange={e => setSystemEn(e.target.value)}
              placeholder="例：PT6A HPC"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">范围（逗号分隔）*</label>
            <input
              value={scope}
              onChange={e => setScope(e.target.value)}
              placeholder="例：3 级轴流, 含转子/静子"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          <div>
            <label className="text-xs text-slate-600 block mb-1">设计意图</label>
            <input
              value={intent}
              onChange={e => setIntent(e.target.value)}
              placeholder="工艺优化"
              className="w-full border border-slate-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:border-blue-400"
            />
          </div>
          {error && <p className="text-xs text-red-600">{error}</p>}
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-1.5 text-sm text-slate-600 border border-slate-300 rounded hover:bg-slate-50"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-40"
            >
              {loading ? '创建中…' : '创建'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
