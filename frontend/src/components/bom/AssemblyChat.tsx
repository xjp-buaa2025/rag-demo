// ============================================================
// AssemblyChat — 装配方案融合问答
//
// 对应 Gradio Tab 2 的装配方案 Chatbot 区域。
// 与 RagChat 结构相同，差异：
//   1. 调用 /api/assembly/chat（双路融合：BOM 图谱 + RAG 知识库）
//   2. 来源脚注同时含 BOM 数据来源 + 知识库参考
//   3. 示例问题为装配相关
// ============================================================

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChat } from '../../hooks/useChat'
import { postAssemblyChat } from '../../api/client'

const EXAMPLES = [
  '请生成高压涡轮的装配方案',
  '风扇叶片的装配顺序和力矩要求是什么？',
  '燃烧室火焰筒的装配注意事项有哪些？',
]

export default function AssemblyChat() {
  const { messages, streamingText, sourcesMd, loading, sendMessage, clearMessages } = useChat()
  const [input, setInput] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return
    setInput('')
    await sendMessage(text, postAssemblyChat(text, messages))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* 说明 */}
      <p className="text-xs text-slate-500 mb-2">
        🔩 同时查询 Neo4j BOM 图谱 + ChromaDB 知识库，融合生成装配方案
      </p>

      {/* 消息列表 */}
      <div className="flex-1 overflow-y-auto space-y-4 p-4 bg-white rounded-lg border border-slate-200 min-h-[460px] max-h-[560px]">
        {messages.length === 0 && !streamingText && (
          <div className="text-center text-slate-400 text-sm pt-8">
            <p className="text-2xl mb-2">🔧</p>
            <p>请输入装配相关问题，大臣将融合 BOM 图谱和技术知识库生成方案</p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-orange-500 text-white'
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

        {/* 流式输出 */}
        {streamingText && (
          <div className="flex justify-start">
            <div className="max-w-[85%] rounded-2xl px-4 py-2 text-sm bg-slate-100 text-slate-800">
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamingText}</ReactMarkdown>
              </div>
              <span className="inline-block w-1.5 h-4 bg-orange-500 animate-pulse ml-0.5 align-middle" />
            </div>
          </div>
        )}

        {/* 来源脚注（BOM + 知识库双来源） */}
        {sourcesMd && !streamingText && messages.at(-1)?.role === 'assistant' && (
          <div className="text-xs text-slate-500 bg-amber-50 rounded-lg p-3 border border-amber-100 prose prose-sm max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{sourcesMd}</ReactMarkdown>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 示例 */}
      <div className="flex gap-2 mt-2 flex-wrap">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setInput(ex)}
            className="text-xs px-3 py-1 bg-orange-50 text-orange-700 rounded-full hover:bg-orange-100 transition-colors"
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
          placeholder="输入装配问题，Enter 发送，Shift+Enter 换行…"
          rows={2}
          className="flex-1 resize-none text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-orange-500 focus:ring-1 focus:ring-orange-500"
        />
        <div className="flex flex-col gap-1">
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="px-4 py-2 bg-orange-500 text-white text-sm rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
