// ============================================================
// usePostSSE — 通用 POST SSE Hook
//
// 用法：
//   const { run, log, loading } = usePostSSE()
//   run(postIngest(false))        // 传入一个 AsyncGenerator
//
// 适用于日志类 SSE（/ingest、/eval/*、/bom/ingest）：
//   每帧是 {log: "完整快照"}，覆盖式显示。
// ============================================================

import { useState, useRef, useCallback } from 'react'
import type { SseFrame, SseLogFrame } from '../types'

interface UsePostSSEResult {
  /** 启动一个 SSE 流，传入从 api/client.ts 返回的 AsyncGenerator */
  run: (gen: AsyncGenerator<SseFrame>) => Promise<void>
  /** 当前日志内容（覆盖式，每帧替换） */
  log: string
  /** 是否正在流式接收 */
  loading: boolean
  /** 清空日志 */
  clear: () => void
}

export function usePostSSE(): UsePostSSEResult {
  const [log, setLog] = useState('')
  const [loading, setLoading] = useState(false)
  const abortRef = useRef(false)

  const run = useCallback(async (gen: AsyncGenerator<SseFrame>) => {
    abortRef.current = false
    setLoading(true)
    setLog('')
    try {
      for await (const frame of gen) {
        if (abortRef.current) break
        if ('log' in frame) {
          setLog((frame as SseLogFrame).log)
        }
      }
    } catch (e) {
      setLog((prev) => prev + `\n❌ 错误：${e}`)
    } finally {
      setLoading(false)
    }
  }, [])

  const clear = useCallback(() => setLog(''), [])

  return { run, log, loading, clear }
}
