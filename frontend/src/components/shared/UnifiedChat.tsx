// ============================================================
// UnifiedChat — 统一聊天组件（合并 RagChat + AssemblyChat）
//
// 模式切换：📖 知识库问答（RAG）| 🔩 装配问答（Assembly）
// - RAG 模式：文本 + 图片上传 → /chat（Qdrant 向量检索）
// - 装配模式：文本 → /assembly/chat（Neo4j BOM + Qdrant 融合）
//
// 布局：双栏（左：聊天消息区 / 右：来源溯源侧边栏）
// ============================================================

import { useEffect, useRef, useState } from 'react'
import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useChat } from '../../hooks/useChat'
import { postChat, postAssemblyChat, postVisionDescribe, postVisionSearch } from '../../api/client'
import { SourceCard } from './SourceCard'

type ChatMode = 'rag' | 'assembly'

const THEMES = {
  rag: {
    userBubble: 'bg-blue-600',
    sendBtn: 'bg-blue-600 hover:bg-blue-700',
    focusRing: 'focus:border-blue-500 focus:ring-blue-500',
    cursor: 'bg-blue-500',
    dots: 'bg-blue-400',
    badge: 'text-blue-700 bg-blue-100 hover:bg-blue-200 active:bg-blue-300 border-blue-300',
    activeLabel: 'text-blue-500',
    preview: 'bg-blue-50 border-blue-200',
    previewText: 'text-blue-600',
    exampleBg: 'bg-slate-100 text-slate-600',
    sourceTheme: 'blue' as const,
  },
  assembly: {
    userBubble: 'bg-orange-500',
    sendBtn: 'bg-orange-500 hover:bg-orange-600',
    focusRing: 'focus:border-orange-500 focus:ring-orange-500',
    cursor: 'bg-orange-500',
    dots: 'bg-orange-400',
    badge: 'text-orange-700 bg-orange-100 hover:bg-orange-200 active:bg-orange-300 border-orange-300',
    activeLabel: 'text-orange-500',
    preview: 'bg-orange-50 border-orange-200',
    previewText: 'text-orange-600',
    exampleBg: 'bg-orange-50 text-orange-700',
    sourceTheme: 'orange' as const,
  },
}

const EXAMPLES = {
  rag: [
    '涡轮发动机的基本工作原理是什么？',
    '压气机有哪些主要类型？',
    '燃烧室的设计需要满足哪些基本要求？',
  ],
  assembly: [
    '请生成高压涡轮的装配方案',
    '风扇叶片的装配顺序和力矩要求是什么？',
    '燃烧室火焰筒的装配注意事项有哪些？',
  ],
}

const EMPTY_STATE = {
  rag: { icon: '🤖', text: '有什么想问的？可以从下方示例开始，或上传图片以图搜文' },
  assembly: { icon: '🔧', text: '请输入装配相关问题，将融合 BOM 图谱和技术知识库生成方案' },
}

// ─── 行内引用处理 ───────────────────────────────────────────

function processChildren(
  children: React.ReactNode,
  onCite: (id: number) => void,
  badgeClass: string,
): React.ReactNode {
  if (typeof children === 'string') {
    const parts = children.split(/(\[\d+\])/)
    if (parts.length === 1) return children
    return parts.map((part, i) => {
      const m = part.match(/^\[(\d+)\]$/)
      if (m) {
        const id = parseInt(m[1])
        return (
          <button
            key={i}
            onClick={() => onCite(id)}
            title={`跳转到来源 [${id}]`}
            className={`inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 text-[10px] font-bold rounded-full cursor-pointer border mx-0.5 align-super transition-colors leading-none ${badgeClass}`}
          >
            {id}
          </button>
        )
      }
      return part || null
    })
  }

  if (Array.isArray(children)) {
    return children.map((child, i) => (
      <React.Fragment key={i}>{processChildren(child, onCite, badgeClass)}</React.Fragment>
    ))
  }

  if (React.isValidElement<{ children?: React.ReactNode }>(children) && children.props.children) {
    return React.cloneElement(children, {
      children: processChildren(children.props.children, onCite, badgeClass),
    })
  }

  return children
}

// ReactMarkdown 图片组件
const imgComponent = ({ src, alt, ...props }: React.ImgHTMLAttributes<HTMLImageElement>) => (
  <img
    src={src}
    alt={alt || ''}
    {...props}
    className="max-w-full rounded border border-slate-200 my-2 cursor-zoom-in hover:border-blue-400 transition-colors"
    onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
    onClick={() => src && window.open(src, '_blank')}
  />
)

// ─── 主组件 ─────────────────────────────────────────────────

export default function UnifiedChat() {
  const { messages, streamingText, sources, imageUrls, loading, currentStage, sendMessage, clearMessages } = useChat()
  const [mode, setMode] = useState<ChatMode>('rag')
  const [input, setInput] = useState('')
  const [pendingImage, setPendingImage] = useState<File | null>(null)
  const [pendingPreviewUrl, setPendingPreviewUrl] = useState<string | null>(null)
  const [isDescribing, setIsDescribing] = useState(false)
  const [activeSource, setActiveSource] = useState<number | null>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const sidebarRef = useRef<HTMLDivElement>(null)

  const theme = THEMES[mode]

  // 消息更新时自动滚到底部
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  // 新问题发送时重置激活来源
  useEffect(() => {
    if (loading) setActiveSource(null)
  }, [loading])

  // 清理 preview URL
  useEffect(() => {
    return () => { if (pendingPreviewUrl) URL.revokeObjectURL(pendingPreviewUrl) }
  }, [pendingPreviewUrl])

  // ─── 模式切换 ─────────────────────────────────────────
  const handleModeSwitch = (newMode: ChatMode) => {
    if (newMode === mode || loading || isDescribing) return
    clearPendingImage()
    clearMessages()
    setMode(newMode)
    setInput('')
  }

  // ─── 引用点击 ─────────────────────────────────────────
  const handleCiteClick = (id: number) => {
    setActiveSource(id)
    document.getElementById(`source-card-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
  }

  // 构建行内引用感知的 ReactMarkdown 组件映射
  const mdComponents = {
    img: imgComponent,
    p: ({ children }: { children?: React.ReactNode }) => (
      <p>{processChildren(children, handleCiteClick, theme.badge)}</p>
    ),
    li: ({ children }: { children?: React.ReactNode }) => (
      <li>{processChildren(children, handleCiteClick, theme.badge)}</li>
    ),
    td: ({ children }: { children?: React.ReactNode }) => (
      <td>{processChildren(children, handleCiteClick, theme.badge)}</td>
    ),
  }

  // ─── 图片处理（仅 RAG 模式）─────────────────────────────
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

  const handlePaste = (e: React.ClipboardEvent) => {
    if (mode !== 'rag') return
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

  // ─── 发送消息 ─────────────────────────────────────────
  const handleSend = async () => {
    const text = input.trim()
    if ((!text && !pendingImage) || loading || isDescribing) return

    if (mode === 'rag') {
      let finalMessage = text
      let imageChunks: Array<{ text: string; source: string; page: number; distance: number; image_url?: string }> | undefined

      if (pendingImage) {
        setIsDescribing(true)
        try {
          const [describeResult, searchResult] = await Promise.allSettled([
            postVisionDescribe(pendingImage),
            postVisionSearch(pendingImage),
          ])
          if (describeResult.status === 'fulfilled') {
            const prefix = `[图片内容：${describeResult.value.description}]`
            finalMessage = text ? `${prefix}\n${text}` : prefix
          } else {
            finalMessage = text || '请根据检索到的知识库内容回答，若有相关图片请展示。'
          }
          if (searchResult.status === 'fulfilled' && searchResult.value.results.length > 0) {
            imageChunks = searchResult.value.results
          }
        } finally {
          setIsDescribing(false)
        }
      }

      clearPendingImage()
      setInput('')
      await sendMessage(finalMessage, postChat(finalMessage, messages, imageChunks))
    } else {
      // assembly 模式
      if (!text) return
      setInput('')
      await sendMessage(text, postAssemblyChat(text, messages))
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isBusy = loading || isDescribing
  const hasSources = sources.length > 0

  return (
    <div className="flex flex-col h-full gap-2">

      {/* ── 模式切换 ── */}
      <div className="flex items-center gap-2">
        <div className="inline-flex rounded-lg border border-slate-200 p-0.5 bg-slate-100">
          <button
            onClick={() => handleModeSwitch('rag')}
            disabled={isBusy}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
              mode === 'rag'
                ? 'bg-white text-blue-600 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            } ${isBusy ? 'cursor-not-allowed opacity-60' : ''}`}
          >
            📖 知识库问答
          </button>
          <button
            onClick={() => handleModeSwitch('assembly')}
            disabled={isBusy}
            className={`px-4 py-1.5 text-sm font-medium rounded-md transition-colors ${
              mode === 'assembly'
                ? 'bg-white text-orange-600 shadow-sm'
                : 'text-slate-500 hover:text-slate-700'
            } ${isBusy ? 'cursor-not-allowed opacity-60' : ''}`}
          >
            🔩 装配问答
          </button>
        </div>
        {mode === 'assembly' && (
          <span className="text-xs text-slate-500">
            同时查询 Neo4j BOM 图谱 + Qdrant 知识库，融合生成装配方案
          </span>
        )}
      </div>

      {/* ── 主区域：聊天 + 侧边栏 ── */}
      <div className="flex gap-3 flex-1 min-h-0">

        {/* 聊天消息区 */}
        <div
          className="flex-1 overflow-y-auto space-y-4 p-4 bg-white rounded-lg border border-slate-200 min-h-[420px] max-h-[520px]"
          onPaste={handlePaste}
        >
          {messages.length === 0 && !streamingText && (
            <div className="text-center text-slate-400 text-sm pt-8">
              <p className="text-2xl mb-2">{EMPTY_STATE[mode].icon}</p>
              <p>{EMPTY_STATE[mode].text}</p>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[85%] rounded-2xl px-4 py-2 text-sm ${
                  msg.role === 'user'
                    ? `${theme.userBubble} text-white`
                    : 'bg-slate-100 text-slate-800'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                ) : (
                  <span className="whitespace-pre-wrap">{msg.content}</span>
                )}
              </div>
            </div>
          ))}

          {/* 阶段状态指示器 */}
          {loading && !streamingText && currentStage && (
            <div className="flex justify-start">
              <div className="flex items-center gap-2 rounded-2xl px-4 py-2 text-sm bg-slate-50 text-slate-500 border border-slate-200">
                <span className="inline-flex gap-1">
                  <span className={`w-1.5 h-1.5 rounded-full ${theme.dots} animate-bounce [animation-delay:0ms]`} />
                  <span className={`w-1.5 h-1.5 rounded-full ${theme.dots} animate-bounce [animation-delay:150ms]`} />
                  <span className={`w-1.5 h-1.5 rounded-full ${theme.dots} animate-bounce [animation-delay:300ms]`} />
                </span>
                <span>{currentStage}</span>
              </div>
            </div>
          )}

          {/* 流式输出中的 assistant 消息 */}
          {streamingText && (
            <div className="flex justify-start">
              <div className="max-w-[85%] rounded-2xl px-4 py-2 text-sm bg-slate-100 text-slate-800">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]} components={mdComponents}>
                    {streamingText}
                  </ReactMarkdown>
                </div>
                <span className={`inline-block w-1.5 h-4 ${theme.cursor} animate-pulse ml-0.5 align-middle`} />
              </div>
            </div>
          )}

          {/* 图片展示（仅 RAG 模式，无侧边栏时） */}
          {mode === 'rag' && !streamingText && !hasSources && messages.at(-1)?.role === 'assistant' && imageUrls.length > 0 && (
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

          <div ref={bottomRef} />
        </div>

        {/* 来源溯源侧边栏 */}
        {hasSources && (
          <aside
            ref={sidebarRef}
            className="w-64 shrink-0 flex flex-col gap-2 overflow-y-auto max-h-[520px] min-h-[420px]"
          >
            <div className="sticky top-0 bg-slate-50 z-10 px-1 py-1.5 border-b border-slate-200 rounded-t-lg">
              <div className="text-[11px] font-semibold text-slate-500 uppercase tracking-wide flex items-center gap-1.5">
                <span>📚</span>
                <span>引用来源</span>
                <span className="ml-auto inline-flex items-center justify-center w-4 h-4 text-[10px] font-bold bg-slate-200 text-slate-600 rounded-full">
                  {sources.length}
                </span>
              </div>
              {activeSource && (
                <div className={`text-[10px] ${theme.activeLabel} mt-0.5`}>
                  当前查看：来源 [{activeSource}]
                </div>
              )}
            </div>

            {sources.map((src) => (
              <SourceCard
                key={src.id}
                src={src}
                active={activeSource === src.id}
                theme={theme.sourceTheme}
                onClick={() => setActiveSource(activeSource === src.id ? null : src.id)}
              />
            ))}
          </aside>
        )}
      </div>

      {/* ── 示例问题 ── */}
      <div className="flex gap-2 flex-wrap">
        {EXAMPLES[mode].map((ex) => (
          <button
            key={ex}
            onClick={() => setInput(ex)}
            className={`text-xs px-3 py-1 rounded-full hover:opacity-80 transition-colors ${theme.exampleBg}`}
          >
            {ex}
          </button>
        ))}
      </div>

      {/* ── 待发图片预览（仅 RAG 模式）── */}
      {mode === 'rag' && pendingPreviewUrl && (
        <div className={`flex items-center gap-2 p-2 ${theme.preview} border rounded-lg`}>
          <img src={pendingPreviewUrl} alt="待发送图片"
               className="h-12 w-auto rounded border border-blue-200 object-cover" />
          <span className={`text-xs ${theme.previewText} flex-1`}>图片已选择，发送后将自动生成描述并检索</span>
          <button
            onClick={clearPendingImage}
            className="text-xs text-slate-400 hover:text-red-500 transition-colors px-1"
          >
            ✕
          </button>
        </div>
      )}

      {/* ── 输入区 ── */}
      <div className="flex gap-2">
        {/* 图片上传按钮（仅 RAG 模式） */}
        {mode === 'rag' && (
          <>
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) handleImageSelect(file)
                e.target.value = ''
              }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isBusy}
              title="上传图片（支持粘贴）"
              className="px-3 py-2 bg-slate-100 text-slate-600 text-sm rounded-lg hover:bg-slate-200 disabled:opacity-50 transition-colors"
            >
              📷
            </button>
          </>
        )}

        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onPaste={handlePaste}
          placeholder={
            mode === 'rag'
              ? (pendingImage ? '（可选）补充说明，Enter 发送…' : '输入问题，Enter 发送，Shift+Enter 换行，或粘贴图片…')
              : '输入装配问题，Enter 发送，Shift+Enter 换行…'
          }
          rows={2}
          className={`flex-1 resize-none text-sm border border-slate-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-1 ${theme.focusRing}`}
        />

        <div className="flex flex-col gap-1">
          <button
            onClick={handleSend}
            disabled={isBusy || (!input.trim() && !pendingImage)}
            className={`px-4 py-2 text-white text-sm rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors ${theme.sendBtn}`}
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
