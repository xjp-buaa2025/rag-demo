// ============================================================
// API 客户端层
//
// 所有后端接口的唯一调用入口。
// 前端请求 /api/xxx，Vite 代理自动转发到 localhost:8000/xxx。
//
// SSE 接口返回 AsyncGenerator，调用方用 for await...of 消费。
// 非 SSE 接口返回普通 Promise<T>。
// ============================================================

import type { HealthResponse, IngestStatus, BomStatus, Chunk, Message, SseFrame, KgGraphData, KgTaskCreateResponse, KgTaskStatus, StagesStatus, TriplesPreview, ValidationReport, KgSseFrame, SyncNeo4jResult } from '../types'

const BASE = '/api'

// ----------------------------------------------------------
// 通用辅助：POST SSE 流（返回 AsyncGenerator）
// 之所以不用 EventSource：EventSource 只支持 GET，
// 后端所有 SSE 接口都是 POST，必须用 fetch + ReadableStream。
// ----------------------------------------------------------
export async function* postSSE(
  path: string,
  body?: object | FormData,
): AsyncGenerator<SseFrame> {
  const isForm = body instanceof FormData
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: isForm ? {} : { 'Content-Type': 'application/json' },
    body: isForm ? body : body ? JSON.stringify(body) : undefined,
  })

  if (!res.ok || !res.body) {
    throw new Error(`HTTP ${res.status}: ${await res.text()}`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buf = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buf += decoder.decode(value, { stream: true })

    // 按 \n 拆分，保留最后一个不完整行
    const lines = buf.split('\n')
    buf = lines.pop()! // 最后一行可能不完整，留到下次

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const payload = line.slice(6).trim()
      if (payload === '[DONE]') return     // 日志流结束信号
      yield JSON.parse(payload) as SseFrame
    }
  }
}

// ----------------------------------------------------------
// 健康检查
// ----------------------------------------------------------
export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${BASE}/health`)
  return res.json()
}

// ----------------------------------------------------------
// 知识库入库状态
// ----------------------------------------------------------
export async function getIngestStatus(): Promise<IngestStatus> {
  const res = await fetch(`${BASE}/ingest/status`)
  return res.json()
}

// ----------------------------------------------------------
// 知识库入库（SSE）
// ----------------------------------------------------------
export function postIngest(clearFirst: boolean) {
  return postSSE('/ingest', { clear_first: clearFirst })
}

// ----------------------------------------------------------
// 向量检索（JSON）
// ----------------------------------------------------------
export async function postRetrieve(query: string, topK = 4): Promise<{ chunks: Chunk[] }> {
  const res = await fetch(`${BASE}/retrieve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, top_k: topK }),
  })
  return res.json()
}

// ----------------------------------------------------------
// RAG 问答（SSE）
// ----------------------------------------------------------
export function postChat(
  message: string,
  history: Message[],
  imageChunks?: Array<{ text: string; source: string; page: number; distance: number; image_url?: string }>
) {
  return postSSE('/chat', {
    message,
    history,
    ...(imageChunks && imageChunks.length > 0 ? { image_chunks: imageChunks } : {}),
  })
}

// ----------------------------------------------------------
// 评估接口（SSE）
// ----------------------------------------------------------
export function postEvalRetrieval()  { return postSSE('/eval/retrieval') }
export function postEvalGeneration() { return postSSE('/eval/generation') }
export function postEvalRagas()      { return postSSE('/eval/ragas') }

// ----------------------------------------------------------
// BOM 状态检查（JSON）
// ----------------------------------------------------------
export async function getBomStatus(): Promise<BomStatus> {
  const res = await fetch(`${BASE}/bom/status`)
  return res.json()
}

// ----------------------------------------------------------
// BOM 入库（multipart SSE）
// ----------------------------------------------------------
export function postBomIngest(file: File | null, clearFirst: boolean) {
  const form = new FormData()
  if (file) form.append('file', file)
  form.append('clear_first', String(clearFirst))
  return postSSE('/bom/ingest', form)
}

// ----------------------------------------------------------
// LangGraph 管道入库（单文件 RAG，multipart SSE）
// ----------------------------------------------------------
export function postIngestPipeline(file: File, clearFirst: boolean) {
  const form = new FormData()
  form.append('file', file)
  form.append('clear_first', String(clearFirst))
  return postSSE('/ingest/pipeline', form)
}

// ----------------------------------------------------------
// LangGraph 管道 BOM 入库（multipart SSE）
// ----------------------------------------------------------
export function postBomIngestPipeline(file: File | null, clearFirst: boolean) {
  const form = new FormData()
  if (file) form.append('file', file)
  form.append('clear_first', String(clearFirst))
  return postSSE('/bom/ingest/pipeline', form)
}

// ----------------------------------------------------------
// 装配方案问答（SSE）
// ----------------------------------------------------------
export function postAssemblyChat(message: string, history: Message[]) {
  return postSSE('/assembly/agent', { message, history })
}

// ----------------------------------------------------------
// 知识图谱可视化数据（JSON）
// ----------------------------------------------------------
export async function getKgGraph(keyword?: string, limit?: number): Promise<KgGraphData> {
  const params = new URLSearchParams()
  if (keyword) params.set('keyword', keyword)
  if (limit) params.set('limit', String(limit))
  const qs = params.toString()
  const res = await fetch(`${BASE}/bom/kg/graph${qs ? `?${qs}` : ''}`)
  return res.json()
}

// ----------------------------------------------------------
// 联合 KG 构建任务接口
// ----------------------------------------------------------

/** POST /kg/task/create — 创建任务，返回 task_id */
export async function kgTaskCreate(): Promise<KgTaskCreateResponse> {
  const res = await fetch(`${BASE}/kg/task/create`, { method: 'POST' })
  if (!res.ok) throw new Error(`创建 KG 任务失败: ${res.status}`)
  return res.json()
}

/**
 * POST /kg/task/{taskId}/upload — 上传单文件并处理（SSE）
 * stage: 'bom' | 'cad' | 'manual'
 */
export function kgTaskUpload(taskId: string, stage: 'bom' | 'cad' | 'manual', file: File, clearFirst = false) {
  const form = new FormData()
  form.append('stage', stage)
  form.append('file', file)
  form.append('clear_first', String(clearFirst))
  return postSSE(`/kg/task/${taskId}/upload`, form)
}

/** POST /kg/task/{taskId}/merge — 触发三源合并+写库（SSE），无需 body */
export function kgTaskMerge(taskId: string) {
  return postSSE(`/kg/task/${taskId}/merge`)
}

/** GET /kg/task/{taskId}/status — 查询各阶段完成情况 */
export async function kgTaskStatus(taskId: string): Promise<KgTaskStatus> {
  const res = await fetch(`${BASE}/kg/task/${taskId}/status`)
  if (!res.ok) throw new Error(`查询 KG 任务状态失败: ${res.status}`)
  return res.json()
}

// ----------------------------------------------------------
// KG 分阶段构建接口
// ----------------------------------------------------------

export async function* postKgStage1(file: File, clearFirst = false): AsyncGenerator<KgSseFrame> {
  const form = new FormData()
  form.append('file', file)
  form.append('clear_first', String(clearFirst))
  yield* postSSE('/kg/stage1/bom', form) as AsyncGenerator<KgSseFrame>
}

export async function* postKgStage2(file: File): AsyncGenerator<KgSseFrame> {
  const form = new FormData()
  form.append('file', file)
  yield* postSSE('/kg/stage2/manual', form) as AsyncGenerator<KgSseFrame>
}

export async function* postKgStage3(files: File[]): AsyncGenerator<KgSseFrame> {
  const form = new FormData()
  files.forEach(f => form.append('files', f))
  yield* postSSE('/kg/stage3/cad', form) as AsyncGenerator<KgSseFrame>
}

export async function postKgStage4Validate(): Promise<ValidationReport> {
  const res = await fetch(`${BASE}/kg/stage4/validate`, { method: 'POST' })
  if (!res.ok) throw new Error(`验证失败: ${res.status}`)
  return res.json()
}

export async function getKgStagesStatus(): Promise<StagesStatus> {
  const res = await fetch(`${BASE}/kg/stages/status`)
  return res.json()
}

export async function getKgStagePreview(
  stage: string, offset = 0, limit = 50
): Promise<TriplesPreview> {
  const res = await fetch(`${BASE}/kg/stages/${stage}/preview?offset=${offset}&limit=${limit}`)
  return res.json()
}

export async function postKgSyncNeo4j(): Promise<SyncNeo4jResult> {
  const res = await fetch(`${BASE}/kg/stages/sync-neo4j`, { method: 'POST' })
  return res.json()
}

// ----------------------------------------------------------
// 视觉接口：上传图片获取描述（用于以图搜文）
// ----------------------------------------------------------
export async function postVisionDescribe(file: File): Promise<{ description: string; query_text: string }> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE}/vision/describe`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Vision API 调用失败: ${res.status}`)
  return res.json()
}

// ----------------------------------------------------------
// 视觉接口：上传图片直接 CLIP 以图搜图（JSON）
// ----------------------------------------------------------
export async function postVisionSearch(file: File, topK = 4): Promise<{
  results: Array<{ text: string; source: string; page: number; distance: number; image_url?: string }>
}> {
  const form = new FormData()
  form.append('file', file)
  form.append('top_k', String(topK))
  const res = await fetch(`${BASE}/vision/search?top_k=${topK}`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`Vision Search 失败: ${res.status}`)
  return res.json()
}
