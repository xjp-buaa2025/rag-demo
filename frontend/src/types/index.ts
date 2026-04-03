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

/** BOM 实体结构化属性（对应后端 entity dict，chunk_type="bom_entity" 时存在） */
export interface BomEntityData {
  entity_type: 'Assembly' | 'Part' | 'Standard' | string
  part_id: string
  part_name: string
  part_name_en?: string
  qty?: number | null
  unit?: string
  material?: string
  weight_kg?: number | null
  spec?: string
  note?: string
  level_code?: string
  parent_id?: string | null
  parent_name?: string | null
}

/** BOM 关系结构化信息（对应后端 relation dict，chunk_type="bom_relation" 时存在） */
export interface BomRelationData {
  rel_type: string        // "CHILD_OF" | "precedes" | "requires" | ...
  from_type: string
  from_id: string
  from_name: string
  to_type: string
  to_id: string
  to_name: string
}

/** 单条引用来源（对应后端 Citation dict） */
export interface Citation {
  id: number
  source: string
  page: number
  chunk_type: 'text' | 'image' | 'flowchart_node' | 'flowchart_path' | 'bom_entity' | 'bom_relation' | 'bom' | string
  text: string
  image_url?: string | null
  /** BOM 实体结构化属性（仅 chunk_type="bom_entity" 时存在） */
  bom_entity?: BomEntityData
  /** BOM 关系结构化信息（仅 chunk_type="bom_relation" 时存在） */
  bom_relation?: BomRelationData
}

/** SSE 聊天完成帧（/chat、/assembly/chat 最后一帧） */
export interface SseDoneFrame {
  done: true
  sources: Citation[]              // 结构化来源列表（供溯源侧边栏使用）
  image_urls?: string[]            // 图片块 URL 列表（从 sources 中提取）
}

/** SSE 错误帧 */
export interface SseErrorFrame {
  error: string
}

/** SSE 阶段状态帧（/chat 流程阶段提示，如"正在向量检索知识库..."） */
export interface SseStageFrame {
  stage: string
}

/** SSE 所有帧类型联合（用于泛型解析） */
export type SseFrame = SseLogFrame | SseDeltaFrame | SseDoneFrame | SseErrorFrame | SseStageFrame

// ============================================================
// 知识图谱可视化类型（对应 GET /bom/kg/graph 响应）
// ============================================================

/** 知识图谱节点 */
export interface KgNode {
  id: string
  label: string
  type: string  // Part | Assembly | Procedure | Tool | Specification | Interface
  [key: string]: unknown
}

/** 知识图谱关系边 */
export interface KgLink {
  source: string
  target: string
  type: string  // CHILD_OF | precedes | participatesIn | requires | specifiedBy | matesWith | ...
}

/** GET /bom/kg/graph 响应 */
export interface KgGraphData {
  nodes: KgNode[]
  links: KgLink[]
  error?: string
}

// ============================================================
// 联合 KG 构建任务类型（对应 /kg/task/* 端点）
// ============================================================

/** POST /kg/task/create 响应 */
export interface KgTaskCreateResponse {
  task_id: string
  status: 'created'
}

/** GET /kg/task/{id}/status 响应 */
export interface KgTaskStatus {
  task_id: string
  stages_done: Array<'bom' | 'cad' | 'manual'>
  created_at: string
  expires_at: string
}
