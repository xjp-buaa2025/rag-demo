import { useState } from 'react'
import SchemeList from '../components/assembly/SchemeList'
import SchemeDetail from '../components/assembly/SchemeDetail'

export default function AssemblyDesignPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  return (
    <div className="flex h-[calc(100vh-73px)]">
      {/* 左侧边栏 */}
      <aside className="w-64 flex-shrink-0 border-r border-slate-200 bg-white overflow-hidden flex flex-col">
        <div className="px-3 py-3 border-b border-slate-200">
          <h2 className="text-sm font-semibold text-slate-700">✈ 装配方案</h2>
        </div>
        <SchemeList
          selectedId={selectedId}
          onSelect={(id) => {
            setSelectedId(id)
            setRefreshKey(k => k + 1)
          }}
          refreshKey={refreshKey}
        />
      </aside>

      {/* 右侧详情 */}
      <main className="flex-1 overflow-y-auto bg-slate-50">
        {selectedId ? (
          <SchemeDetail schemeId={selectedId} />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-slate-400 space-y-2">
            <span className="text-4xl">✈</span>
            <p className="text-sm">从左侧选择方案，或新建一个</p>
          </div>
        )}
      </main>
    </div>
  )
}
