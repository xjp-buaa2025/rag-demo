import { useState } from 'react'
import { postKgStage4Validate } from '../../../api/client'
import type { ValidationReport } from '../../../types'

type FilterMode = 'all' | 'unmatched'

export default function Stage4Validate() {
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState<ValidationReport | null>(null)
  const [filter, setFilter] = useState<FilterMode>('all')
  const [error, setError] = useState<string | null>(null)

  const handleValidate = async () => {
    setLoading(true)
    setError(null)
    try {
      const r = await postKgStage4Validate()
      setReport(r)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  const fmt = (n: number) => (n * 100).toFixed(1) + '%'

  const filteredComparison = report?.comparison.filter(t =>
    filter === 'all' ? true : !t.matched
  ) ?? []

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3">
        <button
          onClick={handleValidate}
          disabled={loading}
          className="px-4 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 disabled:opacity-40"
        >
          {loading ? '验证中…' : '运行验证'}
        </button>
        {error && <span className="text-red-500 text-sm">{error}</span>}
      </div>

      {report && (
        <div className="space-y-4">
          {/* 阶段覆盖信息 */}
          <div className="text-sm text-slate-600">
            <span className="font-medium">阶段覆盖：</span>
            {report.stages_included.join('、')}
          </div>

          {/* 整体指标 */}
          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Precision', value: fmt(report.precision) },
              { label: 'Recall',    value: fmt(report.recall) },
              { label: 'F1',        value: fmt(report.f1) },
            ].map(({ label, value }) => (
              <div key={label} className="bg-purple-50 border border-purple-200 rounded p-3 text-center">
                <div className="text-xs text-purple-500 uppercase tracking-wide">{label}</div>
                <div className="text-2xl font-bold text-purple-700">{value}</div>
              </div>
            ))}
          </div>
          <div className="flex gap-4 text-sm text-slate-600">
            <span>TP: <strong>{report.tp}</strong></span>
            <span>FP: <strong>{report.fp}</strong></span>
            <span>FN: <strong>{report.fn}</strong></span>
            <span>黄金集: <strong>{report.golden_count}</strong></span>
            <span>预测集: <strong>{report.predicted_count}</strong></span>
          </div>

          {/* 按关系类型 F1 表格 */}
          {Object.keys(report.per_relation).length > 0 && (
            <div className="overflow-x-auto">
              <div className="text-sm font-medium text-slate-700 mb-1">按关系类型</div>
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100">
                    {['关系类型', 'Precision', 'Recall', 'F1', '黄金集', '预测集'].map(h => (
                      <th key={h} className="border border-slate-200 px-2 py-1 text-left">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(report.per_relation).map(([rel, s]) => (
                    <tr key={rel} className="hover:bg-slate-50">
                      <td className="border border-slate-200 px-2 py-1 font-medium">{rel}</td>
                      <td className="border border-slate-200 px-2 py-1">{fmt(s.precision)}</td>
                      <td className="border border-slate-200 px-2 py-1">{fmt(s.recall)}</td>
                      <td className="border border-slate-200 px-2 py-1 font-semibold">{fmt(s.f1)}</td>
                      <td className="border border-slate-200 px-2 py-1">{s.golden_count}</td>
                      <td className="border border-slate-200 px-2 py-1">{s.predicted_count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* 对比表格 */}
          {report.comparison.length > 0 && (
            <div className="overflow-x-auto">
              <div className="flex items-center justify-between mb-1">
                <div className="text-sm font-medium text-slate-700">三元组对比</div>
                <div className="flex gap-2 text-xs">
                  {(['all', 'unmatched'] as FilterMode[]).map(f => (
                    <button
                      key={f}
                      onClick={() => setFilter(f)}
                      className={`px-2 py-0.5 rounded border ${filter === f ? 'bg-slate-700 text-white border-slate-700' : 'border-slate-300 text-slate-600'}`}
                    >
                      {f === 'all' ? '全部' : '仅未命中'}
                    </button>
                  ))}
                </div>
              </div>
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-100">
                    {['头实体', '关系', '尾实体', '置信度', '命中'].map(h => (
                      <th key={h} className="border border-slate-200 px-2 py-1 text-left">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {filteredComparison.map((t, i) => (
                    <tr key={i} className={t.matched ? 'bg-green-50' : 'bg-red-50'}>
                      <td className="border border-slate-200 px-2 py-1">{t.head}</td>
                      <td className="border border-slate-200 px-2 py-1">{t.relation}</td>
                      <td className="border border-slate-200 px-2 py-1">{t.tail}</td>
                      <td className="border border-slate-200 px-2 py-1">{t.confidence.toFixed(2)}</td>
                      <td className={`border border-slate-200 px-2 py-1 font-medium ${t.matched ? 'text-green-600' : 'text-red-500'}`}>
                        {t.matched ? '✓' : '✗'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
