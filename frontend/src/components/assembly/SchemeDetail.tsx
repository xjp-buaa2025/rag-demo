import { useState, useEffect, useCallback } from 'react'
import { getScheme, runStage, exportScheme } from '../../api/assemblyDesign'
import type { SchemeDetail as SchemeDetailType, StageKey } from '../../types/assemblyDesign'
import StageCard from './StageCard'

interface StageConfig {
  key: StageKey
  title: string
  prerequisite: StageKey | null
  prerequisiteLabel: string | null
}

const STAGES: StageConfig[] = [
  { key: '1',  title: 'S1 任务调研',  prerequisite: null,  prerequisiteLabel: null },
  { key: '2',  title: 'S2 需求分析',  prerequisite: '1',   prerequisiteLabel: 'S1' },
  { key: '3',  title: 'S3 概念架构',  prerequisite: '2',   prerequisiteLabel: 'S2' },
  { key: '4a', title: 'S4a 工序总表', prerequisite: '3',   prerequisiteLabel: 'S3' },
  { key: '4b', title: 'S4b 工装规划', prerequisite: '4a',  prerequisiteLabel: 'S4a' },
  { key: '5',  title: 'S5 评审导出',  prerequisite: '4b',  prerequisiteLabel: 'S4b' },
]

const STAGE_DATA_KEY: Record<StageKey, keyof SchemeDetailType> = {
  '1': 'stage1', '2': 'stage2', '3': 'stage3',
  '4a': 'stage4a', '4b': 'stage4b', '5': 'stage5',
}

interface Props {
  schemeId: string
}

export default function SchemeDetail({ schemeId }: Props) {
  const [scheme, setScheme] = useState<SchemeDetailType | null>(null)
  const [loadingStage, setLoadingStage] = useState<StageKey | null>(null)
  const [stageError, setStageError] = useState<Partial<Record<StageKey, string>>>({})
  const [exportContent, setExportContent] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)

  const refresh = useCallback(() => {
    getScheme(schemeId).then(setScheme).catch(() => {})
  }, [schemeId])

  useEffect(() => { refresh() }, [refresh])

  const handleGenerate = async (key: StageKey) => {
    setLoadingStage(key)
    setStageError(prev => ({ ...prev, [key]: undefined }))
    try {
      await runStage(schemeId, key, { action: 'generate' })
      refresh()
    } catch (err) {
      setStageError(prev => ({
        ...prev,
        [key]: err instanceof Error ? err.message : '生成失败',
      }))
    } finally {
      setLoadingStage(null)
    }
  }

  const handleExport = async () => {
    setExporting(true)
    try {
      const result = await exportScheme(schemeId)
      setExportContent(result.content_md)
    } catch (err) {
      alert(err instanceof Error ? err.message : '导出失败')
    } finally {
      setExporting(false)
    }
  }

  if (!scheme) {
    return <div className="p-8 text-slate-400 text-sm">加载中…</div>
  }

  const doneSet = new Set(scheme.stages_done)
  const s5Done = doneSet.has('5')

  return (
    <div className="p-4 space-y-3">
      {/* Scheme header */}
      <div className="border border-slate-200 rounded-lg p-4 bg-white">
        <div className="text-base font-semibold text-slate-800">{scheme.subject.system}</div>
        {scheme.subject.system_en && (
          <div className="text-xs text-slate-500">{scheme.subject.system_en}</div>
        )}
        <div className="mt-1 flex flex-wrap gap-3 text-xs text-slate-500">
          <span>设计意图：{scheme.subject.design_intent}</span>
          <span>范围：{scheme.subject.scope.join('、')}</span>
          <span>创建：{scheme.created_at.slice(0, 10)}</span>
          <span className="text-green-600 font-medium">
            已完成 {scheme.stages_done.length}/6 阶段
          </span>
        </div>
      </div>

      {/* Stage cards */}
      {STAGES.map(cfg => {
        const prereqDone = cfg.prerequisite === null || doneSet.has(cfg.prerequisite)
        const isDone = doneSet.has(cfg.key)
        const dataKey = STAGE_DATA_KEY[cfg.key]
        const stageData = scheme[dataKey] as Record<string, unknown> | undefined
        return (
          <div key={cfg.key}>
            <StageCard
              stageKey={cfg.key}
              title={cfg.title}
              isDone={isDone}
              stageData={stageData}
              prerequisiteDone={prereqDone}
              prerequisiteLabel={cfg.prerequisiteLabel}
              loading={loadingStage === cfg.key}
              onGenerate={() => handleGenerate(cfg.key)}
            />
            {stageError[cfg.key] && (
              <p className="text-xs text-red-600 mt-1 px-1">{stageError[cfg.key]}</p>
            )}
          </div>
        )
      })}

      {/* Export button */}
      <div className="pt-2 border-t border-slate-200">
        <button
          onClick={handleExport}
          disabled={!s5Done || exporting}
          title={!s5Done ? '请先完成 S5 评审' : undefined}
          className="px-4 py-2 text-sm bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {exporting ? '导出中…' : '📄 导出方案 MD'}
        </button>
        {exportContent && (
          <div className="mt-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-slate-600 font-medium">final_scheme.md 内容：</span>
              <button
                onClick={() => {
                  const blob = new Blob([exportContent], { type: 'text/markdown' })
                  const url = URL.createObjectURL(blob)
                  const a = document.createElement('a')
                  a.href = url
                  a.download = `${schemeId}_final_scheme.md`
                  a.click()
                  URL.revokeObjectURL(url)
                }}
                className="text-xs text-blue-600 hover:underline"
              >
                ⬇ 下载
              </button>
            </div>
            <pre className="text-xs bg-slate-900 text-green-300 p-3 rounded overflow-x-auto max-h-64 overflow-y-auto">
              {exportContent.slice(0, 2000)}{exportContent.length > 2000 ? '\n…（截断）' : ''}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}
