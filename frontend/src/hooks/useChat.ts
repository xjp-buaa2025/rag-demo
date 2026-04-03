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
import type { Message, Citation, SseFrame, SseDeltaFrame, SseDoneFrame, SseErrorFrame, SseStageFrame } from '../types'

interface UseChatResult {
  messages: Message[]
  /** 当前正在流式输出的文本（streaming 期间显示，done 后归档到 messages） */
  streamingText: string
  /** 最新回复的结构化来源列表（供溯源侧边栏使用） */
  sources: Citation[]
  /** 最新回复关联的图片 URL 列表（图文检索） */
  imageUrls: string[]
  loading: boolean
  /** 当前执行阶段描述（loading 期间有值，首个 token 或 done 后清空） */
  currentStage: string
  sendMessage: (
    userText: string,
    gen: AsyncGenerator<SseFrame>,
  ) => Promise<void>
  clearMessages: () => void
}

export function useChat(): UseChatResult {
  const [messages, setMessages] = useState<Message[]>([])
  const [streamingText, setStreamingText] = useState('')
  const [sources, setSources] = useState<Citation[]>([])
  const [imageUrls, setImageUrls] = useState<string[]>([])
  const [loading, setLoading] = useState(false)
  const [currentStage, setCurrentStage] = useState('')

  const sendMessage = useCallback(
    async (userText: string, gen: AsyncGenerator<SseFrame>) => {
      // 1. 把用户消息追加到历史
      const userMsg: Message = { role: 'user', content: userText }
      setMessages((prev) => [...prev, userMsg])
      setStreamingText('')
      setSources([])
      setCurrentStage('')
      setLoading(true)

      let accumulated = ''
      try {
        for await (const frame of gen) {
          if ('stage' in frame) {
            // 阶段帧：更新当前执行阶段描述
            setCurrentStage((frame as SseStageFrame).stage)
          } else if ('delta' in frame) {
            // 增量帧：累积文本，实时展示（stage 保留至 done 帧才清空）
            accumulated += (frame as SseDeltaFrame).delta
            setStreamingText(accumulated)
          } else if ('done' in frame) {
            // 完成帧：从 streaming 区归档到 messages，提取结构化来源和图片
            setCurrentStage('')
            const done = frame as SseDoneFrame
            setSources(done.sources ?? [])
            setImageUrls(done.image_urls ?? [])
            setMessages((prev) => [
              ...prev,
              { role: 'assistant', content: accumulated },
            ])
            setStreamingText('')
          } else if ('error' in frame) {
            setCurrentStage('')
            const err = (frame as SseErrorFrame).error
            setMessages((prev) => [
              ...prev,
              { role: 'assistant', content: `❌ ${err}` },
            ])
            setStreamingText('')
          }
        }
      } catch (e) {
        setCurrentStage('')
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', content: `❌ 连接错误：${e}` },
        ])
        setStreamingText('')
      } finally {
        setCurrentStage('')
        setLoading(false)
      }
    },
    [],
  )

  const clearMessages = useCallback(() => {
    setMessages([])
    setStreamingText('')
    setSources([])
    setImageUrls([])
    setCurrentStage('')
  }, [])

  return { messages, streamingText, sources, imageUrls, loading, currentStage, sendMessage, clearMessages }
}
