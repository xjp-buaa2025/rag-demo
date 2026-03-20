// ============================================================
// 共享 TypeScript 类型定义
// 对应后端 backend/routers/ 各接口的请求/响应结构
// ============================================================

/** 聊天消息（对应后端 MessageItem） */
export interface Message {
  role: 'user' | 'assistant'
  content: string
}

/** 检索结果文档块（对应 /retrieve 响应） */
export interface Chunk {
  text: string
  source: string
  page: number
  distance: number
  chunk_type?: 'text' | 'image'    // 图文双路检索新增
  image_url?: string               // 图片块的访问 URL（/images/{filename}）
}

/** /health 响应 */
export interface HealthResponse {
  status: string
  collection_count: number
  model: string
}

/** /ingest/status 响应 */
export interface IngestStatus {
  count: number
}

/** /bom/status 响应 */
export interface BomStatus {
  connected: boolean
  nodes?: number
  edges?: number
  uri: string
  error?: string
}

/** SSE 日志帧（/ingest、/eval/*、/bom/ingest） */
export interface SseLogFrame {
  log: string
}

/** SSE 聊天增量帧（/chat、/assembly/chat 中间帧） */
export interface SseDeltaFrame {
  delta: string
}

/** SSE 聊天完成帧（/chat、/assembly/chat 最后一帧） */
export interface SseDoneFrame {
  done: true
  sources_md: string
  image_urls?: string[]            // 本次回答关联的图片 URL 列表（图文检索新增）
}

/** SSE 错误帧 */
export interface SseErrorFrame {
  error: string
}

/** SSE 所有帧类型联合（用于泛型解析） */
export type SseFrame = SseLogFrame | SseDeltaFrame | SseDoneFrame | SseErrorFrame
