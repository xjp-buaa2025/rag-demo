import type {
  SchemeMeta,
  SchemeDetail,
  StageKey,
  StageRunRequest,
  ExportResult,
  CreateSchemeRequest,
} from '../types/assemblyDesign'

const BASE = '/api/assembly-design'

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`HTTP ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export function listSchemes(): Promise<{ schemes: SchemeMeta[] }> {
  return apiFetch('/scheme/list')
}

export function createScheme(
  req: CreateSchemeRequest,
): Promise<{ scheme_id: string; meta: SchemeMeta }> {
  return apiFetch('/scheme/new', {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function getScheme(id: string): Promise<SchemeDetail> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}`)
}

export function runStage(
  id: string,
  key: StageKey,
  req: StageRunRequest,
): Promise<Record<string, unknown>> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}/stage/${key}`, {
    method: 'POST',
    body: JSON.stringify(req),
  })
}

export function exportScheme(id: string): Promise<ExportResult> {
  return apiFetch(`/scheme/${encodeURIComponent(id)}/export`)
}
