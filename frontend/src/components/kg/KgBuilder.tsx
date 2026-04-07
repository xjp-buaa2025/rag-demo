// ============================================================
// KgBuilder — 知识图谱联合构建面板
//
// 三阶段 API 流程（/kg/task/*）：
//   1. POST /kg/task/create          → 创建任务，获得 task_id
//   2. POST /kg/task/{id}/upload     → 依次上传 BOM → CAD → 手册（stage 参数）
//   3. POST /kg/task/{id}/merge      → 触发三源合并 + Neo4j 写库
//
// 每个 upload/merge 步骤均以 SSE 实时推送日志。
// ============================================================

import { useRef, useState, useEffect } from 'react'
import { getBomStatus, kgTaskCreate, kgTaskUpload, kgTaskMerge } from '../../api/client'
import { usePostSSE } from '../../hooks/usePostSSE'
import type { BomStatus } from '../../types'

const FILE_TYPES = {
  rag: { label: '维修手册', accept: '.pdf,.md,.txt,.docx', desc: 'PDF / Markdown / TXT / DOCX' },
  bom: { label: 'BOM 清单', accept: '.xlsx,.xls,.csv,.pdf,.docx', desc: 'Excel / CSV / PDF / DOCX' },
  cad: { label: 'CAD 模型', accept: '.step,.stp', desc: 'STEP / STP' },
}

const CATEGORY_ICONS: Record<FileCategory, string> = {
  rag: '📖',
  bom: '🔩',
  cad: '📦',
}

type FileCategory = keyof typeof FILE_TYPES

// BOM(0) → CAD(1) → RAG(2)，确保权威数据先入库
const CATEGORY_ORDER: Record<FileCategory, number> = { bom: 0, cad: 1, rag: 2 }

const categoryColors: Record<FileCategory, string> = {
  rag: 'bg-blue-100 text-blue-700 border-blue-300',
  bom: 'bg-emerald-100 text-emerald-700 border-emerald-300',
  cad: 'bg-purple-100 text-purple-700 border-purple-300',
}

const categoryBorderColors: Record<FileCategory, string> = {
  rag: 'border-blue-200 bg-blue-50/30',
  bom: 'border-emerald-200 bg-emerald-50/30',
  cad: 'border-purple-200 bg-purple-50/30',
}

function detectCategory(filename: string): FileCategory {
  const ext = filename.split('.').pop()?.toLowerCase() ?? ''
  if (['step', 'stp'].includes(ext)) return 'cad'
  if (['xlsx', 'xls', 'csv'].includes(ext)) return 'bom'
  return 'rag'
}

interface FileEntry {
  file: File
  category: FileCategory
}

interface KgBuilderProps {
  onBuildComplete?: () => void
}

const CATEGORIES: FileCategory[] = ['rag', 'bom', 'cad']

// stage 标签到 API stage 参数的映射
const CATEGORY_TO_STAGE: Record<FileCategory, 'bom' | 'cad' | 'manual'> = {
  bom: 'bom',
  cad: 'cad',
  rag: 'manual',
}

// 阶段进度展示文案
const STAGE_LABELS: Record<string, string> = {
  bom:    '📋 BOM 解析',
  cad:    '📦 CAD 解析',
  manual: '📖 手册解析',
  merge:  '🔗 三源合并',
}

export default function KgBuilder({ onBuildComplete }: KgBuilderProps) {
  const [neo4jStatus, setNeo4jStatus] = useState<BomStatus | null>(null)
  const [checking, setChecking] = useState(false)
  const [files, setFiles] = useState<FileEntry[]>([])
  // 当前阶段标签，用于 UI 展示
  const [currentStage, setCurrentStage] = useState<string>('')
  const ragRef = useRef<HTMLInputElement>(null)
  const bomRef = useRef<HTMLInputElement>(null)
  const cadRef = useRef<HTMLInputElement>(null)
  const fileInputRefs: Record<FileCategory, typeof ragRef> = {
    rag: ragRef,
    bom: bomRef,
    cad: cadRef,
  }
  const { run, log, loading, clear } = usePostSSE()

  useEffect(() => {
    getBomStatus()
      .then(setNeo4jStatus)
      .catch(() => setNeo4jStatus({ connected: false, uri: '', error: '无法连接后端' }))
  }, [])

  const handleCheck = async () => {
    setChecking(true)
    try {
      setNeo4jStatus(await getBomStatus())
    } catch (e) {
      setNeo4jStatus({ connected: false, uri: '', error: String(e) })
    } finally {
      setChecking(false)
    }
  }

  // forcedCategory：从某个栏的按钮触发时，以该栏类别为准（避免 .docx/.pdf 被误归 RAG）
  const addFiles = (fileList: FileList, forcedCategory?: FileCategory) => {
    const existing = new Set(files.map(f => f.file.name))
    const toAdd = Array.from(fileList)
      .filter(f => !existing.has(f.name))
      .map(f => ({ file: f, category: forcedCategory ?? detectCategory(f.name) }))
    setFiles(prev => [...prev, ...toAdd])
  }

  const removeFile = (idx: number) => {
    setFiles(prev => prev.filter((_, i) => i !== idx))
  }

  const handleBuild = async (clearFirst: boolean) => {
    if (files.length === 0) return
    clear()
    setCurrentStage('')

    // Step 1: 创建任务
    let taskId: string
    try {
      const res = await kgTaskCreate()
      taskId = res.task_id
    } catch (e) {
      // 在日志区显示错误（借用 run 的错误路径）
      await run((async function* () { throw e })())
      return
    }

    // Step 2: 按 BOM → CAD → 手册 顺序依次 upload
    const sorted = [...files].sort((a, b) => CATEGORY_ORDER[a.category] - CATEGORY_ORDER[b.category])
    for (let i = 0; i < sorted.length; i++) {
      const { file, category } = sorted[i]
      const stage = CATEGORY_TO_STAGE[category]
      const shouldClear = clearFirst && i === 0
      setCurrentStage(stage)
      await run(kgTaskUpload(taskId, stage, file, shouldClear))
    }

    // Step 3: 触发三源合并写库
    setCurrentStage('merge')
    await run(kgTaskMerge(taskId))

    setCurrentStage('')
    onBuildComplete?.()
  }

  const filesInCategory = (cat: FileCategory) => files.filter(f => f.category === cat)

  return (
    <div className="space-y-3">
      {/* Neo4j 状态行 */}
      <div className="flex items-center gap-3 text-sm">
        <button
          onClick={handleCheck}
          disabled={checking}
          className="px-3 py-1.5 text-xs bg-emerald-600 text-white rounded-md hover:bg-emerald-700 disabled:opacity-50 transition-colors"
        >
          {checking ? '检测中…' : '检测 Neo4j'}
        </button>
        {neo4jStatus && (
          neo4jStatus.connected ? (
            <span className="text-xs text-emerald-600">
              Neo4j 已连接 — 节点 {neo4jStatus.nodes} / 关系 {neo4jStatus.edges} — {neo4jStatus.uri}
            </span>
          ) : (
            <span className="text-xs text-red-500">
              Neo4j 未连接{neo4jStatus.error ? `：${neo4jStatus.error}` : ''} — 请执行 <code className="bg-red-50 px-1 rounded">docker start neo4j</code>
            </span>
          )
        )}
      </div>

      {/* 三栏卡片 */}
      <div className="grid grid-cols-3 gap-3">
        {CATEGORIES.map(cat => (
          <div
            key={cat}
            className={`border rounded-lg p-3 flex flex-col gap-2 ${categoryBorderColors[cat]}`}
          >
            {/* 栏头 */}
            <div className="flex items-center justify-between gap-2">
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full border shrink-0 ${categoryColors[cat]}`}>
                {CATEGORY_ICONS[cat]} {FILE_TYPES[cat].label}
              </span>
              <button
                onClick={() => fileInputRefs[cat].current?.click()}
                disabled={loading}
                className="text-xs px-2 py-0.5 border border-slate-300 rounded hover:bg-white disabled:opacity-50 transition-colors bg-white/70 shrink-0"
              >
                + 添加
              </button>
            </div>

            {/* 格式说明 */}
            <p className="text-[10px] text-slate-400 leading-tight">{FILE_TYPES[cat].desc}</p>

            {/* 隐藏 input */}
            <input
              ref={fileInputRefs[cat]}
              type="file"
              multiple
              accept={FILE_TYPES[cat].accept}
              className="hidden"
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) addFiles(e.target.files, cat)
                e.target.value = ''
              }}
            />

            {/* 文件列表 */}
            <div className="flex-1 min-h-[36px] space-y-1">
              {filesInCategory(cat).length === 0 ? (
                <p className="text-[10px] text-slate-300 italic pt-1">暂无文件</p>
              ) : (
                filesInCategory(cat).map((entry) => {
                  const globalIdx = files.indexOf(entry)
                  return (
                    <div
                      key={entry.file.name}
                      className="flex items-center gap-1 py-0.5 px-1.5 bg-white/80 rounded text-xs"
                    >
                      <span className="truncate flex-1 text-slate-700">{entry.file.name}</span>
                      <button
                        onClick={() => removeFile(globalIdx)}
                        disabled={loading}
                        className="text-red-400 hover:text-red-600 disabled:opacity-40 shrink-0"
                      >
                        ✕
                      </button>
                    </div>
                  )
                })
              )}
            </div>
          </div>
        ))}
      </div>

      {/* 提示文字 */}
      <p className="text-[10px] text-slate-400">
        流程：创建任务 → BOM 解析 → CAD 解析 → 手册解析 → 三源合并写库
      </p>

      {/* 构建按钮 */}
      <div className="flex gap-2">
        <button
          onClick={() => handleBuild(false)}
          disabled={loading || files.length === 0}
          className="flex-1 px-3 py-2 text-sm bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {loading
            ? `⏳ ${STAGE_LABELS[currentStage] ?? '处理中'}…`
            : `🔨 构建图谱（增量）${files.length > 0 ? ` · ${files.length} 个文件` : ''}`}
        </button>
        <button
          onClick={() => handleBuild(true)}
          disabled={loading || files.length === 0}
          className="px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          清空重建
        </button>
      </div>

      {/* 阶段进度条（构建中才显示） */}
      {loading && currentStage && (
        <div className="flex items-center gap-2 text-xs text-slate-500">
          {(['bom', 'cad', 'manual', 'merge'] as const).map((s) => (
            <span
              key={s}
              className={`px-2 py-0.5 rounded-full border transition-colors ${
                s === currentStage
                  ? 'bg-indigo-100 text-indigo-700 border-indigo-300 font-medium'
                  : 'bg-slate-50 text-slate-400 border-slate-200'
              }`}
            >
              {STAGE_LABELS[s]}
            </span>
          ))}
        </div>
      )}

      {/* 入库日志 */}
      {log && (
        <pre className="text-xs bg-slate-900 text-slate-100 rounded-md p-3 max-h-48 overflow-y-auto whitespace-pre-wrap leading-relaxed">
          {log}
        </pre>
      )}
    </div>
  )
}
