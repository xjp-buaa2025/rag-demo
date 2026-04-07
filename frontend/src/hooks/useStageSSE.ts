import { useState, useCallback } from 'react'
import type { KgSseFrame } from '../types'

interface StageSSECallbacks {
  onLog:    (msg: string) => void
  onResult: (data: KgSseFrame) => void
  onDone:   (success: boolean) => void
  onError?: (msg: string) => void
}

export function useStageSSE() {
  const [loading, setLoading] = useState(false)

  const run = useCallback(async (
    gen: AsyncIterable<KgSseFrame>,
    callbacks: StageSSECallbacks
  ) => {
    setLoading(true)
    try {
      for await (const frame of gen) {
        if (!('type' in frame)) continue
        switch (frame.type) {
          case 'log':    callbacks.onLog(frame.message ?? ''); break
          case 'result': callbacks.onResult(frame); break
          case 'done':   callbacks.onDone(frame.success ?? true); break
          case 'error':  callbacks.onError?.(frame.message ?? '未知错误'); break
        }
      }
    } catch (e) {
      callbacks.onError?.(`SSE连接错误: ${e}`)
    } finally {
      setLoading(false)
    }
  }, [])

  return { run, loading }
}
