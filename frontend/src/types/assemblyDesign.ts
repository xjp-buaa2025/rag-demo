// Types for /assembly-design/* endpoints

export interface SchemeMeta {
  scheme_id: string
  created_at: string
  subject: {
    system: string
    system_en?: string
    scope: string[]
    design_intent: string
    constraints: Record<string, string>
  }
  stages_done: string[]
}

export interface SchemeDetail extends SchemeMeta {
  stage1?: Record<string, unknown>
  stage2?: Record<string, unknown>
  stage3?: Record<string, unknown>
  stage4a?: Record<string, unknown>
  stage4b?: Record<string, unknown>
  stage5?: Record<string, unknown>
}

export type StageKey = '1' | '2' | '3' | '4a' | '4b' | '5'

export interface StageRunRequest {
  action: 'generate' | 'regenerate' | 'save_edits'
  payload?: Record<string, unknown>
  user_guidance?: string
}

export interface ExportResult {
  export_path: string
  content_md: string
}

export interface CreateSchemeRequest {
  subject_system: string
  subject_system_en?: string
  subject_scope: string[]
  design_intent?: string
  constraints?: Record<string, string>
}
