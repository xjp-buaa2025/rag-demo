// ============================================================
// RagChat — RAG 知识库问答聊天框（图文检索版）
//
// 新增功能：
//   - 📷 图片上传按钮（点击选择 / 粘贴图片）
//   - 发送时若有待发图片，先调 /vision/describe 生成描述，拼入 message
//   - 回答完成后，来源脚注下方展示相关图片缩略图（可点击放大）
// ============================================================

import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChat } from '../../hooks/useChat'
import { postChat, postVisionDescribe } from '../../api/client'

const EXAMPLES = [
  '涡轮发动机的基本工作原理是什么？',
  '压气机有哪些主要类型？',
  '燃烧室的设计需要满足哪些基本要求？',
]

export default function RagChat() {
  const { messages, streamingText, sourcesMd, imageUrls, loading, sendMessage, clearMessages } = useChat()
  const [input, setInput] = useState('')
  const [pendingImage, setPendingImage] = useState<File | null>(null)
  const [pendingPreviewUrl, setPendingPreviewUrl] = useState<string | null>(null)
  const [isDescribing, setIsDescribing] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // 消息更新时自动滚到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  // 清理 preview URL（防止内存泄露）
  useEffect(() => {
    return () => {
      if (pendingPreviewUrl) URL.revokeObjectURL(pendingPreviewUrl)
    }
  }, [pendingPreviewUrl])

  const handleImageSelect = (file: File) => {
    if (pendingPreviewUrl) URL.revokeObjectURL(pendingPreviewUrl)
    setPendingImage(file)
    setPendingPreviewUrl(URL.createObjectURL(file))
  }

  const clearPendingImage = () => {
    if (pendingPreviewUrl) URL.revokeObjectURL(pendingPreviewUrl)
    setPendingImage(null)
    setPendingPreviewUrl(null)
  }

  // 支持粘贴图片
  const handlePaste = (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items
    if (!items) return
    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) handleImageSelect(file)
        break
      }
    }
  }

  const handleSend = async () => {
    const text = input.trim()
    if ((!text && !pendingImage) || loading || isDescribing) return

    let finalMessage = text

    // 若有待发图片：先获取 Vision 描述，拼入 message
    if (pendingImage) {
      setIsDescribing(true)
      try {
        const { description } = await postVisionDescribe(pendingImage)
        const prefix = `[图片内容：${description}]`
        finalMessage = text ? `${prefix}\n${text}` : prefix
      } catch {
        finalMessage = text || '请帮我分析这张图片中的相关内容。'
      } finally {
        setIsDescribing(false)
      }
    }

    clearPendingImage()
    setInput('')
    await sendMessage(finalMessage, postChat(finalMessage, messages))
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isBusy = loading || isDescribing

  return (
    <div className="flex flex-col h-full">
      {/* 消息列表 */}
      <div
        className="flex-1 overflow-y-auto space-y-4 p-4 bg-white rounded-lg border border-slate-200 min-h-[420px] max-h-[520px]"
        onPaste={handlePaste}
      >
        {messages.length === 0 && !streamingText && (
          <div className="text-center text-slate-400 text-sm pt-8">
            <p className="text-2xl mb-2">🤖</p>
            <p>有什么想问的？可以从下方示例开始，或上传图片以图搜文</p>
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

        {/* 来源脚注 + 相关图片展示 */}
        {!streamingText && messages.at(-1)?.role === 'assistant' && (
          <>
            {sourcesMd && (
              <div className="text-xs text-slate-500 bg-slate-50 rounded-lg p-3 border border-slate-100 prose prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{sourcesMd}</ReactMarkdown>
              </div>
            )}
            {imageUrls.length > 0 && (
              <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                <p className="text-xs text-slate-500 mb-2">🖼️ 相关图片</p>
                <div className="flex flex-wrap gap-2">
                  {imageUrls.map((url, idx) => (
                    <a key={idx} href={url} target="_blank" rel="noopener noreferrer">
                      <img
                        src={url}
                        alt={`相关图片${idx + 1}`}
                        className="h-24 w-auto rounded border border-slate-200 cursor-zoom-in hover:border-blue-400 transition-colors object-cover"
                      />
                    </a>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 示例问题 */}
      <div className="flex gap-2 mt-2 flex-wrap">
        {EXAMPLES.map((ex) => (
          <button
            key={ex}
            onClick={() => setInput(ex)}
            className="text-xs px-3 py-1 bg-slate-100 text-slate-600 rounded-full hover:bg-slate-200 transition-colors"
          >
            {ex}
          </button>
        ))}
      </div>

      {/* 待发图片预览 */}
      {pendingPreviewUrl && (
        <div className="flex items-center gap-2 mt-2 p-2 bg-blue-50 border border-blue-200 rounded-lg">
          <img src={pendingPreviewUrl} alt="待发送图片"
               className="h-12 w-auto rounded border border-blue-200 object-cover" />
          <span className="text-xs text-blue-600 flex-1">图片已选择，发送后将自动生成描述并检索</span>
          <button
            onClick={clearPendingImage}
            className="text-xs text-slate-400 hover:text-red-500 transition-colors px-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* 输入区 */}
      <div className="flex gap-2 mt-2">
        {/* 隐藏的文件输入 */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) handleImageSelect(file)
            e.target.value = ''  // 允许重复选择同一文件
          }}
        />

        {/* 图片上传按钮 */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={isBusy}
          title="上传图片（支持粘贴）"
          className="px-3 py-2 bg-slate-100 text-slate-600 text-sm rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors"
        >
          📷
        </button>

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder={pendingImage ? '（可选）补充说明，Enter 发送…' : '输入问题，Enter 发送，Shift+Enter 换行，或粘贴图片…'}
          rows={2}
          className="flex-1 resize-none text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
        />

        <div className="flex flex-col gap-1">
          <button
            onClick={handleSend}
            disabled={isBusy || (!input.trim() && !pendingImage)}
            className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isDescribing ? '分析…' : loading ? '…' : '发送'}
          </button>
          <button
            onClick={clearMessages}
            disabled={isBusy}
            className="px-4 py-1 bg-slate-200 text-slate-600 text-xs rounded-lg hover:bg-slate-300 disabled:opacity-50 transition-colors"
          >
            清空
          </button>
        </div>
      </div>
    </div>
  )
}
