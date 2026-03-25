// ============================================================
// API 客户端层
//
// 所有后端接口的唯一调用入口。
// 前端请求 /api/xxx，Vite 代理自动转发到 localhost:8000/xxx。
//
// SSE 接口返回 AsyncGenerator，调用方用 for await...of 消费。
// 非 SSE 接口返回普通 Promise<T>。
// ============================================================

import type { HealthResponse, IngestStatus, BomStatus, Chunk, Message, SseFrame } from '../types'

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
export function postChat(message: string, history: Message[]) {
  return postSSE('/chat', { message, history })
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
  return postSSE('/assembly/chat', { message, history })
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
