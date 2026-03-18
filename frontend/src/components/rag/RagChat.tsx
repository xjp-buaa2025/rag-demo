// ============================================================
// RagChat — RAG 知识库问答聊天框
//
// 对应 Gradio Tab 1 的 Chatbot + 输入框区域。
// 功能：
//   - 流式接收 LLM 回复（delta 增量追加）
//   - Markdown 渲染（react-markdown + remark-gfm）
//   - 发送完成后显示来源脚注
//   - 支持 Enter 提交（Shift+Enter 换行）
//   - 消息列表自动滚动到底部
// ============================================================

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChat } from '../../hooks/useChat'
import { postChat } from '../../api/client'

const EXAMPLES = [
  '涡轮发动机的基本工作原理是什么？',
  '压气机有哪些主要类型？',
  '燃烧室的设计需要满足哪些基本要求？',
]

export default function RagChat() {
  const { messages, streamingText, sourcesMd, loading, sendMessage, clearMessages } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  // 消息更新时自动滚到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    // history 传当前已有的对话记录（不含本次用户消息）
    await sendMessage(text, postChat(text, messages))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-white rounded-lg border border-slate-200 min-h-[420px] max-h-[520px]">
        {messages.length === 0 && !streamingText && (
          <div className="text-center text-slate-400 text-sm pt-8">
            <p className="text-2xl mb-2">🤖</p>
            <p>有什么想问的？可以从下方示例开始</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-100 text-slate-800'
              }`}
            >
              {msg.role === 'assistant' ? (
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown>
                </div>
              ) : (
                <span className="whitespace-pre-wrap">{msg.content}</span>
              )}
            </div>
          </div>
        ))}

        {/* 流式输出中的 assistant 消息 */}
        {streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[80%] rounded-2xl px-4 py-2 text-sm bg-slate-100 text-slate-800">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamingText}</ReactMarkdown>
              </div>
              <span className="inline-block w-1.5 h-4 bg-blue-500 animate-pulse ml-0.5 align-middle" />
            </div>
          </div>
        )}

        {/* 来源脚注 */}
        {sourcesMd && !streamingText && messages.at(-1)?.role === 'assistant' && (
          <div className="text-xs text-slate-500 bg-slate-50 rounded-lg p-3 border border-slate-100 prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{sourcesMd}</ReactMarkdown>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 示例问题 */}
      <div className="flex gap-2 mt-2 flex-wrap">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => { setInput(ex) }}
            className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full hover:bg-slate-200 transition-colors"
          >
            {ex}
          </button>
        ))}
      </div>

      {/* 输入区 */}
      <div className="flex gap-2 mt-2">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入问题，Enter 发送，Shift+Enter 换行…"
          rows={2}
          className="flex-1 resize-none text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />
        <div className="flex flex-col gap-1">
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? '…' : '发送'}
          </button>
          <button
            onClick={clearMessages}
            disabled={loading}
            className="px-4 py-1 bg-slate-200 text-slate-600 text-xs rounded-lg hover:bg-slate-300 disabled:opacity-50 transition-colors"
          >
            清空
          </button>
        </div>
      </div>
    </div>
  )
}
