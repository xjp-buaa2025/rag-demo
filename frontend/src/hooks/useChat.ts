// ============================================================
// useChat — 聊天状态管理 Hook
//
// 封装：
//   - messages: 完整对话历史列表
//   - streaming: 当前流式输出中的 assistant 消息内容
//   - sourcesmd: 最新回复的来源 Markdown（脚注）
//   - sendMessage: 发送消息，消费 AsyncGenerator<SseFrame>
//
// 适用于 /chat 和 /assembly/chat（delta 增量帧 + done 完成帧）。
// ============================================================

import { useState, useCallback } from 'react'
import type { Message, SseFrame, SseDeltaFrame, SseDoneFrame, SseErrorFrame } from '../types'

interface UseChatResult {
  messages: Message[]
  /** 当前正在流式输出的文本（streaming 期间显示，done 后归档到 messages） */
  streamingText: string
  /** 最新回复的来源脚注 Markdown */
  sourcesMd: string
  loading: boolean
  sendMessage: (
    userText: string,
    gen: AsyncGenerator<SseFrame>,
  ) => Promise<void>
  clearMessages: () => void
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingText, setStreamingText] = useState('')
  const [sourcesMd, setSourcesMd] = useState('')
  const [loading, setLoading] = useState(false)

  const sendMessage = useCallback(
    async (userText: string, gen: AsyncGenerator<SseFrame>) => {
      // 1. 把用户消息追加到历史
      const userMsg: Message = { role: 'user', content: userText }
      setMessages((prev) => [...prev, userMsg])
      setStreamingText('')
      setSourcesMd('')
      setLoading(true)

      let accumulated = ''
      try {
        for await (const frame of gen) {
          if ('delta' in frame) {
            // 增量帧：累积文本，实时展示
            accumulated += (frame as SseDeltaFrame).delta
            setStreamingText(accumulated)
          } else if ('done' in frame) {
            // 完成帧：从 streaming 区归档到 messages，提取来源
            const done = frame as SseDoneFrame
            setSourcesMd(done.sources_md ?? '')
            setMessages((prev) => [
              ...prev,
              { role: 'assistant', content: accumulated },
            ])
            setStreamingText('')
          } else if ('error' in frame) {
            const err = (frame as SseErrorFrame).error
            setMessages((prev) => [
              ...prev,
              { role: 'assistant', content: `❌ ${err}` },
            ])
            setStreamingText('')
          }
        }
      } catch (e) {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: `❌ 连接错误：${e}` },
        ])
        setStreamingText('')
      } finally {
        setLoading(false)
      }
    },
    [],
  )

  const clearMessages = useCallback(() => {
    setMessages([])
    setStreamingText('')
    setSourcesMd('')
  }, [])

  return { messages, streamingText, sourcesMd, loading, sendMessage, clearMessages }
}
